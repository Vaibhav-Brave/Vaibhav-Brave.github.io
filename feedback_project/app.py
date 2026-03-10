# =============================================
# AI Feedback Intelligence System
# Main Application File (app.py)
# =============================================

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import mysql.connector
import nltk
from textblob import TextBlob
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend (required for Flask)
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os
import io
import base64
import json
from datetime import datetime

# ── Download required NLTK data (only needed once) ──────────────────────────
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# ── Initialize Flask app ─────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'  # Used for flash messages

# ── Database Configuration ───────────────────────────────────────────────────
# Change these values to match your MySQL setup
DB_CONFIG = {
    'host': 'localhost',
    'user': 'vaibhav',
    'password': '123456',
    'database': 'feedback_db'
}

# ── Helper: Get database connection ─────────────────────────────────────────
def get_db():
    """Returns a new MySQL database connection."""
    return mysql.connector.connect(**DB_CONFIG)


# ── Helper: Analyze sentiment of a text ─────────────────────────────────────
def analyze_sentiment(text):
    """
    Uses TextBlob to analyze sentiment.
    Returns a dict with sentiment label, polarity score, and subjectivity score.
    
    Polarity:     -1.0 = very negative,  0 = neutral,  +1.0 = very positive
    Subjectivity:  0.0 = very objective,              +1.0 = very subjective
    """
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 4)
    subjectivity = round(blob.sentiment.subjectivity, 4)

    # Classify sentiment based on polarity score
    if polarity > 0.1:
        sentiment = 'positive'
    elif polarity < -0.1:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'

    return {
        'sentiment': sentiment,
        'polarity': polarity,
        'subjectivity': subjectivity
    }


# ── Helper: Generate a chart and return it as a base64 image string ──────────
def fig_to_base64(fig):
    """Converts a matplotlib figure to a base64 string for embedding in HTML."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


# ════════════════════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════════════════════

# ── Home / Dashboard ─────────────────────────────────────────────────────────
@app.route('/')
def dashboard():
    """Main dashboard showing analytics and recent feedback."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Get total counts by sentiment
    cursor.execute("""
        SELECT sentiment, COUNT(*) as count 
        FROM feedback 
        GROUP BY sentiment
    """)
    sentiment_counts = {row['sentiment']: row['count'] for row in cursor.fetchall()}

    # Get total feedback count
    cursor.execute("SELECT COUNT(*) as total FROM feedback")
    total = cursor.fetchone()['total']

    # Get recent 10 feedbacks
    cursor.execute("""
        SELECT id, text, sentiment, polarity, category, created_at 
        FROM feedback 
        ORDER BY created_at DESC 
        LIMIT 10
    """)
    recent_feedback = cursor.fetchall()

    # Get average polarity
    cursor.execute("SELECT AVG(polarity) as avg_polarity FROM feedback")
    avg_polarity = round(cursor.fetchone()['avg_polarity'] or 0, 3)

    cursor.close()
    db.close()

    # ── Generate Charts ───────────────────────────────────────────────────

    # Chart 1: Sentiment Pie Chart
    pie_chart = None
    if sentiment_counts:
        labels = list(sentiment_counts.keys())
        sizes = list(sentiment_counts.values())
        colors = {'positive': '#28a745', 'negative': '#dc3545', 'neutral': '#ffc107'}
        chart_colors = [colors.get(l, '#6c757d') for l in labels]

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.pie(sizes, labels=labels, colors=chart_colors, autopct='%1.1f%%',
               startangle=90, textprops={'fontsize': 12})
        ax.set_title('Sentiment Distribution', fontsize=14, fontweight='bold')
        pie_chart = fig_to_base64(fig)

    # Chart 2: Polarity Bar Chart (last 20 feedbacks)
    polarity_chart = None
    db2 = get_db()
    cursor2 = db2.cursor(dictionary=True)
    cursor2.execute("SELECT id, polarity, sentiment FROM feedback ORDER BY created_at DESC LIMIT 20")
    polarity_data = cursor2.fetchall()
    cursor2.close()
    db2.close()

    if polarity_data:
        ids = [str(row['id']) for row in reversed(polarity_data)]
        polarities = [row['polarity'] for row in reversed(polarity_data)]
        bar_colors = ['#28a745' if p > 0.1 else '#dc3545' if p < -0.1 else '#ffc107'
                      for p in polarities]

        fig2, ax2 = plt.subplots(figsize=(8, 3.5))
        ax2.bar(ids, polarities, color=bar_colors, edgecolor='white')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax2.set_xlabel('Feedback ID', fontsize=10)
        ax2.set_ylabel('Polarity Score', fontsize=10)
        ax2.set_title('Polarity Scores (Last 20 Feedbacks)', fontsize=12, fontweight='bold')
        ax2.set_ylim(-1.1, 1.1)
        plt.xticks(rotation=45, fontsize=8)
        plt.tight_layout()
        polarity_chart = fig_to_base64(fig2)

    return render_template('dashboard.html',
                           total=total,
                           sentiment_counts=sentiment_counts,
                           recent_feedback=recent_feedback,
                           avg_polarity=avg_polarity,
                           pie_chart=pie_chart,
                           polarity_chart=polarity_chart)


# ── Submit Single Feedback ───────────────────────────────────────────────────
@app.route('/submit', methods=['GET', 'POST'])
def submit_feedback():
    """Page to manually enter a single feedback."""
    if request.method == 'POST':
        text = request.form.get('feedback_text', '').strip()
        category = request.form.get('category', 'general').strip()

        if not text:
            flash('Please enter some feedback text.', 'warning')
            return redirect(url_for('submit_feedback'))

        if len(text) < 5:
            flash('Feedback is too short. Please enter at least 5 characters.', 'warning')
            return redirect(url_for('submit_feedback'))

        # Analyze the sentiment
        result = analyze_sentiment(text)

        # Save to database
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO feedback (text, source, sentiment, polarity, subjectivity, category)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (text, 'manual', result['sentiment'], result['polarity'], result['subjectivity'], category))
        db.commit()
        new_id = cursor.lastrowid
        cursor.close()
        db.close()

        flash(f'Feedback saved! Sentiment detected: {result["sentiment"].upper()} '
              f'(Polarity: {result["polarity"]})', 'success')
        return redirect(url_for('view_feedback', feedback_id=new_id))

    return render_template('submit.html')


# ── Upload CSV File ───────────────────────────────────────────────────────────
@app.route('/upload', methods=['GET', 'POST'])
def upload_csv():
    """Upload a CSV file containing multiple feedbacks for batch analysis."""
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            flash('No file selected.', 'warning')
            return redirect(url_for('upload_csv'))

        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected.', 'warning')
            return redirect(url_for('upload_csv'))

        if not file.filename.endswith('.csv'):
            flash('Only CSV files are supported.', 'danger')
            return redirect(url_for('upload_csv'))

        # Read the CSV into a DataFrame
        try:
            df = pd.read_csv(file)
        except Exception as e:
            flash(f'Could not read CSV file: {str(e)}', 'danger')
            return redirect(url_for('upload_csv'))

        # Look for a column named 'text', 'feedback', or 'comment'
        text_column = None
        for col in ['text', 'feedback', 'comment', 'review', 'message']:
            if col in df.columns.str.lower().tolist():
                text_column = col
                break

        if text_column is None:
            flash('CSV must have a column named "text", "feedback", "comment", or "review".', 'danger')
            return redirect(url_for('upload_csv'))

        # Process each row
        db = get_db()
        cursor = db.cursor()
        saved_count = 0
        skipped_count = 0

        for _, row in df.iterrows():
            text = str(row[text_column]).strip()
            if not text or text == 'nan' or len(text) < 5:
                skipped_count += 1
                continue

            category = str(row.get('category', 'general')).strip() if 'category' in df.columns else 'general'
            result = analyze_sentiment(text)

            cursor.execute("""
                INSERT INTO feedback (text, source, sentiment, polarity, subjectivity, category)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (text, 'csv_upload', result['sentiment'], result['polarity'], result['subjectivity'], category))
            saved_count += 1

        db.commit()
        cursor.close()
        db.close()

        flash(f'CSV processed! {saved_count} feedbacks saved, {skipped_count} rows skipped.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('upload.html')


# ── View All Feedback ─────────────────────────────────────────────────────────
@app.route('/all-feedback')
def all_feedback():
    """Shows all feedback with filter options."""
    sentiment_filter = request.args.get('sentiment', 'all')
    category_filter = request.args.get('category', 'all')

    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Build dynamic query based on filters
    query = "SELECT * FROM feedback WHERE 1=1"
    params = []

    if sentiment_filter != 'all':
        query += " AND sentiment = %s"
        params.append(sentiment_filter)

    if category_filter != 'all':
        query += " AND category = %s"
        params.append(category_filter)

    query += " ORDER BY created_at DESC"
    cursor.execute(query, params)
    feedbacks = cursor.fetchall()

    # Get all unique categories for filter dropdown
    cursor.execute("SELECT DISTINCT category FROM feedback ORDER BY category")
    categories = [row['category'] for row in cursor.fetchall()]

    cursor.close()
    db.close()

    return render_template('all_feedback.html',
                           feedbacks=feedbacks,
                           categories=categories,
                           sentiment_filter=sentiment_filter,
                           category_filter=category_filter)


# ── View Single Feedback ──────────────────────────────────────────────────────
@app.route('/feedback/<int:feedback_id>')
def view_feedback(feedback_id):
    """Shows detailed view of a single feedback."""
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM feedback WHERE id = %s", (feedback_id,))
    feedback = cursor.fetchone()
    cursor.close()
    db.close()

    if not feedback:
        flash('Feedback not found.', 'danger')
        return redirect(url_for('all_feedback'))

    return render_template('view_feedback.html', feedback=feedback)


# ── Delete Feedback ───────────────────────────────────────────────────────────
@app.route('/delete/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    """Deletes a feedback entry."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM feedback WHERE id = %s", (feedback_id,))
    db.commit()
    cursor.close()
    db.close()
    flash('Feedback deleted.', 'info')
    return redirect(url_for('all_feedback'))


# ── Analytics Page ────────────────────────────────────────────────────────────
@app.route('/analytics')
def analytics():
    """Detailed analytics page with multiple charts."""
    db = get_db()
    cursor = db.cursor(dictionary=True)

    # Sentiment counts
    cursor.execute("SELECT sentiment, COUNT(*) as count FROM feedback GROUP BY sentiment")
    sentiment_data = cursor.fetchall()

    # Category breakdown
    cursor.execute("SELECT category, COUNT(*) as count FROM feedback GROUP BY category ORDER BY count DESC LIMIT 8")
    category_data = cursor.fetchall()

    # All polarity values for histogram
    cursor.execute("SELECT polarity FROM feedback")
    all_polarities = [row['polarity'] for row in cursor.fetchall()]

    cursor.close()
    db.close()

    charts = {}

    # Chart 1: Category Bar Chart
    if category_data:
        cats = [row['category'] for row in category_data]
        counts = [row['count'] for row in category_data]
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.barh(cats, counts, color='#028090', edgecolor='white')
        ax.set_xlabel('Number of Feedbacks')
        ax.set_title('Feedback by Category', fontsize=13, fontweight='bold')
        for bar, count in zip(bars, counts):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                    str(count), va='center', fontsize=10)
        plt.tight_layout()
        charts['category'] = fig_to_base64(fig)

    # Chart 2: Polarity Distribution Histogram
    if all_polarities:
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        ax2.hist(all_polarities, bins=20, color='#1A2B5E', edgecolor='white', alpha=0.85)
        ax2.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='Neutral threshold')
        ax2.set_xlabel('Polarity Score')
        ax2.set_ylabel('Number of Feedbacks')
        ax2.set_title('Polarity Distribution', fontsize=13, fontweight='bold')
        ax2.legend()
        plt.tight_layout()
        charts['histogram'] = fig_to_base64(fig2)

    # Chart 3: Word Cloud (from all feedback text)
    db3 = get_db()
    cursor3 = db3.cursor(dictionary=True)
    cursor3.execute("SELECT text FROM feedback")
    all_texts = ' '.join([row['text'] for row in cursor3.fetchall()])
    cursor3.close()
    db3.close()

    if all_texts.strip():
        wc = WordCloud(width=700, height=350, background_color='white',
                       colormap='Blues', max_words=60,
                       stopwords=set(nltk.corpus.stopwords.words('english'))).generate(all_texts)
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        ax3.imshow(wc, interpolation='bilinear')
        ax3.axis('off')
        ax3.set_title('Most Common Words in Feedback', fontsize=13, fontweight='bold')
        plt.tight_layout()
        charts['wordcloud'] = fig_to_base64(fig3)

    return render_template('analytics.html', charts=charts, sentiment_data=sentiment_data)


# ── API: Analyze text without saving ─────────────────────────────────────────
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Quick API endpoint to analyze text on-the-fly (used by the live preview)."""
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    result = analyze_sentiment(text)
    return jsonify(result)


# ════════════════════════════════════════════════════════════════════════════
# Run the app
# ════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 50)
    print("  AI Feedback Intelligence System")
    print("  Running at: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
