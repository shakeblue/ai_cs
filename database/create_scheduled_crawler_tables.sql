-- =====================================================
-- Scheduled Crawler Tables Creation Script
-- Purpose: Automated crawler scheduling and management
-- Feature: scheduled-crawler
-- =====================================================

-- Drop existing tables (in reverse order due to foreign keys)
DROP TABLE IF EXISTS crawler_executions CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS brands CASCADE;
DROP TABLE IF EXISTS platforms CASCADE;
DROP TABLE IF EXISTS crawler_config CASCADE;

-- =====================================================
-- Platforms Table
-- =====================================================
CREATE TABLE platforms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    url_pattern TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    schedule_cron TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_platforms_status ON platforms(status);
CREATE INDEX idx_platforms_name ON platforms(name);

-- Add comments
COMMENT ON TABLE platforms IS 'Platform configurations for crawler (e.g., Naver Shopping Live)';
COMMENT ON COLUMN platforms.url_pattern IS 'URL template with {query} placeholder, e.g., https://shoppinglive.naver.com/search/lives?query={query}';
COMMENT ON COLUMN platforms.schedule_cron IS 'Default cron schedule for crawling this platform, e.g., "0 */6 * * *" (every 6 hours)';

-- =====================================================
-- Brands Table
-- =====================================================
CREATE TABLE brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    search_text TEXT NOT NULL,
    platform_id UUID NOT NULL REFERENCES platforms(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    schedule_cron TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(name, platform_id)
);

-- Indexes for common queries
CREATE INDEX idx_brands_platform_id ON brands(platform_id);
CREATE INDEX idx_brands_status ON brands(status);
CREATE INDEX idx_brands_name ON brands(name);

-- Add comments
COMMENT ON TABLE brands IS 'Brand configurations for monitoring specific brands across platforms';
COMMENT ON COLUMN brands.search_text IS 'Search query text for this brand (e.g., "설화수" for Sulwhasoo)';
COMMENT ON COLUMN brands.schedule_cron IS 'Override platform schedule if set, otherwise inherits from platform';

-- =====================================================
-- Crawler Config Table
-- =====================================================
CREATE TABLE crawler_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for key lookups
CREATE INDEX idx_crawler_config_key ON crawler_config(key);

-- Add comments
COMMENT ON TABLE crawler_config IS 'System-wide crawler configuration settings';
COMMENT ON COLUMN crawler_config.key IS 'Configuration key (e.g., "past_days_range", "future_days_range")';
COMMENT ON COLUMN crawler_config.value IS 'Configuration value as string (parse as needed)';

-- Insert default configurations
INSERT INTO crawler_config (key, value, description) VALUES
    ('past_days_range', '7', 'Number of days in the past to fetch events (default: 7)'),
    ('future_days_range', '14', 'Number of days in the future to fetch events (default: 14)'),
    ('default_schedule_cron', '0 */6 * * *', 'Default cron schedule for platforms/brands without custom schedule (every 6 hours)'),
    ('crawler_timeout_seconds', '600', 'Maximum time in seconds for crawler execution (default: 10 minutes)'),
    ('max_concurrent_jobs', '5', 'Maximum number of concurrent crawler jobs (default: 5)')
ON CONFLICT (key) DO NOTHING;

-- =====================================================
-- Events Table (Crawled Live/Replay Events)
-- =====================================================
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id TEXT NOT NULL,
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    platform_id UUID NOT NULL REFERENCES platforms(id) ON DELETE CASCADE,
    execution_id UUID,
    title TEXT,
    url TEXT,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    status TEXT CHECK (status IN ('upcoming', 'ongoing', 'ended')),
    event_type TEXT CHECK (event_type IN ('live', 'replay')),
    raw_data JSONB,
    extracted_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(platform_id, external_id)
);

-- Indexes for common queries and performance
CREATE INDEX idx_events_brand_id ON events(brand_id);
CREATE INDEX idx_events_platform_id ON events(platform_id);
CREATE INDEX idx_events_execution_id ON events(execution_id);
CREATE INDEX idx_events_external_id ON events(external_id);
CREATE INDEX idx_events_start_date ON events(start_date);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_event_type ON events(event_type);
CREATE INDEX idx_events_platform_external ON events(platform_id, external_id);

-- Add comments
COMMENT ON TABLE events IS 'Crawled live and replay events from platforms';
COMMENT ON COLUMN events.external_id IS 'Unique identifier from the platform (used for duplicate detection)';
COMMENT ON COLUMN events.execution_id IS 'Reference to crawler execution that created/updated this event';
COMMENT ON COLUMN events.raw_data IS 'Original crawled data in JSON format';
COMMENT ON COLUMN events.extracted_data IS 'LLM-extracted structured data in JSON format';

-- =====================================================
-- Crawler Executions Table (Execution Logs)
-- =====================================================
CREATE TABLE crawler_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    platform_id UUID NOT NULL REFERENCES platforms(id) ON DELETE CASCADE,
    trigger_type TEXT NOT NULL CHECK (trigger_type IN ('scheduled', 'manual')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'success', 'failed')),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    items_found INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX idx_executions_brand_id ON crawler_executions(brand_id);
CREATE INDEX idx_executions_platform_id ON crawler_executions(platform_id);
CREATE INDEX idx_executions_status ON crawler_executions(status);
CREATE INDEX idx_executions_trigger_type ON crawler_executions(trigger_type);
CREATE INDEX idx_executions_started_at ON crawler_executions(started_at DESC);

-- Add comments
COMMENT ON TABLE crawler_executions IS 'Log of all crawler execution attempts with status and results';
COMMENT ON COLUMN crawler_executions.trigger_type IS 'How the crawl was initiated: scheduled (by cron) or manual (via API)';
COMMENT ON COLUMN crawler_executions.items_found IS 'Number of events found during this execution';
COMMENT ON COLUMN crawler_executions.error_message IS 'Error details if status is failed';

-- Add foreign key constraint to events table (execution_id)
-- Note: This is done after crawler_executions table is created
ALTER TABLE events
    ADD CONSTRAINT fk_events_execution_id
    FOREIGN KEY (execution_id)
    REFERENCES crawler_executions(id)
    ON DELETE SET NULL;

-- =====================================================
-- Row Level Security (RLS) Policies
-- =====================================================

-- Enable RLS on all tables
ALTER TABLE platforms ENABLE ROW LEVEL SECURITY;
ALTER TABLE brands ENABLE ROW LEVEL SECURITY;
ALTER TABLE crawler_config ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE crawler_executions ENABLE ROW LEVEL SECURITY;

-- Allow public read access to all tables
CREATE POLICY "Allow public read access on platforms"
    ON platforms FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on brands"
    ON brands FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on crawler_config"
    ON crawler_config FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on events"
    ON events FOR SELECT
    USING (true);

CREATE POLICY "Allow public read access on crawler_executions"
    ON crawler_executions FOR SELECT
    USING (true);

-- Allow service role full access (for backend API and crawler)
CREATE POLICY "Allow service role full access on platforms"
    ON platforms FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on brands"
    ON brands FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on crawler_config"
    ON crawler_config FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on events"
    ON events FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role full access on crawler_executions"
    ON crawler_executions FOR ALL
    USING (auth.role() = 'service_role');

-- =====================================================
-- Triggers for Updated_At Timestamps
-- =====================================================

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers to relevant tables
CREATE TRIGGER update_platforms_updated_at
    BEFORE UPDATE ON platforms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_brands_updated_at
    BEFORE UPDATE ON brands
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crawler_config_updated_at
    BEFORE UPDATE ON crawler_config
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at
    BEFORE UPDATE ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

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
--     AND t.table_name IN ('platforms', 'brands', 'crawler_config', 'events', 'crawler_executions')
-- GROUP BY t.table_name
-- ORDER BY t.table_name;

-- =====================================================
-- Sample Data for Testing
-- =====================================================

-- Uncomment to insert sample data:
-- INSERT INTO platforms (name, url_pattern, status, schedule_cron) VALUES
--     ('Naver Shopping Live', 'https://shoppinglive.naver.com/search/lives?query={query}', 'active', '0 */6 * * *');
--
-- INSERT INTO brands (name, search_text, platform_id, status) VALUES
--     ('Sulwhasoo', '설화수', (SELECT id FROM platforms WHERE name = 'Naver Shopping Live'), 'active'),
--     ('Innisfree', '이니스프리', (SELECT id FROM platforms WHERE name = 'Naver Shopping Live'), 'active');
