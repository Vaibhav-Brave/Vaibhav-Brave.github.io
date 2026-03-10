# AI-Driven Comment / Feedback Intelligence System
### S.M Joshi College – Final Year Project

---

## What This Project Does

This is a **Flask web application** that:
- Accepts text feedback (manually or via CSV upload)
- Analyzes each feedback using **AI / NLP (TextBlob)**
- Labels it as **Positive, Negative, or Neutral**
- Stores everything in a **MySQL database**
- Shows a **dashboard** with charts, word clouds, and statistics

---

## Project Folder Structure

```
feedback_project/
│
├── app.py                  ← Main Python file (Flask app + all routes)
├── requirements.txt        ← List of Python packages to install
├── setup_database.sql      ← Run this in MySQL to create the database
├── README.md               ← This file
│
└── templates/              ← HTML pages (Jinja2 templates)
    ├── base.html           ← Shared layout (sidebar, header)
    ├── dashboard.html      ← Home page with stats and charts
    ├── submit.html         ← Form to submit one feedback
    ├── upload.html         ← Upload a CSV file
    ├── all_feedback.html   ← View and filter all feedback
    ├── view_feedback.html  ← Detailed view of one feedback
    └── analytics.html      ← Charts: word cloud, histogram, etc.
```

---

## Step-by-Step Setup Guide

### STEP 1 — Install Python
- Download Python 3.10 or newer from https://python.org
- During install, check the box **"Add Python to PATH"**
- Verify: open Command Prompt and type `python --version`

---

### STEP 2 — Install MySQL
- Download MySQL Community Server from https://dev.mysql.com/downloads/
- During setup, set a root password (remember it!)
- Also install **MySQL Workbench** (easier to manage the database)

---

### STEP 3 — Create the Database
1. Open **MySQL Workbench** (or MySQL command line)
2. Open the file `setup_database.sql` from this folder
3. Click **Run** (the lightning bolt icon) to execute it
4. You should see: `Database setup complete!`

This creates a database called `feedback_db` with sample data.

---

### STEP 4 — Configure Database Password in app.py
Open `app.py` and find this section (around line 28):

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',       ← Your MySQL username (usually 'root')
    'password': '',       ← PUT YOUR MYSQL PASSWORD HERE
    'database': 'feedback_db'
}
```

Change `password` to your MySQL password. Example:
```python
'password': 'mypassword123',
```

---

### STEP 5 — Install Python Packages
Open **Command Prompt** inside the `feedback_project` folder and run:

```bash
pip install -r requirements.txt
```

This installs Flask, NLTK, TextBlob, Pandas, Matplotlib, etc.

If you get an error with `flask-mysqldb`, try:
```bash
pip install mysql-connector-python flask nltk textblob pandas matplotlib seaborn wordcloud
```

---

### STEP 6 — Run the App
In the same Command Prompt, run:

```bash
python app.py
```

You should see:
```
==================================================
  AI Feedback Intelligence System
  Running at: http://localhost:5000
==================================================
```

---

### STEP 7 — Open in Browser
Go to: **http://localhost:5000**

You will see the dashboard with sample data already loaded!

---

## How to Use the App

| Page | What to do |
|------|-----------|
| **Dashboard** | View stats, recent feedback, and charts |
| **Submit Feedback** | Type a feedback and see sentiment analyzed live |
| **Upload CSV** | Upload a `.csv` file with many feedbacks at once |
| **All Feedback** | Browse, filter, and delete feedback |
| **Analytics** | Word cloud, category chart, polarity histogram |

---

## CSV Format for Upload

Your CSV file must have a column named `text` (or `feedback`, `comment`, `review`):

```csv
text,category
"The product quality is amazing!",product
"Very slow delivery and bad packaging",delivery
"Support team was helpful",support
```

---

## Technologies Used

| Technology | Purpose |
|-----------|---------|
| Python 3.x | Main programming language |
| Flask | Web framework (routes, templates) |
| MySQL | Database to store feedback |
| TextBlob | Sentiment analysis (NLP) |
| NLTK | Text preprocessing |
| Pandas | Reading and processing CSV files |
| Matplotlib & Seaborn | Generating charts |
| WordCloud | Generating word cloud image |
| Bootstrap 5 | Frontend styling |
| Jinja2 | HTML templates |

---

## Common Errors and Fixes

**"ModuleNotFoundError: No module named 'flask'"**
→ Run: `pip install flask`

**"Access denied for user 'root'@'localhost'"**
→ Wrong MySQL password. Update `DB_CONFIG` in `app.py`

**"Unknown database 'feedback_db'"**
→ You haven't run `setup_database.sql` yet. Follow Step 3 above.

**"Port 5000 is already in use"**
→ Change `port=5000` to `port=5001` at the bottom of `app.py`

---

## Project By
- Ms. Snehal Balaji Nagane
- Ms. Payal Sanjay Latkar
- Under the Guidance of Prof. Ganesh
- S.M Joshi College, Hadapsar
