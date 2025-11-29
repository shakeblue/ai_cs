# 온라인 캠페인, 프로모션 조회 시스템 (Online Campaign & Promotion Inquiry System)

화장품 브랜드의 온라인 채널(직영몰, 입점몰, 라이브 쇼핑)에서 진행되는 프로모션/이벤트 정보를 통합 관리하여 상담원의 고객 응대 효율성을 향상시키는 시스템입니다.

## 📋 목차

- [주요 기능](#주요-기능)
- [시스템 아키텍처](#시스템-아키텍처)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [설치 및 실행](#설치-및-실행)
- [API 문서](#api-문서)
- [사용 가이드](#사용-가이드)
- [개발 가이드](#개발-가이드)

---

## 🎯 주요 기능

### 1. 대시보드
- **실시간 통계**: 진행 중인 이벤트, 예정 이벤트, 활성 채널 수 실시간 표시
- **채널별 분석**: 채널별 이벤트 현황을 막대 차트와 파이 차트로 시각화
- **트렌드 분석**: 최근 7일간 신규 이벤트 트렌드 라인 차트
- **긴급 알림**: 곧 종료되는 이벤트 자동 감지 및 표시
- **인기 이벤트**: 즐겨찾기와 조회수 기반 인기 이벤트 목록

### 2. 프로모션 조회
- **고급 검색**: 키워드, 채널, 상태, 날짜 범위 등 다양한 필터 지원
- **카드 뷰**: 이벤트 정보를 직관적인 카드 형식으로 표시
- **상세 보기**: 이벤트 상세 정보 다이얼로그
- **상담 문구 생성**: 클릭 한 번으로 상담용 문구 자동 생성 및 클립보드 복사
- **즐겨찾기**: 자주 참조하는 이벤트 저장
- **페이지네이션**: 대용량 데이터 효율적 처리

### 3. 크롤링 시스템
- **다채널 지원**: 아모레몰, 이니스프리몰, 쿠팡, 네이버 등 다양한 채널
- **자동 스케줄링**: 채널별 설정된 주기로 자동 크롤링
- **중복 체크**: 기존 이벤트 자동 감지 및 업데이트
- **에러 처리**: 실패 시 재시도 및 알림
- **로깅**: 상세한 크롤링 로그 기록

### 4. 관리 기능
- **사용자 관리**: 역할 기반 접근 제어 (ADMIN, AGENT, VIEWER)
- **JWT 인증**: 안전한 토큰 기반 인증
- **API Rate Limiting**: API 남용 방지
- **감사 로그**: 모든 이벤트 변경 이력 추적

---

## 🏗 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  - Dashboard: 실시간 통계 및 차트                            │
│  - Search: 이벤트 검색 및 필터링                             │
│  - Zustand: 전역 상태 관리                                   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (JWT)
┌────────────────────────┴────────────────────────────────────┐
│              Backend (Node.js/Express)                       │
│  - API Gateway: 요청 라우팅 및 인증                          │
│  - Event Service: 이벤트 비즈니스 로직                       │
│  - User Service: 사용자 관리                                 │
│  - Favorite Service: 즐겨찾기 관리                           │
│  - Redis: API 응답 캐싱 (5분 TTL)                            │
└────────────────────────┬────────────────────────────────────┘
                         │ PostgreSQL
┌────────────────────────┴────────────────────────────────────┐
│              Database (PostgreSQL)                           │
│  - events: 이벤트 정보                                       │
│  - channels: 채널 정보                                       │
│  - users: 사용자 정보                                        │
│  - favorites: 즐겨찾기                                       │
│  - crawl_logs: 크롤링 로그                                   │
│  - event_history: 이벤트 변경 이력                           │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│         Crawler System (Python)                              │
│  - Base Crawler: 공통 크롤링 로직                            │
│  - Channel Parsers: 채널별 파싱 로직                         │
│  - Scheduler: 주기적 실행 관리                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 💻 기술 스택

### Frontend
- **React 18**: UI 라이브러리
- **Material-UI (MUI)**: UI 컴포넌트 프레임워크
- **Zustand**: 상태 관리
- **Axios**: HTTP 클라이언트
- **Recharts**: 차트 라이브러리
- **React Router**: 라우팅
- **Moment.js**: 날짜/시간 처리

### Backend
- **Node.js 18+**: 런타임 환경
- **Express.js**: 웹 프레임워크
- **PostgreSQL**: 관계형 데이터베이스
- **Redis**: 캐싱 시스템
- **JWT**: 인증
- **bcrypt**: 비밀번호 해싱
- **Winston**: 로깅
- **Helmet**: 보안 헤더
- **Express Validator**: 입력 검증
- **Express Rate Limit**: API 속도 제한

### Crawler
- **Python 3.10+**: 프로그래밍 언어
- **Requests**: HTTP 클라이언트
- **BeautifulSoup4**: HTML 파싱
- **Selenium**: 동적 페이지 크롤링
- **psycopg2**: PostgreSQL 드라이버
- **Schedule**: 작업 스케줄링
- **python-dotenv**: 환경 변수 관리

### DevOps
- **Docker**: 컨테이너화 (선택)
- **Git**: 버전 관리
- **PM2**: Node.js 프로세스 관리 (프로덕션)

---

## 📁 프로젝트 구조

```
ai_cs 시스템/
├── database/
│   └── schema.sql                 # PostgreSQL 스키마
├── backend/
│   ├── package.json
│   └── src/
│       ├── server.js              # 메인 서버
│       ├── config/
│       │   ├── database.js        # DB 연결
│       │   ├── logger.js          # 로깅 설정
│       │   └── redis.js           # Redis 설정
│       ├── middleware/
│       │   ├── auth.js            # JWT 인증
│       │   ├── validator.js       # 입력 검증
│       │   └── rateLimit.js       # Rate Limiting
│       ├── services/
│       │   ├── eventService.js    # 이벤트 서비스
│       │   ├── userService.js     # 사용자 서비스
│       │   └── favoriteService.js # 즐겨찾기 서비스
│       └── routes/
│           ├── authRoutes.js      # 인증 API
│           ├── eventRoutes.js     # 이벤트 API
│           ├── dashboardRoutes.js # 대시보드 API
│           └── favoriteRoutes.js  # 즐겨찾기 API
├── crawler/
│   ├── requirements.txt
│   ├── config.py                  # 크롤러 설정
│   ├── database.py                # DB 연결
│   ├── base_crawler.py            # 기본 크롤러
│   └── main.py                    # 메인 실행
├── frontend/
│   ├── package.json
│   └── src/
│       ├── index.js               # 엔트리 포인트
│       ├── App.jsx                # 메인 App
│       ├── api/
│       │   ├── axios.js           # Axios 설정
│       │   └── services.js        # API 함수
│       ├── store/
│       │   └── authStore.js       # 인증 상태 관리
│       └── pages/
│           ├── Login.jsx          # 로그인 페이지
│           ├── Dashboard.jsx      # 대시보드 페이지
│           └── SearchEvents.jsx   # 프로모션 조회 페이지
├── SYSTEM_DESIGN.md               # 시스템 설계 문서
└── README.md                      # 이 파일
```

---

## 🚀 설치 및 실행

### 사전 요구사항

- **Node.js**: 18.x 이상
- **Python**: 3.10 이상
- **PostgreSQL**: 14 이상
- **Redis**: 6.x 이상 (선택적, 캐싱용)

### 1. 데이터베이스 설정

```bash
# PostgreSQL 데이터베이스 생성
createdb cosmetic_consultation_system

# 스키마 생성
psql -d cosmetic_consultation_system -f database/schema.sql
```

### 2. 백엔드 설정 및 실행

```bash
cd backend

# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 데이터베이스 정보 등 설정

# 개발 모드 실행
npm run dev

# 또는 프로덕션 모드
npm start
```

백엔드 서버: http://localhost:3000

### 3. 프론트엔드 설정 및 실행

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

프론트엔드: http://localhost:3001

### 4. 크롤러 설정 및 실행

```bash
cd crawler

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 데이터베이스 정보 설정

# 크롤러 실행
python main.py
```

---

## 📚 API 문서

### 인증 API

#### POST /api/auth/login
로그인

**요청:**
```json
{
  "username": "agent001",
  "password": "password123"
}
```

**응답:**
```json
{
  "success": true,
  "data": {
    "user": {
      "user_id": 1,
      "username": "agent001",
      "full_name": "상담원1",
      "role": "AGENT"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

#### GET /api/auth/me
현재 사용자 정보 조회 (인증 필요)

### 대시보드 API

#### GET /api/dashboard
대시보드 전체 데이터 조회 (인증 필요)

**응답:**
```json
{
  "success": true,
  "data": {
    "statistics": {
      "active_events": 42,
      "pending_events": 15,
      "total_channels": 8,
      "avg_discount": "25.50"
    },
    "by_channel": [...],
    "trend": [...],
    "urgent_events": [...],
    "popular_events": [...]
  }
}
```

### 이벤트 API

#### GET /api/events/search
이벤트 검색

**쿼리 파라미터:**
- `channel`: 채널 코드 (선택)
- `status`: 상태 (ACTIVE, PENDING, ENDED)
- `keyword`: 검색 키워드 (선택)
- `page`: 페이지 번호 (기본: 0)
- `page_size`: 페이지 크기 (기본: 20)

**응답:**
```json
{
  "success": true,
  "data": [
    {
      "event_id": "uuid",
      "title": "이벤트 제목",
      "channel_name": "아모레몰",
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-12-31T23:59:59Z",
      "discount_rate": 30.0,
      "benefit_summary": "신규회원 30% 할인",
      "event_url": "https://...",
      "status": "ACTIVE"
    }
  ],
  "pagination": {
    "total": 100,
    "page": 0,
    "page_size": 20,
    "total_pages": 5
  }
}
```

#### GET /api/events/:event_id
이벤트 상세 조회

#### GET /api/events/:event_id/consultation-text
상담용 문구 생성 (인증 필요)

### 즐겨찾기 API

#### GET /api/favorites
즐겨찾기 목록 조회 (인증 필요)

#### POST /api/favorites
즐겨찾기 추가 (인증 필요)

**요청:**
```json
{
  "event_id": "uuid",
  "memo": "자주 문의하는 이벤트"
}
```

#### DELETE /api/favorites/:favorite_id
즐겨찾기 삭제 (인증 필요)

---

## 📖 사용 가이드

### 1. 로그인
- 테스트 계정으로 로그인
  - 사용자명: `agent001`
  - 비밀번호: `agent001` (스키마의 샘플 데이터 참조)

### 2. 대시보드 확인
- 진행 중인 이벤트 현황 실시간 확인
- 채널별 통계 및 트렌드 분석
- 긴급 이벤트 및 인기 이벤트 목록 확인

### 3. 이벤트 검색
- 키워드, 채널, 상태로 이벤트 필터링
- 검색 결과 카드 뷰로 확인
- 이벤트 클릭하여 상세 정보 보기

### 4. 상담 문구 생성
- 이벤트 카드의 복사 아이콘 클릭
- 자동 생성된 상담 문구가 클립보드에 복사됨
- 고객 상담 시 바로 활용

### 5. 즐겨찾기
- 자주 참조하는 이벤트를 즐겨찾기에 추가
- 빠른 접근 가능

---

## 🔧 개발 가이드

### 환경 변수 설정

#### 백엔드 (.env)
```env
NODE_ENV=development
PORT=3000
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cosmetic_consultation_system
DB_USER=postgres
DB_PASSWORD=your_password
JWT_SECRET=your_jwt_secret_key
REDIS_HOST=localhost
REDIS_PORT=6379
```

#### 크롤러 (.env)
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=cosmetic_consultation_system
DB_USER=postgres
DB_PASSWORD=your_password
LOG_LEVEL=INFO
```

### 코드 스타일
- **백엔드**: 파라미터는 `p_` 접두사, 지역변수는 `_v_` 접두사 사용
- **프론트엔드**: ESLint 설정 준수
- **주석**: 모든 함수에 설명 주석 작성

### 테스트
```bash
# 백엔드 테스트
cd backend
npm test

# 프론트엔드 테스트
cd frontend
npm test
```

### 프로덕션 배포

```bash
# 백엔드
cd backend
npm run build  # 필요시
pm2 start src/server.js --name cs-backend

# 프론트엔드
cd frontend
npm run build
# 빌드된 파일을 웹 서버(Nginx 등)로 서빙

# 크롤러
cd crawler
pm2 start main.py --name cs-crawler --interpreter python3
```

---

## 📊 성능 지표

- **API 응답 시간**: < 300ms (목표)
- **크롤링 성공률**: > 98%
- **데이터베이스**: 10만+ 이벤트 처리 가능
- **동시 사용자**: 100+ 지원

---

## 🛡 보안

- JWT 기반 인증
- bcrypt 비밀번호 해싱
- SQL Injection 방지 (Prepared Statements)
- XSS 방지 (입출력 Sanitization)
- API Rate Limiting
- Helmet.js 보안 헤더
- CORS 설정

---

## 🐛 트러블슈팅

### 데이터베이스 연결 실패
- PostgreSQL이 실행 중인지 확인
- 환경 변수의 DB 정보가 올바른지 확인
- 방화벽 설정 확인

### Redis 연결 실패
- Redis 서버가 실행 중인지 확인
- Redis는 선택적 기능이므로 연결 실패해도 시스템은 동작함

### 크롤링 실패
- robots.txt 준수 여부 확인
- 대상 사이트의 HTML 구조 변경 여부 확인
- 네트워크 연결 상태 확인

---

## 📝 라이선스

PROPRIETARY - Amore Pacific

---

## 👥 개발자

- **시스템 아키텍트**: AI Assistant
- **프로젝트 관리자**: Amore Pacific

---

## 📞 문의

프로젝트 관련 문의사항은 이슈 트래커를 통해 등록해주세요.

---

**© 2024 Amore Pacific. All Rights Reserved.**


