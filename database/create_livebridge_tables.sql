-- =====================================================
-- Livebridge Tables Creation Script
-- Purpose: Store Naver Shopping Live livebridge data
-- Feature: naver-livebridge-data-extraction (Phase 2)
-- =====================================================

-- Drop existing tables (in reverse order due to foreign keys)
DROP TABLE IF EXISTS livebridge_simple_coupons CASCADE;
DROP TABLE IF EXISTS livebridge_benefits_by_amount CASCADE;
DROP TABLE IF EXISTS livebridge_live_benefits CASCADE;
DROP TABLE IF EXISTS livebridge_products CASCADE;
DROP TABLE IF EXISTS livebridge_coupons CASCADE;
DROP TABLE IF EXISTS livebridge CASCADE;

-- =====================================================
-- Main Livebridge Table
-- =====================================================
CREATE TABLE livebridge (
    id BIGSERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    live_datetime TIMESTAMPTZ,
    title TEXT NOT NULL,
    brand_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_livebridge_url ON livebridge(url);
CREATE INDEX idx_livebridge_datetime ON livebridge(live_datetime);
CREATE INDEX idx_livebridge_brand_name ON livebridge(brand_name);

-- Add comment
COMMENT ON TABLE livebridge IS 'Main table storing Naver Shopping Live livebridge promotional pages metadata';

-- =====================================================
-- Livebridge Special Coupons Table
-- =====================================================
CREATE TABLE livebridge_coupons (
    id BIGSERIAL PRIMARY KEY,
    livebridge_id BIGINT NOT NULL REFERENCES livebridge(id) ON DELETE CASCADE,
    coupon_name TEXT NOT NULL,
    coupon_type TEXT,
    benefit_unit TEXT,
    benefit_value INTEGER,
    min_order_amount INTEGER,
    max_discount_amount INTEGER,
    coupon_kind TEXT,
    valid_period_start TIMESTAMPTZ,
    valid_period_end TIMESTAMPTZ,
    availability_status TEXT,
    benefit_status TEXT,
    provider_name TEXT,
    source TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for foreign key lookups
CREATE INDEX idx_livebridge_coupons_livebridge_id ON livebridge_coupons(livebridge_id);
CREATE INDEX idx_livebridge_coupons_valid_period ON livebridge_coupons(valid_period_start, valid_period_end);

-- Add comment
COMMENT ON TABLE livebridge_coupons IS 'Detailed coupon information from livebridge pages (API source)';

-- =====================================================
-- Livebridge Products Table
-- =====================================================
CREATE TABLE livebridge_products (
    id BIGSERIAL PRIMARY KEY,
    livebridge_id BIGINT NOT NULL REFERENCES livebridge(id) ON DELETE CASCADE,
    image TEXT,
    name TEXT NOT NULL,
    discount_rate INTEGER,
    discount_price INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for foreign key lookups
CREATE INDEX idx_livebridge_products_livebridge_id ON livebridge_products(livebridge_id);

-- Add comment
COMMENT ON TABLE livebridge_products IS 'Products featured in livebridge promotions with discount information';

-- =====================================================
-- Livebridge Live Benefits Table
-- =====================================================
CREATE TABLE livebridge_live_benefits (
    id BIGSERIAL PRIMARY KEY,
    livebridge_id BIGINT NOT NULL REFERENCES livebridge(id) ON DELETE CASCADE,
    benefit_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for foreign key lookups
CREATE INDEX idx_livebridge_live_benefits_livebridge_id ON livebridge_live_benefits(livebridge_id);

-- Add comment
COMMENT ON TABLE livebridge_live_benefits IS 'Live-specific promotional benefits extracted from images';

-- =====================================================
-- Livebridge Benefits by Amount Table
-- =====================================================
CREATE TABLE livebridge_benefits_by_amount (
    id BIGSERIAL PRIMARY KEY,
    livebridge_id BIGINT NOT NULL REFERENCES livebridge(id) ON DELETE CASCADE,
    benefit_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for foreign key lookups
CREATE INDEX idx_livebridge_benefits_by_amount_livebridge_id ON livebridge_benefits_by_amount(livebridge_id);

-- Add comment
COMMENT ON TABLE livebridge_benefits_by_amount IS 'Tiered benefits based on purchase amounts extracted from images';

-- =====================================================
-- Livebridge Simple Coupons Table
-- =====================================================
CREATE TABLE livebridge_simple_coupons (
    id BIGSERIAL PRIMARY KEY,
    livebridge_id BIGINT NOT NULL REFERENCES livebridge(id) ON DELETE CASCADE,
    coupon_text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for foreign key lookups
CREATE INDEX idx_livebridge_simple_coupons_livebridge_id ON livebridge_simple_coupons(livebridge_id);

-- Add comment
COMMENT ON TABLE livebridge_simple_coupons IS 'Simple coupon descriptions extracted from images';

-- =====================================================
-- Row Level Security (RLS) Policies
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE livebridge ENABLE ROW LEVEL SECURITY;
ALTER TABLE livebridge_coupons ENABLE ROW LEVEL SECURITY;
ALTER TABLE livebridge_products ENABLE ROW LEVEL SECURITY;
ALTER TABLE livebridge_live_benefits ENABLE ROW LEVEL SECURITY;
ALTER TABLE livebridge_benefits_by_amount ENABLE ROW LEVEL SECURITY;
ALTER TABLE livebridge_simple_coupons ENABLE ROW LEVEL SECURITY;

-- Allow public read access to all tables
CREATE POLICY "Allow public read access on livebridge"
    ON livebridge FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on livebridge_coupons"
    ON livebridge_coupons FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on livebridge_products"
    ON livebridge_products FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on livebridge_live_benefits"
    ON livebridge_live_benefits FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on livebridge_benefits_by_amount"
    ON livebridge_benefits_by_amount FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on livebridge_simple_coupons"
    ON livebridge_simple_coupons FOR SELECT
    USING (true);

-- Allow service role full access (for crawler and backend)
CREATE POLICY "Allow service role full access on livebridge"
    ON livebridge FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on livebridge_coupons"
    ON livebridge_coupons FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on livebridge_products"
    ON livebridge_products FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on livebridge_live_benefits"
    ON livebridge_live_benefits FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on livebridge_benefits_by_amount"
    ON livebridge_benefits_by_amount FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on livebridge_simple_coupons"
    ON livebridge_simple_coupons FOR ALL
    USING (auth.role() = 'service_role');

-- =====================================================
-- Sample Query to Verify Schema
-- =====================================================

-- Uncomment to test after creation:
-- SELECT
--     t.table_name,
--     COUNT(c.column_name) as column_count
-- FROM information_schema.tables t
-- LEFT JOIN information_schema.columns c
--     ON t.table_name = c.table_name
-- WHERE t.table_schema = 'public'
--     AND t.table_name LIKE 'livebridge%'
-- GROUP BY t.table_name
-- ORDER BY t.table_name;
