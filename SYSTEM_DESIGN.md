# 화장품 상담 시스템 설계 문서

## 1. 시스템 개요

### 1.1 목적
화장품 브랜드의 온라인 채널(직영몰, 입점몰, 라이브 쇼핑)에서 진행되는 프로모션/이벤트 정보를 통합 관리하여 상담원의 고객 응대 효율성을 향상시킨다.

### 1.2 주요 기능
- **대시보드**: 실시간 이벤트 현황, 채널별 통계, 최근 문의 트렌드
- **조회 시스템**: 채널/기간/키워드 기반 이벤트 검색, 상세 정보 확인
- **상담 지원**: 즐겨찾기, 상담용 문구 자동 생성, 채널 비교

---

## 2. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Dashboard   │  │  Search View │  │  Detail View    │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────┴────────────────────────────────────┐
│              Backend (Node.js/Express)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  API Gateway │  │ Auth Service │  │ Event Service   │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│              Database (PostgreSQL)                           │
│  - events 테이블                                             │
│  - channels 테이블                                           │
│  - favorites 테이블                                          │
│  - crawl_logs 테이블                                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│         Crawler System (Python)                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │Direct Mall   │  │Partner Mall  │  │ Live Shopping   │   │
│  │Crawler       │  │Crawler       │  │ Crawler         │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 의사코드 (Pseudocode)

### 3.1 크롤러 시스템

```
PSEUDOCODE: EventCrawler

BEGIN
    // 크롤러 초기화
    FUNCTION initialize_crawler(p_channel_config)
        _v_crawler = new Crawler(p_channel_config)
        _v_parser = new HTMLParser()
        _v_db_connection = connect_database()
        RETURN _v_crawler, _v_parser, _v_db_connection
    END FUNCTION

    // 이벤트 데이터 수집
    FUNCTION crawl_events(p_channel_name, p_target_url)
        TRY
            // 1단계: 페이지 접근
            _v_html_content = _v_crawler.fetch_page(p_target_url)
            
            // 2단계: 동적 콘텐츠 처리 (필요시)
            IF p_channel_name IN ['naver_live', 'kakao_live'] THEN
                _v_html_content = _v_crawler.fetch_dynamic_page(p_target_url)
            END IF
            
            // 3단계: 데이터 파싱
            _v_event_list = _v_parser.parse_events(_v_html_content, p_channel_name)
            
            // 4단계: 데이터 정규화
            FOR EACH _v_event IN _v_event_list DO
                _v_normalized_event = normalize_event_data(_v_event)
                
                // 5단계: 중복 체크 및 저장
                _v_existing_event = check_existing_event(_v_normalized_event.event_id)
                
                IF _v_existing_event IS NULL THEN
                    insert_event(_v_normalized_event)
                    log_activity("NEW_EVENT", _v_normalized_event.event_id)
                ELSE IF _v_existing_event != _v_normalized_event THEN
                    update_event(_v_normalized_event)
                    log_activity("UPDATE_EVENT", _v_normalized_event.event_id)
                END IF
            END FOR
            
            // 6단계: 크롤링 성공 로그
            log_crawl_success(p_channel_name, COUNT(_v_event_list))
            
        CATCH Exception AS _v_error
            // 에러 처리 및 로깅
            log_crawl_failure(p_channel_name, _v_error.message)
            send_alert_notification(p_channel_name, _v_error)
            
            // 재시도 로직
            IF retry_count < MAX_RETRY THEN
                wait(EXPONENTIAL_BACKOFF)
                crawl_events(p_channel_name, p_target_url)
            END IF
        END TRY
    END FUNCTION

    // 데이터 정규화
    FUNCTION normalize_event_data(p_raw_event)
        _v_event = new Event()
        _v_event.event_id = generate_unique_id(p_raw_event)
        _v_event.title = sanitize_text(p_raw_event.title)
        _v_event.channel = p_raw_event.channel
        _v_event.start_date = parse_date(p_raw_event.start_date)
        _v_event.end_date = parse_date(p_raw_event.end_date)
        _v_event.discount_rate = extract_discount(p_raw_event.benefit)
        _v_event.benefit_text = sanitize_text(p_raw_event.benefit)
        _v_event.url = validate_url(p_raw_event.url)
        _v_event.status = determine_status(_v_event.start_date, _v_event.end_date)
        _v_event.crawled_at = current_timestamp()
        
        RETURN _v_event
    END FUNCTION
END

```

### 3.2 백엔드 API 서비스

```
PSEUDOCODE: EventAPIService

BEGIN
    // 이벤트 검색 API
    FUNCTION search_events(p_filters)
        // 1단계: 입력 검증
        validate_search_params(p_filters)
        
        // 2단계: 쿼리 빌더 초기화
        _v_query = new QueryBuilder("events")
        
        // 3단계: 필터 적용
        IF p_filters.channel IS NOT NULL THEN
            _v_query.where("channel", "=", p_filters.channel)
        END IF
        
        IF p_filters.status IS NOT NULL THEN
            _v_query.where("status", "=", p_filters.status)
        END IF
        
        IF p_filters.keyword IS NOT NULL THEN
            _v_query.where_like("title", p_filters.keyword)
            _v_query.or_where_like("benefit_text", p_filters.keyword)
        END IF
        
        IF p_filters.start_date IS NOT NULL THEN
            _v_query.where("start_date", ">=", p_filters.start_date)
        END IF
        
        IF p_filters.end_date IS NOT NULL THEN
            _v_query.where("end_date", "<=", p_filters.end_date)
        END IF
        
        // 4단계: 정렬 및 페이징
        _v_query.order_by(p_filters.sort_by, p_filters.sort_order)
        _v_query.limit(p_filters.page_size)
        _v_query.offset(p_filters.page * p_filters.page_size)
        
        // 5단계: 쿼리 실행
        _v_results = _v_query.execute()
        _v_total_count = _v_query.count()
        
        // 6단계: 응답 생성
        RETURN {
            success: true,
            data: _v_results,
            pagination: {
                total: _v_total_count,
                page: p_filters.page,
                page_size: p_filters.page_size,
                total_pages: CEIL(_v_total_count / p_filters.page_size)
            }
        }
    END FUNCTION

    // 대시보드 데이터 조회
    FUNCTION get_dashboard_data()
        // 1단계: 진행 중인 이벤트 수
        _v_active_events = count_events_by_status("ACTIVE")
        
        // 2단계: 채널별 이벤트 분포
        _v_channel_stats = query("
            SELECT channel, COUNT(*) as count, 
                   COUNT(CASE WHEN status='ACTIVE' THEN 1 END) as active_count
            FROM events
            WHERE end_date >= CURRENT_DATE
            GROUP BY channel
        ")
        
        // 3단계: 최근 7일 신규 이벤트
        _v_recent_events = query("
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM events
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
            GROUP BY DATE(created_at)
            ORDER BY date
        ")
        
        // 4단계: 긴급 알림 (곧 종료되는 이벤트)
        _v_urgent_events = query("
            SELECT *
            FROM events
            WHERE status = 'ACTIVE' 
              AND end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '2 days'
            ORDER BY end_date
            LIMIT 10
        ")
        
        // 5단계: 인기 이벤트 (즐겨찾기 많은 순)
        _v_popular_events = query("
            SELECT e.*, COUNT(f.favorite_id) as favorite_count
            FROM events e
            LEFT JOIN favorites f ON e.event_id = f.event_id
            WHERE e.status = 'ACTIVE'
            GROUP BY e.event_id
            ORDER BY favorite_count DESC
            LIMIT 10
        ")
        
        // 6단계: 응답 구성
        RETURN {
            statistics: {
                total_active: _v_active_events,
                by_channel: _v_channel_stats,
                trend: _v_recent_events
            },
            urgent_events: _v_urgent_events,
            popular_events: _v_popular_events
        }
    END FUNCTION

    // 상담용 문구 생성
    FUNCTION generate_consultation_text(p_event_id)
        // 1단계: 이벤트 정보 조회
        _v_event = get_event_by_id(p_event_id)
        
        IF _v_event IS NULL THEN
            THROW EventNotFoundException("이벤트를 찾을 수 없습니다")
        END IF
        
        // 2단계: 문구 템플릿 생성
        _v_text = "안녕하세요, 고객님.\n\n"
        _v_text += "문의하신 [" + _v_event.title + "] 이벤트는\n"
        _v_text += _v_event.channel + "에서 진행 중입니다.\n\n"
        _v_text += "■ 이벤트 기간\n"
        _v_text += format_date(_v_event.start_date) + " ~ " + format_date(_v_event.end_date) + "\n\n"
        _v_text += "■ 혜택 내용\n"
        _v_text += _v_event.benefit_text + "\n\n"
        
        IF _v_event.conditions IS NOT NULL THEN
            _v_text += "■ 유의사항\n"
            _v_text += _v_event.conditions + "\n\n"
        END IF
        
        _v_text += "자세한 내용은 아래 링크에서 확인하실 수 있습니다.\n"
        _v_text += _v_event.url + "\n\n"
        _v_text += "감사합니다."
        
        RETURN _v_text
    END FUNCTION

    // 채널 비교 기능
    FUNCTION compare_channels(p_product_keyword)
        // 1단계: 제품 관련 이벤트 조회
        _v_events = query("
            SELECT *
            FROM events
            WHERE status = 'ACTIVE'
              AND (title LIKE '%' + p_product_keyword + '%' 
                   OR target_products LIKE '%' + p_product_keyword + '%')
            ORDER BY channel, discount_rate DESC
        ")
        
        // 2단계: 채널별 그룹화
        _v_comparison = GROUP_BY(_v_events, 'channel')
        
        // 3단계: 최적 혜택 분석
        FOR EACH _v_channel IN _v_comparison DO
            _v_channel.best_benefit = MAX(_v_channel.events, 'discount_rate')
            _v_channel.total_benefits = COUNT(_v_channel.events)
        END FOR
        
        // 4단계: 추천 채널 결정
        _v_recommended = MAX(_v_comparison, 'best_benefit.discount_rate')
        
        RETURN {
            comparison: _v_comparison,
            recommended_channel: _v_recommended.channel,
            reason: "최대 " + _v_recommended.best_benefit.discount_rate + "% 할인"
        }
    END FUNCTION
END

```

### 3.3 프론트엔드 컴포넌트

```
PSEUDOCODE: DashboardComponent

BEGIN
    // 대시보드 초기화
    FUNCTION initialize_dashboard()
        // 1단계: 상태 초기화
        _v_state = {
            statistics: NULL,
            urgent_events: [],
            popular_events: [],
            loading: TRUE,
            error: NULL
        }
        
        // 2단계: 데이터 로드
        load_dashboard_data()
        
        // 3단계: 자동 새로고침 설정 (5분 주기)
        set_interval(refresh_dashboard, 300000)
    END FUNCTION

    // 대시보드 데이터 로드
    FUNCTION load_dashboard_data()
        TRY
            _v_state.loading = TRUE
            
            // API 호출
            _v_response = await fetch_api("/api/dashboard")
            
            IF _v_response.success THEN
                _v_state.statistics = _v_response.data.statistics
                _v_state.urgent_events = _v_response.data.urgent_events
                _v_state.popular_events = _v_response.data.popular_events
                _v_state.error = NULL
            ELSE
                THROW APIError(_v_response.message)
            END IF
            
        CATCH Exception AS _v_error
            _v_state.error = _v_error.message
            show_error_notification(_v_error.message)
            
        FINALLY
            _v_state.loading = FALSE
        END TRY
    END FUNCTION

    // 렌더링
    FUNCTION render()
        IF _v_state.loading THEN
            RETURN <LoadingSpinner />
        END IF
        
        IF _v_state.error IS NOT NULL THEN
            RETURN <ErrorMessage message={_v_state.error} />
        END IF
        
        RETURN (
            <DashboardLayout>
                <StatisticsCards data={_v_state.statistics} />
                <ChannelChart data={_v_state.statistics.by_channel} />
                <TrendChart data={_v_state.statistics.trend} />
                <UrgentEventsPanel events={_v_state.urgent_events} />
                <PopularEventsPanel events={_v_state.popular_events} />
            </DashboardLayout>
        )
    END FUNCTION
END

PSEUDOCODE: SearchComponent

BEGIN
    // 검색 컴포넌트 초기화
    FUNCTION initialize_search()
        _v_state = {
            filters: {
                channel: NULL,
                status: 'ACTIVE',
                keyword: '',
                start_date: NULL,
                end_date: NULL,
                page: 0,
                page_size: 20,
                sort_by: 'start_date',
                sort_order: 'DESC'
            },
            results: [],
            total_count: 0,
            loading: FALSE,
            selected_event: NULL
        }
    END FUNCTION

    // 검색 실행
    FUNCTION search_events()
        TRY
            _v_state.loading = TRUE
            
            // 1단계: 필터 검증
            validate_filters(_v_state.filters)
            
            // 2단계: API 호출
            _v_response = await fetch_api("/api/events/search", {
                method: 'POST',
                body: JSON.stringify(_v_state.filters)
            })
            
            // 3단계: 결과 처리
            IF _v_response.success THEN
                _v_state.results = _v_response.data
                _v_state.total_count = _v_response.pagination.total
            END IF
            
        CATCH Exception AS _v_error
            show_error_notification(_v_error.message)
            
        FINALLY
            _v_state.loading = FALSE
        END TRY
    END FUNCTION

    // 필터 변경 핸들러
    FUNCTION handle_filter_change(p_filter_name, p_value)
        _v_state.filters[p_filter_name] = p_value
        _v_state.filters.page = 0  // 첫 페이지로 리셋
        search_events()
    END FUNCTION

    // 이벤트 상세보기
    FUNCTION show_event_detail(p_event_id)
        _v_event = await fetch_api("/api/events/" + p_event_id)
        _v_state.selected_event = _v_event.data
        open_modal("EventDetailModal")
    END FUNCTION

    // 즐겨찾기 추가
    FUNCTION add_to_favorites(p_event_id)
        TRY
            await fetch_api("/api/favorites", {
                method: 'POST',
                body: JSON.stringify({ event_id: p_event_id })
            })
            show_success_notification("즐겨찾기에 추가되었습니다")
            
        CATCH Exception AS _v_error
            show_error_notification("즐겨찾기 추가 실패: " + _v_error.message)
        END TRY
    END FUNCTION

    // 상담 문구 생성
    FUNCTION generate_text(p_event_id)
        TRY
            _v_response = await fetch_api("/api/consultation/generate/" + p_event_id)
            
            // 클립보드에 복사
            copy_to_clipboard(_v_response.data.text)
            show_success_notification("상담 문구가 클립보드에 복사되었습니다")
            
        CATCH Exception AS _v_error
            show_error_notification("문구 생성 실패: " + _v_error.message)
        END TRY
    END FUNCTION
END

```

---

## 4. 데이터 흐름

### 4.1 크롤링 데이터 흐름
```
채널 웹사이트 → 크롤러 → 파싱 → 정규화 → 중복체크 → DB 저장 → 로그 기록
```

### 4.2 조회 데이터 흐름
```
사용자 입력 → 프론트엔드 필터 → API 요청 → 백엔드 쿼리 → DB 조회 → 응답 → UI 렌더링
```

### 4.3 상담 지원 흐름
```
이벤트 선택 → 문구 생성 API → 템플릿 적용 → 클립보드 복사 → 상담원 활용
```

---

## 5. 보안 및 성능 고려사항

### 5.1 보안
- JWT 기반 인증
- API Rate Limiting
- SQL Injection 방지 (Prepared Statement)
- XSS 방지 (입출력 Sanitization)
- robots.txt 준수

### 5.2 성능
- 데이터베이스 인덱스 최적화
- API 응답 캐싱 (Redis)
- 페이지네이션
- 연결 풀링
- 크롤링 실패 재시도 로직

---

## 6. 모니터링 지표

- API 응답 시간 (목표: < 300ms)
- 크롤링 성공률 (목표: > 98%)
- 일일 활성 이벤트 수
- 상담원 즐겨찾기 사용 빈도
- 시스템 가용성 (목표: 99.9%)

---

## 7. 기술 스택

**Frontend**
- React 18+
- TypeScript
- Material-UI / Ant Design
- Axios
- Chart.js / Recharts

**Backend**
- Node.js + Express
- PostgreSQL
- JWT Authentication
- Redis (캐싱)

**Crawler**
- Python 3.10+
- Selenium
- BeautifulSoup4
- Requests
- Schedule

**DevOps**
- Docker
- GitHub Actions (CI/CD)
- PM2 (Process Manager)
- Nginx (Reverse Proxy)

---


