# Naver Brand Event Data Extractor

OCR 기술을 활용한 네이버 브랜드 페이지 이벤트 정보 자동 추출 시스템

## 개요

이 시스템은 다음 기능을 제공합니다:

1. **이미지 크롤링**: 네이버 브랜드 페이지에서 특정 div 클래스 내의 이미지를 다운로드
2. **OCR 텍스트 추출**: OCR.space Free API를 사용하여 이미지에서 텍스트 추출
3. **데이터 파싱**: 추출된 텍스트에서 이벤트 정보 자동 파싱
4. **DB 저장**: Supabase 데이터베이스에 자동 저장
5. **웹 UI**: 추출된 데이터를 보기 좋게 표시하는 프론트엔드 페이지

## 추출되는 정보

- 플랫폼 이름 (Platform Name)
- 브랜드 이름 (Brand Name)
- 이벤트 URL (URL)
- 이벤트 제목 (Event Title)
- 이벤트 기간 (Event Date)
- 금액대별 혜택 (Benefits by Purchase Amount)
- 쿠폰 혜택 (Coupon Benefits)

## 설치

### 1. Python 환경 설정

```bash
cd crawler/cj

# 가상환경 생성 (선택사항)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일에 Supabase 정보가 설정되어 있는지 확인:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your-secret-key
SUPABASE_ANON_KEY=your-anon-key
```

### 3. Supabase 테이블 생성

Supabase SQL Editor에서 다음 SQL 실행:

```sql
-- Create naver_smartstore_event table
CREATE TABLE IF NOT EXISTS naver_smartstore_event (
    id BIGSERIAL PRIMARY KEY,
    platform_name TEXT NOT NULL DEFAULT 'Naver Brand',
    brand_name TEXT,
    url TEXT NOT NULL,
    event_title TEXT,
    event_date TEXT,
    benefits_by_purchase_amount JSONB DEFAULT '[]'::jsonb,
    coupon_benefits JSONB DEFAULT '[]'::jsonb,
    raw_ocr_data JSONB,
    image_urls JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_naver_smartstore_event_brand ON naver_smartstore_event(brand_name);
CREATE INDEX IF NOT EXISTS idx_naver_smartstore_event_created ON naver_smartstore_event(created_at DESC);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_naver_smartstore_event_updated_at
    BEFORE UPDATE ON naver_smartstore_event
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## 사용 방법

### 전체 파이프라인 실행 (권장)

```bash
# 기본 사용법 - 이미지 크롤링 + OCR 추출 + DB 저장
python naver_event_pipeline.py --url "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"

# DB 저장 없이 JSON 파일만 생성
python naver_event_pipeline.py --url "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684" --no-save

# 커스텀 div 클래스 지정
python naver_event_pipeline.py --url "https://..." --div-class "custom-container"

# 커스텀 출력 디렉토리 지정
python naver_event_pipeline.py --url "https://..." --output-dir "my_output"
```

### 개별 스크립트 실행

#### 1. 이미지 크롤링만 실행

```bash
python naver_brand_image_crawler.py
```

#### 2. OCR 추출만 실행 (이미지가 이미 다운로드된 경우)

```bash
python naver_event_ocr_extractor.py
```

#### 3. Supabase 저장만 실행

```bash
python save_to_supabase.py
```

## 파일 구조

```
crawler/cj/
├── naver_brand_image_crawler.py    # 이미지 크롤러
├── naver_event_ocr_extractor.py    # OCR 텍스트 추출기
├── save_to_supabase.py             # Supabase 저장 모듈
├── naver_event_pipeline.py         # 전체 파이프라인
├── requirements.txt                # Python 패키지 목록
├── README.md                       # 이 파일
└── naver_event_output/            # 출력 디렉토리 (자동 생성)
    ├── images/                    # 다운로드된 이미지
    └── event_data.json           # 추출된 이벤트 데이터
```

## 백엔드 API

백엔드 서버에 다음 API 엔드포인트가 추가되었습니다:

### 이벤트 목록 조회
```
GET /api/naver-smartstore-events
Query Parameters:
  - brand_name: 브랜드 필터 (선택)
  - limit: 페이지 크기 (기본: 20)
  - offset: 오프셋 (기본: 0)
  - sort_by: 정렬 필드 (기본: created_at)
  - sort_order: 정렬 순서 (asc/desc, 기본: desc)
```

### 이벤트 상세 조회
```
GET /api/naver-smartstore-events/:id
```

### 브랜드 목록 조회
```
GET /api/naver-smartstore-events/brands/list
```

### 이벤트 생성 (크롤러용)
```
POST /api/naver-smartstore-events
Body: { event_data }
```

## 프론트엔드 페이지

프론트엔드에 네이버 스마트스토어 이벤트 표시 페이지가 추가되었습니다:

위치: `frontend/cj/NaverSmartStoreEvents.jsx`

기능:
- 이벤트 그리드 표시
- 브랜드별 필터링
- 이벤트 상세 다이얼로그
- 반응형 다크 테마 디자인

## 백엔드 서버에 라우트 추가

`backend/src/server.js` 파일에 다음 라우트를 추가해야 합니다:

```javascript
const naverSmartstoreRoutes = require('../cj/naver_smartstore_routes');

// ...

app.use('/api/naver-smartstore-events', naverSmartstoreRoutes);
```

## 트러블슈팅

### SSL 인증서 오류
스크립트는 자동으로 SSL 경고를 무시합니다. 프로덕션 환경에서는 적절한 인증서 검증이 필요합니다.

### OCR API 제한
OCR.space Free API는 요청 제한이 있을 수 있습니다. 많은 이미지를 처리할 경우:
- API 키 업그레이드 고려
- 요청 간 딜레이 추가
- 대체 OCR 솔루션 사용 (Tesseract 등)

### Supabase 연결 오류
환경 변수가 올바르게 설정되었는지 확인하세요.

## 라이선스

이 프로젝트는 AI CS 시스템의 일부입니다.

## 기여

문제가 발생하거나 개선 사항이 있으면 이슈를 생성해주세요.
