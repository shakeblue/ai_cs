-- 이니스프리 이벤트 데이터 삽입 스크립트
-- https://www.innisfree.com/kr/ko/ca/event/102214

-- 이니스프리 이벤트: "오직 APP에서만 더 챙겨드립니다🎁"
INSERT INTO events (
    channel_id,
    external_id,
    title,
    subtitle,
    description,
    start_date,
    end_date,
    discount_rate,
    benefit_summary,
    benefit_detail,
    target_products,
    conditions,
    event_url,
    status,
    priority,
    tags
) VALUES (
    (SELECT channel_id FROM channels WHERE channel_code = 'INNISFREE_MALL'),
    'innisfree_event_102214',
    '오직 APP에서만 더 챙겨드립니다🎁',
    '이니스프리 앱 전용 특별 할인',
    '이니스프리 앱에서만 제공하는 특별 할인 이벤트입니다. 레티놀, 비타민C 등 인기 제품을 최대 30% 할인된 가격으로 만나보세요.',
    '2025-11-25',
    '2025-11-30',
    30.00,
    '레티놀 시카 앰플 28% 할인, 비타민C 캡슐 세럼 28% 할인, 레티놀 시카 흔적 장벽크림 30% 할인, 비타민C 캡슐 크림 대용량 30% 할인',
    '참여 상품 4개
- 레티놀 시카 앰플 기획세트 (30mL+10mL): 28,800원 (28% 할인, 정상가 40,000원)
- 레티놀 시카 흔적 장벽크림 세트 (50mL+30mL): 24,500원 (30% 할인, 정상가 35,000원)  
- 비타민C 캡슐 세럼 기획세트 (30mL+10mL): 27,360원 (28% 할인, 정상가 38,000원)
- 비타민C 캡슐 크림 대용량 80mL: 31,500원 (30% 할인, 정상가 45,000원)

모든 상품 APP 전용 혜택 적용',
    '레티놀 시카 앰플, 레티놀 시카 흔적 장벽크림, 비타민C 캡슐 세럼, 비타민C 캡슐 크림',
    'APP 전용 이벤트입니다. 이니스프리 공식 앱에서만 구매 가능합니다. 재고 소진 시 조기 종료될 수 있습니다.',
    'https://www.innisfree.com/kr/ko/ca/event/102214',
    'ACTIVE',
    8,
    ARRAY['이니스프리', 'APP전용', '레티놀', '비타민C', '할인', '기획세트']
)
ON CONFLICT (channel_id, external_id) 
DO UPDATE SET
    title = EXCLUDED.title,
    subtitle = EXCLUDED.subtitle,
    description = EXCLUDED.description,
    start_date = EXCLUDED.start_date,
    end_date = EXCLUDED.end_date,
    discount_rate = EXCLUDED.discount_rate,
    benefit_summary = EXCLUDED.benefit_summary,
    benefit_detail = EXCLUDED.benefit_detail,
    target_products = EXCLUDED.target_products,
    conditions = EXCLUDED.conditions,
    event_url = EXCLUDED.event_url,
    status = EXCLUDED.status,
    priority = EXCLUDED.priority,
    tags = EXCLUDED.tags,
    updated_at = CURRENT_TIMESTAMP;

-- 추가 이벤트: 홀리데이 에디션
INSERT INTO events (
    channel_id,
    external_id,
    title,
    subtitle,
    description,
    start_date,
    end_date,
    discount_rate,
    benefit_summary,
    benefit_detail,
    target_products,
    event_url,
    status,
    priority,
    tags
) VALUES (
    (SELECT channel_id FROM channels WHERE channel_code = 'INNISFREE_MALL'),
    'innisfree_holiday_2025',
    '2025 홀리데이 에디션 출시! ~50% 특가!',
    '홀리데이 한정 패키지',
    '연말을 맞이하여 특별 제작된 홀리데이 에디션 제품들을 최대 50% 할인된 가격으로 만나보세요.',
    '2025-11-20',
    '2025-11-30',
    50.00,
    '그린티 씨드 히알루론산 크림 100mL 세트 50% 할인, 레티놀 그린티 앰플 30% 할인',
    '홀리데이 한정 패키지
- 그린티 씨드 히알루론산 크림 100mL세트: 45,000원 (50% 할인)
- 레티놀 그린티 피디알엔 스킨부스터 앰플 40mL 세트: 39,900원 (30% 할인)
- 레티놀 시카 흔적 앰플 50mL 세트: 39,900원 (30% 할인)
- 마이 퍼퓸드 핸드크림 2종 세트: 16,800원 (30% 할인)',
    '그린티 씨드 히알루론산 크림, 레티놀 그린티 앰플, 레티놀 시카 흔적 앰플, 마이 퍼퓸드 핸드크림',
    'https://www.innisfree.com/kr/ko/event',
    'ACTIVE',
    7,
    ARRAY['이니스프리', '홀리데이', '한정판', '대용량', '할인']
)
ON CONFLICT (channel_id, external_id) 
DO UPDATE SET
    title = EXCLUDED.title,
    updated_at = CURRENT_TIMESTAMP;

-- 결과 확인
SELECT 
    e.event_id,
    e.title,
    c.channel_name,
    e.start_date,
    e.end_date,
    e.discount_rate,
    e.status
FROM events e
INNER JOIN channels c ON e.channel_id = c.channel_id
WHERE c.channel_code = 'INNISFREE_MALL'
ORDER BY e.created_at DESC
LIMIT 5;


