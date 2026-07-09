-- ===========================
-- PakWheels Cars Table Setup
-- Author: ChatGPT
-- Date: 2025-07-03
-- ===========================

-- 1. Create Table for car listings

CREATE TABLE IF NOT EXISTS pakwheels_cars (
    id SERIAL PRIMARY KEY,
    car_url TEXT UNIQUE NOT NULL,
    data JSONB NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'sold')),
    first_seen DATE NOT NULL DEFAULT CURRENT_DATE,
    last_seen DATE NOT NULL DEFAULT CURRENT_DATE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Create Index on status for faster active/sold filtering

CREATE INDEX IF NOT EXISTS idx_pakwheels_status ON pakwheels_cars(status);

-- 3. Create Index on first_seen for chronological queries

CREATE INDEX IF NOT EXISTS idx_pakwheels_first_seen ON pakwheels_cars(first_seen);

-- 4. (Optional) Create Index on updated_at for data freshness queries

CREATE INDEX IF NOT EXISTS idx_pakwheels_updated_at ON pakwheels_cars(updated_at);

-- 5. Query to mark listings as sold (run daily after scraping)

UPDATE pakwheels_cars
SET status = 'sold', last_seen = CURRENT_DATE, updated_at = CURRENT_TIMESTAMP
WHERE last_seen < CURRENT_DATE AND status = 'active';

-- ===========================
-- DONE
-- ===========================
