# Quick Start Guide

네이버 브랜드 이벤트 데이터 추출 시스템을 빠르게 시작하는 가이드입니다.

## 1분 빠른 시작

### 1단계: Supabase 테이블 생성

1. Supabase 대시보드로 이동
2. SQL Editor 열기
3. `create_table.sql` 파일의 내용을 복사하여 실행

### 2단계: Python 환경 설정

```bash
cd crawler/cj

# 가상환경 생성 및 활성화 (권장)
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt
```

### 3단계: 파이프라인 실행

```bash
# 전체 파이프라인 실행 (크롤링 + OCR + DB 저장)
python naver_event_pipeline.py --url "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"
```

완료! 이제 Supabase 데이터베이스에서 추출된 데이터를 확인할 수 있습니다.

## 프론트엔드에서 확인

### 1단계: 백엔드 서버 재시작

```bash
cd ../../backend
npm start
```

### 2단계: 프론트엔드 실행

```bash
cd ../frontend
npm start
```

### 3단계: 브라우저에서 확인

브라우저에서 `http://localhost:3000/naver-smartstore-events` 접속

## 다른 페이지 크롤링하기

```bash
# 다른 네이버 브랜드 페이지 URL로 실행
python naver_event_pipeline.py --url "https://brand.naver.com/BRAND_NAME/shoppingstory/detail?id=XXXXXXXX"
```

## 출력 파일 확인

실행 후 다음 위치에 파일이 생성됩니다:

```
naver_event_output/
├── images/              # 다운로드된 이미지들
│   ├── iope_001.jpg
│   ├── iope_002.jpg
│   └── ...
└── event_data.json     # 추출된 이벤트 정보 (JSON)
```

## 문제 해결

### "ModuleNotFoundError: No module named 'supabase'"
```bash
pip install -r requirements.txt
```

### "Supabase credentials not found"
`.env` 파일에 Supabase 정보가 있는지 확인:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SECRET_KEY=your-secret-key
```

### "No images found"
- 페이지 URL이 올바른지 확인
- `--div-class` 옵션으로 다른 div 클래스 시도

## 다음 단계

더 자세한 사용법은 `README.md`를 참조하세요.
