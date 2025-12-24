# Livebridge Schema Setup Guide

## Overview
This guide explains how to create the livebridge database schema in Supabase for Phase 2 of the Naver Livebridge Data Extraction feature.

## Tables Created
1. **livebridge** - Main table with URL, title, brand, datetime
2. **livebridge_coupons** - Detailed coupon information (API source)
3. **livebridge_products** - Product listings with discounts
4. **livebridge_live_benefits** - Live-specific benefits
5. **livebridge_benefits_by_amount** - Tiered benefits based on purchase amounts
6. **livebridge_simple_coupons** - Simple coupon descriptions

## Setup Steps

### Method 1: Supabase Dashboard (Recommended)

1. **Open Supabase SQL Editor**
   - Go to your Supabase project dashboard
   - Navigate to **SQL Editor** in the left sidebar
   - Click **New Query**

2. **Copy and Execute SQL**
   - Open the file: `database/create_livebridge_tables.sql`
   - Copy the entire contents
   - Paste into the Supabase SQL Editor
   - Click **Run** or press `Ctrl+Enter`

3. **Verify Creation**
   - Go to **Table Editor** in the left sidebar
   - You should see all 6 new livebridge tables
   - Check that indexes and foreign keys are created

### Method 2: Supabase CLI

```bash
# Make sure you're logged in to Supabase CLI
supabase login

# Link your project (if not already linked)
supabase link --project-ref your-project-ref

# Execute the SQL file
supabase db execute -f database/create_livebridge_tables.sql
```

## Schema Features

### Foreign Key Relationships
All child tables have foreign keys to the main `livebridge` table with `ON DELETE CASCADE`:
- When a livebridge record is deleted, all related coupons, products, and benefits are automatically deleted

### Indexes
Optimized indexes for common query patterns:
- `idx_livebridge_url` - Fast lookup by URL (for upsert operations)
- `idx_livebridge_datetime` - Query by live broadcast datetime
- `idx_livebridge_brand_name` - Filter by brand
- Foreign key indexes on all child tables

### Row Level Security (RLS)
- **Public read access** - Anonymous users can read all livebridge data
- **Service role full access** - Crawler and backend can insert/update/delete

## Testing the Schema

After creation, run this query to verify all tables exist:

```sql
SELECT
    t.table_name,
    COUNT(c.column_name) as column_count
FROM information_schema.tables t
LEFT JOIN information_schema.columns c
    ON t.table_name = c.table_name
WHERE t.table_schema = 'public'
    AND t.table_name LIKE 'livebridge%'
GROUP BY t.table_name
ORDER BY t.table_name;
```

Expected output:
```
livebridge                        | 6
livebridge_benefits_by_amount     | 4
livebridge_coupons                | 15
livebridge_live_benefits          | 4
livebridge_products               | 6
livebridge_simple_coupons         | 4
```

## Next Steps

After schema creation:

1. **Update Crawler** - Add Supabase integration to `crawler/cj/livebridge_crawler.py`
2. **Create Backend API** - Implement routes and services in `/backend/src/`
3. **Build Frontend Components** - Create display components in `/frontend/src/components/livebridge/`

## Rollback

If you need to drop all tables:

```sql
DROP TABLE IF EXISTS livebridge_simple_coupons CASCADE;
DROP TABLE IF EXISTS livebridge_benefits_by_amount CASCADE;
DROP TABLE IF EXISTS livebridge_live_benefits CASCADE;
DROP TABLE IF EXISTS livebridge_products CASCADE;
DROP TABLE IF EXISTS livebridge_coupons CASCADE;
DROP TABLE IF EXISTS livebridge CASCADE;
```

## Data Model Reference

### Sample Data Structure
Based on `crawler/cj/output/livebridge_1776510_optimized.json`:

```
livebridge (main record)
├── livebridge_coupons (3 special coupons with detailed info)
├── livebridge_products (20 products with discounts)
├── livebridge_live_benefits (1 live benefit)
├── livebridge_benefits_by_amount (7 tiered benefits)
└── livebridge_simple_coupons (7 simple coupon descriptions)
```

## Troubleshooting

### Error: "relation already exists"
The tables already exist. Either:
- Run the DROP statements first (see Rollback section)
- Or skip table creation if intentional

### Error: "permission denied"
Make sure you're using the SQL Editor with proper permissions or using the service role key.

### Missing RLS policies
RLS policies should be created automatically. If not, check the bottom section of the SQL file.
