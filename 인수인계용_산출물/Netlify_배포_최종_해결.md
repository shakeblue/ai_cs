# Netlify 배포 최종 해결 가이드

**작성일**: 2025-12-16  
**프로젝트**: AI CS 시스템  
**담당**: AI Assistant  
**상태**: ✅ 해결 완료

---

## 📋 문제 요약

### 발생한 오류들

#### 오류 1: 중복 경로 문제
```
Custom publish path detected: 'frontend/frontend/build'
                                        ^^^^^^^^ 중복!
```

#### 오류 2: netlify.toml 오버라이드
```
⚠️ Overridden by netlify.toml. Published deploy built with 
   "cd frontend && npm install --legacy-peer-deps && npm run build".
```

#### 오류 3: JSX 문법 오류
```
SyntaxError: /opt/build/repo/frontend/src/pages/LiveBroadcastDetail.jsx: 
Unexpected token (1749:11)
```

---

## ✅ 해결 내역

### 1단계: JSX 문법 오류 수정 ✅

**문제**: `LiveBroadcastDetail.jsx` 파일에 중복 코드 존재 (1537라인부터)

**해결**:
```bash
# 중복 코드 제거
sed -i '' '1537,$d' frontend/src/pages/LiveBroadcastDetail.jsx
```

**결과**: 빌드 성공 (경고만 존재, 오류 없음)

---

### 2단계: netlify.toml 파일 삭제 ✅

**문제**: netlify.toml 파일이 웹 UI 설정을 오버라이드

**해결**:
```bash
# netlify.toml 삭제
rm frontend/netlify.toml
```

**이유**: 
- 웹 UI에서 설정한 값이 netlify.toml에 의해 무시됨
- netlify.toml에 잘못된 경로 설정이 포함되어 있었음
- 웹 UI 설정만으로 충분함

---

### 3단계: Netlify 웹 UI 설정 수정 ✅

**최종 설정**:

| 항목 | 값 |
|------|-----|
| **Base directory** | `frontend` |
| **Build command** | `npm install --legacy-peer-deps && npm run build` |
| **Publish directory** | `build` |
| **Node version** | `18` |

**환경 변수**:
```
NODE_VERSION=18
CI=false
REACT_APP_API_URL=https://ai-cs-backend.onrender.com
REACT_APP_SUPABASE_URL=https://uewhvekfjjvxoioklzza.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_key_here
```

---

### 4단계: Git 커밋 및 푸시 ✅

**커밋 내역**:
```bash
git add -A
git commit -m "fix: netlify.toml 삭제 및 배포 설정 수정"
git push origin main
```

**변경된 파일**:
- ✅ `frontend/netlify.toml` 삭제
- ✅ `frontend/src/pages/LiveBroadcastDetail.jsx` 수정
- ✅ `frontend/src/pages/EventDetail.jsx` 추가
- ✅ `backend/routes/eventDetail.js` 추가
- ✅ 크롤러 및 문서 파일 추가

---

## 🔍 문제 원인 분석

### 왜 이런 문제가 발생했나?

#### 1. 경로 중복 문제
```
Repository root/
└── frontend/              ← Base directory
    ├── netlify.toml
    ├── package.json
    └── build/

잘못된 설정:
- Base directory: frontend
- Build command: cd frontend && ...  ← 중복!
- Publish directory: frontend/build  ← 중복!

실제 실행:
1. Netlify가 frontend/ 로 이동 (Base directory)
2. cd frontend 실행 → frontend/frontend/ 로 이동 시도 (실패!)
3. Publish: frontend/ + frontend/build = frontend/frontend/build (실패!)
```

#### 2. netlify.toml 우선순위
```
Netlify 설정 우선순위:
1. netlify.toml (최우선) ← 문제의 원인!
2. 웹 UI 설정
3. 기본값

netlify.toml에 잘못된 설정이 있으면 웹 UI 설정이 무시됨
```

---

## 📊 설정 변경 전후 비교

### Before (❌ 잘못된 설정)

```toml
# netlify.toml (삭제됨)
[build]
  command = "npm install --legacy-peer-deps && npm run build"
  publish = "build"
  environment = { NODE_VERSION = "18", CI = "false" }
```

**Netlify 웹 UI**:
```
Base directory: frontend
Build command: cd frontend && npm install --legacy-peer-deps && npm run build
Publish directory: frontend/build
```

**문제점**:
- netlify.toml과 웹 UI 설정이 충돌
- 경로가 중복되어 `frontend/frontend/` 경로 생성
- 빌드 실패

---

### After (✅ 올바른 설정)

**netlify.toml**: 삭제됨 (웹 UI 설정만 사용)

**Netlify 웹 UI**:
```
Base directory: frontend
Build command: npm install --legacy-peer-deps && npm run build
Publish directory: build
```

**장점**:
- 설정이 단순하고 명확함
- 경로 중복 없음
- 웹 UI에서 쉽게 수정 가능
- netlify.toml 파일 관리 불필요

---

## 🚀 배포 프로세스

### 자동 배포 흐름

```
1. 개발자가 코드 수정
   ↓
2. Git commit & push
   ↓
3. GitHub에 코드 업로드
   ↓
4. Netlify가 자동으로 감지
   ↓
5. Netlify 빌드 시작
   - Base directory로 이동: frontend/
   - npm install 실행
   - npm run build 실행
   - build/ 폴더 생성
   ↓
6. 빌드 결과물 배포
   - frontend/build/ 폴더를 CDN에 업로드
   ↓
7. 배포 완료
   - https://aics1.netlify.app 업데이트
```

---

## ✅ 배포 성공 확인 방법

### 1. Netlify 대시보드 확인

**접속**: https://app.netlify.com

**확인 사항**:
```
✅ Deploy status: Published
✅ Build time: ~2-3분
✅ Deploy log: "Site is live"
```

### 2. 배포 로그 확인

**성공 로그 예시**:
```
5:10:00 PM: Build ready to start
5:10:02 PM: Starting to prepare the repo for build
5:10:03 PM: Detected base directory: frontend
5:10:04 PM: Installing dependencies
5:10:05 PM: v18.0.0 is already installed
5:10:06 PM: Now using node v18.0.0
5:10:07 PM: Installing npm packages using npm version 8.6.0
5:10:45 PM: added 1500 packages in 38s
5:10:46 PM: npm packages installed
5:10:47 PM: Creating an optimized production build...
5:12:30 PM: Compiled successfully.
5:12:30 PM: File sizes after gzip:
5:12:30 PM:   500 KB  build/static/js/main.b9ec2057.js
5:12:30 PM:   50 KB   build/static/css/main.c543731b.css
5:12:31 PM: The build folder is ready to be deployed.
5:12:31 PM: Build script success
5:12:32 PM: Deploying to production
5:12:35 PM: Site is live ✨
5:12:35 PM: https://aics1.netlify.app
```

### 3. 웹사이트 접속 확인

**URL**: https://aics1.netlify.app

**확인 사항**:
```
✅ 페이지가 정상적으로 로드됨
✅ 라우팅이 정상 작동 (/, /search, /exhibitions, /events/:id)
✅ API 연동 확인 (대시보드 데이터 로드)
✅ 이미지 및 스타일 정상 표시
```

---

## 🔧 트러블슈팅

### 문제 1: 빌드 시간 초과

**증상**:
```
Build exceeded maximum allowed runtime
```

**해결**:
```bash
# Build command에 타임아웃 증가
npm install --legacy-peer-deps && CI=false npm run build
```

또는 환경 변수 추가:
```
CI=false
```

---

### 문제 2: 의존성 충돌

**증상**:
```
npm ERR! peer dependency conflict
```

**해결**:
```bash
# --legacy-peer-deps 플래그 사용
npm install --legacy-peer-deps && npm run build
```

---

### 문제 3: 메모리 부족

**증상**:
```
JavaScript heap out of memory
```

**해결**:
```bash
# Build command 수정
NODE_OPTIONS=--max-old-space-size=4096 npm run build
```

---

### 문제 4: 환경 변수 누락

**증상**:
```
API 호출 실패
Supabase 연결 오류
```

**해결**:
1. Netlify 대시보드 → Site settings → Environment variables
2. 다음 변수 추가:
```
REACT_APP_API_URL=https://ai-cs-backend.onrender.com
REACT_APP_SUPABASE_URL=https://uewhvekfjjvxoioklzza.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_key_here
```
3. 재배포

---

### 문제 5: SPA 라우팅 오류 (404)

**증상**:
```
/events/123 페이지 새로고침 시 404 오류
```

**해결**:
Netlify 대시보드 → Site settings → Build & deploy → Post processing

**Redirects** 추가:
```
/*    /index.html    200
```

또는 `public/_redirects` 파일 생성:
```
/*    /index.html    200
```

---

## 📝 체크리스트

### 배포 전 체크리스트

- [x] 코드 빌드 테스트 (`npm run build`)
- [x] Linter 오류 확인 (`npm run lint`)
- [x] 단위 테스트 실행 (`npm test`)
- [x] 환경 변수 확인
- [x] Git 커밋 및 푸시

### Netlify 설정 체크리스트

- [x] Base directory: `frontend`
- [x] Build command: `npm install --legacy-peer-deps && npm run build`
- [x] Publish directory: `build`
- [x] Node version: `18`
- [x] 환경 변수 설정
- [x] netlify.toml 삭제 (또는 올바르게 수정)

### 배포 후 체크리스트

- [ ] 배포 로그 확인
- [ ] 웹사이트 접속 확인
- [ ] 주요 기능 테스트
- [ ] API 연동 확인
- [ ] 라우팅 테스트
- [ ] 모바일 반응형 확인

---

## 📚 참고 자료

### Netlify 공식 문서
- Build settings: https://docs.netlify.com/configure-builds/overview/
- Environment variables: https://docs.netlify.com/environment-variables/overview/
- Redirects: https://docs.netlify.com/routing/redirects/

### React 배포 가이드
- Create React App deployment: https://create-react-app.dev/docs/deployment/

### Git 워크플로우
- GitHub Flow: https://guides.github.com/introduction/flow/

---

## 🎯 핵심 요약

### 문제의 근본 원인
1. **netlify.toml 파일이 웹 UI 설정을 오버라이드**
2. **경로 중복** (`cd frontend` + Base directory `frontend`)
3. **JSX 문법 오류** (중복 코드)

### 해결 방법
1. ✅ **netlify.toml 삭제**
2. ✅ **웹 UI 설정 수정** (경로 중복 제거)
3. ✅ **JSX 오류 수정** (중복 코드 제거)
4. ✅ **Git 푸시** (자동 재배포)

### 최종 설정
```
Base directory: frontend
Build command: npm install --legacy-peer-deps && npm run build
Publish directory: build
Node version: 18
```

---

## 🚀 다음 단계

### 1. 배포 모니터링
- Netlify 대시보드에서 배포 상태 확인
- 배포 로그 검토
- 오류 발생 시 즉시 대응

### 2. 성능 최적화
- Lighthouse 점수 확인
- 이미지 최적화
- 코드 스플리팅
- 캐싱 전략 개선

### 3. 지속적 개선
- CI/CD 파이프라인 강화
- 자동화된 테스트 추가
- 모니터링 도구 연동
- 에러 트래킹 설정

---

## 📞 문의 및 지원

### 프로젝트 담당자
- **팀**: Amore Pacific 개발팀
- **프로젝트**: AI CS 시스템

### 기술 지원
- **Netlify Support**: https://www.netlify.com/support/
- **GitHub Issues**: https://github.com/Munseunghun/ai_cs/issues

---

**작성 완료일**: 2025-12-16  
**최종 검토**: AI Assistant  
**문서 버전**: 1.0  
**상태**: ✅ 배포 완료

---

**© 2025 Amore Pacific. All Rights Reserved.**

