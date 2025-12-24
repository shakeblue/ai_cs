-- ============================================================================
-- 화장품 상담 시스템 데이터베이스 스키마
-- PostgreSQL 14+
-- ============================================================================

-- 데이터베이스 생성 (선택적)
-- CREATE DATABASE cosmetic_consultation_system;
-- \c cosmetic_consultation_system;

-- 확장 기능 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";  -- UUID 생성
CREATE EXTENSION IF NOT EXISTS "pg_trgm";     -- 텍스트 검색 최적화

-- ============================================================================
-- 1. 채널 정보 테이블
-- ============================================================================
-- 목적: 온라인 판매 채널 (직영몰, 입점몰, 라이브 쇼핑) 정보 관리
-- 활용: 크롤링 대상 채널 관리 및 채널별 통계 집계
CREATE TABLE channels (
    channel_id          SERIAL PRIMARY KEY,                          -- 채널 고유 ID
    channel_code        VARCHAR(50) UNIQUE NOT NULL,                 -- 채널 코드 (예: AMORE_MALL, NAVER, COUPANG)
    channel_name        VARCHAR(100) NOT NULL,                       -- 채널 표시명
    channel_type        VARCHAR(20) NOT NULL,                        -- 채널 유형 (DIRECT: 직영몰, PARTNER: 입점몰, LIVE: 라이브쇼핑)
    base_url            TEXT NOT NULL,                               -- 크롤링 대상 기본 URL
    crawl_interval      INTEGER DEFAULT 360,                         -- 크롤링 주기 (분 단위)
    is_active           BOOLEAN DEFAULT TRUE,                        -- 활성화 상태
    icon_url            TEXT,                                        -- 채널 아이콘 URL
    description         TEXT,                                        -- 채널 설명
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 생성 일시
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 수정 일시
    
    CONSTRAINT chk_channel_type CHECK (channel_type IN ('DIRECT', 'PARTNER', 'LIVE'))
);

-- 채널 코드 인덱스 (검색 최적화)
CREATE INDEX idx_channels_code ON channels(channel_code);
CREATE INDEX idx_channels_type ON channels(channel_type);

-- 채널 초기 데이터
INSERT INTO channels (channel_code, channel_name, channel_type, base_url, crawl_interval) VALUES
('AMORE_MALL', '아모레몰', 'DIRECT', 'https://www.amoremall.com/kr/ko/display/event', 360),
('INNISFREE_MALL', '이니스프리몰', 'DIRECT', 'https://www.innisfree.com/kr/ko/event', 360),
('OSULLOC_MALL', '오설록몰', 'DIRECT', 'https://www.osulloc.com/kr/ko/event', 360),
('NAVER', '네이버', 'PARTNER', 'https://brand.naver.com/amorepacific', 720),
('COUPANG', '쿠팡', 'PARTNER', 'https://www.coupang.com/np/campaigns/82', 720),
('KAKAO', '카카오', 'PARTNER', 'https://shopping.kakao.com', 720),
('STREET11', '11번가', 'PARTNER', 'https://www.11st.co.kr', 720),
('NAVER_LIVE', '네이버 쇼핑라이브', 'LIVE', 'https://shopping.naver.com/live', 60),
('KAKAO_LIVE', '카카오 쇼핑라이브', 'LIVE', 'https://shoppinglive.kakao.com', 60);

-- ============================================================================
-- 2. 이벤트/프로모션 정보 테이블
-- ============================================================================
-- 목적: 각 채널에서 진행되는 이벤트 및 프로모션 정보 저장
-- 활용: 상담원이 조회하는 핵심 데이터
CREATE TABLE events (
    event_id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(), -- 이벤트 고유 ID
    channel_id          INTEGER NOT NULL REFERENCES channels(channel_id) ON DELETE CASCADE, -- 채널 ID (외래키)
    external_id         VARCHAR(255),                                -- 외부 시스템 이벤트 ID
    title               VARCHAR(500) NOT NULL,                       -- 이벤트 제목
    subtitle            VARCHAR(500),                                -- 이벤트 부제목
    description         TEXT,                                        -- 이벤트 상세 설명
    
    -- 기간 정보
    start_date          TIMESTAMP NOT NULL,                          -- 시작 일시
    end_date            TIMESTAMP NOT NULL,                          -- 종료 일시
    
    -- 혜택 정보
    discount_rate       NUMERIC(5, 2),                               -- 할인율 (%)
    discount_amount     NUMERIC(12, 2),                              -- 할인 금액 (원)
    coupon_code         VARCHAR(100),                                -- 쿠폰 코드
    benefit_summary     VARCHAR(500),                                -- 혜택 요약
    benefit_detail      TEXT,                                        -- 혜택 상세
    
    -- 적용 대상
    target_products     TEXT,                                        -- 대상 제품 (JSON 또는 텍스트)
    target_brands       TEXT,                                        -- 대상 브랜드
    target_categories   TEXT,                                        -- 대상 카테고리
    
    -- 조건 및 유의사항
    conditions          TEXT,                                        -- 적용 조건
    cautions            TEXT,                                        -- 유의사항
    
    -- URL 정보
    event_url           TEXT NOT NULL,                               -- 이벤트 페이지 URL
    image_url           TEXT,                                        -- 대표 이미지 URL
    thumbnail_url       TEXT,                                        -- 썸네일 이미지 URL
    
    -- 상태 정보
    status              VARCHAR(20) DEFAULT 'PENDING',               -- 이벤트 상태 (PENDING: 예정, ACTIVE: 진행중, ENDED: 종료, CANCELLED: 취소)
    priority            INTEGER DEFAULT 0,                           -- 우선순위 (높을수록 중요)
    
    -- 메타 정보
    view_count          INTEGER DEFAULT 0,                           -- 조회 수 (상담원)
    favorite_count      INTEGER DEFAULT 0,                           -- 즐겨찾기 수
    tags                TEXT[],                                      -- 태그 배열
    
    -- 크롤링 정보
    crawled_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 크롤링 일시
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 생성 일시
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 수정 일시
    
    CONSTRAINT chk_event_status CHECK (status IN ('PENDING', 'ACTIVE', 'ENDED', 'CANCELLED')),
    CONSTRAINT chk_event_dates CHECK (end_date >= start_date)
);

-- 이벤트 테이블 인덱스 (성능 최적화)
CREATE INDEX idx_events_channel ON events(channel_id);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_dates ON events(start_date, end_date);
CREATE INDEX idx_events_created ON events(created_at DESC);
CREATE INDEX idx_events_external ON events(channel_id, external_id);

-- 전문 검색을 위한 GIN 인덱스
CREATE INDEX idx_events_title_search ON events USING gin(title gin_trgm_ops);
CREATE INDEX idx_events_benefit_search ON events USING gin(benefit_summary gin_trgm_ops);
CREATE INDEX idx_events_tags ON events USING gin(tags);

-- ============================================================================
-- 3. 이벤트 변경 이력 테이블
-- ============================================================================
-- 목적: 이벤트 정보 변경 이력 추적
-- 활용: 프로모션 조건 변경 추적, 감사 로그
CREATE TABLE event_history (
    history_id          SERIAL PRIMARY KEY,                          -- 이력 고유 ID
    event_id            UUID NOT NULL REFERENCES events(event_id) ON DELETE CASCADE, -- 이벤트 ID
    change_type         VARCHAR(20) NOT NULL,                        -- 변경 유형 (INSERT, UPDATE, DELETE)
    changed_fields      JSONB,                                       -- 변경된 필드 (JSON)
    old_values          JSONB,                                       -- 변경 전 값
    new_values          JSONB,                                       -- 변경 후 값
    changed_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 변경 일시
    changed_by          VARCHAR(100),                                -- 변경자 (시스템 또는 사용자 ID)
    
    CONSTRAINT chk_change_type CHECK (change_type IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX idx_event_history_event ON event_history(event_id);
CREATE INDEX idx_event_history_date ON event_history(changed_at DESC);

-- ============================================================================
-- 4. 사용자 테이블
-- ============================================================================
-- 목적: 상담원 및 관리자 계정 관리
-- 활용: 인증, 권한 관리, 활동 추적
CREATE TABLE users (
    user_id             SERIAL PRIMARY KEY,                          -- 사용자 고유 ID
    username            VARCHAR(50) UNIQUE NOT NULL,                 -- 사용자명 (로그인 ID)
    password_hash       VARCHAR(255) NOT NULL,                       -- 비밀번호 해시 (bcrypt)
    full_name           VARCHAR(100) NOT NULL,                       -- 실명
    email               VARCHAR(255) UNIQUE NOT NULL,                -- 이메일
    phone               VARCHAR(20),                                 -- 전화번호
    
    -- 역할 및 권한
    role                VARCHAR(20) DEFAULT 'AGENT',                 -- 역할 (ADMIN: 관리자, AGENT: 상담원, VIEWER: 조회만)
    department          VARCHAR(100),                                -- 부서
    team                VARCHAR(100),                                -- 팀
    
    -- 상태 정보
    is_active           BOOLEAN DEFAULT TRUE,                        -- 활성화 상태
    last_login_at       TIMESTAMP,                                   -- 마지막 로그인 일시
    login_count         INTEGER DEFAULT 0,                           -- 로그인 횟수
    
    -- 메타 정보
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 생성 일시
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 수정 일시
    
    CONSTRAINT chk_user_role CHECK (role IN ('ADMIN', 'AGENT', 'VIEWER'))
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ============================================================================
-- 5. 즐겨찾기 테이블
-- ============================================================================
-- 목적: 상담원이 자주 참조하는 이벤트 저장
-- 활용: 빠른 접근, 인기 이벤트 분석
CREATE TABLE favorites (
    favorite_id         SERIAL PRIMARY KEY,                          -- 즐겨찾기 고유 ID
    user_id             INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE, -- 사용자 ID
    event_id            UUID NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,  -- 이벤트 ID
    memo                TEXT,                                        -- 개인 메모
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 생성 일시
    
    CONSTRAINT uk_favorites_user_event UNIQUE(user_id, event_id)    -- 중복 즐겨찾기 방지
);

CREATE INDEX idx_favorites_user ON favorites(user_id);
CREATE INDEX idx_favorites_event ON favorites(event_id);
CREATE INDEX idx_favorites_created ON favorites(created_at DESC);

-- ============================================================================
-- 6. 조회 로그 테이블
-- ============================================================================
-- 목적: 상담원의 이벤트 조회 활동 기록
-- 활용: 인기 이벤트 분석, 사용 패턴 분석
CREATE TABLE view_logs (
    log_id              BIGSERIAL PRIMARY KEY,                       -- 로그 고유 ID
    user_id             INTEGER REFERENCES users(user_id) ON DELETE SET NULL, -- 사용자 ID
    event_id            UUID REFERENCES events(event_id) ON DELETE CASCADE,   -- 이벤트 ID
    view_type           VARCHAR(20) DEFAULT 'DETAIL',                -- 조회 유형 (LIST: 목록, DETAIL: 상세, CONSULTATION: 상담문구생성)
    ip_address          INET,                                        -- IP 주소
    user_agent          TEXT,                                        -- User Agent
    viewed_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 조회 일시
    
    CONSTRAINT chk_view_type CHECK (view_type IN ('LIST', 'DETAIL', 'CONSULTATION'))
);

-- 파티션을 위한 인덱스 (대용량 로그 처리)
CREATE INDEX idx_view_logs_user ON view_logs(user_id);
CREATE INDEX idx_view_logs_event ON view_logs(event_id);
CREATE INDEX idx_view_logs_date ON view_logs(viewed_at DESC);

-- ============================================================================
-- 7. 크롤링 로그 테이블
-- ============================================================================
-- 목적: 크롤링 작업 실행 이력 및 결과 기록
-- 활용: 모니터링, 장애 감지, 성능 분석
CREATE TABLE crawl_logs (
    log_id              BIGSERIAL PRIMARY KEY,                       -- 로그 고유 ID
    channel_id          INTEGER NOT NULL REFERENCES channels(channel_id) ON DELETE CASCADE, -- 채널 ID
    status              VARCHAR(20) NOT NULL,                        -- 상태 (SUCCESS: 성공, FAILED: 실패, PARTIAL: 부분성공)
    
    -- 실행 정보
    started_at          TIMESTAMP NOT NULL,                          -- 시작 일시
    completed_at        TIMESTAMP,                                   -- 완료 일시
    duration_ms         INTEGER,                                     -- 소요 시간 (밀리초)
    
    -- 결과 정보
    items_found         INTEGER DEFAULT 0,                           -- 발견된 아이템 수
    items_new           INTEGER DEFAULT 0,                           -- 신규 아이템 수
    items_updated       INTEGER DEFAULT 0,                           -- 업데이트된 아이템 수
    items_failed        INTEGER DEFAULT 0,                           -- 실패한 아이템 수
    
    -- 에러 정보
    error_message       TEXT,                                        -- 에러 메시지
    error_stack         TEXT,                                        -- 에러 스택 트레이스
    
    -- 메타 정보
    crawler_version     VARCHAR(20),                                 -- 크롤러 버전
    metadata            JSONB,                                       -- 추가 메타데이터
    
    CONSTRAINT chk_crawl_status CHECK (status IN ('SUCCESS', 'FAILED', 'PARTIAL'))
);

CREATE INDEX idx_crawl_logs_channel ON crawl_logs(channel_id);
CREATE INDEX idx_crawl_logs_status ON crawl_logs(status);
CREATE INDEX idx_crawl_logs_started ON crawl_logs(started_at DESC);

-- ============================================================================
-- 8. 시스템 설정 테이블
-- ============================================================================
-- 목적: 시스템 운영을 위한 설정값 관리
-- 활용: 크롤링 주기, 알림 설정, 기능 토글 등
CREATE TABLE system_settings (
    setting_id          SERIAL PRIMARY KEY,                          -- 설정 고유 ID
    setting_key         VARCHAR(100) UNIQUE NOT NULL,                -- 설정 키
    setting_value       TEXT,                                        -- 설정 값
    value_type          VARCHAR(20) DEFAULT 'STRING',                -- 값 유형 (STRING, INTEGER, BOOLEAN, JSON)
    description         TEXT,                                        -- 설명
    is_editable         BOOLEAN DEFAULT TRUE,                        -- 수정 가능 여부
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 생성 일시
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,         -- 수정 일시
    
    CONSTRAINT chk_value_type CHECK (value_type IN ('STRING', 'INTEGER', 'BOOLEAN', 'JSON'))
);

-- 초기 시스템 설정
INSERT INTO system_settings (setting_key, setting_value, value_type, description) VALUES
('crawl.retry.max_attempts', '3', 'INTEGER', '크롤링 실패 시 최대 재시도 횟수'),
('crawl.retry.delay_seconds', '60', 'INTEGER', '재시도 대기 시간 (초)'),
('alert.slack.enabled', 'true', 'BOOLEAN', 'Slack 알림 활성화 여부'),
('alert.slack.webhook_url', '', 'STRING', 'Slack Webhook URL'),
('cache.ttl_seconds', '300', 'INTEGER', '캐시 만료 시간 (초)'),
('api.rate_limit.requests_per_minute', '100', 'INTEGER', 'API 요청 제한 (분당)');

-- ============================================================================
-- 트리거 함수
-- ============================================================================

-- 1. updated_at 자동 갱신 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. 이벤트 상태 자동 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_event_status()
RETURNS TRIGGER AS $$
BEGIN
    -- 시작일과 종료일을 기반으로 상태 자동 결정
    IF NEW.start_date > CURRENT_TIMESTAMP THEN
        NEW.status = 'PENDING';
    ELSIF NEW.end_date < CURRENT_TIMESTAMP THEN
        NEW.status = 'ENDED';
    ELSE
        NEW.status = 'ACTIVE';
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 3. 이벤트 변경 이력 자동 기록 트리거 함수
CREATE OR REPLACE FUNCTION log_event_changes()
RETURNS TRIGGER AS $$
DECLARE
    _v_change_type VARCHAR(20);
    _v_old_values JSONB;
    _v_new_values JSONB;
BEGIN
    IF TG_OP = 'INSERT' THEN
        _v_change_type = 'INSERT';
        _v_new_values = row_to_json(NEW)::JSONB;
        INSERT INTO event_history (event_id, change_type, new_values, changed_by)
        VALUES (NEW.event_id, _v_change_type, _v_new_values, 'system');
        
    ELSIF TG_OP = 'UPDATE' THEN
        _v_change_type = 'UPDATE';
        _v_old_values = row_to_json(OLD)::JSONB;
        _v_new_values = row_to_json(NEW)::JSONB;
        INSERT INTO event_history (event_id, change_type, old_values, new_values, changed_by)
        VALUES (NEW.event_id, _v_change_type, _v_old_values, _v_new_values, 'system');
        
    ELSIF TG_OP = 'DELETE' THEN
        _v_change_type = 'DELETE';
        _v_old_values = row_to_json(OLD)::JSONB;
        INSERT INTO event_history (event_id, change_type, old_values, changed_by)
        VALUES (OLD.event_id, _v_change_type, _v_old_values, 'system');
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 4. 즐겨찾기 카운트 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_favorite_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE events SET favorite_count = favorite_count + 1 WHERE event_id = NEW.event_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE events SET favorite_count = favorite_count - 1 WHERE event_id = OLD.event_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 트리거 생성
-- ============================================================================

-- updated_at 자동 갱신 트리거
CREATE TRIGGER trigger_channels_updated_at BEFORE UPDATE ON channels
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_events_updated_at BEFORE UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 이벤트 상태 자동 업데이트 트리거
CREATE TRIGGER trigger_event_status BEFORE INSERT OR UPDATE ON events
    FOR EACH ROW EXECUTE FUNCTION update_event_status();

-- 이벤트 변경 이력 기록 트리거
CREATE TRIGGER trigger_event_history AFTER INSERT OR UPDATE OR DELETE ON events
    FOR EACH ROW EXECUTE FUNCTION log_event_changes();

-- 즐겨찾기 카운트 업데이트 트리거
CREATE TRIGGER trigger_favorite_count AFTER INSERT OR DELETE ON favorites
    FOR EACH ROW EXECUTE FUNCTION update_favorite_count();

-- ============================================================================
-- 뷰(View) 생성
-- ============================================================================

-- 1. 활성 이벤트 뷰 (상담원이 가장 자주 사용)
CREATE OR REPLACE VIEW v_active_events AS
SELECT 
    e.event_id,
    e.title,
    e.subtitle,
    c.channel_name,
    c.channel_code,
    c.channel_type,
    e.start_date,
    e.end_date,
    e.discount_rate,
    e.benefit_summary,
    e.event_url,
    e.thumbnail_url,
    e.favorite_count,
    e.view_count,
    e.tags
FROM events e
INNER JOIN channels c ON e.channel_id = c.channel_id
WHERE e.status = 'ACTIVE'
  AND c.is_active = TRUE
ORDER BY e.priority DESC, e.start_date DESC;

-- 2. 채널별 이벤트 통계 뷰
CREATE OR REPLACE VIEW v_channel_statistics AS
SELECT 
    c.channel_id,
    c.channel_name,
    c.channel_type,
    COUNT(e.event_id) as total_events,
    COUNT(CASE WHEN e.status = 'ACTIVE' THEN 1 END) as active_events,
    COUNT(CASE WHEN e.status = 'PENDING' THEN 1 END) as pending_events,
    AVG(e.discount_rate) as avg_discount_rate,
    MAX(e.created_at) as last_event_date
FROM channels c
LEFT JOIN events e ON c.channel_id = e.channel_id
WHERE c.is_active = TRUE
GROUP BY c.channel_id, c.channel_name, c.channel_type;

-- 3. 인기 이벤트 뷰 (즐겨찾기 + 조회수 기반)
CREATE OR REPLACE VIEW v_popular_events AS
SELECT 
    e.event_id,
    e.title,
    c.channel_name,
    e.start_date,
    e.end_date,
    e.benefit_summary,
    e.favorite_count,
    e.view_count,
    (e.favorite_count * 3 + e.view_count) as popularity_score
FROM events e
INNER JOIN channels c ON e.channel_id = c.channel_id
WHERE e.status = 'ACTIVE'
ORDER BY popularity_score DESC
LIMIT 50;

-- ============================================================================
-- 유틸리티 함수
-- ============================================================================

-- 1. 이벤트 검색 함수 (전문 검색)
CREATE OR REPLACE FUNCTION search_events(
    p_keyword VARCHAR,
    p_channel_codes VARCHAR[] DEFAULT NULL,
    p_status VARCHAR DEFAULT 'ACTIVE',
    p_limit INTEGER DEFAULT 20,
    p_offset INTEGER DEFAULT 0
)
RETURNS TABLE (
    event_id UUID,
    title VARCHAR,
    channel_name VARCHAR,
    benefit_summary VARCHAR,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    event_url TEXT,
    relevance REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        e.event_id,
        e.title,
        c.channel_name,
        e.benefit_summary,
        e.start_date,
        e.end_date,
        e.event_url,
        GREATEST(
            similarity(e.title, p_keyword),
            similarity(e.benefit_summary, p_keyword)
        ) as relevance
    FROM events e
    INNER JOIN channels c ON e.channel_id = c.channel_id
    WHERE 
        (p_status IS NULL OR e.status = p_status)
        AND (p_channel_codes IS NULL OR c.channel_code = ANY(p_channel_codes))
        AND (
            e.title ILIKE '%' || p_keyword || '%'
            OR e.benefit_summary ILIKE '%' || p_keyword || '%'
            OR e.target_products ILIKE '%' || p_keyword || '%'
        )
    ORDER BY relevance DESC, e.priority DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- 2. 통계 데이터 조회 함수
CREATE OR REPLACE FUNCTION get_dashboard_stats()
RETURNS JSON AS $$
DECLARE
    _v_result JSON;
BEGIN
    SELECT json_build_object(
        'total_active_events', (SELECT COUNT(*) FROM events WHERE status = 'ACTIVE'),
        'total_channels', (SELECT COUNT(*) FROM channels WHERE is_active = TRUE),
        'total_users', (SELECT COUNT(*) FROM users WHERE is_active = TRUE),
        'today_views', (SELECT COUNT(*) FROM view_logs WHERE DATE(viewed_at) = CURRENT_DATE),
        'channel_breakdown', (
            SELECT json_agg(row_to_json(t))
            FROM v_channel_statistics t
        ),
        'urgent_events', (
            SELECT json_agg(row_to_json(e))
            FROM (
                SELECT event_id, title, channel_name, end_date
                FROM v_active_events
                WHERE end_date BETWEEN CURRENT_TIMESTAMP AND CURRENT_TIMESTAMP + INTERVAL '2 days'
                LIMIT 10
            ) e
        )
    ) INTO _v_result;
    
    RETURN _v_result;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 샘플 데이터 (개발/테스트용)
-- ============================================================================

-- 관리자 계정 생성 (비밀번호: admin123 - 실제로는 해시화 필요)
INSERT INTO users (username, password_hash, full_name, email, role, department) VALUES
('admin', '$2b$10$rQJ5WZ5ZY5YZ5YZ5YZ5YZOeK5YZ5YZ5YZ5YZ5YZ5YZ5YZ5YZ5YZ5Y', '시스템 관리자', 'admin@amore.com', 'ADMIN', 'IT'),
('agent001', '$2b$10$rQJ5WZ5ZY5YZ5YZ5YZ5YZOeK5YZ5YZ5YZ5YZ5YZ5YZ5YZ5YZ5YZ5Y', '상담원1', 'agent001@amore.com', 'AGENT', '상담센터'),
('agent002', '$2b$10$rQJ5WZ5ZY5YZ5YZ5YZ5YZOeK5YZ5YZ5YZ5YZ5YZ5YZ5YZ5YZ5YZ5Y', '상담원2', 'agent002@amore.com', 'AGENT', '상담센터');

-- 샘플 이벤트 데이터
INSERT INTO events (channel_id, external_id, title, subtitle, description, start_date, end_date, discount_rate, benefit_summary, event_url, status) VALUES
(1, 'AMORE_2024_001', '아모레몰 신규회원 가입 혜택', '최대 30% 할인쿠폰', '신규 가입 고객 대상 전 브랜드 30% 할인쿠폰 제공', '2024-01-01', '2024-12-31', 30.00, '신규회원 30% 할인쿠폰', 'https://www.amoremall.com/kr/ko/event/detail/1', 'ACTIVE'),
(2, 'INNISFREE_2024_001', '이니스프리 그린티 기획전', '2+1 증정 이벤트', '그린티 라인 2개 구매시 1개 증정', '2024-11-01', '2024-11-30', NULL, '그린티 라인 2+1', 'https://www.innisfree.com/kr/ko/event/detail/1', 'ACTIVE'),
(5, 'COUPANG_2024_001', '쿠팡 아모레퍼시픽 브랜드데이', '로켓배송 + 추가할인', '로켓배송 대상 상품 15% 추가 할인', '2024-11-20', '2024-11-26', 15.00, '로켓배송 + 15% 할인', 'https://www.coupang.com/np/campaigns/amorepacific', 'ACTIVE');

-- ============================================================================
-- 데이터베이스 권한 설정 (선택적)
-- ============================================================================

-- 애플리케이션용 사용자 생성 및 권한 부여
-- CREATE USER cs_app_user WITH PASSWORD 'secure_password_here';
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO cs_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO cs_app_user;

-- ============================================================================
-- 유지보수용 쿼리
-- ============================================================================

-- 1. 만료된 이벤트 자동 종료
-- CREATE OR REPLACE FUNCTION cleanup_expired_events()
-- RETURNS void AS $$
-- BEGIN
--     UPDATE events SET status = 'ENDED' 
--     WHERE status = 'ACTIVE' AND end_date < CURRENT_TIMESTAMP;
-- END;
-- $$ LANGUAGE plpgsql;

-- 2. 오래된 로그 데이터 정리 (6개월 이상)
-- DELETE FROM view_logs WHERE viewed_at < CURRENT_TIMESTAMP - INTERVAL '6 months';
-- DELETE FROM crawl_logs WHERE started_at < CURRENT_TIMESTAMP - INTERVAL '6 months';

-- ============================================================================
-- 스키마 완료
-- ============================================================================


