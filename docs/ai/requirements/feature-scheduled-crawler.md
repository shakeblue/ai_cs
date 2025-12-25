---
phase: requirements
title: Requirements & Problem Understanding
description: Clarify the problem space, gather requirements, and define success criteria
feature: scheduled-crawler
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- **Core Problem**: Currently, live events and promotions from Naver Shopping Live must be crawled manually by running scripts (`naver_broadcast_crawler.py` and `run_livebridge_crawler.py`). This manual process is inefficient, time-consuming, and doesn't scale well for monitoring multiple brands across different platforms.

- **Who is affected**: Internal team members (admins) who need to monitor and collect live event data for configured brands across multiple platforms.

- **Current Situation**:
  - Manual execution of crawler scripts with specific live URLs
  - No automated scheduling mechanism
  - No centralized management of platforms and brands
  - Existing config files (`platforms.json`, `brands.json`) are not integrated with an admin interface
  - No visibility into crawler execution history or status

## Goals & Objectives
**What do we want to achieve?**

**Primary Goals:**
- Automate crawling of live events and promotions based on configured schedules
- Provide admin interface for managing platforms, brands, and crawler configurations
- Capture events that are recent (within 7 days), currently ongoing, or upcoming (within 2 weeks)
- Store crawled data in database with LLM-based extraction happening immediately
- Track crawler execution history and status

**Secondary Goals:**
- Allow flexible scheduling per platform/brand (default: every 6 hours)
- Enable manual triggering of crawls for specific brand/platform combinations
- Make time range filters configurable
- Handle duplicate events gracefully (update existing, last write wins)

**Non-Goals:**
- Public-facing user interface (internal use only)
- Real-time streaming of live events
- Multi-tenancy or user-specific configurations
- Historical data analysis or reporting (beyond basic logs)

## User Stories & Use Cases
**How will users interact with the solution?**

**User Type: Admin**

1. **As an admin**, I want to configure platforms with their URL patterns and schedules, so that the system knows where to crawl from and how often.

2. **As an admin**, I want to manage brands with their search text and associated platforms, so that I can control which brands are being monitored.

3. **As an admin**, I want to set crawling schedules per platform/brand, so that I can optimize crawler frequency based on brand importance or platform activity.

4. **As an admin**, I want to manually trigger a crawl for a specific brand/platform, so that I can immediately fetch latest data when needed.

5. **As an admin**, I want to view crawler execution history (success/failure, items found), so that I can monitor system health and troubleshoot issues.

6. **As an admin**, I want to enable/disable platforms or brands without deleting them, so that I can temporarily pause monitoring when needed.

**Key Workflows:**
- **Initial Setup**: Admin adds platforms → adds brands → configures schedules → activates monitoring
- **Ongoing Management**: Review crawler logs → adjust schedules if needed → manually trigger crawls for urgent updates
- **Maintenance**: Disable underperforming platforms → update brand search queries → monitor success rates

**Edge Cases:**
- Platform URL becomes invalid or changes structure
- Brand search returns no results
- Crawler script fails or times out
- Duplicate events detected from multiple crawls
- Schedule conflicts (multiple crawls for same brand/platform at same time)

## Success Criteria
**How will we know when we're done?**

**Measurable Outcomes:**
1. **Automation**: 100% of configured brands are crawled automatically according to their schedules without manual intervention
2. **Data Collection**: System successfully captures live events within the defined time ranges (past 7 days, current, upcoming 14 days)
3. **Admin Functionality**: Admins can perform all CRUD operations on platforms and brands through the interface
4. **Logging**: Every crawler execution is logged with timestamp, status, and count of items found
5. **Manual Trigger**: Admins can trigger a crawl and see results within expected timeframe

**Acceptance Criteria:**
- [ ] Scheduled crawler runs at configured intervals (default: 6 hours)
- [ ] Admin can create/edit/delete platforms with: name, URL pattern, status, schedule
- [ ] Admin can create/edit/delete brands with: name, search text, status, schedule
- [ ] Admin can manually trigger crawl for any brand/platform combination
- [ ] Crawler execution history is stored and viewable (status, timestamp, items count)
- [ ] Duplicate events are updated (last write wins) rather than creating duplicates
- [ ] LLM extraction happens immediately after data is crawled
- [ ] Time range filters (7 days past, 14 days future) are applied correctly
- [ ] Time range filters are configurable by admin
- [ ] Failed crawls are logged with error details

**Performance Benchmarks:**
- Crawler execution completes within 5 minutes per brand/platform
- System handles at least 20 concurrent brand/platform configurations
- Admin interface responds within 2 seconds for CRUD operations

## Constraints & Assumptions
**What limitations do we need to work within?**

**Technical Constraints:**
- Must integrate with existing crawler scripts (`naver_broadcast_crawler.py`, `run_livebridge_crawler.py`)
- Must use existing config file structure as reference (`platforms.json`, `brands.json`)
- Backend must support scheduled job execution
- Database must store crawled data and execution logs
- LLM extraction must run immediately after crawling

**Business Constraints:**
- Internal use only (no public access)
- Single admin role (no complex permission system needed initially)
- Focus on Naver Shopping Live platform initially

**Assumptions:**
- Admin users have technical understanding of crawler operations
- Network connectivity to target platforms is stable
- LLM extraction service is available and performant
- Crawler scripts can be invoked programmatically with parameters
- Search URL pattern for brands follows consistent format: `https://shoppinglive.naver.com/search/lives?query={encoded_brand_name}`

## Questions & Open Items
**What do we still need to clarify?**

**Unresolved Questions:**
1. Should there be notifications/alerts when crawlers fail repeatedly?
2. What should happen if a brand has no events in the time range - should it log as "0 found" or skip logging?
3. Should there be a maximum retry limit for failed crawls?
4. How should schedule conflicts be resolved if a previous crawl is still running when the next is scheduled?
5. Should admins be able to see crawled data in the admin interface, or only the execution logs?

**Items Requiring Stakeholder Input:**
- Exact error handling strategy for different failure scenarios
- Whether to support multiple platforms beyond Naver initially
- Priority of features (admin interface vs scheduling vs logging)

**Research Needed:**
- Best approach for job scheduling in current backend stack
- Database schema design for efficient duplicate detection
- LLM extraction performance impact on crawler throughput
