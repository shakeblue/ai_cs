-- ========================================
-- Truncate Naver Shopping Live Database
-- WARNING: This will DELETE ALL DATA!
-- Date: 2025-12-23
-- ========================================

-- Disable triggers temporarily (optional)
SET session_replication_role = 'replica';

-- Truncate all tables in reverse dependency order
-- This removes all data but keeps the table structure

TRUNCATE TABLE broadcast_chat CASCADE;
TRUNCATE TABLE broadcast_benefits CASCADE;
TRUNCATE TABLE broadcast_coupons CASCADE;
TRUNCATE TABLE broadcast_products CASCADE;
TRUNCATE TABLE crawl_metadata CASCADE;
TRUNCATE TABLE broadcasts CASCADE;

-- Re-enable triggers
SET session_replication_role = 'origin';

-- Verify truncation
SELECT
  'broadcasts' as table_name,
  COUNT(*) as remaining_rows
FROM broadcasts
UNION ALL
SELECT
  'broadcast_products' as table_name,
  COUNT(*) as remaining_rows
FROM broadcast_products
UNION ALL
SELECT
  'broadcast_coupons' as table_name,
  COUNT(*) as remaining_rows
FROM broadcast_coupons
UNION ALL
SELECT
  'broadcast_benefits' as table_name,
  COUNT(*) as remaining_rows
FROM broadcast_benefits
UNION ALL
SELECT
  'broadcast_chat' as table_name,
  COUNT(*) as remaining_rows
FROM broadcast_chat
UNION ALL
SELECT
  'crawl_metadata' as table_name,
  COUNT(*) as remaining_rows
FROM crawl_metadata
ORDER BY table_name;

-- ========================================
-- All data has been cleared!
-- Tables are ready for fresh data.
-- ========================================
