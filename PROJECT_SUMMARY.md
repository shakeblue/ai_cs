# Online Campaign & Promotion Inquiry System
## Project Summary Document

**Owner:** Amore Pacific
**Last Updated:** 2025-12-16
**Document Version:** 1.0

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Data Collection (Crawling)](#data-collection-crawling)
5. [Database Schema](#database-schema)
6. [Current Status](#current-status)
7. [Issues & Limitations](#issues--limitations)
8. [Roadmap & Recommendations](#roadmap--recommendations)
9. [Quick Start Guide](#quick-start-guide)

---

## Project Overview

### Purpose

A **live shopping broadcast data collection and management system** designed for Amore Pacific customer service operations. The system helps CS agents efficiently respond to customer inquiries about online promotions, events, and live shopping broadcasts across multiple e-commerce platforms.

### Korean Name
온라인 캠페인, 프로모션 조회 시스템

### Business Value

- **Centralized Data**: Aggregates live shopping broadcasts from 10 major e-commerce platforms
- **Real-time Updates**: Hourly scheduled crawling keeps data fresh
- **CS Efficiency**: Provides quick access to broadcast details, products, benefits, and CS scripts
- **Multi-Brand Support**: Tracks 10 Amore Pacific brands simultaneously
- **Advanced Search**: Filter and search broadcasts by multiple criteria

---

## Architecture

### Tech Stack

#### Frontend
- **Framework:** React 18.2
- **UI Library:** Material-UI (MUI) v5
- **State Management:** Zustand
- **Charts:** Recharts
- **Routing:** React Router v6
- **HTTP Client:** Axios
- **Design:** Glassmorphism dark theme

#### Backend
- **Runtime:** Node.js
- **Framework:** Express.js
- **Database:** Supabase (PostgreSQL-based)
- **Cache:** Redis (optional)
- **Auth:** JWT-based authentication
- **CORS:** Enabled for frontend integration

#### Crawler
- **Language:** Python 3.10+
- **Web Automation:** Selenium WebDriver
- **HTML Parsing:** BeautifulSoup4
- **Scheduling:** Python Schedule library
- **Database Client:** Supabase Python SDK
- **Browser:** Chrome/Chromium with ChromeDriver

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐   │
│  │  Dashboard   │ │ Search Events│ │ Broadcast Detail      │   │
│  └──────────────┘ └──────────────┘ └──────────────────────┘   │
│  ┌──────────────┐ ┌──────────────┐                            │
│  │ Admin Panel  │ │    Login     │                            │
│  └──────────────┘ └──────────────┘                            │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP/REST API
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (Node.js/Express)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Routes: /api/dashboard, /api/events, /api/admin, /auth  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Services: eventService, userService, favoriteService     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Supabase (PostgreSQL)                      │
│  Tables: live_broadcasts, channels, live_products,              │
│          live_benefits, live_cs_info, live_qa, etc.             │
└────────────────────────┬────────────────────────────────────────┘
                         ▲
                         │
┌────────────────────────┴────────────────────────────────────────┐
│                    Crawler (Python/Selenium)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Dynamic Scheduler (runs every hour)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Platform Crawlers: Naver, Kakao, 11st, Gmarket, etc.    │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Supabase Client (save_live_broadcast)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

### Frontend Features

#### 1. Dashboard (`/`)
- **Real-time Statistics:**
  - Total broadcasts count
  - Active broadcasts
  - Pending broadcasts
  - Ended broadcasts
- **Platform Statistics:** Bar chart showing distribution across 10 platforms
- **Brand Statistics:** Bar chart showing distribution across 10 brands
- **Recent Active Broadcasts:** Last 5 active broadcasts
- **Recent Pending Broadcasts:** Last 5 upcoming broadcasts
- **Auto-refresh:** Every 1 hour

#### 2. Search Events (`/search`)
- **Advanced Filtering:**
  - Platform/channel selection
  - Brand selection
  - Status filter (Active, Pending, Ended)
  - Keyword search (broadcast title, description)
  - Date range selection (start/end date)
- **Pagination:** Browse through results
- **Quick View:** Click to see detailed broadcast information

#### 3. Live Broadcast Detail (`/events/:event_id`)
- **Meta Information:**
  - Event ID, title, platform, brand
  - Status, broadcast URL
  - Created/updated timestamps
- **Schedule:**
  - Start time, end time, duration
- **Products:**
  - Product name, brand, price, discount, image
- **Benefits:**
  - Discounts, gifts, coupons, points
  - Benefit conditions and values
- **CS Information:**
  - Expected questions from customers
  - Recommended response scripts
  - Risk points and precautions
- **STT-based Content:**
  - Key mentions from broadcast
  - Q&A extracted from live chat
  - Timeline of important moments
- **Restrictions:**
  - Excluded products/channels
  - Geographic restrictions
  - Time-based restrictions
- **Duplicate Policies:**
  - Same-day duplicate restrictions
  - Cross-platform duplicate rules

#### 4. Admin Panel (`/admin`)
- **Platform Management:**
  - Add/edit/delete platforms
  - Activate/deactivate platforms for crawling
  - Configure platform-specific settings
- **Brand Management:**
  - Add/edit/delete brands
  - Manage brand list for tracking
- **Save to Backend:** Configurations saved to both localStorage and backend API

#### 5. Authentication (`/login`)
- JWT-based login system
- Secure token storage
- Protected routes

### Backend Features

#### API Endpoints

**Dashboard API:**
- `GET /api/dashboard/stats` - Overall statistics
- `GET /api/dashboard/platform-stats` - Platform-wise distribution
- `GET /api/dashboard/brand-stats` - Brand-wise distribution
- `GET /api/dashboard/recent-active` - Recent active broadcasts
- `GET /api/dashboard/recent-pending` - Recent pending broadcasts

**Events API:**
- `GET /api/events/search` - Search broadcasts with filters
  - Query params: `channel`, `brand`, `status`, `keyword`, `startDate`, `endDate`, `page`, `limit`
- `GET /api/events/:event_id` - Get broadcast details
- `GET /api/events/:event_id/consultation-text` - Generate CS response text

**Admin API:**
- `GET /api/admin/platforms` - Retrieve platforms from config file
- `POST /api/admin/platforms` - Save platforms to config file
- `GET /api/admin/brands` - Retrieve brands from config file
- `POST /api/admin/brands` - Save brands to config file

**Auth API:**
- `POST /api/auth/login` - User authentication
- `POST /api/auth/register` - User registration (if enabled)

**Favorites API:**
- `GET /api/favorites` - Get user's favorite broadcasts
- `POST /api/favorites` - Add broadcast to favorites
- `DELETE /api/favorites/:event_id` - Remove from favorites

#### Services

- **eventService.js:** Business logic for broadcast operations
- **userService.js:** User management
- **favoriteService.js:** Favorites functionality

### Crawler Features

#### Supported Platforms (10)

1. **Naver Shopping Live** (네이버 쇼핑라이브)
2. **Kakao Shopping Live** (카카오 쇼핑라이브)
3. **11st Live** (11번가 라이브)
4. **Gmarket Live** (G마켓 라이브)
5. **Oliveyoung Live** (올리브영 라이브)
6. **Grip** (그립)
7. **Musinsa Live** (무신사 라이브)
8. **Lotteon Live** (롯데온 라이브)
9. **Amoremall Live** (아모레몰 라이브)
10. **Innisfree Mall Live** (이니스프리몰 라이브)

#### Supported Brands (10)

1. **Sulwhasoo** (설화수)
2. **Laneige** (라네즈)
3. **IOPE** (아이오페)
4. **Hera** (헤라)
5. **Estee** (에스트라)
6. **Innisfree** (이니스프리)
7. **Happybath** (해피바스)
8. **Vitalbeauty** (바이탈뷰티)
9. **Primera** (프리메라)
10. **Osulloc** (오설록)

#### Crawler Components

**Main Crawlers:**
- `improved_multi_platform_crawler.py` - Multi-platform crawler with Selenium
- `naver_shopping_crawler.py` - Naver Shopping exhibition page crawler
- `amoremall_live_crawler.py` - Amoremall live broadcast crawler
- `kakao_live_crawler.py` - Kakao live crawler
- `naver_stt_crawler.py` - STT-based Naver live analysis
- `comprehensive_naver_crawler.py` - Comprehensive Naver data collection

**Schedulers:**
- `dynamic_scheduler.py` - Dynamic scheduler (reads platform config, runs hourly)
- `scheduler.py` - Basic scheduler (hourly intervals)

**Database Integration:**
- `supabase_client.py` - Supabase client with save functions
  - `save_live_broadcast(p_live_data)` - Main save function
  - `_save_products()` - Save products
  - `_save_benefits()` - Save benefits
  - `_save_key_mentions()` - Save STT key mentions
  - `_save_qa()` - Save Q&A
  - `_save_timeline()` - Save timeline
  - `_save_cs_info()` - Save CS information
  - `_save_restrictions()` - Save restrictions
  - `_save_duplicate_policy()` - Save duplicate policies

**Configuration:**
- `config/platforms.json` - Platform definitions (editable via Admin Panel)
- `config/brands.json` - Brand definitions (editable via Admin Panel)

---

## Data Collection (Crawling)

### How Crawling Works

#### Method 1: Scheduled Crawling (Primary Method) ⭐

**File:** `crawler/dynamic_scheduler.py`

**Frequency:** Every hour at :00 (e.g., 09:00, 10:00, 11:00)

**Process:**
1. Scheduler reads active platforms from `crawler/config/platforms.json`
2. For each active platform, scheduler runs the corresponding crawler
3. Crawler uses Selenium to navigate to platform website
4. Crawler extracts broadcast data (title, schedule, products, benefits, etc.)
5. Crawler saves data to Supabase using `supabase_client.py`
6. Logs written to `logs/dynamic_scheduler_YYYYMMDD.log`
7. Statistics saved to `crawler/output/dynamic_scheduler_stats.json`

**Starting the Scheduler:**
```bash
cd /home/long/ai_cs/crawler

# Run in foreground
python3 dynamic_scheduler.py

# Run in background
nohup python3 dynamic_scheduler.py > logs/scheduler_service.log 2>&1 &
```

**Stopping the Scheduler:**
```bash
# Find process
ps aux | grep dynamic_scheduler.py

# Kill process
kill <PID>
```

#### Method 2: Manual Execution

Run crawlers manually for testing or one-time collection:

```bash
cd /home/long/ai_cs/crawler

# Multi-platform crawler
python3 improved_multi_platform_crawler.py

# Specific platform crawlers
python3 naver_shopping_crawler.py
python3 amoremall_live_crawler.py
python3 kakao_live_crawler.py
```

#### Method 3: Frontend-Triggered (NOT Implemented)

**Current Status:** ❌ Not implemented

**What Exists:**
- Admin Panel allows editing platform/brand configurations
- Configurations saved to backend API (`/api/admin/platforms`)
- Backend saves to `crawler/config/platforms.json`
- Scheduler reads config in next hourly run

**What's Missing:**
- No "Crawl Now" button in frontend
- No immediate trigger to start crawling

**Future Implementation:**
- Add "Trigger Crawl" button in Admin Panel
- Create backend API endpoint `/api/admin/trigger-crawl`
- Backend executes crawler subprocess

#### Method 4: Backend-Triggered (NOT Implemented)

**Current Status:** ❌ Not implemented

**What's Missing:**
- No API endpoint to trigger on-demand crawling
- Backend does not have subprocess execution for crawlers

**Future Implementation:**
- Create `/api/admin/trigger-crawl` endpoint
- Use Node.js `child_process` to execute Python crawlers
- Return crawl status and results

### Data Flow

```
Platform Website
      │
      ▼
Selenium WebDriver (Python Crawler)
      │
      ├─ Extract HTML
      ├─ Parse data (BeautifulSoup4)
      ├─ Structure data (JSON)
      │
      ▼
supabase_client.py
      │
      ├─ save_live_broadcast()
      ├─ _save_products()
      ├─ _save_benefits()
      ├─ _save_cs_info()
      ├─ _save_key_mentions()
      ├─ _save_qa()
      └─ _save_timeline()
      │
      ▼
Supabase Database (PostgreSQL)
      │
      ▼
Backend API (Express.js)
      │
      ▼
Frontend (React)
      │
      ▼
CS Agent / End User
```

---

## Database Schema

### Supabase Tables

#### 1. `live_broadcasts` (Main Table)
Primary table storing broadcast metadata.

**Key Columns:**
- `event_id` (PK) - Unique broadcast identifier
- `title` - Broadcast title
- `channel_id` (FK) - References `channels` table
- `brand` - Brand name
- `status` - Broadcast status (Active, Pending, Ended)
- `broadcast_url` - Link to live broadcast
- `start_time` - Scheduled start time
- `end_time` - Scheduled end time
- `description` - Broadcast description
- `created_at` - Record creation timestamp
- `updated_at` - Record update timestamp

#### 2. `channels`
Platform/channel definitions.

**Key Columns:**
- `channel_id` (PK) - Unique channel identifier
- `channel_name` - Channel/platform name
- `platform` - Platform type (Naver, Kakao, etc.)
- `is_active` - Whether channel is active for crawling

#### 3. `live_products`
Products featured in broadcasts.

**Key Columns:**
- `product_id` (PK)
- `event_id` (FK) - References `live_broadcasts`
- `product_name` - Product name
- `brand` - Product brand
- `price` - Original price
- `discount_price` - Discounted price
- `discount_rate` - Discount percentage
- `product_url` - Product page URL
- `image_url` - Product image URL

#### 4. `live_benefits`
Benefits offered during broadcasts (discounts, gifts, coupons, points).

**Key Columns:**
- `benefit_id` (PK)
- `event_id` (FK)
- `benefit_type` - Type (discount, gift, coupon, point)
- `benefit_name` - Benefit description
- `benefit_value` - Numerical value
- `benefit_condition` - Conditions to receive benefit
- `quantity_limit` - Limited quantity
- `time_limit` - Time-based limitation

#### 5. `live_cs_info`
Customer service information.

**Key Columns:**
- `cs_info_id` (PK)
- `event_id` (FK)
- `expected_questions` - Common customer questions (JSON array)
- `response_scripts` - Recommended response templates (JSON array)
- `risk_points` - Potential issues to watch (JSON array)
- `precautions` - Precautions for CS agents (JSON array)

#### 6. `live_chat_messages` (STT Key Mentions)
Important mentions extracted from live chat using STT.

**Key Columns:**
- `message_id` (PK)
- `event_id` (FK)
- `timestamp` - When mention occurred
- `speaker` - Who mentioned (host, guest, etc.)
- `message_content` - Content of mention
- `message_type` - Type (product_intro, benefit_announcement, etc.)

#### 7. `live_qa`
Q&A extracted from broadcasts.

**Key Columns:**
- `qa_id` (PK)
- `event_id` (FK)
- `question` - Customer question
- `answer` - Host's answer
- `timestamp` - When Q&A occurred
- `question_category` - Category (product, shipping, benefit, etc.)

#### 8. `live_timeline`
Timeline of important broadcast moments.

**Key Columns:**
- `timeline_id` (PK)
- `event_id` (FK)
- `timestamp` - When event occurred
- `event_type` - Type of event (product_intro, benefit_drop, etc.)
- `description` - Event description
- `video_timestamp` - Timestamp in video (for replay)

#### 9. `live_restrictions`
Restrictions and exclusions.

**Key Columns:**
- `restriction_id` (PK)
- `event_id` (FK)
- `restriction_type` - Type (product, channel, region, time)
- `excluded_items` - List of excluded items (JSON array)
- `description` - Restriction description

#### 10. `live_duplicate_policy`
Duplicate benefit policies.

**Key Columns:**
- `policy_id` (PK)
- `event_id` (FK)
- `policy_type` - Type (same_day, cross_platform, etc.)
- `is_allowed` - Whether duplicates are allowed
- `description` - Policy description
- `conditions` - Conditions (JSON)

#### 11. `live_notices`
Important notices.

**Key Columns:**
- `notice_id` (PK)
- `event_id` (FK)
- `notice_type` - Type (shipping, return, etc.)
- `notice_content` - Notice content
- `priority` - Priority level

#### 12. `live_faqs`
Frequently asked questions.

**Key Columns:**
- `faq_id` (PK)
- `event_id` (FK)
- `question` - FAQ question
- `answer` - FAQ answer
- `category` - Category

---

## Current Status

### What's Working ✅

1. **Frontend:**
   - Dashboard displays real-time statistics
   - Search page with advanced filtering
   - Detailed broadcast view with all information
   - Admin panel for platform/brand management
   - Glassmorphism design implemented
   - Auto-refresh every hour

2. **Backend:**
   - All API endpoints functional
   - Supabase integration working
   - Authentication system in place
   - CORS configured for frontend

3. **Crawler Infrastructure:**
   - Dynamic scheduler runs on schedule (every hour)
   - Supabase client saves data correctly
   - Configuration files (platforms.json, brands.json) work
   - Logging system functional

4. **Database:**
   - Supabase tables created and structured
   - Relationships established
   - Data models defined

### What's Not Working ⚠️

1. **Crawler Data Collection:**
   - **Status:** Failing (see `crawler/SCHEDULER_STATUS_REPORT.md`)
   - **Issue:** Websites blocking Selenium/detecting bot
   - **Impact:** No real data being collected
   - **Workaround:** Using mock data for frontend demonstration

2. **Platform-Specific Crawlers:**
   - **Primary implementation:** Naver only (most complete)
   - **Other 9 platforms:** Generic crawler or incomplete implementation
   - **Impact:** Cannot reliably collect data from non-Naver platforms

3. **On-Demand Crawling:**
   - **Frontend trigger:** Not implemented
   - **Backend trigger:** Not implemented
   - **Impact:** Cannot test crawlers immediately or refresh data on-demand

---

## Issues & Limitations

### Critical Issues 🔴

#### 1. Anti-Bot Detection
**Problem:** E-commerce platforms detect Selenium and block crawlers

**Evidence:**
- Scheduler runs but returns empty results
- Websites returning CAPTCHA or bot detection pages
- Selenium detected by anti-bot systems

**Potential Solutions:**
- Implement advanced anti-detection techniques:
  - Rotate user agents
  - Use residential proxies
  - Implement random delays
  - Mimic human behavior (mouse movements, scrolling)
  - Use undetected-chromedriver package
- Consider API-based approaches if platforms offer APIs
- Use headless browser alternatives (Puppeteer with stealth plugin)

#### 2. Platform Structure Changes
**Problem:** Website HTML structure changes break CSS selectors

**Impact:** Crawlers fail silently or extract incorrect data

**Solutions:**
- Implement robust selector fallbacks
- Add structure validation before parsing
- Set up monitoring alerts for selector failures
- Regular selector maintenance schedule

#### 3. Limited Platform Coverage
**Problem:** Only Naver platform has comprehensive crawler implementation

**Impact:** 9 out of 10 platforms have limited or no data collection

**Solutions:**
- Develop platform-specific crawler for each platform
- Test with each platform's unique structure
- Create platform-specific parsing logic

### Medium Issues 🟡

#### 4. No Real-Time Crawl Trigger
**Problem:** Cannot trigger crawling on-demand

**Impact:**
- Testing is slow (must wait for next hour)
- Cannot refresh data immediately when needed
- Admin changes to platform config require waiting

**Solutions:**
- Add "Crawl Now" button in Admin Panel
- Create backend API endpoint `/api/admin/trigger-crawl`
- Implement crawler subprocess execution in Node.js backend

#### 5. Limited Error Handling
**Problem:** Crawlers may fail silently without proper alerts

**Impact:** Data collection failures go unnoticed

**Solutions:**
- Implement email/Slack notifications on failures
- Add crawler health dashboard
- Set up automated retry with exponential backoff

#### 6. No Crawler Monitoring
**Problem:** No visibility into crawler health and performance

**Impact:** Cannot track success rate, errors, or performance

**Solutions:**
- Build crawler monitoring dashboard
- Track metrics: success rate, last run time, error counts
- Visualize crawler performance over time

### Minor Issues 🟢

#### 7. STT Analysis Limited to Naver
**Problem:** STT-based analysis only works for Naver platform

**Impact:** Other platforms lack key mentions, Q&A, timeline data

**Solutions:**
- Expand STT crawlers to other platforms
- Develop platform-agnostic STT parser

#### 8. No Role-Based Access Control
**Problem:** All authenticated users have same permissions

**Impact:** Security risk, no admin/agent separation

**Solutions:**
- Implement RBAC (Admin, CS Agent, Viewer roles)
- Protect admin endpoints with role checks

---

## Roadmap & Recommendations

### Phase 1: Fix Critical Issues (High Priority)

#### 1.1 Fix Crawler Anti-Bot Detection
**Goal:** Get crawlers successfully collecting real data

**Tasks:**
- [ ] Research anti-detection techniques for each platform
- [ ] Implement undetected-chromedriver or Puppeteer with stealth
- [ ] Add user agent rotation
- [ ] Implement random delays and human-like behavior
- [ ] Set up proxy rotation (if needed)
- [ ] Test crawlers with each platform
- [ ] Update selectors for current website structures

**Success Criteria:**
- 80%+ success rate on Naver platform
- At least 3 other platforms working

**Estimated Effort:** 2-3 weeks

#### 1.2 Implement Platform-Specific Crawlers
**Goal:** Support all 10 platforms with dedicated crawlers

**Tasks:**
- [ ] Analyze HTML structure for each platform
- [ ] Build platform-specific parser for Kakao
- [ ] Build platform-specific parser for 11st
- [ ] Build platform-specific parser for Gmarket
- [ ] Build platform-specific parser for Oliveyoung
- [ ] Build platform-specific parser for Grip
- [ ] Build platform-specific parser for Musinsa
- [ ] Build platform-specific parser for Lotteon
- [ ] Build platform-specific parser for Amoremall
- [ ] Build platform-specific parser for Innisfree
- [ ] Test each crawler independently
- [ ] Integrate into dynamic_scheduler

**Success Criteria:**
- All 10 platforms have working crawlers
- Data quality validated for each platform

**Estimated Effort:** 4-6 weeks

### Phase 2: Enhance User Experience (Medium Priority)

#### 2.1 Add On-Demand Crawl Trigger
**Goal:** Enable immediate crawling from frontend

**Frontend Tasks:**
- [ ] Add "Crawl Now" button in Admin Panel
- [ ] Create platform selection for targeted crawling
- [ ] Show crawl progress indicator
- [ ] Display crawl results (success/failure, records added)

**Backend Tasks:**
- [ ] Create `/api/admin/trigger-crawl` endpoint
- [ ] Implement subprocess execution for Python crawlers
- [ ] Add request validation and authentication
- [ ] Return crawl status and results
- [ ] Implement rate limiting (prevent abuse)

**Success Criteria:**
- Admin can trigger crawl from UI
- Crawl completes within 5 minutes
- Results displayed to user

**Estimated Effort:** 1 week

#### 2.2 Build Crawler Monitoring Dashboard
**Goal:** Provide visibility into crawler health

**Tasks:**
- [ ] Create new frontend page `/admin/crawler-status`
- [ ] Add backend API for crawler metrics
- [ ] Track metrics in database:
  - Last run time per platform
  - Success/failure counts
  - Error messages
  - Records collected
  - Average execution time
- [ ] Display metrics with charts (Recharts)
- [ ] Add real-time status indicators
- [ ] Implement email/Slack alerts on failures

**Success Criteria:**
- Admin can see crawler health at a glance
- Alerts sent within 5 minutes of failure
- Historical metrics available for 30 days

**Estimated Effort:** 2 weeks

### Phase 3: Improve Data Quality (Medium Priority)

#### 3.1 Expand STT Analysis to All Platforms
**Goal:** Extract key mentions, Q&A, and timeline for all platforms

**Tasks:**
- [ ] Research STT capabilities on each platform
- [ ] Build STT crawler for Kakao
- [ ] Build STT crawler for 11st, Gmarket, etc.
- [ ] Implement unified STT parser
- [ ] Extract key mentions, Q&A, timeline
- [ ] Save to Supabase tables

**Success Criteria:**
- STT data available for at least 5 platforms
- Data quality matches Naver implementation

**Estimated Effort:** 3 weeks

#### 3.2 Enhance CS Information Generation
**Goal:** Automatically generate better CS scripts

**Tasks:**
- [ ] Implement AI-based script generation (GPT-4 API)
- [ ] Generate expected questions from broadcast content
- [ ] Generate response scripts based on benefits/products
- [ ] Identify risk points automatically
- [ ] Add manual editing capability in frontend

**Success Criteria:**
- CS scripts generated for 90% of broadcasts
- CS agents report improved script quality

**Estimated Effort:** 2 weeks

### Phase 4: Advanced Features (Low Priority)

#### 4.1 Role-Based Access Control
**Goal:** Separate admin and CS agent permissions

**Tasks:**
- [ ] Define roles (Admin, CS Agent, Viewer)
- [ ] Update database schema with user roles
- [ ] Implement role-based middleware in backend
- [ ] Protect admin routes
- [ ] Update frontend to show/hide features based on role

**Success Criteria:**
- Admins can access all features
- CS Agents can search/view but not configure
- Viewers can only view broadcasts

**Estimated Effort:** 1 week

#### 4.2 Data Export & Reporting
**Goal:** Enable data export for analysis

**Tasks:**
- [ ] Add Excel export for search results
- [ ] Add PDF export for broadcast details
- [ ] Create scheduled email reports (daily/weekly summaries)
- [ ] Add analytics dashboard (trends, insights)

**Success Criteria:**
- Users can export search results to Excel
- Weekly email reports sent to stakeholders

**Estimated Effort:** 1-2 weeks

#### 4.3 Real-Time Notifications
**Goal:** Alert users when new broadcasts start

**Tasks:**
- [ ] Implement WebSocket or SSE for real-time updates
- [ ] Send notifications when new broadcasts detected
- [ ] Add push notifications for high-priority events
- [ ] Allow users to set notification preferences

**Success Criteria:**
- Users notified within 5 minutes of new broadcast
- Notification preferences configurable

**Estimated Effort:** 2 weeks

#### 4.4 Analytics & Insights
**Goal:** Provide business insights from collected data

**Tasks:**
- [ ] Add analytics page with metrics:
  - Most popular platforms
  - Most popular brands
  - Best-performing broadcasts (by engagement)
  - Trending products
  - Benefit effectiveness
- [ ] Historical comparison charts
- [ ] Predictive analytics (forecast broadcast performance)

**Success Criteria:**
- Business insights available in dashboard
- Trends identified for decision-making

**Estimated Effort:** 3-4 weeks

---

## Quick Start Guide

### Prerequisites

- **Node.js:** v16+ installed
- **Python:** 3.10+ installed
- **Chrome/Chromium:** Latest version
- **ChromeDriver:** Matching Chrome version
- **Supabase Account:** Active project with credentials

### Setup Instructions

#### 1. Clone Repository
```bash
cd /home/long/ai_cs
```

#### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
REACT_APP_API_BASE_URL=http://localhost:3001
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
EOF

# Start development server
npm start
```

Frontend runs on: http://localhost:3000

#### 3. Backend Setup
```bash
cd backend

# Install dependencies
npm install

# Create .env file
cat > .env << EOF
PORT=3001
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
JWT_SECRET=your_jwt_secret
NODE_ENV=development
EOF

# Start server
npm start
```

Backend runs on: http://localhost:3001

#### 4. Crawler Setup
```bash
cd crawler

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
EOF

# Test crawler
python3 improved_multi_platform_crawler.py

# Start scheduler (background)
nohup python3 dynamic_scheduler.py > logs/scheduler_service.log 2>&1 &
```

### Configuration

#### Platform Configuration
Edit: `crawler/config/platforms.json`

```json
[
  {
    "id": "NAVER_SHOPPING",
    "name": "네이버 쇼핑라이브",
    "is_active": true,
    "crawler_module": "naver_shopping_crawler"
  }
]
```

#### Brand Configuration
Edit: `crawler/config/brands.json`

```json
[
  {
    "id": "SULWHASOO",
    "name": "설화수",
    "keywords": ["설화수", "Sulwhasoo"]
  }
]
```

### Running Services

#### Start All Services
```bash
# Use provided script
./start_services.sh
```

#### Check Service Status
```bash
# Use provided script
./status_services.sh
```

#### View Logs
```bash
# Use provided script
./view_logs.sh
```

#### Stop All Services
```bash
# Use provided script
./stop_services.sh
```

### Accessing the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:3001
- **API Documentation:** http://localhost:3001/api-docs (if Swagger implemented)

### Default Login Credentials

Check `backend/src/config/auth.js` for default credentials or create user via registration endpoint.

---

## Project Structure

```
/home/long/ai_cs/
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── pages/             # Page components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── SearchEvents.jsx
│   │   │   ├── LiveBroadcastDetail.jsx
│   │   │   ├── AdminPanel.jsx
│   │   │   └── Login.jsx
│   │   ├── components/        # Reusable components
│   │   ├── services/          # API services
│   │   ├── store/             # Zustand state management
│   │   └── App.js             # Main app component
│   ├── public/
│   ├── package.json
│   └── .env
│
├── backend/                   # Node.js backend
│   ├── src/
│   │   ├── routes/           # API routes
│   │   │   ├── eventRoutes.js
│   │   │   ├── dashboardRoutes.js
│   │   │   ├── adminRoutes.js
│   │   │   ├── authRoutes.js
│   │   │   └── favoriteRoutes.js
│   │   ├── services/         # Business logic
│   │   │   ├── eventService.js
│   │   │   ├── userService.js
│   │   │   └── favoriteService.js
│   │   ├── middleware/       # Express middleware
│   │   ├── config/           # Configuration
│   │   └── app.js            # Express app
│   ├── package.json
│   └── .env
│
├── crawler/                   # Python crawlers
│   ├── improved_multi_platform_crawler.py
│   ├── dynamic_scheduler.py
│   ├── scheduler.py
│   ├── supabase_client.py
│   ├── naver_shopping_crawler.py
│   ├── amoremall_live_crawler.py
│   ├── kakao_live_crawler.py
│   ├── naver_stt_crawler.py
│   ├── config/
│   │   ├── platforms.json    # Platform configuration
│   │   └── brands.json       # Brand configuration
│   ├── output/               # Crawler output files
│   ├── logs/                 # Crawler logs
│   ├── requirements.txt
│   └── .env
│
├── logs/                     # Application logs
├── start_services.sh         # Start all services
├── stop_services.sh          # Stop all services
├── status_services.sh        # Check service status
├── view_logs.sh              # View logs
└── PROJECT_SUMMARY.md        # This document
```

---

## Key Files Reference

### Frontend
- **Dashboard:** `/home/long/ai_cs/frontend/src/pages/Dashboard.jsx`
- **Search:** `/home/long/ai_cs/frontend/src/pages/SearchEvents.jsx`
- **Detail:** `/home/long/ai_cs/frontend/src/pages/LiveBroadcastDetail.jsx`
- **Admin:** `/home/long/ai_cs/frontend/src/pages/AdminPanel.jsx`

### Backend
- **Events API:** `/home/long/ai_cs/backend/src/routes/eventRoutes.js`
- **Dashboard API:** `/home/long/ai_cs/backend/src/routes/dashboardRoutes.js`
- **Admin API:** `/home/long/ai_cs/backend/src/routes/adminRoutes.js`

### Crawler
- **Scheduler:** `/home/long/ai_cs/crawler/dynamic_scheduler.py`
- **Multi-platform Crawler:** `/home/long/ai_cs/crawler/improved_multi_platform_crawler.py`
- **Supabase Client:** `/home/long/ai_cs/crawler/supabase_client.py`
- **Platform Config:** `/home/long/ai_cs/crawler/config/platforms.json`
- **Brand Config:** `/home/long/ai_cs/crawler/config/brands.json`

### Logs
- **Scheduler Logs:** `/home/long/ai_cs/logs/dynamic_scheduler_YYYYMMDD.log`
- **Crawler Stats:** `/home/long/ai_cs/crawler/output/dynamic_scheduler_stats.json`

---

## Support & Maintenance

### Monitoring
- Check scheduler logs daily: `/home/long/ai_cs/logs/`
- Review crawler stats: `/home/long/ai_cs/crawler/output/dynamic_scheduler_stats.json`
- Monitor Supabase dashboard for database health

### Regular Maintenance Tasks
- **Weekly:** Review crawler success rates, update selectors if needed
- **Monthly:** Update dependencies (npm, pip packages)
- **Quarterly:** Review platform structure changes, update crawlers

### Troubleshooting

**Crawler Not Collecting Data:**
1. Check if scheduler is running: `ps aux | grep dynamic_scheduler`
2. Review logs: `tail -f logs/dynamic_scheduler_*.log`
3. Test crawler manually: `python3 improved_multi_platform_crawler.py`
4. Verify Supabase credentials in `.env`
5. Check ChromeDriver version matches Chrome

**Frontend Not Loading Data:**
1. Verify backend is running: `curl http://localhost:3001/api/dashboard/stats`
2. Check browser console for errors
3. Verify CORS settings in backend
4. Check Supabase credentials

**Backend API Errors:**
1. Check backend logs
2. Verify database connection to Supabase
3. Check environment variables in `.env`

---

## Appendix

### Technologies Used

**Frontend:**
- React 18.2
- Material-UI v5
- Zustand (state management)
- Recharts (charts)
- Axios (HTTP client)
- React Router v6

**Backend:**
- Node.js
- Express.js
- Supabase JS Client
- JWT (authentication)

**Crawler:**
- Python 3.10+
- Selenium WebDriver
- BeautifulSoup4
- Supabase Python SDK
- Schedule (task scheduling)

**Database:**
- Supabase (PostgreSQL)

### External Dependencies

**Frontend:**
```json
{
  "react": "^18.2.0",
  "@mui/material": "^5.x",
  "zustand": "^4.x",
  "recharts": "^2.x",
  "axios": "^1.x",
  "react-router-dom": "^6.x"
}
```

**Backend:**
```json
{
  "express": "^4.x",
  "@supabase/supabase-js": "^2.x",
  "jsonwebtoken": "^9.x",
  "cors": "^2.x",
  "dotenv": "^16.x"
}
```

**Crawler:**
```txt
selenium
beautifulsoup4
supabase
schedule
python-dotenv
lxml
requests
```

### Environment Variables

**Frontend (.env):**
```
REACT_APP_API_BASE_URL=http://localhost:3001
REACT_APP_SUPABASE_URL=your_supabase_url
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Backend (.env):**
```
PORT=3001
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
JWT_SECRET=your_jwt_secret
NODE_ENV=development
```

**Crawler (.env):**
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
```

---

## Document History

| Version | Date       | Author | Changes                          |
|---------|------------|--------|----------------------------------|
| 1.0     | 2025-12-16 | System | Initial comprehensive summary    |

---

**End of Document**
