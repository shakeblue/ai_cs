-- =====================================================
-- Seed Data for Scheduled Crawler
-- Run this in Supabase SQL Editor
-- =====================================================

-- Insert Naver Shopping Live Platform
INSERT INTO platforms (name, url_pattern, status, schedule_cron)
VALUES (
    'Naver Shopping Live',
    'https://shoppinglive.naver.com/search/lives?query={query}',
    'active',
    '0 */6 * * *'
)
ON CONFLICT (name) DO UPDATE SET
    url_pattern = EXCLUDED.url_pattern,
    status = EXCLUDED.status,
    schedule_cron = EXCLUDED.schedule_cron,
    updated_at = NOW();

-- Insert Test Brands
INSERT INTO brands (name, search_text, platform_id, status, schedule_cron)
VALUES
    (
        'Sulwhasoo',
        '설화수',
        (SELECT id FROM platforms WHERE name = 'Naver Shopping Live'),
        'active',
        '0 */6 * * *'
    ),
    (
        'Innisfree',
        '이니스프리',
        (SELECT id FROM platforms WHERE name = 'Naver Shopping Live'),
        'active',
        '0 */12 * * *'
    ),
    (
        'Laneige',
        '라네즈',
        (SELECT id FROM platforms WHERE name = 'Naver Shopping Live'),
        'active',
        '0 0 * * *'
    ),
    (
        'Amorepacific',
        '아모레퍼시픽',
        (SELECT id FROM platforms WHERE name = 'Naver Shopping Live'),
        'active',
        '0 */6 * * *'
    )
ON CONFLICT (name, platform_id) DO UPDATE SET
    search_text = EXCLUDED.search_text,
    status = EXCLUDED.status,
    schedule_cron = EXCLUDED.schedule_cron,
    updated_at = NOW();

-- Verify the data
SELECT
    'Platforms' as type,
    COUNT(*) as count
FROM platforms
UNION ALL
SELECT
    'Brands' as type,
    COUNT(*) as count
FROM brands
UNION ALL
SELECT
    'Crawler Config' as type,
    COUNT(*) as count
FROM crawler_config;

-- Show all platforms and brands
SELECT
    p.name as platform,
    p.status as platform_status,
    b.name as brand,
    b.search_text,
    b.status as brand_status,
    b.schedule_cron
FROM platforms p
LEFT JOIN brands b ON b.platform_id = p.id
ORDER BY p.name, b.name;
