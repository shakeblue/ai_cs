---
phase: testing
title: Testing Strategy & Test Cases
description: Define testing approach, write test cases, and track coverage
feature: scheduled-crawler
---

# Testing Strategy & Test Cases

## Testing Approach
**How will we test this feature?**

**Testing Levels:**
- **Unit Tests**: Test individual functions/methods in isolation
- **Integration Tests**: Test component interactions (API + DB, Crawler + LLM)
- **End-to-End Tests**: Test complete workflows (create brand → schedule → crawl → view results)

**Testing Frameworks:**
- Python: pytest
- API Testing: pytest + requests or httpx
- Database: Test database with fixtures
- Mocking: unittest.mock or pytest-mock for external services

**Test Data Strategy:**
- Use fixtures for test platforms and brands
- Mock external services (Naver Shopping Live, LLM)
- Use in-memory database or test database for integration tests
- Clean up test data after each test

## Unit Test Cases
**What unit tests do we need?**

### Platform Service Tests
- `test_create_platform_success()` - Valid platform creation
- `test_create_platform_invalid_url_pattern()` - URL pattern validation
- `test_update_platform_schedule()` - Schedule update
- `test_delete_platform_with_brands()` - Cascade delete or prevent deletion
- `test_list_platforms_filter_by_status()` - Filter active/inactive

### Brand Service Tests
- `test_create_brand_success()` - Valid brand creation
- `test_create_brand_invalid_platform()` - Foreign key validation
- `test_update_brand_search_text()` - Search text update
- `test_brand_schedule_inheritance()` - Inherits platform schedule if not set
- `test_brand_schedule_override()` - Overrides platform schedule

### URL Construction Tests
- `test_build_search_url_valid()` - Correct URL construction
- `test_build_search_url_encoding()` - Proper URL encoding of search text
- `test_build_search_url_invalid_pattern()` - Error handling for invalid pattern

### Time Range Filter Tests
- `test_filter_events_past_7_days()` - Include events from past 7 days
- `test_filter_events_future_14_days()` - Include events up to 14 days ahead
- `test_filter_events_outside_range()` - Exclude events outside range
- `test_configurable_time_ranges()` - Use config values instead of hardcoded

### Duplicate Detection Tests
- `test_duplicate_event_update()` - Update existing event with same external_id
- `test_duplicate_event_last_write_wins()` - Latest data overwrites previous
- `test_new_event_creation()` - Create new event if external_id doesn't exist

### Crawler Orchestrator Tests
- `test_orchestrator_successful_crawl()` - End-to-end successful crawl
- `test_orchestrator_crawler_script_failure()` - Handle script errors
- `test_orchestrator_llm_extraction_failure()` - Handle LLM errors
- `test_orchestrator_logging()` - Execution log created correctly

### Scheduler Tests
- `test_register_job_for_brand()` - Job created with correct schedule
- `test_update_job_schedule()` - Job updated when schedule changes
- `test_remove_job_for_deleted_brand()` - Job removed when brand deleted
- `test_job_execution_calls_orchestrator()` - Job triggers orchestrator correctly

**Expected Code Coverage Target: 85%+**

## Integration Test Cases
**How do components work together?**

### API Integration Tests
- `test_api_create_platform_persists_to_db()` - POST /api/platforms saves to DB
- `test_api_list_platforms_returns_all()` - GET /api/platforms returns all records
- `test_api_update_brand_schedule_updates_job()` - PUT /api/brands/{id} updates scheduler
- `test_api_delete_brand_removes_job()` - DELETE /api/brands/{id} removes scheduled job

### Crawler Integration Tests
- `test_crawl_and_store_events()` - Full crawl → extraction → storage flow
- `test_crawl_duplicate_events()` - Crawling same brand twice updates events
- `test_crawl_with_time_filters()` - Only events in time range are stored
- `test_crawl_logs_execution()` - CrawlerExecution record created and updated

### Scheduler Integration Tests
- `test_scheduled_job_executes_crawl()` - Scheduled job triggers crawl
- `test_manual_trigger_executes_immediately()` - POST /api/crawler/trigger runs crawl
- `test_schedule_update_reflected_in_jobs()` - Changing schedule updates job timing

### Database Integration Tests
- `test_cascade_delete_platform_brands()` - Deleting platform handles related brands
- `test_query_performance_with_many_events()` - Queries remain fast with 1000+ events
- `test_concurrent_crawls_no_conflicts()` - Multiple concurrent crawls don't cause race conditions

## Manual Testing Checklist
**What should be tested manually?**

### Admin UI Workflows
- [ ] Create a new platform with valid data
- [ ] Try to create platform with invalid URL pattern (should show error)
- [ ] Update platform schedule and verify job updates
- [ ] Delete platform and verify brands are handled correctly
- [ ] Create a new brand linked to a platform
- [ ] Update brand search text and verify it's saved
- [ ] Set brand schedule to override platform schedule
- [ ] Delete brand and verify scheduled job is removed

### Manual Crawl Trigger
- [ ] Click "Trigger Crawl" button for a brand
- [ ] Verify loading state appears
- [ ] Verify success message and item count displayed
- [ ] Check execution log shows the manual trigger
- [ ] Trigger multiple crawls in quick succession (test concurrency)

### Scheduled Crawl
- [ ] Set a brand schedule to run in 2 minutes
- [ ] Wait and verify crawl executes automatically
- [ ] Check execution log shows scheduled trigger
- [ ] Verify events are stored in database
- [ ] Update schedule and verify next run time changes

### Execution History
- [ ] View execution history page
- [ ] Filter by brand, platform, status
- [ ] View execution details (timestamp, items found, errors)
- [ ] Verify failed executions show error messages

### Configuration
- [ ] Update "past_days_range" configuration
- [ ] Update "future_days_range" configuration
- [ ] Trigger crawl and verify new time ranges are applied

### Error Scenarios
- [ ] Trigger crawl for brand with invalid search URL (should fail gracefully)
- [ ] Simulate network failure during crawl (test error handling)
- [ ] Simulate LLM service failure (test fallback behavior)
- [ ] Create overlapping schedules (test conflict resolution)

### Performance Testing
- [ ] Create 20 brands with different schedules
- [ ] Verify all jobs are registered correctly
- [ ] Verify system performance remains acceptable
- [ ] Test admin UI response time with many records

## Test Coverage
**What's our coverage status?**

*This section will be updated during testing phase*

- Current coverage percentage: __%
- Uncovered code sections: (to be documented)
- Coverage gaps to address: (to be documented)

## Known Test Gaps
**What still needs testing?**

*This section will be updated during testing phase*

- Missing test cases: (to be documented)
- Hard-to-test scenarios: (to be documented)
- Future test improvements: (to be documented)

## Test Execution Commands

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest --cov=. --cov-report=html tests/

# Run specific test file
pytest tests/test_platform_service.py

# Run specific test
pytest tests/test_platform_service.py::test_create_platform_success

# Run integration tests only
pytest -m integration tests/

# Run unit tests only
pytest -m unit tests/
```

## Test Data Setup

**Sample Platform:**
```json
{
  "name": "Naver Shopping Live",
  "url_pattern": "https://shoppinglive.naver.com/search/lives?query={query}",
  "status": "active",
  "schedule_cron": "0 */6 * * *"
}
```

**Sample Brand:**
```json
{
  "name": "Sulwhasoo",
  "search_text": "설화수",
  "platform_id": "...",
  "status": "active",
  "schedule_cron": null
}
```

**Mock LLM Response:**
```json
{
  "title": "Sulwhasoo Live Event",
  "description": "...",
  "extracted_fields": {...}
}
```
