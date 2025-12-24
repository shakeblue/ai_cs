-- ========================================
-- Complete Database Setup with New Schema
-- Includes truncation + migration v2
-- Date: 2025-12-23
-- ========================================

-- Step 1: Truncate all existing data
-- ========================================

SET session_replication_role = 'replica';

TRUNCATE TABLE broadcast_chat CASCADE;
TRUNCATE TABLE broadcast_benefits CASCADE;
TRUNCATE TABLE broadcast_coupons CASCADE;
TRUNCATE TABLE broadcast_products CASCADE;
TRUNCATE TABLE crawl_metadata CASCADE;
TRUNCATE TABLE broadcasts CASCADE;

SET session_replication_role = 'origin';

-- Step 2: Add new columns (Migration v2)
-- ========================================

-- Add stand_by_image column to broadcasts table
ALTER TABLE broadcasts
ADD COLUMN IF NOT EXISTS stand_by_image TEXT;

-- Add broadcast_type column to broadcasts table
ALTER TABLE broadcasts
ADD COLUMN IF NOT EXISTS broadcast_type TEXT;

-- Step 3: Add indexes
-- ========================================

CREATE INDEX IF NOT EXISTS idx_broadcasts_broadcast_type ON broadcasts(broadcast_type);

-- Step 4: Add comments
-- ========================================

COMMENT ON COLUMN broadcasts.stand_by_image IS 'Standby/thumbnail image URL for the broadcast';
COMMENT ON COLUMN broadcasts.broadcast_type IS 'Type of broadcast: replays, lives, or shortclips (from URL type)';

-- Step 5: Verify setup
-- ========================================

-- Check table structure
SELECT
  column_name,
  data_type,
  is_nullable,
  column_default
FROM information_schema.columns
WHERE table_name = 'broadcasts'
ORDER BY ordinal_position;

-- Check all tables are empty
SELECT
  'broadcasts' as table_name,
  COUNT(*) as row_count
FROM broadcasts
UNION ALL
SELECT
  'broadcast_products' as table_name,
  COUNT(*) as row_count
FROM broadcast_products
UNION ALL
SELECT
  'broadcast_coupons' as table_name,
  COUNT(*) as row_count
FROM broadcast_coupons
UNION ALL
SELECT
  'broadcast_benefits' as table_name,
  COUNT(*) as row_count
FROM broadcast_benefits
UNION ALL
SELECT
  'broadcast_chat' as table_name,
  COUNT(*) as row_count
FROM broadcast_chat
UNION ALL
SELECT
  'crawl_metadata' as table_name,
  COUNT(*) as row_count
FROM crawl_metadata
ORDER BY table_name;

-- ========================================
-- Setup Complete!
-- Database is now ready with new schema:
-- - stand_by_image column added
-- - broadcast_type column added
-- - All data cleared
-- - Ready for fresh crawling
-- ========================================
