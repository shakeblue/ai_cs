-- Supabase Table Creation Script for Naver SmartStore Events
-- Run this in Supabase SQL Editor

-- Create naver_smartstore_event table
CREATE TABLE IF NOT EXISTS naver_smartstore_event (
    id BIGSERIAL PRIMARY KEY,
    platform_name TEXT NOT NULL DEFAULT 'Naver Brand',
    brand_name TEXT,
    url TEXT NOT NULL,
    event_title TEXT,
    event_date TEXT,
    benefits_by_purchase_amount JSONB DEFAULT '[]'::jsonb,
    coupon_benefits JSONB DEFAULT '[]'::jsonb,
    raw_ocr_data JSONB,
    image_urls JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_naver_smartstore_event_brand
    ON naver_smartstore_event(brand_name);

CREATE INDEX IF NOT EXISTS idx_naver_smartstore_event_created
    ON naver_smartstore_event(created_at DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
CREATE TRIGGER update_naver_smartstore_event_updated_at
    BEFORE UPDATE ON naver_smartstore_event
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Verify table creation
SELECT
    'Table created successfully' as status,
    COUNT(*) as row_count
FROM naver_smartstore_event;
