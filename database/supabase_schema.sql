-- ============================================================================
-- Supabase 테이블 스키마
-- 온라인 캠페인, 프로모션 조회 시스템
-- ============================================================================

-- 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- 1. 채널 정보 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS channels (
    channel_id          SERIAL PRIMARY KEY,
    channel_code        VARCHAR(50) UNIQUE NOT NULL,
    channel_name        VARCHAR(100) NOT NULL,
    channel_type        VARCHAR(20) NOT NULL CHECK (channel_type IN ('DIRECT', 'PARTNER', 'LIVE')),
    base_url            TEXT NOT NULL,
    crawl_interval      INTEGER DEFAULT 360,
    is_active           BOOLEAN DEFAULT TRUE,
    icon_url            TEXT,
    description         TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_channels_code ON channels(channel_code);
CREATE INDEX IF NOT EXISTS idx_channels_type ON channels(channel_type);

-- 채널 초기 데이터
INSERT INTO channels (channel_code, channel_name, channel_type, base_url, crawl_interval) VALUES
('NAVER', '네이버', 'LIVE', 'https://shoppinglive.naver.com', 60),
('KAKAO', '카카오', 'LIVE', 'https://shoppinglive.kakao.com', 60),
('11ST', '11번가', 'LIVE', 'https://m.11st.co.kr/page/main/live11', 60),
('GMARKET', 'G마켓', 'LIVE', 'https://m.gmarket.co.kr/n/live/schedule', 60),
('OLIVEYOUNG', '올리브영', 'LIVE', 'https://m.oliveyoung.co.kr/m/mtn/explorer?menu=live', 60),
('GRIP', '그립', 'LIVE', 'https://www.grip.show/discover/category', 60),
('MUSINSA', '무신사', 'LIVE', 'https://www.musinsa.com', 60),
('LOTTEON', '롯데온', 'LIVE', 'https://www.lotteon.com', 60),
('AMOREMALL', '아모레몰', 'LIVE', 'https://www.amoremall.com', 60)
ON CONFLICT (channel_code) DO NOTHING;

-- ============================================================================
-- 2. 라이브 방송 기본 정보 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_broadcasts (
    live_id             VARCHAR(255) PRIMARY KEY,
    channel_id          INTEGER REFERENCES channels(channel_id) ON DELETE CASCADE,
    channel_code        VARCHAR(50) NOT NULL,
    platform_name       VARCHAR(50) NOT NULL,
    brand_name          VARCHAR(100) NOT NULL,
    live_title_customer VARCHAR(500) NOT NULL,
    live_title_cs       VARCHAR(500),
    source_url          TEXT NOT NULL,
    thumbnail_url       TEXT,
    
    -- 방송 스케줄
    broadcast_date      DATE NOT NULL,
    broadcast_start_time TIME,
    broadcast_end_time  TIME,
    benefit_valid_type  VARCHAR(50),
    benefit_start_datetime TIMESTAMP WITH TIME ZONE,
    benefit_end_datetime TIMESTAMP WITH TIME ZONE,
    broadcast_type      VARCHAR(50),
    
    -- 상태 정보
    status              VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACTIVE', 'ENDED', 'CANCELLED')),
    
    -- 메타 정보
    collected_at        TIMESTAMP WITH TIME ZONE,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_broadcasts_channel ON live_broadcasts(channel_id);
CREATE INDEX IF NOT EXISTS idx_live_broadcasts_status ON live_broadcasts(status);
CREATE INDEX IF NOT EXISTS idx_live_broadcasts_date ON live_broadcasts(broadcast_date);
CREATE INDEX IF NOT EXISTS idx_live_broadcasts_brand ON live_broadcasts(brand_name);
CREATE INDEX IF NOT EXISTS idx_live_broadcasts_platform ON live_broadcasts(platform_name);

-- ============================================================================
-- 3. 라이브 방송 상품 정보 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_products (
    product_id          SERIAL PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    product_order       INTEGER DEFAULT 0,
    product_name        VARCHAR(500) NOT NULL,
    sku                 VARCHAR(100),
    original_price      VARCHAR(100),
    sale_price          VARCHAR(100),
    discount_rate       VARCHAR(50),
    product_type        VARCHAR(100),
    stock_info          VARCHAR(200),
    set_composition     TEXT,
    product_url         TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_products_live ON live_products(live_id);
CREATE INDEX IF NOT EXISTS idx_live_products_order ON live_products(live_id, product_order);

-- ============================================================================
-- 4. 라이브 방송 혜택 정보 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_benefits (
    benefit_id          SERIAL PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    benefit_type        VARCHAR(50) NOT NULL CHECK (benefit_type IN ('할인', '사은품', '쿠폰', '포인트', '배송')),
    benefit_name        VARCHAR(500),
    benefit_detail      TEXT,
    benefit_condition    TEXT,
    benefit_valid_period TEXT,
    quantity_limit      VARCHAR(200),
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_benefits_live ON live_benefits(live_id);
CREATE INDEX IF NOT EXISTS idx_live_benefits_type ON live_benefits(live_id, benefit_type);

-- ============================================================================
-- 5. 라이브 방송 키 멘션/채팅 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_chat_messages (
    message_id          SERIAL PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    message_time        VARCHAR(20),
    message_content     TEXT NOT NULL,
    message_type        VARCHAR(50) DEFAULT 'MENTION',
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_chat_live ON live_chat_messages(live_id);
CREATE INDEX IF NOT EXISTS idx_live_chat_time ON live_chat_messages(live_id, message_time);

-- ============================================================================
-- 6. 라이브 방송 Q&A 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_qa (
    qa_id               SERIAL PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    question            TEXT NOT NULL,
    answer              TEXT,
    questioner          VARCHAR(100),
    answerer            VARCHAR(100),
    question_date       VARCHAR(50),
    answer_date         VARCHAR(50),
    is_answered         BOOLEAN DEFAULT FALSE,
    helpful_count       INTEGER DEFAULT 0,
    status              VARCHAR(50) DEFAULT '답변대기',
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_qa_live ON live_qa(live_id);
CREATE INDEX IF NOT EXISTS idx_live_qa_answered ON live_qa(live_id, is_answered);

-- ============================================================================
-- 7. 라이브 방송 공지사항 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_notices (
    notice_id           VARCHAR(255) PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    title               VARCHAR(500) NOT NULL,
    content             TEXT,
    post_date           DATE,
    view_count          INTEGER DEFAULT 0,
    is_important        BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_notices_live ON live_notices(live_id);
CREATE INDEX IF NOT EXISTS idx_live_notices_important ON live_notices(live_id, is_important);

-- ============================================================================
-- 8. 라이브 방송 FAQ 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_faqs (
    faq_id              VARCHAR(255) PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    category            VARCHAR(100),
    question            TEXT NOT NULL,
    answer              TEXT NOT NULL,
    view_count          INTEGER DEFAULT 0,
    helpful_count       INTEGER DEFAULT 0,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_faqs_live ON live_faqs(live_id);
CREATE INDEX IF NOT EXISTS idx_live_faqs_category ON live_faqs(live_id, category);

-- ============================================================================
-- 9. 라이브 방송 타임라인 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_timeline (
    timeline_id         SERIAL PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    time                VARCHAR(20) NOT NULL,
    content             TEXT NOT NULL,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_timeline_live ON live_timeline(live_id);
CREATE INDEX IF NOT EXISTS idx_live_timeline_time ON live_timeline(live_id, time);

-- ============================================================================
-- 10. 라이브 방송 중복 정책 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_duplicate_policy (
    policy_id           SERIAL PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    coupon_duplicate    VARCHAR(50),
    point_duplicate     VARCHAR(50),
    other_promotion_duplicate VARCHAR(50),
    employee_discount   VARCHAR(50),
    duplicate_note      TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(live_id)
);

CREATE INDEX IF NOT EXISTS idx_live_policy_live ON live_duplicate_policy(live_id);

-- ============================================================================
-- 11. 라이브 방송 제한사항 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_restrictions (
    restriction_id      SERIAL PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    restriction_type    VARCHAR(50) NOT NULL CHECK (restriction_type IN ('제외상품', '채널제한', '결제제한', '지역제한', '기타제한')),
    restriction_detail  TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_live_restrictions_live ON live_restrictions(live_id);
CREATE INDEX IF NOT EXISTS idx_live_restrictions_type ON live_restrictions(live_id, restriction_type);

-- ============================================================================
-- 12. 라이브 방송 CS 정보 테이블
-- ============================================================================
CREATE TABLE IF NOT EXISTS live_cs_info (
    cs_info_id          SERIAL PRIMARY KEY,
    live_id             VARCHAR(255) NOT NULL REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    expected_questions  TEXT[],
    response_scripts    TEXT[],
    risk_points         TEXT[],
    cs_note             TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(live_id)
);

CREATE INDEX IF NOT EXISTS idx_live_cs_live ON live_cs_info(live_id);

-- ============================================================================
-- 트리거 함수: updated_at 자동 갱신
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성
CREATE TRIGGER trigger_channels_updated_at BEFORE UPDATE ON channels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_live_broadcasts_updated_at BEFORE UPDATE ON live_broadcasts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- RLS (Row Level Security) 설정 (선택사항)
-- ============================================================================
-- ALTER TABLE channels ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE live_broadcasts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE live_products ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE live_benefits ENABLE ROW LEVEL SECURITY;

-- 모든 사용자가 읽기 가능한 정책 (예시)
-- CREATE POLICY "Anyone can read channels" ON channels FOR SELECT USING (true);
-- CREATE POLICY "Anyone can read live_broadcasts" ON live_broadcasts FOR SELECT USING (true);
-- CREATE POLICY "Anyone can read live_products" ON live_products FOR SELECT USING (true);
-- CREATE POLICY "Anyone can read live_benefits" ON live_benefits FOR SELECT USING (true);

-- ============================================================================
-- 스키마 완료
-- ============================================================================

