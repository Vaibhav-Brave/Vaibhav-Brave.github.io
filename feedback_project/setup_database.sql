-- =============================================
-- AI Feedback Intelligence System - Database Setup
-- Run this file in MySQL to create the database
-- =============================================

-- Step 1: Create the database
CREATE DATABASE IF NOT EXISTS feedback_db;
USE feedback_db;

-- Step 2: Create the feedback table
-- This stores every piece of feedback submitted
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,          -- Unique ID for each feedback
    text TEXT NOT NULL,                         -- The actual feedback text
    source VARCHAR(100) DEFAULT 'manual',       -- Where it came from (manual/csv/api)
    sentiment VARCHAR(20),                      -- positive / negative / neutral
    polarity FLOAT,                             -- Score from -1.0 (very negative) to +1.0 (very positive)
    subjectivity FLOAT,                         -- Score from 0 (objective) to 1 (subjective)
    category VARCHAR(100) DEFAULT 'general',    -- Topic category
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- When it was added
);

-- Step 3: Insert some sample data so the dashboard isn't empty on first run
INSERT INTO feedback (text, source, sentiment, polarity, subjectivity, category) VALUES
('The product quality is excellent and I love using it every day!', 'sample', 'positive', 0.85, 0.75, 'product'),
('Delivery was very slow and the packaging was damaged.', 'sample', 'negative', -0.60, 0.70, 'delivery'),
('The customer support team was helpful and resolved my issue quickly.', 'sample', 'positive', 0.70, 0.60, 'support'),
('Average experience, nothing special about this product.', 'sample', 'neutral', 0.05, 0.40, 'product'),
('I am extremely disappointed with the quality. Will not buy again.', 'sample', 'negative', -0.80, 0.80, 'product'),
('Fast shipping and great value for money!', 'sample', 'positive', 0.75, 0.65, 'delivery'),
('The interface is confusing and hard to navigate.', 'sample', 'negative', -0.45, 0.55, 'usability'),
('Overall satisfied with the purchase. Would recommend to friends.', 'sample', 'positive', 0.60, 0.50, 'product'),
('Service was okay, but the wait time was too long.', 'sample', 'neutral', -0.10, 0.45, 'support'),
('Absolutely fantastic! Best purchase I have made this year.', 'sample', 'positive', 0.95, 0.85, 'product');

-- Confirm setup
SELECT 'Database setup complete!' AS status;
SELECT COUNT(*) AS total_sample_records FROM feedback;
