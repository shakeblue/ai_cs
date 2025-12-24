# Livebridge Crawler Usage Guide

## Overview
The Livebridge Crawler extracts promotional data from Naver Shopping Live livebridge pages and saves it directly to Supabase with optional JSON output.

## Phase 2 Features
✅ Direct Supabase integration
✅ Optional JSON file output via `--save-json` flag
✅ Upsert functionality (prevents duplicates)
✅ Comprehensive error handling
✅ Support for multiple vision providers

## Prerequisites

### 1. Install Python Dependencies
```bash
cd /home/long/ai_cs/crawler
source venv/bin/activate  # Activate virtual environment
pip install supabase python-dotenv
```

### 2. Setup Environment Variables
Create or update `/home/long/ai_cs/crawler/.env`:

```bash
# Supabase credentials
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# OpenAI API (for LLM extraction)
OPENAI_API_KEY=your_openai_api_key
```

### 3. Create Database Tables
Execute the SQL schema in Supabase:
```bash
# See: /home/long/ai_cs/database/create_livebridge_tables.sql
```

## Usage

### Basic Usage (Save to Supabase only)
```bash
cd /home/long/ai_cs/crawler/cj
python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510
```

### Save to Both Supabase and JSON
```bash
python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --save-json
```

### JSON Only (Skip Supabase)
```bash
python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --save-json --no-supabase
```

### Skip LLM Extraction (Faster)
```bash
python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --no-llm
```

### Choose Vision Provider
```bash
# Use GPT-4o (more accurate but more expensive)
python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --vision-provider gpt-4o

# Use GPT-4o-mini (default, cost-effective)
python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --vision-provider gpt-4o-mini

# Use Claude Sonnet
python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --vision-provider claude-sonnet
```

### Verbose Logging
```bash
python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 -v
```

## Command-Line Options

```
positional arguments:
  url                   Livebridge URL to crawl

optional arguments:
  -h, --help            Show help message
  --save-json           Save JSON output in addition to Supabase
  --no-llm              Disable LLM image extraction
  --no-supabase         Disable Supabase storage
  --vision-provider     Vision LLM provider (gpt-4o, gpt-4o-mini, claude-sonnet)
  --output-dir DIR      Directory for JSON output (default: output)
  -v, --verbose         Enable verbose logging
```

## What Gets Extracted

### From API (Direct)
- **Special Coupons**: Detailed coupon information with discount values, conditions, validity
- **Products**: Product listings with images, names, discount rates, prices

### From Images (LLM Extraction)
- **Live Benefits**: Live-specific promotional benefits
- **Benefits by Amount**: Tiered benefits based on purchase amounts
- **Simple Coupons**: Additional coupon descriptions from images

## Output

### Supabase Tables Populated
1. `livebridge` - Main record (URL, title, brand, datetime)
2. `livebridge_coupons` - Special coupons
3. `livebridge_products` - Products
4. `livebridge_live_benefits` - Live benefits
5. `livebridge_benefits_by_amount` - Tiered benefits
6. `livebridge_simple_coupons` - Simple coupons

### JSON Output (if --save-json)
Location: `/home/long/ai_cs/crawler/cj/output/livebridge_{id}_optimized.json`

Structure:
```json
{
  "url": "https://shoppinglive.naver.com/livebridge/1776510",
  "live_datetime": "2025-12-03T20:00:00",
  "title": "...",
  "brand_name": "...",
  "special_coupons": [...],
  "products": [...],
  "live_benefits": [...],
  "benefits_by_amount": [...],
  "coupons": [...]
}
```

## Workflow

### Phase 1 (Completed): Data Extraction
1. Fetch livebridge page
2. Extract __NEXT_DATA__ JSON
3. Parse bridge info
4. Extract products from API
5. Extract coupons from API
6. Download promotional images
7. Use LLM to extract benefits from images
8. Combine and structure data

### Phase 2 (Current): Database Integration
9. **Upsert main record** to `livebridge` table
10. **Delete existing related records** (for updates)
11. **Insert special coupons** to `livebridge_coupons`
12. **Insert products** to `livebridge_products`
13. **Insert live benefits** to `livebridge_live_benefits`
14. **Insert tiered benefits** to `livebridge_benefits_by_amount`
15. **Insert simple coupons** to `livebridge_simple_coupons`
16. **(Optional) Save JSON** if `--save-json` flag specified

## Example Session

```bash
$ cd /home/long/ai_cs/crawler/cj
$ source ../venv/bin/activate
$ python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --save-json

======================================================================
Livebridge Crawler - Phase 2 (Supabase Integration)
======================================================================
URL: https://shoppinglive.naver.com/livebridge/1776510
Save JSON: True
Use LLM: True
Use Supabase: True
Vision Provider: gpt-4o-mini
======================================================================
✓ Vision extractor initialized: gpt-4o-mini
✓ Supabase client initialized
Fetching: https://shoppinglive.naver.com/livebridge/1776510
Successfully extracted __NEXT_DATA__
Found bridgeInfo for broadcast: 1776510
Extracting content from 5 images using LLM...
Processing 5 images with vision LLM...

======================================================================
CRAWL RESULT SUMMARY
======================================================================
Title: [강세일]베스트 어워즈💙특집 라이브(~40%+트리플 혜택)
Brand: 아이오페
Live Date: 2025-12-03T20:00:00
Special Coupons: 3
Products: 20
Live Benefits: 1
Benefits by Amount: 7
Simple Coupons: 7
======================================================================

Saving to Supabase...
✓ Main record saved (ID: 1)
Cleaning up existing related records...
✓ Inserted 3 special coupons
✓ Inserted 20 products
✓ Inserted 1 live benefits
✓ Inserted 7 benefits by amount
✓ Inserted 7 simple coupons
✓ Successfully saved all data to Supabase (ID: 1)
✓ Saved to Supabase with ID: 1
✓ JSON saved to: /home/long/ai_cs/crawler/cj/output/livebridge_1_optimized.json

======================================================================
CRAWL COMPLETED SUCCESSFULLY
======================================================================
```

## Troubleshooting

### "Supabase client not available"
```bash
pip install supabase
```

### "SUPABASE_URL or SUPABASE_SERVICE_KEY not found"
- Check `.env` file exists in `/home/long/ai_cs/crawler/`
- Verify environment variables are set correctly
- Make sure you're using `SUPABASE_SERVICE_KEY` not `SUPABASE_ANON_KEY`

### "Vision extractor not available"
```bash
pip install openai anthropic
```

### "Failed to insert main livebridge record"
- Verify database tables exist (run the SQL schema)
- Check Supabase service key has proper permissions
- Look for constraint violations in verbose logs

### Duplicate URL Error
The crawler uses upsert, so duplicate URLs will update existing records instead of creating duplicates. This is normal behavior.

## Next Steps (Phase 3)

After successfully crawling and storing data:

1. **Create Backend API** - `GET /api/livebridge/:id`
2. **Build Frontend Components** - Display livebridge data in BroadcastDetail page
3. **Link to Broadcasts** - Associate livebridge data with broadcast records

## Related Documentation

- Requirements: `/home/long/ai_cs/docs/ai/requirements/feature-naver-livebridge-data-extraction.md`
- Design: `/home/long/ai_cs/docs/ai/design/feature-naver-livebridge-data-extraction.md`
- Database Schema: `/home/long/ai_cs/database/create_livebridge_tables.sql`
- Schema Setup Guide: `/home/long/ai_cs/database/LIVEBRIDGE_SCHEMA_SETUP.md`
