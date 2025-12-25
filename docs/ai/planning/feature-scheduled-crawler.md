---
phase: planning
title: Project Planning & Task Breakdown
description: Break down the work into tasks, estimate effort, and identify dependencies
feature: scheduled-crawler
---

# Project Planning & Task Breakdown

## Task Breakdown
**What are the specific tasks to complete?**

### Phase 1: Database & Models (Foundation)
**1.1 Database Schema Design**
- Define tables for Platform, Brand, CrawlerExecution, Event, CrawlerConfig
- Design indexes for performance (brand_id, platform_id, external_id, start_date)
- Plan migration strategy
- **Complexity**: Medium

**1.2 Create Database Models**
- Implement ORM models for all entities
- Add validation logic
- Set up relationships (ForeignKeys, etc.)
- **Complexity**: Medium

**1.3 Create Database Migrations**
- Generate migration files
- Test migrations (up and down)
- **Complexity**: Low

### Phase 2: Backend API (Core CRUD)
**2.1 Platform API Endpoints**
- Implement GET /api/platforms (list)
- Implement POST /api/platforms (create)
- Implement GET /api/platforms/{id} (detail)
- Implement PUT /api/platforms/{id} (update)
- Implement DELETE /api/platforms/{id} (delete)
- Add validation for URL patterns and schedules
- **Complexity**: Medium

**2.2 Brand API Endpoints**
- Implement GET /api/brands (list with platform filter)
- Implement POST /api/brands (create)
- Implement GET /api/brands/{id} (detail)
- Implement PUT /api/brands/{id} (update)
- Implement DELETE /api/brands/{id} (delete)
- Add validation for search text and schedules
- **Complexity**: Medium

**2.3 Configuration API Endpoints**
- Implement GET /api/config (get all settings)
- Implement PUT /api/config/{key} (update setting)
- Add validation for config values
- **Complexity**: Low

**2.4 Crawler Execution API Endpoints**
- Implement GET /api/crawler/executions (list with filters)
- Implement GET /api/crawler/executions/{id} (detail)
- **Complexity**: Low

**2.5 Event API Endpoints (Optional)**
- Implement GET /api/events (list with filters)
- Implement GET /api/events/{id} (detail)
- **Complexity**: Low

### Phase 3: Crawler Orchestrator (Core Logic)
**3.1 Crawler Service Foundation**
- Create CrawlerOrchestrator service class
- Implement configuration loading (read brands/platforms from DB)
- Add logging infrastructure
- **Complexity**: Medium

**3.2 URL Construction Logic**
- Implement search URL builder (platform URL pattern + brand search text)
- Add URL encoding for search text
- Validate constructed URLs
- **Complexity**: Low

**3.3 Crawler Script Integration**
- Refactor existing scripts to accept parameters (search URL, time filters)
- Create wrapper to execute scripts programmatically
- Parse script output/results
- **Complexity**: Medium

**3.4 Time Range Filtering**
- Implement date range logic (past 7 days, future 14 days)
- Read configurable ranges from CrawlerConfig table
- Filter events based on start_date
- **Complexity**: Low

**3.5 LLM Extraction Integration**
- Call LLM service for each crawled event
- Handle extraction errors gracefully
- Store both raw_data and extracted_data
- **Complexity**: Medium

**3.6 Event Storage & Duplicate Handling**
- Implement event save logic
- Add duplicate detection by external_id
- Implement "last write wins" update strategy
- **Complexity**: Medium

**3.7 Execution Logging**
- Create CrawlerExecution record at start
- Update status (pending → running → success/failed)
- Log items_found, error_message, timestamps
- **Complexity**: Low

### Phase 4: Job Scheduler
**4.1 Scheduler Setup**
- Choose and install scheduler library (APScheduler or Celery)
- Configure scheduler settings
- Set up job persistence (if needed)
- **Complexity**: Medium

**4.2 Dynamic Job Registration**
- Implement logic to load active brands/platforms from DB
- Create jobs based on schedule_cron settings
- Handle schedule inheritance (brand overrides platform)
- **Complexity**: Medium

**4.3 Job Execution Handler**
- Create job function that calls CrawlerOrchestrator
- Pass brand_id and platform_id to orchestrator
- Handle job failures and retries
- **Complexity**: Medium

**4.4 Schedule Update Logic**
- Implement job add/remove when brands/platforms are created/deleted
- Update jobs when schedules change
- Handle system restart (reload jobs from DB)
- **Complexity**: High

### Phase 5: Manual Trigger
**5.1 Manual Trigger API**
- Implement POST /api/crawler/trigger endpoint
- Validate brand_id and platform_id
- Call CrawlerOrchestrator directly (bypass scheduler)
- Return execution status
- **Complexity**: Medium

**5.2 Manual Trigger UI Integration**
- Add trigger button in admin interface
- Show immediate feedback (loading state, success/error)
- **Complexity**: Low

### Phase 6: Admin Interface
**6.1 Platform Management UI**
- Create platform list view
- Create platform create/edit form (name, URL pattern, status, schedule)
- Add delete confirmation
- **Complexity**: Medium

**6.2 Brand Management UI**
- Create brand list view (with platform filter)
- Create brand create/edit form (name, search text, platform, status, schedule)
- Add delete confirmation
- **Complexity**: Medium

**6.3 Execution History UI**
- Create execution log viewer
- Add filters (brand, platform, status, date range)
- Show execution details (timestamp, items found, errors)
- **Complexity**: Medium

**6.4 Configuration UI**
- Create settings page for configurable values
- Add form to update time ranges (past_days, future_days)
- **Complexity**: Low

**6.5 Manual Trigger UI**
- Add "Trigger Crawl" button for each brand
- Show execution status and results
- **Complexity**: Low

### Phase 7: Testing
**7.1 Unit Tests**
- Test Platform/Brand CRUD operations
- Test URL construction logic
- Test time range filtering
- Test duplicate detection
- Test LLM extraction wrapper
- **Complexity**: Medium

**7.2 Integration Tests**
- Test API endpoints (all CRUD operations)
- Test scheduler job registration and execution
- Test manual trigger flow
- Test crawler orchestrator end-to-end
- **Complexity**: High

**7.3 Manual Testing**
- Test full workflow (create platform → create brand → schedule runs)
- Test manual trigger
- Test error scenarios (invalid URLs, failed crawls, LLM errors)
- Test schedule updates and job reloading
- **Complexity**: Medium

### Phase 8: Documentation & Deployment
**8.1 Code Documentation**
- Add docstrings to all services and functions
- Document API endpoints (OpenAPI/Swagger)
- **Complexity**: Low

**8.2 Deployment Setup**
- Configure environment variables
- Set up database in production
- Configure scheduler to run as daemon/service
- **Complexity**: Medium

**8.3 User Documentation**
- Create admin user guide (how to manage platforms/brands)
- Document troubleshooting steps
- **Complexity**: Low

## Dependencies
**What needs to happen first?**

### Task Dependencies
- Phase 1 (Database) must complete before Phase 2 (API) and Phase 3 (Crawler)
- Phase 2 (API) must complete before Phase 6 (Admin UI)
- Phase 3 (Crawler Orchestrator) must complete before Phase 4 (Scheduler) and Phase 5 (Manual Trigger)
- Phase 4 (Scheduler) depends on Phase 3 (Crawler)
- Phase 5 (Manual Trigger) depends on Phase 3 (Crawler)
- Phase 6 (Admin UI) depends on Phase 2 (API)
- Phase 7 (Testing) can start partially after each phase, full integration testing at the end
- Phase 8 (Deployment) is final phase

### External Dependencies
- Existing crawler scripts (`naver_broadcast_crawler.py`, `run_livebridge_crawler.py`)
- LLM extraction service must be available
- Backend framework already set up (FastAPI/Flask/Django)
- Database system available (PostgreSQL/MongoDB)
- Job scheduler library (APScheduler/Celery)

### Parallel Work Opportunities
- Phase 2 (API) and Phase 3 (Crawler) can be developed in parallel after Phase 1
- Phase 4 (Scheduler) and Phase 5 (Manual Trigger) can be developed in parallel
- Unit tests can be written alongside implementation (Test-Driven Development)

## Effort Estimation
**How complex is each task?**

| Phase | Tasks | Complexity | Risk Level |
|-------|-------|-----------|-----------|
| Phase 1: Database | 3 tasks | Medium | Low |
| Phase 2: Backend API | 5 tasks | Medium | Low |
| Phase 3: Crawler Orchestrator | 7 tasks | Medium-High | Medium |
| Phase 4: Job Scheduler | 4 tasks | High | High |
| Phase 5: Manual Trigger | 2 tasks | Low | Low |
| Phase 6: Admin Interface | 5 tasks | Medium | Low |
| Phase 7: Testing | 3 tasks | Medium-High | Medium |
| Phase 8: Documentation & Deployment | 3 tasks | Medium | Medium |

**Risk Assessment:**
- **High Risk**: Phase 4 (Scheduler) - Dynamic job management, schedule updates, system restart handling
- **Medium Risk**: Phase 3 (Crawler Orchestrator) - Integration with existing scripts, LLM extraction, error handling
- **Low Risk**: Phases 1, 2, 5, 6 - Standard CRUD operations and UI development

## Implementation Order
**In what sequence should we build this?**

### Recommended Implementation Phases

**Phase 1: Foundation (Week 1)**
1. Database schema and models
2. Basic API endpoints (Platform, Brand)
3. Simple admin UI for Platform/Brand management
- **Goal**: Be able to create and manage platforms/brands

**Phase 2: Core Crawler Logic (Week 2)**
1. Crawler Orchestrator foundation
2. Integration with existing scripts
3. LLM extraction and event storage
4. Duplicate handling
- **Goal**: Be able to manually call crawler and see events stored

**Phase 3: Manual Trigger (Week 2-3)**
1. Manual trigger API endpoint
2. Manual trigger UI
3. Execution logging
- **Goal**: Admins can manually trigger crawls and view results

**Phase 4: Automation (Week 3-4)**
1. Scheduler setup
2. Dynamic job registration
3. Schedule update logic
4. Testing schedule-based crawling
- **Goal**: Automated crawling based on schedules

**Phase 5: Polish & Testing (Week 4-5)**
1. Execution history UI
2. Configuration UI
3. Comprehensive testing
4. Bug fixes and refinements
- **Goal**: Production-ready system

**Phase 6: Deployment (Week 5)**
1. Documentation
2. Deployment setup
3. Production testing
- **Goal**: Live system in production

### Quick Wins vs Foundational Work

**Quick Wins** (deliver early value):
- Platform/Brand management UI (Phase 1)
- Manual trigger functionality (Phase 3)
- Basic execution logging (Phase 3)

**Foundational Work** (necessary but no immediate user value):
- Database schema design (Phase 1)
- Crawler script refactoring (Phase 2)
- Scheduler infrastructure (Phase 4)

### Parallel vs Sequential Tasks

**Can be done in parallel:**
- API development + Crawler Orchestrator (after database is ready)
- Unit tests + Feature development (TDD approach)
- Manual trigger + Scheduler development (both depend on Crawler Orchestrator)

**Must be sequential:**
- Database → API/Crawler
- API → Admin UI
- Crawler Orchestrator → Scheduler/Manual Trigger

## Risks & Mitigation
**What could go wrong?**

### Technical Risks

**Risk 1: Scheduler Complexity**
- **Description**: Dynamic job management with schedule updates is complex and error-prone
- **Impact**: High - core functionality may not work reliably
- **Likelihood**: Medium
- **Mitigation**:
  - Start with simple static schedule for testing
  - Use well-tested library (APScheduler/Celery)
  - Comprehensive testing of schedule update scenarios
  - Implement job state persistence for crash recovery

**Risk 2: Crawler Script Integration**
- **Description**: Existing scripts may not be easily adaptable to programmatic invocation
- **Impact**: High - delays crawler automation
- **Likelihood**: Medium
- **Mitigation**:
  - Review scripts early to understand structure
  - Refactor scripts to accept parameters if needed
  - Create wrapper layer for backward compatibility
  - Test thoroughly with sample data

**Risk 3: LLM Extraction Performance**
- **Description**: LLM extraction may be slow or fail frequently, blocking crawler
- **Impact**: Medium - slower data availability, failed executions
- **Likelihood**: Medium
- **Mitigation**:
  - Implement timeout for LLM calls
  - Store raw data first, then extract (two-phase approach)
  - Add retry logic for failed extractions
  - Consider async/background processing if too slow

**Risk 4: Duplicate Detection Edge Cases**
- **Description**: external_id may not be unique or may change between crawls
- **Impact**: Medium - duplicate events in database
- **Likelihood**: Low
- **Mitigation**:
  - Use composite key (platform_id + external_id) for uniqueness
  - Add additional deduplication logic (URL + start_date)
  - Monitor for duplicates in production

**Risk 5: Schedule Conflicts**
- **Description**: New crawl scheduled while previous crawl still running
- **Impact**: Low - resource contention, potential data conflicts
- **Likelihood**: Medium
- **Mitigation**:
  - Implement job locking mechanism
  - Skip scheduled run if previous run still in progress
  - Log skipped runs for visibility

### Integration Risks

**Risk 6: Platform Changes**
- **Description**: Naver Shopping Live may change their website structure, breaking crawler
- **Impact**: High - crawler stops working
- **Likelihood**: Medium
- **Mitigation**:
  - Implement robust error handling
  - Add alerts for repeated failures
  - Keep crawler scripts modular for easy updates
  - Monitor platform for changes

**Risk 7: Database Performance**
- **Description**: Large number of events may slow down queries
- **Impact**: Medium - slow admin UI, slow crawls
- **Likelihood**: Low (initially)
- **Mitigation**:
  - Proper indexing on key fields
  - Pagination for list views
  - Archive old events periodically
  - Monitor query performance

### Mitigation Strategies Summary
1. **Early Testing**: Test high-risk components (scheduler, crawler integration) early
2. **Incremental Development**: Build and test in phases, validate each phase before moving on
3. **Comprehensive Logging**: Log all operations for debugging and monitoring
4. **Error Handling**: Graceful degradation, don't crash on failures
5. **Monitoring**: Track execution success rates, performance metrics
6. **Documentation**: Clear documentation for troubleshooting and maintenance
