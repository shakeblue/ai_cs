-- 라이브 방송 상세 정보 테이블 스키마
-- 수집정보 문서의 모든 항목을 저장할 수 있도록 설계

-- 1) 기본 정보 (Metadata)
CREATE TABLE IF NOT EXISTS live_broadcasts (
    live_id VARCHAR(100) PRIMARY KEY,  -- 플랫폼+날짜+브랜드코드
    channel_id INTEGER REFERENCES channels(channel_id),
    platform_name VARCHAR(50) NOT NULL,  -- 네이버/카카오/쿠팡/그립 등
    brand_name VARCHAR(100) NOT NULL,  -- 설화수/라네즈/이니스프리 등
    live_title_customer VARCHAR(500) NOT NULL,  -- 고객용 방송명
    live_title_cs VARCHAR(500),  -- CS용 요약명
    source_url TEXT NOT NULL,  -- 원천 URL
    
    -- 2) 방송 스케줄 & 혜택 유효시간
    broadcast_date DATE NOT NULL,
    broadcast_start_time TIME,
    broadcast_end_time TIME,
    benefit_valid_type VARCHAR(50),  -- '방송중만'/'당일23:59'/'기간형'
    benefit_start_datetime TIMESTAMP,
    benefit_end_datetime TIMESTAMP,
    broadcast_format VARCHAR(50),  -- '단독라이브'/'콜라보'/'브랜드관연계'
    
    -- 메타데이터
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    crawled_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- 3) 판매 상품 정보
CREATE TABLE IF NOT EXISTS live_products (
    product_id SERIAL PRIMARY KEY,
    live_id VARCHAR(100) REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    sku VARCHAR(100),
    product_name VARCHAR(500) NOT NULL,
    product_option VARCHAR(200),
    is_main_product BOOLEAN DEFAULT FALSE,  -- 대표상품 여부
    is_set_product BOOLEAN DEFAULT FALSE,  -- 세트상품 여부
    set_composition TEXT,  -- 세트 구성 상세
    original_price INTEGER,
    sale_price INTEGER,
    discount_rate INTEGER,
    stock_info VARCHAR(100),  -- '재고충분'/'품절임박'/'선착순N개' 등
    stock_quantity INTEGER,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4-a) 할인 관련 혜택
CREATE TABLE IF NOT EXISTS live_discounts (
    discount_id SERIAL PRIMARY KEY,
    live_id VARCHAR(100) REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    discount_type VARCHAR(50),  -- '%할인'/'금액할인'/'타임특가'
    discount_detail TEXT NOT NULL,  -- '방송 중 결제 시 20% 할인'
    discount_value VARCHAR(50),  -- '20%' 또는 '5000원'
    conditions TEXT,  -- 적용 조건
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4-b) 사은품(GWP) 정보
CREATE TABLE IF NOT EXISTS live_gifts (
    gift_id SERIAL PRIMARY KEY,
    live_id VARCHAR(100) REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    gift_type VARCHAR(50),  -- '구매조건형'/'증정형'/'선착순형'
    gift_name VARCHAR(500) NOT NULL,
    gift_quantity INTEGER,
    gift_condition TEXT,  -- '결제금액 3만원 이상'
    quantity_limit INTEGER,  -- 선착순 수량 제한
    quantity_limit_text VARCHAR(100),  -- '선착순 100명'
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4-c) 쿠폰/적립 정보
CREATE TABLE IF NOT EXISTS live_coupons (
    coupon_id SERIAL PRIMARY KEY,
    live_id VARCHAR(100) REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    coupon_type VARCHAR(50),  -- '플랫폼쿠폰'/'브랜드쿠폰'/'장바구니쿠폰'
    coupon_name VARCHAR(500) NOT NULL,
    coupon_value VARCHAR(50),  -- '5000원'/'10%'
    issue_condition TEXT,  -- '다운로드 필요'
    usage_condition TEXT,  -- 사용 조건
    reward_type VARCHAR(50),  -- '네이버페이적립'/'카카오페이적립' 등
    reward_detail TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4-d) 배송 혜택
CREATE TABLE IF NOT EXISTS live_shipping (
    shipping_id SERIAL PRIMARY KEY,
    live_id VARCHAR(100) REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    shipping_benefit VARCHAR(100),  -- '무료배송'/'특급배송'/'당일배송'
    shipping_detail TEXT,
    shipping_condition TEXT,  -- 조건
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5) 중복 적용 정책 (Risk Point)
CREATE TABLE IF NOT EXISTS live_policy (
    policy_id SERIAL PRIMARY KEY,
    live_id VARCHAR(100) REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    coupon_duplicate VARCHAR(20),  -- '가능'/'불가'
    reward_duplicate VARCHAR(20),  -- '가능'/'불가'
    other_event_combination TEXT,  -- 타행사 중복 가능 조합
    employee_discount_applicable VARCHAR(20),  -- '가능'/'불가'
    policy_detail TEXT,  -- 기타 정책 상세
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6) 제외/제한 사항
CREATE TABLE IF NOT EXISTS live_restrictions (
    restriction_id SERIAL PRIMARY KEY,
    live_id VARCHAR(100) REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    excluded_products TEXT,  -- '기획세트/대용량 제외'
    channel_restriction TEXT,  -- '방송 중 결제만, 앱 전용'
    payment_restriction TEXT,  -- 'N페이 전용, 카드 전용'
    region_restriction TEXT,  -- '도서산간 제외'
    other_restrictions TEXT,  -- 기타 제한사항
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7) 라이브 특화 정보 (STT 기반)
CREATE TABLE IF NOT EXISTS live_stt_info (
    stt_id SERIAL PRIMARY KEY,
    live_id VARCHAR(100) REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    key_message TEXT,  -- 핵심 세일즈 멘트 (JSON Array)
    broadcast_qa TEXT,  -- 시청자 질문-답변 (JSON Array)
    timeline_summary TEXT,  -- 타임라인 요약 (JSON Array)
    full_transcript TEXT,  -- 전체 스크립트 (선택)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 8) CS 응대용 정보
CREATE TABLE IF NOT EXISTS live_cs_info (
    cs_info_id SERIAL PRIMARY KEY,
    live_id VARCHAR(100) REFERENCES live_broadcasts(live_id) ON DELETE CASCADE,
    expected_questions TEXT,  -- 예상 질문 (JSON Array)
    response_scripts TEXT,  -- 응답 스크립트 (JSON Array)
    risk_points TEXT,  -- 리스크 포인트 (JSON Array)
    cs_notes TEXT,  -- CS 추가 노트
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_live_broadcasts_date ON live_broadcasts(broadcast_date DESC);
CREATE INDEX IF NOT EXISTS idx_live_broadcasts_brand ON live_broadcasts(brand_name);
CREATE INDEX IF NOT EXISTS idx_live_broadcasts_platform ON live_broadcasts(platform_name);
CREATE INDEX IF NOT EXISTS idx_live_products_live_id ON live_products(live_id);
CREATE INDEX IF NOT EXISTS idx_live_discounts_live_id ON live_discounts(live_id);
CREATE INDEX IF NOT EXISTS idx_live_gifts_live_id ON live_gifts(live_id);
CREATE INDEX IF NOT EXISTS idx_live_coupons_live_id ON live_coupons(live_id);

-- 코멘트 추가
COMMENT ON TABLE live_broadcasts IS '라이브 방송 기본 정보 및 스케줄';
COMMENT ON TABLE live_products IS '라이브 방송 판매 상품 목록';
COMMENT ON TABLE live_discounts IS '라이브 방송 할인 혜택';
COMMENT ON TABLE live_gifts IS '라이브 방송 사은품 정보';
COMMENT ON TABLE live_coupons IS '라이브 방송 쿠폰/적립 정보';
COMMENT ON TABLE live_shipping IS '라이브 방송 배송 혜택';
COMMENT ON TABLE live_policy IS '라이브 방송 중복 적용 정책';
COMMENT ON TABLE live_restrictions IS '라이브 방송 제외/제한 사항';
COMMENT ON TABLE live_stt_info IS '라이브 방송 STT 기반 특화 정보';
COMMENT ON TABLE live_cs_info IS '라이브 방송 CS 응대용 정보';

