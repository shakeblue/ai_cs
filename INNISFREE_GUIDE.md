# 이니스프리 이벤트 크롤링 가이드

## 📋 개요

[이니스프리 이벤트 페이지](https://www.innisfree.com/kr/ko/ca/event/102214)의 이벤트 정보를 크롤링하여 상담 시스템에서 조회할 수 있도록 구현했습니다.

### 크롤링된 이벤트 정보

#### 🎁 오직 APP에서만 더 챙겨드립니다
- **이벤트 기간**: 2025.11.25 ~ 2025.11.30
- **할인율**: 최대 30%
- **주요 상품**:
  1. 레티놀 시카 앰플 기획세트 (30mL+10mL): **28,800원** (28% 할인)
  2. 레티놀 시카 흔적 장벽크림 세트 (50mL+30mL): **24,500원** (30% 할인)
  3. 비타민C 캡슐 세럼 기획세트 (30mL+10mL): **27,360원** (28% 할인)
  4. 비타민C 캡슐 크림 대용량 80mL: **31,500원** (30% 할인)

## 🚀 데이터 삽입 방법

### 방법 1: SQL 스크립트 실행 (권장)

```bash
# PostgreSQL 접속
psql -U postgres -d cosmetic_consultation

# SQL 파일 실행
\i database/insert_innisfree_event.sql
```

### 방법 2: Python 크롤러 실행

```bash
cd crawler
python3 crawl_innisfree_event.py
```

**사전 요구사항**:
- PostgreSQL 데이터베이스 실행 중
- `crawler/.env` 파일에 데이터베이스 연결 정보 설정
- Python 패키지 설치: `pip install -r requirements.txt`

### 방법 3: 수동 SQL 실행

데이터베이스 클라이언트(DBeaver, pgAdmin 등)에서 아래 SQL을 실행하세요:

```sql
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
    '이니스프리 앱에서만 제공하는 특별 할인 이벤트입니다.',
    '2025-11-25',
    '2025-11-30',
    30.00,
    '레티놀 시카 앰플 28% 할인, 비타민C 캡슐 세럼 28% 할인',
    '참여 상품 4개 - 레티놀 시카 앰플 기획세트: 28,800원 (28% 할인)',
    '레티놀 시카 앰플, 레티놀 시카 흔적 장벽크림, 비타민C 캡슐 세럼',
    'APP 전용 이벤트입니다.',
    'https://www.innisfree.com/kr/ko/ca/event/102214',
    'ACTIVE',
    8,
    ARRAY['이니스프리', 'APP전용', '레티놀', '비타민C', '할인']
);
```

## 📊 상담 시스템에서 조회하기

### 1. 프론트엔드 접속

```bash
# 브라우저에서 열기
open http://localhost:3001/search
```

### 2. 검색 방법

상담 시스템의 **프로모션 조회** 메뉴에서 다음 키워드로 검색 가능:

- **채널**: 이니스프리
- **키워드**: 레티놀, 비타민C, 앱전용, 할인
- **기간**: 2025-11-25 ~ 2025-11-30

### 3. 조회 결과

이벤트 카드에서 확인 가능한 정보:
- ✅ 이벤트 제목 및 기간
- ✅ 할인율 (최대 30%)
- ✅ 혜택 요약
- ✅ 참여 상품 목록
- ✅ 이벤트 상세 조건
- ✅ 원본 페이지 링크

## 🛠 구현 파일

### 새로 추가된 파일

1. **`crawler/parsers/innisfree_parser.py`**
   - 이니스프리 이벤트 페이지 HTML 파싱
   - 상품 정보, 가격, 할인율 추출
   - 데이터베이스 저장 형식으로 변환

2. **`crawler/crawl_innisfree_event.py`**
   - 이니스프리 이벤트 크롤링 실행 스크립트
   - HTTP 요청 및 HTML 다운로드
   - 파싱 및 데이터베이스 저장

3. **`database/insert_innisfree_event.sql`**
   - 이니스프리 이벤트 데이터 직접 삽입 SQL
   - 2개 이벤트 데이터 포함 (APP 전용, 홀리데이 에디션)

## 🎯 상담원 활용 예시

### 고객 문의 예시 1
**고객**: "이니스프리에서 레티놀 제품 할인하나요?"

**상담원 (시스템 조회 후)**:
> 네, 현재 이니스프리 앱에서 레티놀 제품 특별 할인 중입니다!
> 
> 📱 **오직 APP에서만 더 챙겨드립니다**
> - 기간: 11월 25일 ~ 11월 30일
> - 레티놀 시카 앰플 기획세트: 28,800원 (28% 할인)
> - 레티놀 시카 흔적 장벽크림 세트: 24,500원 (30% 할인)
>
> ⚠️ 이니스프리 공식 앱에서만 구매 가능합니다.

### 고객 문의 예시 2
**고객**: "비타민C 세럼 이벤트 있나요?"

**상담원 (시스템 조회 후)**:
> 네, 비타민C 제품도 할인 중입니다!
>
> - 비타민C 캡슐 세럼 기획세트 (30mL+10mL): 27,360원 (28% 할인)
> - 비타민C 캡슐 크림 대용량 80mL: 31,500원 (30% 할인)
>
> 이벤트 페이지: https://www.innisfree.com/kr/ko/ca/event/102214

## 🔄 자동 크롤링 설정 (선택사항)

정기적으로 이니스프리 이벤트를 자동 크롤링하려면:

```bash
# crontab 편집
crontab -e

# 매일 오전 9시에 크롤링 실행
0 9 * * * cd "/Users/amore/ai_cs 시스템/crawler" && python3 crawl_innisfree_event.py >> /tmp/innisfree_crawl.log 2>&1
```

## 📝 참고사항

- 이니스프리 웹사이트 구조가 변경되면 파서 수정 필요
- APP 전용 이벤트는 웹에서 구매 불가
- 재고 소진 시 조기 종료될 수 있음
- 상담 시 이벤트 페이지 링크를 고객에게 제공 권장

## ✅ 완료 체크리스트

- [x] 이니스프리 파서 구현
- [x] 크롤러 스크립트 작성
- [x] SQL 삽입 스크립트 생성
- [ ] 데이터베이스에 데이터 삽입
- [ ] 상담 시스템에서 조회 확인

## 🆘 문제 해결

### 데이터가 조회되지 않는 경우

1. 데이터베이스 확인:
```sql
SELECT * FROM events WHERE external_id = 'innisfree_event_102214';
```

2. 백엔드 API 확인:
```bash
curl http://localhost:3000/api/events?search=이니스프리
```

3. 로그 확인:
```bash
# 백엔드 로그
tail -f backend/logs/combined.log

# 크롤러 로그
tail -f /tmp/innisfree_crawl.log
```

---

**문의사항이 있으시면 시스템 관리자에게 연락하세요.**

