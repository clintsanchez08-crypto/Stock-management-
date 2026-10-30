-- =====================================================
-- Stocks Management System - Database Setup Script
-- Run this script ONCE before starting the Python app.
-- Example: mysql -u root -p < stocks_db.sql
-- =====================================================

-- 1. Create the database (drop it first for a clean re-run, optional)
-- DROP DATABASE IF EXISTS stocks_db;
CREATE DATABASE IF NOT EXISTS stocks_db;

-- 2. Select the database
USE stocks_db;

-- 3. Create the 'stocks' table
CREATE TABLE IF NOT EXISTS stocks (
    stock_id     INT AUTO_INCREMENT PRIMARY KEY,
    item_name    VARCHAR(100) NOT NULL,
    quantity     INT NOT NULL,
    price        DECIMAL(10, 2) NOT NULL,
    status       VARCHAR(20) NOT NULL DEFAULT 'Available'
);

-- 4. (Optional) Insert sample data for testing
INSERT INTO stocks (item_name, quantity, price, status) VALUES
('Ballpen', 50, 8.00, 'Available'),
('Notebook', 20, 25.00, 'Available');

-- 5. Verify the table was created
SELECT * FROM stocks;
