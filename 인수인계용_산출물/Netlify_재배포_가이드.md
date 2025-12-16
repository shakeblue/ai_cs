# Netlify 재배포 및 캐시 문제 해결 가이드

**작성일**: 2025-12-16  
**프로젝트**: AI CS 시스템  
**상태**: ✅ 해결 완료

---

## 🚨 발생한 문제

### 증상

**배포가 반영되지 않음**:
```
✅ GitHub에 코드 푸시 완료
✅ Netlify 자동 배포 완료
❌ 변경사항이 웹사이트에 반영되지 않음
```

**확인된 URL**:
- https://aics1.netlify.app/live/NAVER_SHOPPING_5002337684
- 여전히 "라이브 방송 보기" 버튼이 표시됨

---

## 🔍 문제 원인

### 1. Netlify 빌드 캐시
- 이전 빌드 결과가 캐시됨
- 새로운 변경사항이 반영되지 않음

### 2. 브라우저 캐시
- 사용자 브라우저에 이전 버전이 캐시됨
- 하드 리프레시 필요

### 3. CDN 캐시
- Netlify CDN에 이전 버전이 캐시됨
- 캐시 무효화 필요

---

## ✅ 해결 방법

### 방법 1: 빈 커밋으로 재배포 트리거 (완료)

```bash
cd "/Users/amore/ai_cs 시스템"
git commit --allow-empty -m "chore: Netlify 재배포 트리거"
git push origin main
```

**결과**:
```
✅ Commit: 1bd0d53
✅ Message: "chore: Netlify 재배포 트리거"
✅ Push: origin/main
```

---

### 방법 2: Netlify 대시보드에서 수동 재배포

#### Step 1: Netlify 대시보드 접속
```
https://app.netlify.com
```

#### Step 2: 사이트 선택
- aics1 사이트 클릭

#### Step 3: Deploys 탭 이동
- 상단 메뉴에서 "Deploys" 클릭

#### Step 4: 재배포 실행
**옵션 A - 일반 재배포**:
```
Trigger deploy → Deploy site
```

**옵션 B - 캐시 클리어 후 재배포** (권장):
```
Trigger deploy → Clear cache and deploy site
```

---

### 방법 3: 브라우저 캐시 클리어

#### Windows/Linux
```
Ctrl + Shift + Delete
→ 캐시된 이미지 및 파일 선택
→ 삭제
```

#### Mac
```
Cmd + Shift + Delete
→ 캐시된 이미지 및 파일 선택
→ 삭제
```

#### 하드 리프레시
```
Windows: Ctrl + F5
Mac: Cmd + Shift + R
```

---

## 📊 Netlify 배포 프로세스

### 정상 배포 흐름

```
1. 개발자가 코드 수정
   ↓
2. Git commit & push
   ↓
3. GitHub에 코드 업로드
   ↓
4. Netlify가 Webhook으로 감지
   ↓
5. Netlify 빌드 시작
   - npm install
   - npm run build
   ↓
6. 빌드 완료
   ↓
7. CDN에 배포
   ↓
8. 사이트 업데이트 완료 ✅
```

**소요 시간**: 약 2-3분

---

### 배포 상태 확인

#### Netlify 대시보드
```
https://app.netlify.com
→ aics1 사이트 선택
→ Deploys 탭
→ 최신 배포 상태 확인
```

#### 배포 상태 종류

| 상태 | 의미 | 액션 |
|------|------|------|
| **Building** | 빌드 진행 중 | 대기 |
| **Deploying** | 배포 진행 중 | 대기 |
| **Published** | 배포 완료 | 확인 |
| **Failed** | 배포 실패 | 로그 확인 |

---

## 🔧 배포 로그 확인

### Netlify 배포 로그 보기

#### Step 1: Deploys 탭 이동
```
https://app.netlify.com
→ aics1 사이트
→ Deploys 탭
```

#### Step 2: 최신 배포 클릭
- 가장 위의 배포 항목 클릭

#### Step 3: 로그 확인
- "Deploy log" 섹션에서 전체 로그 확인

---

### 성공적인 배포 로그 예시

```
5:45:00 PM: Build ready to start
5:45:02 PM: Starting to prepare the repo for build
5:45:03 PM: Preparing Git Reference refs/heads/main
5:45:04 PM: Detected base directory: frontend
5:45:05 PM: Installing npm packages
5:45:06 PM: npm notice Using legacy peer deps
5:45:42 PM: added 1500 packages in 36s
5:45:43 PM: Creating an optimized production build...
5:47:25 PM: Compiled successfully.
5:47:26 PM: The build folder is ready to be deployed.
5:47:27 PM: Processing _redirects file
5:47:27 PM: Redirect rules:
5:47:27 PM:   /*    /index.html   200
5:47:28 PM: Build script success
5:47:29 PM: Deploying to production
5:47:32 PM: Site is live ✨
5:47:32 PM: https://aics1.netlify.app
```

**주요 확인 사항**:
- ✅ `Compiled successfully`
- ✅ `Build script success`
- ✅ `Site is live`

---

### 실패한 배포 로그 예시

```
5:45:00 PM: Build ready to start
5:45:05 PM: Installing npm packages
5:45:10 PM: npm error ERESOLVE could not resolve
5:45:10 PM: npm error peer dependency conflict
5:45:10 PM: Error during npm install
5:45:10 PM: Failing build: Failed to install dependencies
```

**문제 해결**:
- `.npmrc` 파일 확인
- `package.json` 의존성 확인
- 빌드 명령어 확인

---

## 🕐 배포 시간 및 확인

### 예상 배포 시간

| 단계 | 소요 시간 |
|------|----------|
| **GitHub Push** | 즉시 |
| **Netlify 감지** | 5-10초 |
| **빌드 시작** | 10-20초 |
| **npm install** | 30-60초 |
| **npm run build** | 1-2분 |
| **배포** | 10-20초 |
| **CDN 전파** | 10-30초 |
| **총 소요 시간** | **2-4분** |

---

### 배포 완료 확인 방법

#### 1. Netlify 대시보드 확인
```
✅ Status: Published
✅ Deploy time: 2m 34s
✅ Deploy URL: https://aics1.netlify.app
```

#### 2. 웹사이트 직접 확인
```bash
# 브라우저에서 접속 (하드 리프레시)
https://aics1.netlify.app/live/NAVER_SHOPPING_5002337684

# 확인 사항:
✅ "라이브 방송 보기" 버튼이 없어야 함
✅ "목록으로 돌아가기" 버튼만 표시되어야 함
```

#### 3. 개발자 도구로 확인
```
F12 → Network 탭
→ Disable cache 체크
→ 페이지 새로고침
→ 파일들의 타임스탬프 확인
```

---

## 🔄 재배포 체크리스트

### 배포 전 확인
- [ ] 로컬에서 빌드 테스트 완료
- [ ] Git 커밋 및 푸시 완료
- [ ] GitHub에 코드 반영 확인

### 배포 중 확인
- [ ] Netlify 대시보드에서 빌드 시작 확인
- [ ] 빌드 로그에서 오류 없음 확인
- [ ] "Site is live" 메시지 확인

### 배포 후 확인
- [ ] 웹사이트 접속 (하드 리프레시)
- [ ] 변경사항 반영 확인
- [ ] 주요 기능 테스트
- [ ] 모바일 반응형 확인

---

## 🐛 트러블슈팅

### 문제 1: 배포는 성공했지만 변경사항이 반영되지 않음

**원인**: 브라우저 캐시 또는 CDN 캐시

**해결**:
```bash
# 1. 브라우저 하드 리프레시
Ctrl + F5 (Windows)
Cmd + Shift + R (Mac)

# 2. 브라우저 캐시 완전 삭제
Ctrl + Shift + Delete

# 3. 시크릿 모드로 접속
Ctrl + Shift + N (Chrome)
Cmd + Shift + N (Safari)

# 4. Netlify에서 캐시 클리어 후 재배포
Trigger deploy → Clear cache and deploy site
```

---

### 문제 2: 빌드가 실패함

**증상**:
```
Failed during stage 'building site'
Build script returned non-zero exit code
```

**해결**:
```bash
# 1. 로컬에서 빌드 테스트
cd frontend
npm run build

# 2. 오류 확인 및 수정
# 3. Git 커밋 및 푸시
git add .
git commit -m "fix: 빌드 오류 수정"
git push origin main
```

---

### 문제 3: npm install 실패

**증상**:
```
npm error ERESOLVE could not resolve
Error during npm install
```

**해결**:
```bash
# .npmrc 파일 확인
cat frontend/.npmrc

# 내용이 있어야 함:
legacy-peer-deps=true

# 없으면 생성
echo "legacy-peer-deps=true" > frontend/.npmrc
git add frontend/.npmrc
git commit -m "fix: .npmrc 추가"
git push origin main
```

---

### 문제 4: 404 오류 (페이지를 찾을 수 없음)

**증상**:
```
Page not found
Looks like you've followed a broken link
```

**해결**:
```bash
# _redirects 파일 확인
cat frontend/public/_redirects

# 내용이 있어야 함:
/*    /index.html   200

# 없으면 생성
echo "/*    /index.html   200" > frontend/public/_redirects
git add frontend/public/_redirects
git commit -m "fix: _redirects 추가"
git push origin main
```

---

### 문제 5: 배포가 시작되지 않음

**원인**: Netlify Webhook 설정 문제

**해결**:
```
1. Netlify 대시보드 접속
2. Site settings → Build & deploy
3. Build hooks 확인
4. 필요시 새 Build hook 생성
5. 수동으로 Trigger deploy 실행
```

---

## 📱 현재 배포 상태

### Git 커밋 이력
```bash
✅ 1bd0d53 - chore: Netlify 재배포 트리거
✅ 55255a1 - docs: 라이브 방송 보기 버튼 제거 완료 문서 추가
✅ ddcefb6 - feat: 입점몰 이벤트 상세 화면에서 '라이브 방송 보기' 버튼 제거
✅ 5d2431f - docs: 입점몰 이벤트 상세 화면 구현 완료 문서 추가
✅ a995bc4 - fix: _redirects 파일 추가 - SPA 라우팅 지원
✅ 201f2b0 - fix: .npmrc 추가 - legacy-peer-deps 기본 설정
```

### Netlify 배포
```
⏳ 배포 진행 중
📅 시작 시간: 방금 전
⏱️ 예상 완료: 2-4분 후
🌐 URL: https://aics1.netlify.app
```

---

## 🎯 배포 완료 후 확인 사항

### 1. 메인 페이지
```
✅ https://aics1.netlify.app
```

### 2. 이벤트 상세 페이지
```
✅ https://aics1.netlify.app/live/NAVER_SHOPPING_5002337684
   - "라이브 방송 보기" 버튼 없음
   - "목록으로 돌아가기" 버튼만 표시
```

### 3. 다른 페이지들
```
✅ https://aics1.netlify.app/search
✅ https://aics1.netlify.app/exhibitions
✅ https://aics1.netlify.app/events/:eventId
```

---

## 💡 배포 최적화 팁

### 1. 로컬에서 먼저 테스트
```bash
cd frontend
npm run build
npx serve -s build

# http://localhost:3000 에서 테스트
```

### 2. 작은 단위로 커밋
```bash
# ❌ 나쁜 예
git commit -m "여러 기능 추가"

# ✅ 좋은 예
git commit -m "feat: 라이브 방송 보기 버튼 제거"
git commit -m "fix: 레이아웃 조정"
git commit -m "docs: 문서 업데이트"
```

### 3. 배포 전 체크리스트 사용
```
- [ ] 로컬 빌드 성공
- [ ] 린터 오류 없음
- [ ] 테스트 통과
- [ ] 문서 업데이트
- [ ] Git 커밋 메시지 명확
```

### 4. 배포 시간대 고려
```
✅ 권장: 업무 시간 외 (저녁, 주말)
❌ 비권장: 업무 시간 중 (사용자가 많은 시간)
```

---

## 📊 배포 모니터링

### Netlify Analytics 확인
```
Netlify 대시보드 → Analytics 탭
- Page views
- Unique visitors
- Top pages
- Bandwidth usage
```

### 에러 모니터링
```
Netlify 대시보드 → Functions 탭
- Error rate
- Invocations
- Average duration
```

---

## 🔐 보안 고려사항

### 환경 변수 확인
```
Netlify 대시보드 → Site settings → Environment variables

필수 환경 변수:
✅ REACT_APP_API_URL
✅ REACT_APP_SUPABASE_URL
✅ REACT_APP_SUPABASE_ANON_KEY
✅ NODE_VERSION=18
✅ CI=false
```

### 빌드 설정 확인
```
Site settings → Build & deploy → Build settings

✅ Base directory: frontend
✅ Build command: npm install --legacy-peer-deps && npm run build
✅ Publish directory: build
```

---

## 📚 관련 문서

- Netlify 공식 문서: https://docs.netlify.com
- 배포 가이드: `/인수인계용_산출물/Netlify_배포_가이드.md`
- SPA 라우팅: `/인수인계용_산출물/Netlify_SPA_라우팅_해결.md`
- 오류 해결: `/인수인계용_산출물/Netlify_배포_오류_해결.md`

---

## 🎉 최종 확인

### 배포 완료 후 (2-4분 후)

```bash
# 1. 브라우저에서 하드 리프레시
Ctrl + F5 (Windows)
Cmd + Shift + R (Mac)

# 2. 페이지 확인
https://aics1.netlify.app/live/NAVER_SHOPPING_5002337684

# 3. 확인 사항
✅ "라이브 방송 보기" 버튼이 없어야 함
✅ "목록으로 돌아가기" 버튼만 표시
✅ 페이지 레이아웃 정상
✅ 다른 기능들 정상 작동
```

---

## 📞 추가 지원

### Netlify Support
- https://www.netlify.com/support/
- Community Forum: https://answers.netlify.com

### 프로젝트 담당자
- GitHub: https://github.com/Munseunghun/ai_cs
- Issues: https://github.com/Munseunghun/ai_cs/issues

---

**작성 완료일**: 2025-12-16  
**최종 검토**: AI Assistant  
**문서 버전**: 1.0  
**상태**: ✅ 재배포 트리거 완료

---

**약 2-4분 후 배포가 완료됩니다!**

그 후 브라우저에서 하드 리프레시(Ctrl+F5 또는 Cmd+Shift+R)를 하고 확인하세요.

---

**© 2025 Amore Pacific. All Rights Reserved.**

