# Naver Search Crawler - Bug Fix Summary

## Issue
Crawler Orchestrator was returning **0 broadcasts** when searching for brands.

## Root Causes

### 1. SSL Certificate Error
Chrome was blocking the page with `net::ERR_CERT_AUTHORITY_INVALID`, preventing page load.

**Fix**: Added SSL bypass options in `setup_driver()`:
```python
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
```

### 2. Outdated CSS Selectors with Hardcoded Hashes
Naver uses CSS Modules that generate hashed class names like `VideoBoxWrapper_wrap_Usbk7`.
The hash changes with each deployment, breaking hardcoded selectors.

**Fix**: Changed from exact class names to prefix matching:
```python
# Before (brittle)
".VideoBoxWrapper_wrap_Usbk7"

# After (resilient)
"[class*='VideoBoxWrapper_wrap']"
```

### 3. Wrong Element Selection
Crawler was selecting `<a>` links directly, but title/thumbnail are in sibling elements.

**Fix**: Select parent container first, then extract all data from within:
```python
# Find container
cards = driver.find_elements(By.CSS_SELECTOR, "[class*='VideoBoxWrapper_wrap']")

# Extract from container
title = card.find_element(By.CSS_SELECTOR, "[class*='VideoTitle_wrap']")
```

## Results

| Metric | Before | After |
|--------|--------|-------|
| Broadcasts found | 0 | 126+ |
| Titles extracted | ❌ "Untitled" | ✅ Actual titles |
| Thumbnails | ❌ null | ✅ CDN URLs |
| Status | ❌ null | ✅ "ongoing"/"ended" |
| Event type | ❌ null | ✅ "live"/"replay" |

## Files Modified

1. `naver_search_crawler.py` - Main fixes
   - SSL bypass (lines 60-62)
   - Resilient selectors (lines 144-154, 310-320, 336-342)
   - Container-based extraction (lines 203-209, 255-283)

2. `debug_search_page.py` - Same SSL fix for debugging

3. `requirements.txt` - Added missing dependencies

## New Tools

1. `debug_search_page.py` - Analyzes HTML structure, finds working selectors
2. `test_search_crawler.sh` - Quick test script
3. `docs/SELECTOR_STRATEGY.md` - Documentation on resilient selectors

## Testing

```bash
# Activate venv
source venv/bin/activate

# Quick test
python naver_search_crawler.py "https://shoppinglive.naver.com/search/lives?query=설화수" --json --limit 5

# Debug mode (see what selectors work)
python debug_search_page.py "https://shoppinglive.naver.com/search/lives?query=설화수"

# Full test
./test_search_crawler.sh
```

## Maintenance

When selectors break again:
1. Run `debug_search_page.py` to capture HTML
2. Inspect `debug_output/*.html` files
3. Find new stable prefixes
4. Update selector arrays in `naver_search_crawler.py`
5. Test with actual search

See `docs/SELECTOR_STRATEGY.md` for detailed guide.
