-- ========================================
-- Naver Shopping Live Broadcast Database Schema
-- Phase 3: Database Integration
-- Date: 2025-12-23
-- ========================================

-- ========================================
-- Core Broadcasts Table
-- ========================================
CREATE TABLE IF NOT EXISTS broadcasts (
    id BIGINT PRIMARY KEY,
    replay_url TEXT UNIQUE NOT NULL,
    broadcast_url TEXT,
    livebridge_url TEXT NOT NULL,
    title TEXT NOT NULL,
    brand_name TEXT NOT NULL,
    description TEXT,
    broadcast_date TIMESTAMPTZ,
    broadcast_end_date TIMESTAMPTZ,
    expected_start_date TIMESTAMPTZ,
    status TEXT,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for broadcasts
CREATE INDEX IF NOT EXISTS idx_broadcasts_brand_name ON broadcasts(brand_name);
CREATE INDEX IF NOT EXISTS idx_broadcasts_status ON broadcasts(status);
CREATE INDEX IF NOT EXISTS idx_broadcasts_broadcast_date ON broadcasts(broadcast_date DESC);
CREATE INDEX IF NOT EXISTS idx_broadcasts_created_at ON broadcasts(created_at DESC);

COMMENT ON TABLE broadcasts IS 'Main table for storing Naver Shopping Live broadcast information';
COMMENT ON COLUMN broadcasts.id IS 'Broadcast ID from Naver (natural primary key)';
COMMENT ON COLUMN broadcasts.replay_url IS 'Unique replay URL for this broadcast';
COMMENT ON COLUMN broadcasts.raw_data IS 'Complete original JSON data from crawler';

-- ========================================
-- Broadcast Products Table
-- ========================================
CREATE TABLE IF NOT EXISTS broadcast_products (
    id BIGSERIAL PRIMARY KEY,
    broadcast_id BIGINT NOT NULL REFERENCES broadcasts(id) ON DELETE CASCADE,
    product_id TEXT NOT NULL,
    name TEXT NOT NULL,
    brand_name TEXT,
    discount_rate NUMERIC(5,2),
    discounted_price NUMERIC(12,2),
    original_price NUMERIC(12,2),
    stock INTEGER,
    image_url TEXT,
    link_url TEXT,
    review_count INTEGER,
    delivery_fee NUMERIC(10,2),
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(broadcast_id, product_id)
);

-- Indexes for products
CREATE INDEX IF NOT EXISTS idx_products_broadcast_id ON broadcast_products(broadcast_id);
CREATE INDEX IF NOT EXISTS idx_products_product_id ON broadcast_products(product_id);
CREATE INDEX IF NOT EXISTS idx_products_discount_rate ON broadcast_products(discount_rate DESC);

COMMENT ON TABLE broadcast_products IS 'Products featured in each broadcast';
COMMENT ON COLUMN broadcast_products.product_id IS 'Naver Shopping product ID';

-- ========================================
-- Broadcast Coupons Table
-- ========================================
CREATE TABLE IF NOT EXISTS broadcast_coupons (
    id BIGSERIAL PRIMARY KEY,
    broadcast_id BIGINT NOT NULL REFERENCES broadcasts(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    benefit_type TEXT,
    benefit_unit TEXT,
    benefit_value NUMERIC(10,2),
    min_order_amount NUMERIC(12,2),
    max_discount_amount NUMERIC(12,2),
    valid_start TIMESTAMPTZ,
    valid_end TIMESTAMPTZ,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for coupons
CREATE INDEX IF NOT EXISTS idx_coupons_broadcast_id ON broadcast_coupons(broadcast_id);
CREATE INDEX IF NOT EXISTS idx_coupons_valid_end ON broadcast_coupons(valid_end DESC);

COMMENT ON TABLE broadcast_coupons IS 'Coupons available during each broadcast';
COMMENT ON COLUMN broadcast_coupons.benefit_type IS 'Type of coupon benefit (e.g., ADMIN_COUPON, SELLER_COUPON)';

-- ========================================
-- Broadcast Benefits Table
-- ========================================
CREATE TABLE IF NOT EXISTS broadcast_benefits (
    id BIGSERIAL PRIMARY KEY,
    broadcast_id BIGINT NOT NULL REFERENCES broadcasts(id) ON DELETE CASCADE,
    benefit_id TEXT,
    message TEXT NOT NULL,
    detail TEXT,
    benefit_type TEXT,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create unique index only if benefit_id is not null
CREATE UNIQUE INDEX IF NOT EXISTS idx_benefits_broadcast_benefit_id
ON broadcast_benefits(broadcast_id, benefit_id)
WHERE benefit_id IS NOT NULL;

-- Indexes for benefits
CREATE INDEX IF NOT EXISTS idx_benefits_broadcast_id ON broadcast_benefits(broadcast_id);

COMMENT ON TABLE broadcast_benefits IS 'Additional benefits offered during broadcasts (e.g., extra points, special discounts)';

-- ========================================
-- Broadcast Chat Table
-- ========================================
CREATE TABLE IF NOT EXISTS broadcast_chat (
    id BIGSERIAL PRIMARY KEY,
    broadcast_id BIGINT NOT NULL REFERENCES broadcasts(id) ON DELETE CASCADE,
    nickname TEXT,
    message TEXT NOT NULL,
    created_at_source TIMESTAMPTZ,
    comment_type TEXT,
    raw_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for chat
CREATE INDEX IF NOT EXISTS idx_chat_broadcast_id ON broadcast_chat(broadcast_id);
CREATE INDEX IF NOT EXISTS idx_chat_created_at_source ON broadcast_chat(created_at_source DESC);

COMMENT ON TABLE broadcast_chat IS 'Chat messages from broadcast (replays only)';
COMMENT ON COLUMN broadcast_chat.created_at_source IS 'Original timestamp from the broadcast';

-- ========================================
-- Crawl Metadata Table
-- ========================================
CREATE TABLE IF NOT EXISTS crawl_metadata (
    id BIGSERIAL PRIMARY KEY,
    broadcast_id BIGINT NOT NULL REFERENCES broadcasts(id) ON DELETE CASCADE,
    source_url TEXT NOT NULL,
    extraction_method TEXT,
    url_type TEXT,
    crawler_version TEXT,
    errors JSONB,
    warnings JSONB,
    crawled_at TIMESTAMPTZ NOT NULL,
    saved_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'success',
    error_message TEXT
);

-- Indexes for metadata
CREATE INDEX IF NOT EXISTS idx_metadata_broadcast_id ON crawl_metadata(broadcast_id);
CREATE INDEX IF NOT EXISTS idx_metadata_crawled_at ON crawl_metadata(crawled_at DESC);
CREATE INDEX IF NOT EXISTS idx_metadata_status ON crawl_metadata(status);

COMMENT ON TABLE crawl_metadata IS 'Audit trail of all crawl operations for each broadcast';
COMMENT ON COLUMN crawl_metadata.extraction_method IS 'Method used: API, JSON, or HYBRID';
COMMENT ON COLUMN crawl_metadata.url_type IS 'Source URL type: replays, lives, or shortclips';

-- ========================================
-- Triggers for updated_at
-- ========================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Drop triggers if they exist (idempotent)
DROP TRIGGER IF EXISTS update_broadcasts_updated_at ON broadcasts;
DROP TRIGGER IF EXISTS update_products_updated_at ON broadcast_products;
DROP TRIGGER IF EXISTS update_coupons_updated_at ON broadcast_coupons;
DROP TRIGGER IF EXISTS update_benefits_updated_at ON broadcast_benefits;

-- Create triggers
CREATE TRIGGER update_broadcasts_updated_at BEFORE UPDATE ON broadcasts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON broadcast_products
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_coupons_updated_at BEFORE UPDATE ON broadcast_coupons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_benefits_updated_at BEFORE UPDATE ON broadcast_benefits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- Sample Queries for Testing
-- ========================================

-- Get single broadcast with all related data
/*
SELECT
    b.*,
    COALESCE(json_agg(DISTINCT p.*) FILTER (WHERE p.id IS NOT NULL), '[]') as products,
    COALESCE(json_agg(DISTINCT c.*) FILTER (WHERE c.id IS NOT NULL), '[]') as coupons,
    COALESCE(json_agg(DISTINCT bf.*) FILTER (WHERE bf.id IS NOT NULL), '[]') as benefits,
    COALESCE(json_agg(DISTINCT ch.*) FILTER (WHERE ch.id IS NOT NULL), '[]') as chat
FROM broadcasts b
LEFT JOIN broadcast_products p ON b.id = p.broadcast_id
LEFT JOIN broadcast_coupons c ON b.id = c.broadcast_id
LEFT JOIN broadcast_benefits bf ON b.id = bf.broadcast_id
LEFT JOIN broadcast_chat ch ON b.id = ch.broadcast_id
WHERE b.id = 1776510
GROUP BY b.id;
*/

-- List recent broadcasts
/*
SELECT
    id,
    title,
    brand_name,
    status,
    broadcast_date,
    created_at
FROM broadcasts
ORDER BY broadcast_date DESC
LIMIT 20;
*/

-- Get crawl statistics
/*
SELECT
    COUNT(*) as total_broadcasts,
    COUNT(DISTINCT brand_name) as total_brands,
    SUM((SELECT COUNT(*) FROM broadcast_products WHERE broadcast_id = broadcasts.id)) as total_products,
    SUM((SELECT COUNT(*) FROM broadcast_coupons WHERE broadcast_id = broadcasts.id)) as total_coupons,
    MAX(created_at) as last_crawl
FROM broadcasts;
*/

-- ========================================
-- End of Schema
-- ========================================
