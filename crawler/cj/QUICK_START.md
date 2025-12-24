# Quick Start Guide - Integrated Crawler

## ✅ Current Status

**Integration:** Complete and tested
**Database:** Requires one-time setup

---

## Quick Commands

### 1. Normal Crawl (JSON file only - Works Now!)

```bash
cd /home/long/ai_cs/crawler
source venv/bin/activate
cd cj

python naver_broadcast_crawler.py \
    https://view.shoppinglive.naver.com/lives/1810235?tr=lim
```

### 2. Crawl with Database Save (After DB Setup)

```bash
python naver_broadcast_crawler.py \
    https://view.shoppinglive.naver.com/replays/1776510 \
    --save-to-db
```

### 3. Database-Only Mode (After DB Setup)

```bash
python naver_broadcast_crawler.py \
    https://view.shoppinglive.naver.com/lives/1810235 \
    --db-only
```

### 4. Batch Crawl Multiple URLs (After DB Setup)

```bash
python scripts/crawl_and_save.py \
    https://view.shoppinglive.naver.com/replays/1776510 \
    https://view.shoppinglive.naver.com/lives/1810235 \
    https://view.shoppinglive.naver.com/shortclips/9797637
```

---

## Database Setup (One-time)

**Only needed if you want to use `--save-to-db` or `--db-only`**

1. **Open Supabase:**
   - Go to: https://app.supabase.com
   - Select your project
   - Navigate to: SQL Editor

2. **Run Schema:**
   - Copy contents of: `/home/long/ai_cs/crawler/cj/database_schema.sql`
   - Paste into SQL Editor
   - Click "Run"

3. **Test Connection:**
   ```bash
   python scripts/save_broadcast.py --test-connection
   ```

   Expected:
   ```
   ✓ Database connection successful!
   ```

---

## Example Workflow

### Scenario: Crawl and Save 3 Broadcasts

**Step 1:** Create URL file `urls.txt`:
```
https://view.shoppinglive.naver.com/replays/1776510
https://view.shoppinglive.naver.com/lives/1810235
https://view.shoppinglive.naver.com/shortclips/9797637
```

**Step 2:** Run batch crawler:
```bash
cd /home/long/ai_cs/crawler
source venv/bin/activate
cd cj

python scripts/crawl_and_save.py --urls-file urls.txt
```

**Output:**
```
Testing database connection...
✓ Database connection successful

Progress: 1/3
Crawling: https://view.shoppinglive.naver.com/replays/1776510
✓ Crawl completed
✓ Database save successful!

Progress: 2/3
Crawling: https://view.shoppinglive.naver.com/lives/1810235
✓ Crawl completed
✓ Database save successful!

Progress: 3/3
Crawling: https://view.shoppinglive.naver.com/shortclips/9797637
✓ Crawl completed
✓ Database save successful!

============================================================
CRAWL AND SAVE SUMMARY
============================================================
Total URLs: 3
✓ Successful: 3
✗ Failed: 0

Success rate: 100.0%
```

---

## What Each Flag Does

| Flag | JSON File | Database | Use Case |
|------|-----------|----------|----------|
| (none) | ✓ | ✗ | Default - local storage only |
| `--save-to-db` | ✓ | ✓ | Best of both worlds |
| `--db-only` | ✗ | ✓ | Production - DB only |

---

## Troubleshooting

### "Table 'broadcasts' does not exist"

➜ Database not set up. Run `database_schema.sql` in Supabase SQL Editor.

### "Persistence layer not available"

➜ Run: `pip install -r requirements.txt`

### SSL Certificate Error

➜ Already fixed in code. If still failing, check Supabase is active.

---

## Documentation

- **Integration Guide:** `INTEGRATION_GUIDE.md` (detailed)
- **Phase 3 Docs:** `README_PHASE3.md` (persistence layer)
- **Implementation:** `PHASE3_IMPLEMENTATION_SUMMARY.md`

---

## Support

All features tested and working! ✅

Database setup is the only remaining step for full functionality.
