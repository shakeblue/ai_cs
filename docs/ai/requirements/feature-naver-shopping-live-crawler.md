# Requirements: Naver Shopping Live Crawler

**Feature Name:** Naver Shopping Live Crawler
**Script Name:** `naver_broadcast_crawler.py`
**Date:** 2025-12-23
**Status:** Draft
**Priority:** High

---

## Problem Statement

Extract promotional data from Naver Shopping Live broadcasts to gather comprehensive information about products, coupons, benefits, and engagement metrics from replay videos, live broadcasts, and short clips.

---

## Target Users

- Data analysts requiring e-commerce promotional data
- Marketing teams analyzing competitive promotions
- Researchers studying live commerce trends
- Internal systems needing structured broadcast data

---

## User Stories

### As a data analyst
- I want to crawl a single broadcast URL and get complete data
- So that I can efficiently gather promotional data without manual intervention

### As a marketing researcher
- I want to extract all product details, coupons, and benefits from broadcasts
- So that I can analyze promotional strategies used by brands

### As a system integrator
- I want structured JSON output with consistent schema
- So that I can easily import data into downstream systems

### As an operations user
- I want the crawler to run in the background without opening a browser
- So that it doesn't interfere with my other work

---

## Functional Requirements

### FR-1: URL Type Support
**Priority:** Must Have

The crawler must support three URL types:
- **Replays:** `https://view.shoppinglive.naver.com/replays/{id}`
- **Lives:** `https://view.shoppinglive.naver.com/lives/{id}?tr=lim`
- **ShortClips:** `https://view.shoppinglive.naver.com/shortclips/{id}?tr=sclim`

**Acceptance Criteria:**
- Auto-detect URL type from pattern
- Apply appropriate extraction method for each type
- Support all three types in single execution

---

### FR-2: Data Extraction Fields
**Priority:** Must Have

Extract the following 14 fields per broadcast:

| Field | Type | Required | Source | Notes |
|-------|------|----------|--------|-------|
| `broadcast_id` | Integer | Yes | URL/API/JSON | Unique identifier |
| `replay_url` | String (URL) | Yes | API/JSON | Replay page URL |
| `broadcast_url` | String (URL) | Yes | API/JSON | Live broadcast URL |
| `livebridge_url` | String (URL) | Yes | Constructed | `https://shoppinglive.naver.com/livebridge/{broadcast_id}` |
| `title` | String | Yes | API/JSON/Meta | Broadcast title with emojis |
| `brand_name` | String | Yes | API/JSON | Brand/channel name |
| `description` | String | No | API/JSON/Meta | Broadcast description |
| `broadcast_date` | DateTime | Yes | API/JSON | Start date/time (ISO 8601) |
| `broadcast_end_date` | DateTime | No | API/JSON | End date/time (ISO 8601) |
| `expected_start_date` | DateTime | No | API/JSON | Scheduled start time |
| `status` | String | No | API/JSON | Broadcast status (BLOCK, OPENED, etc.) |
| `coupons[]` | Array | Yes | API/JSON | Coupon list with details |
| `products[]` | Array | Yes | API/JSON/HTML | Product list with pricing |
| `live_benefits[]` | Array | Yes | API | Benefits/promotions |
| `live_chat[]` | Array | No | API/HTML | Chat comments (if available) |

**Livebridge URL Construction:**
- Pattern: `https://shoppinglive.naver.com/livebridge/{broadcast_id}`
- Example: `https://shoppinglive.naver.com/livebridge/1776510`
- Always generated from extracted broadcast_id

**Coupon Object Schema:**
```json
{
  "title": "String - Coupon name",
  "benefit_type": "String - Coupon type",
  "benefit_unit": "String - PERCENT or AMOUNT",
  "benefit_value": "Number - Discount value",
  "min_order_amount": "Number - Minimum purchase",
  "max_discount_amount": "Number - Maximum discount",
  "valid_start": "DateTime - Valid from",
  "valid_end": "DateTime - Valid until",
  "availability": "String - Status"
}
```

**Product Object Schema:**
```json
{
  "product_id": "String - Product key",
  "name": "String - Product name",
  "brand_name": "String - Brand",
  "discount_rate": "Number - Discount %",
  "discounted_price": "Number - Sale price",
  "original_price": "Number - Original price",
  "stock": "Number - Available stock",
  "image": "String URL - Product image",
  "link": "String URL - Product page",
  "review_count": "Number - Reviews",
  "delivery_fee": "Number - Shipping cost"
}
```

**Benefit Object Schema:**
```json
{
  "id": "Number - Benefit ID",
  "message": "String - Short message",
  "detail": "String - Full description",
  "type": "String - Benefit type (ONAIR, etc.)"
}
```

**Chat Comment Object Schema:**
```json
{
  "nickname": "String - User nickname",
  "message": "String - Comment text",
  "created_at": "DateTime - Timestamp",
  "comment_type": "String - Comment type"
}
```

**Acceptance Criteria:**
- All required fields must be extracted or logged as missing
- Arrays can be empty but must be present
- Dates in ISO 8601 format
- Product/coupon details complete as per schema
- Livebridge URL correctly constructed for all broadcasts

---

### FR-3: Single Broadcast Crawling
**Priority:** Must Have

Crawl a single broadcast from the provided URL.

**Requirements:**
- Accept single URL as command-line argument
- Extract data from that broadcast only
- No navigation to related broadcasts

**Out of Scope (Future Phase):**
- Multi-broadcast navigation via video-pager
- Automatic discovery of related broadcasts
- Batch processing of multiple URLs

**Acceptance Criteria:**
- Processes exactly one broadcast per execution
- URL provided via command-line argument
- Completes within 20 seconds for typical broadcast

---

### FR-4: JSON Output Format
**Priority:** Must Have

Save extracted data to JSON file with consistent structure.

**File Naming:**
- Pattern: `broadcast_{broadcast_id}.json`
- Location: `crawler/cj/output/` directory
- Behavior: Overwrite existing files

**JSON Structure:**
```json
{
  "metadata": {
    "crawled_at": "ISO 8601 timestamp",
    "source_url": "Original URL provided",
    "extraction_method": "API|JSON|HYBRID",
    "url_type": "replays|lives|shortclips",
    "crawler_version": "1.0.0"
  },
  "broadcast": {
    "broadcast_id": 1776510,
    "replay_url": "https://view.shoppinglive.naver.com/replays/1776510",
    "broadcast_url": "https://view.shoppinglive.naver.com/lives/1776510?tr=lim",
    "livebridge_url": "https://shoppinglive.naver.com/livebridge/1776510",
    "title": "[강세일]베스트 어워즈💙특집 라이브(~40%+트리플 혜택)",
    "brand_name": "아이오페",
    "description": "아이오페 베스트템💙+혜택",
    "broadcast_date": "2025-12-03T19:58:13.344",
    "broadcast_end_date": "2025-12-03T21:02:20",
    "expected_start_date": "2025-12-03T20:00:00",
    "status": "BLOCK",
    "coupons": [...],
    "products": [...],
    "live_benefits": [...],
    "live_chat": [...]
  }
}
```

**Acceptance Criteria:**
- Valid JSON format
- UTF-8 encoding
- Pretty-printed with 2-space indentation
- Metadata section included
- Single broadcast object (not array)
- Output directory created if doesn't exist

---

### FR-5: Error Handling
**Priority:** Must Have

Handle errors gracefully without crashing.

**Requirements:**
- Log errors to console with timestamps
- Save partial data when some fields missing
- Include error information in metadata
- Exit with appropriate status code

**Error Types:**
- Network errors (timeout, connection failure)
- Missing data fields
- Invalid JSON in embedded data
- API response errors
- HTML parsing failures

**Acceptance Criteria:**
- Errors logged with timestamp and context
- Partial data saved with `"errors"` array in metadata
- Exit code 0 for success, non-zero for failure
- Error messages user-friendly and actionable

---

### FR-6: Browser Automation
**Priority:** Must Have

Use Playwright for browser automation running in background (headless mode).

**Requirements:**
- Chromium browser in headless mode (no visible window)
- User agent: Mozilla/5.0 Windows
- Viewport: 1920x1080
- Ignore HTTPS errors
- Network interception enabled for API capture

**Acceptance Criteria:**
- Runs in headless mode by default
- No browser window opens during execution
- SSL certificate errors ignored
- Network requests/responses captured
- Page load timeout: 60 seconds
- Can optionally run with visible browser via `--headful` flag (for debugging)

---

## Non-Functional Requirements

### NFR-1: Performance
**Priority:** Should Have

- Initial page load: ≤ 15 seconds per broadcast
- Total execution time: ≤ 20 seconds per broadcast
- Memory usage: ≤ 500 MB

### NFR-2: Reliability
**Priority:** Must Have

- Success rate: ≥ 95% for valid URLs
- Data completeness: ≥ 90% of required fields extracted
- No data corruption in JSON output

### NFR-3: Maintainability
**Priority:** Should Have

- Code structure: Modular classes for each URL type
- Logging: Structured logging with levels (INFO, WARNING, ERROR)
- Configuration: Command-line arguments with defaults
- Documentation: Inline docstrings for all public methods

### NFR-4: Compatibility
**Priority:** Must Have

- Python: 3.8+
- Playwright: Latest stable version
- Platform: Linux, macOS, Windows
- Output: JSON compatible with standard parsers

---

## Out of Scope (Phase 1)

The following are explicitly **NOT** included in this phase:

### Deferred to Future Phases
- ❌ Multi-broadcast navigation via video-pager (Phase 2)
- ❌ Batch processing of multiple URLs (Phase 2)
- ❌ Database storage (Phase 3)
- ❌ Real-time live broadcast monitoring
- ❌ Comment sentiment analysis
- ❌ Historical data tracking/comparison
- ❌ Automatic retry with exponential backoff
- ❌ Distributed crawling
- ❌ GUI interface
- ❌ Cloud deployment

---

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ Extract all 14 required fields from replays URLs
- ✅ Generate valid JSON output with single broadcast
- ✅ Handle errors without crashing
- ✅ Run in headless mode (background)

### Full Success
- ✅ Support all three URL types (replays, lives, shortclips)
- ✅ 95%+ extraction success rate
- ✅ Complete product/coupon details
- ✅ Comprehensive error logging
- ✅ Clean, maintainable codebase
- ✅ Livebridge URL correctly generated

---

## User Acceptance Testing Scenarios

### Test Case 1: Single Replay Extraction
**Given:** A valid replays URL
**When:** User runs `python naver_broadcast_crawler.py URL`
**Then:**
- JSON file created in `crawler/cj/output/broadcast_{id}.json`
- All 14 fields present (or logged as missing)
- Livebridge URL matches pattern `https://shoppinglive.naver.com/livebridge/{id}`
- Products array has 15+ items
- Coupons array has 5+ items
- No browser window opened

### Test Case 2: Lives URL Extraction
**Given:** A lives URL (active or ended)
**When:** User runs `python naver_broadcast_crawler.py URL`
**Then:**
- JSON file created successfully
- Title extracted from meta tags or embedded JSON
- Brand name extracted from embedded JSON
- Products array has 2+ items
- Benefits extracted from embedded JSON or API
- Livebridge URL generated correctly
- No browser window opened

### Test Case 3: ShortClips Support
**Given:** A shortclips URL
**When:** User runs `python naver_broadcast_crawler.py URL`
**Then:**
- Auto-detects as shortclip type
- Extracts from embedded JSON or API
- Products, title, brand all present
- Livebridge URL generated correctly
- Output structure matches schema
- No browser window opened

### Test Case 4: Error Handling
**Given:** Invalid URL or network error occurs
**When:** Crawler encounters error
**Then:**
- Error logged to console with details
- Partial JSON saved with error metadata
- Process exits with non-zero exit code
- Error message indicates what went wrong

### Test Case 5: Headless Mode
**Given:** Any valid URL
**When:** User runs `python naver_broadcast_crawler.py URL`
**Then:**
- No browser window appears
- Crawler completes successfully
- Output file generated
- Console shows progress logs

### Test Case 6: Debug Mode (Optional)
**Given:** Any valid URL
**When:** User runs `python naver_broadcast_crawler.py URL --headful`
**Then:**
- Browser window opens for debugging
- Crawler completes successfully
- User can see what's happening

---

## Dependencies

### External Services
- Naver Shopping Live APIs (`apis.naver.com/live_commerce_web`)
- Naver CDN for images/videos
- Network connectivity to `view.shoppinglive.naver.com`

### Python Packages
- `playwright` - Browser automation
- `asyncio` - Async/await support
- `json` - JSON parsing/writing
- `pathlib` - File path handling
- `re` - Regular expressions
- `datetime` - Timestamp handling
- `argparse` - Command-line argument parsing

### System Requirements
- Chromium browser (installed via Playwright)
- Sufficient disk space for browser and output files
- Internet connection

---

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API structure changes | High | Medium | Version embedded JSON parsing; add API response validation |
| Embedded JSON structure changes | Medium | Low | Add fallback to HTML parsing; log schema changes |
| Browser detection/blocking | Medium | Low | Use realistic user agents and viewport sizes |
| Network timeouts | Low | Medium | Add configurable timeouts; proper error handling |
| Headless detection | Medium | Low | Use standard Playwright headless; avoid obvious patterns |

---

## Future Enhancements

### Phase 2: Multi-Broadcast Support
- Video-pager navigation to crawl related broadcasts
- Batch processing of multiple URLs from file
- Configurable max broadcasts limit
- Progress tracking for multi-broadcast crawls

### Phase 3: Data Management
- Save broadcasts to database (PostgreSQL/Supabase)
- Incremental crawling (only new/updated broadcasts)
- Data deduplication by broadcast_id
- Database schema with proper indexes

### Phase 4: Frontend Display
- Load saved broadcasts from database
- Display broadcasts in web interface
- Filter/search by brand, date, products
- View broadcast details, products, coupons
- Responsive design for mobile/desktop

### Phase 5: Analytics & Automation
- Trend analysis across time
- Price history tracking
- Promotional effectiveness metrics
- Scheduled crawling (cron jobs)
- Notification system for new promotions

---

## Appendix

### Investigation Summary
Comprehensive technical investigation completed on 2025-12-23:

- **Replays URLs:** Pure API interception approach validated
- **Lives URLs:** Embedded JSON parsing optimal (fastest method)
- **ShortClips URLs:** Both embedded JSON and API available

**Key Documents:**
- `crawler/cj/INVESTIGATION_FINDINGS.md` - Detailed comparison
- `crawler/cj/DATA_SOURCE_ANALYSIS.md` - Technical deep dive

### Example URLs (for testing)
- **Replays:** `https://view.shoppinglive.naver.com/replays/1776510`
- **Lives:** `https://view.shoppinglive.naver.com/lives/1810235?tr=lim`
- **ShortClips:** `https://view.shoppinglive.naver.com/shortclips/9797637?tr=sclim`

### Related Files
- Script location: `crawler/cj/naver_broadcast_crawler.py`
- Output directory: `crawler/cj/output/`
- Investigation scripts: `crawler/cj/investigate_*.py`
- Test outputs: `crawler/cj/*/`

### Command-Line Interface
```bash
# Basic usage (headless mode)
python crawler/cj/naver_broadcast_crawler.py <URL>

# With debug mode (visible browser)
python crawler/cj/naver_broadcast_crawler.py <URL> --headful

# Examples
python crawler/cj/naver_broadcast_crawler.py https://view.shoppinglive.naver.com/replays/1776510
python crawler/cj/naver_broadcast_crawler.py https://view.shoppinglive.naver.com/lives/1810235?tr=lim
python crawler/cj/naver_broadcast_crawler.py https://view.shoppinglive.naver.com/shortclips/9797637?tr=sclim

# Future: with output directory
python crawler/cj/naver_broadcast_crawler.py <URL> --output /path/to/output

# Future: with custom timeout
python crawler/cj/naver_broadcast_crawler.py <URL> --timeout 30
```
