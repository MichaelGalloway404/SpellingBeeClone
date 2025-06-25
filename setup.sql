-- Create database (if you haven't yet)
CREATE DATABASE IF NOT EXISTS spellingbee;
USE spellingbee;

-- Table for valid dictionary words
CREATE TABLE valid_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) UNIQUE NOT NULL
);

-- Table for user sessions and found words
CREATE TABLE user_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    found_words TEXT, -- will store JSON list of words
    date_played DATE,
    UNIQUE (session_id, date_played)
);
