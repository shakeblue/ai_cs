---
phase: requirements
title: Requirements & Problem Understanding
description: Clarify the problem space, gather requirements, and define success criteria
feature: naver-livebridge-data-extraction
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- **Core Problem**: We need to extract comprehensive data from Naver Shopping Live "livebridge" pages (e.g., https://shoppinglive.naver.com/livebridge/1776510), which are promotional landing pages for upcoming live broadcasts
- **Who is affected**: Marketing analysts, data collectors, and business intelligence teams who need to track live broadcast promotions, special offers, and product discounts across Naver Shopping Live
- **Current situation**: Currently, there's no automated way to extract structured data from livebridge pages. Manual collection is time-consuming and error-prone, especially for image-embedded content like benefits, coupons, and special offers

## Goals & Objectives
**What do we want to achieve?**

### Phase 1 Goals (Completed)
- Extract all available data from Naver livebridge pages in a structured format
- Use LLM-based image extraction for content embedded in promotional images
- Save extracted data as JSON for verification before database storage
- Support standalone execution for single-URL processing

### Phase 2 Goals (Current)
- Design and create Supabase database schema for livebridge data
- Implement backend service to save livebridge data to Supabase
- Create API endpoints to retrieve livebridge data
- Build frontend components to display livebridge information
- Integrate livebridge data into the existing broadcast list and detail pages

### Secondary Goals
- Maintain compatibility with existing crawler infrastructure
- Reuse the proven LLM extraction pipeline from CJ crawlers
- Enable future integration with scheduled crawling and database storage
- Follow existing patterns for Supabase integration (similar to broadcasts, events)

### Non-Goals
- Batch processing multiple URLs (manual, single URL at a time for now)
- Real-time monitoring of livebridge pages
- Auto-scheduling of crawler execution

## User Stories & Use Cases
**How will users interact with the solution?**

### Phase 1 User Stories (Completed)
1. **As a data analyst**, I want to extract all promotional information from a livebridge URL so that I can analyze marketing strategies and special offers
2. **As a business intelligence team member**, I want to capture product discounts and benefits so that I can track competitive pricing
3. **As a marketing researcher**, I want to extract image-based content (benefits, coupons) using AI so that I don't have to manually transcribe promotional materials

### Phase 2 User Stories
1. **As a developer**, I want the crawler to save extracted data directly to Supabase so that data is immediately available in the database
2. **As a developer**, I want a command-line option to control JSON output so that I can debug or verify data when needed
3. **As a frontend user**, I want to see livebridge promotional data (coupons, benefits, products) on the broadcast detail page so that I can make informed purchase decisions
4. **As a developer**, I want API endpoints to retrieve livebridge data so that I can display it in the frontend

### Key Workflows

#### Phase 1 Workflows (Completed)
1. **Single URL Extraction**:
   - User provides a livebridge URL
   - Crawler fetches the page
   - Extracts basic info from embedded JSON (__NEXT_DATA__)
   - Downloads all promotional images from contentsJson
   - Uses LLM (GPT-4o-mini) to extract data from images
   - Saves complete result to JSON file for verification

2. **Data Verification**:
   - User reviews generated JSON output
   - Validates extracted data quality
   - Confirms accuracy before database import

#### Phase 2 Workflows
1. **Database Schema Creation**:
   - Design tables for livebridge data (main table + related tables for coupons, products, benefits)
   - Create foreign key relationships
   - Add appropriate indexes for query performance
   - Execute SQL schema in Supabase

2. **Crawler Direct Integration**:
   - Add Supabase client to crawler script
   - After extraction, save data directly to Supabase
   - Add command-line flag `--save-json` (optional) to also save JSON file
   - Default behavior: save to Supabase only
   - With `--save-json`: save to both Supabase and JSON file
   - Handle duplicates (upsert based on URL or broadcast_id)

3. **API Development**:
   - Create GET endpoint to fetch livebridge data by broadcast_id or URL
   - Include all related data (coupons, products, benefits)
   - Add filtering and pagination if needed
   - Follow existing API patterns (broadcastRoutes, eventRoutes)

4. **Frontend Display**:
   - Add livebridge data section to BroadcastDetail page
   - Display special coupons with detailed information
   - Show product list with images, names, discounts, prices
   - Display live benefits and benefits by amount
   - Style components to match existing design (dark theme compatible)

### Edge Cases

#### Phase 1 Edge Cases
- Livebridge pages with no images in se-main-container
- Pages with expired or deleted broadcasts
- Network failures during image download
- LLM extraction failures for low-quality images

#### Phase 2 Edge Cases
- Duplicate livebridge URLs (same URL crawled multiple times)
- Supabase connection failures during crawler execution
- Database constraint violations (missing required fields)
- Null or empty values in extracted data
- Frontend displaying livebridge data when no data exists for a broadcast

## Success Criteria
**How will we know when we're done?**

### Phase 1 Measurable Outcomes (Completed)
1. **Data Completeness**: Extract 100% of the following fields:
   - Current link (bridgeEndUrl)
   - Live date/time (expectedStartDate)
   - Broadcast title (broadcastTitle)
   - Brand name (nickname)
   - Special offers/coupons
   - Product benefits (image, name, discount rate, price)
   - LiveBenefits (from images)
   - Benefits by Purchase Amount (from images)
   - Coupons (from images)

2. **Extraction Accuracy**:
   - LLM-based image extraction achieves >85% accuracy (based on CJ crawler benchmarks)
   - Basic metadata extraction has 100% accuracy

3. **Output Quality**:
   - Generated JSON is valid and well-structured
   - All image URLs are accessible and downloaded
   - Extracted text from images is human-readable

### Phase 2 Measurable Outcomes
1. **Database Schema**:
   - All tables created with proper relationships
   - Foreign keys properly configured
   - Indexes added for query performance
   - Schema supports all extracted data fields

2. **Crawler Integration**:
   - Crawler successfully saves data to Supabase
   - `--save-json` flag works correctly
   - Duplicate handling (upsert) works properly
   - Error handling for database failures

3. **API Functionality**:
   - GET endpoint retrieves livebridge data correctly
   - All related data (coupons, products, benefits) included
   - Response format matches frontend expectations
   - Error handling for missing data

4. **Frontend Display**:
   - Livebridge data displays correctly on BroadcastDetail page
   - All data fields rendered properly
   - Dark theme styling consistent
   - Responsive design works on mobile

### Acceptance Criteria

#### Phase 1 (Completed)
- [x] Crawler successfully extracts data from sample livebridge URL
- [x] All required fields are present in JSON output
- [x] LLM extraction works for image-based content
- [x] Error handling covers network failures and missing data
- [x] Output JSON can be manually verified for correctness
- [x] Code follows existing CJ crawler patterns

#### Phase 2
- [ ] Database schema created in Supabase
- [ ] Crawler saves data directly to Supabase after extraction
- [ ] `--save-json` flag allows optional JSON output
- [ ] Duplicate livebridge URLs handled with upsert
- [ ] API endpoint returns livebridge data with all related records
- [ ] Frontend displays livebridge coupons, products, and benefits
- [ ] Error handling for missing livebridge data in frontend
- [ ] Code follows existing backend/frontend patterns

## Constraints & Assumptions
**What limitations do we need to work within?**

### Phase 1 Technical Constraints
- Must use existing LLM extraction pipeline (/crawler/cj/run_pipeline.py)
- Must follow CJ crawler patterns and code structure
- Must handle SSL certificate verification issues with Naver
- Image extraction dependent on GPT-4o-mini API availability

### Phase 2 Technical Constraints
- Must use existing Supabase connection patterns
- Must follow existing backend API patterns (broadcastRoutes, eventRoutes)
- Must follow existing frontend component patterns
- Crawler must work with Python Supabase client
- Backend must work with Node.js Supabase client

### Business Constraints
- Single URL processing only (no batch) - Phase 1 & 2
- Manual execution required - Phase 1 & 2
- JSON output optional (via `--save-json` flag) - Phase 2
- Cost considerations for LLM API usage ($0.40/1000 images for GPT-4o-mini)

### Phase 1 Assumptions
- Naver livebridge pages consistently use __NEXT_DATA__ structure
- All promotional content is embedded in contentsJson.components
- Image quality is sufficient for LLM extraction
- API endpoints are not available (verified through investigation)
- Livebridge pages follow the same structure across different broadcasts

### Phase 2 Assumptions
- Livebridge data can be linked to broadcasts via broadcast_id or URL
- Frontend users will access livebridge data through BroadcastDetail page
- Supabase environment variables are configured in crawler environment
- Database schema can accommodate all extracted data fields
- API response time is acceptable for frontend use

## Questions & Open Items
**What do we still need to clarify?**

### Phase 1 Resolved Questions
- ✅ Is there a JSON API available? **No**, all data is embedded in __NEXT_DATA__
- ✅ What LLM provider to use? **GPT-4o-mini** (following CJ crawler pattern)
- ✅ Where to store output? **JSON files** for verification first, then Supabase in Phase 2
- ✅ What extraction strategy? **Hybrid**: Direct parsing for metadata, LLM for images

### Phase 2 Resolved Questions
- ✅ Should crawler save directly to Supabase? **Yes**, with optional `--save-json` flag
- ✅ How to handle duplicates? **Upsert** based on URL or broadcast_id
- ✅ Where to display livebridge data? **BroadcastDetail page**
- ✅ What API pattern to follow? **Existing patterns** (broadcastRoutes, eventRoutes)

### Phase 2 Open Items
- Database schema design (table names, column types, relationships)
- Linking strategy between livebridge data and broadcasts table
- Frontend component structure for displaying livebridge data
- Data validation rules for required vs optional fields

## Data Fields to Extract

Based on investigation of https://shoppinglive.naver.com/livebridge/1776510:

### Direct Extraction (from __NEXT_DATA__.props.pageProps.initialRecoilState.bridgeInfo)
1. **Current Link**: `bridgeEndUrl`
2. **Live Date/Time**: `expectedStartDate`
3. **Broadcast Title**: `broadcastTitle` or `title`
4. **Brand Name**: `nickname`
5. **Broadcast ID**: `broadcastId`
6. **Profile Image**: `profileUrl`
7. **Background Images**: `backgroundImage`, `backgroundImagePc`
8. **Landing Button**: `landingBtnTitle`, `landingBtnLink`

### LLM Extraction (from contentsJson.components array - images)
9. **LiveBenefits**: Extract text/offers from benefit images
10. **Benefits by Purchase Amount**: Extract tiered benefits from images
11. **Coupons**: Extract coupon details (discount amount, conditions, expiry)
12. **Product Offers**: Extract product images, names, discount rates, prices

### HTML Parsing (if needed as fallback)
- Class prefixes mentioned:
  - BridgeInfoSection_time_* (time info)
  - BridgeInfoSection_text_* (text content)
  - BridgeSellerInfo_nickname_* (seller name)
  - BridgeCoupon_coupon_* (coupon cards)
  - ProductCard_product_* (product cards)
  - se-main-container (main content area)

## Phase 2: Data to Store and Display

Based on the optimized JSON output (livebridge_1776510_optimized.json):

### Required Data for Storage
1. **Main Information**: URL, live datetime, title, brand name
2. **Special Coupons**: Detailed coupon objects with discount values, conditions, expiry dates
3. **Products**: Product images, names, discount rates, and prices
4. **Live Benefits**: Live-specific promotional benefits
5. **Benefits by Amount**: Tiered benefits based on purchase amounts
6. **Simple Coupons**: Simple coupon descriptions

### Frontend Display Requirements
- Display all livebridge promotional data on BroadcastDetail page
- Show special coupons with full details (discount, conditions, validity)
- Present product list with images, names, discounts, prices
- List live benefits and tiered benefits
- Maintain dark theme compatibility
- Handle missing data gracefully

> **Note**: Technical implementation details (database schema, API design, component structure) are documented in the design document.
