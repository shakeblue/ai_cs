# Naver Shopping Live Crawler - Selector Strategy

## Problem: CSS Module Hashing

Naver Shopping Live uses CSS Modules (or similar CSS-in-JS approach) that generates hashed class names. This means class names change with each deployment:

```html
<!-- Before deployment -->
<div class="VideoBoxWrapper_wrap_Usbk7">

<!-- After deployment -->
<div class="VideoBoxWrapper_wrap_aB3c9">
```

The prefix (`VideoBoxWrapper_wrap`) stays stable, but the hash suffix (`Usbk7` → `aB3c9`) changes.

## Solution: Prefix-Only Matching

Instead of using exact class names, we use CSS attribute selectors with wildcard matching:

### ❌ Bad (will break on deployment)
```python
card_selectors = [
    ".VideoBoxWrapper_wrap_Usbk7",  # Hardcoded hash
]
```

### ✅ Good (resilient to changes)
```python
card_selectors = [
    "[class*='VideoBoxWrapper_wrap']",  # Matches any hash
]
```

## Current Selectors

### Broadcast Cards
```python
[
    "[class*='VideoBoxWrapper_wrap']",      # Main container
    "[class*='BroadcastUnderCard']",        # Card variant 1
    "[class*='BroadcastCard']",             # Card variant 2
    "[class*='BroadcastSideCard']",         # Card variant 3
    "[class*='VerticalCardList_item']",     # List item
]
```

### Titles
```python
[
    "[class*='VideoTitle_wrap']",           # Main title
    "[class*='BroadcastUnderCard_title']",  # Card title variant
    "[class*='BroadcastSideCard_title']",   # Side card title
]
```

### Thumbnails
```python
[
    "[class*='CardThumbnail_image']",       # Main thumbnail
    "[class*='BroadcastAutoPlayCard_image']", # Autoplay variant
    "img[src*='pstatic.net']",              # Naver CDN (fallback)
]
```

### Status/Badges
```python
[
    ".blind",  # Contains "다시보기" (replay) or "LIVE"
    "[class*='badge']",
]
```

## Benefits

1. **Deployment-proof**: Survives Naver's CSS recompilation
2. **Multiple fallbacks**: Tries several patterns for robustness
3. **Documented**: Clear comments explain why we use prefixes
4. **Tested**: Verified to find 126+ broadcasts consistently

## Maintenance

When selectors stop working:

1. Use `debug_search_page.py` to capture current HTML
2. Inspect the saved HTML in `debug_output/`
3. Find new stable prefixes in class names
4. Add new patterns to the selector arrays
5. Keep old patterns for backward compatibility

## Example Debug Session

```bash
# Capture and analyze current page structure
source venv/bin/activate
python debug_search_page.py "https://shoppinglive.naver.com/search/lives?query=설화수"

# Check what HTML structure looks like
cat debug_output/search_page_*_after_scroll.html | grep -A 20 "href.*lives/"
```

## Testing

Always test after selector changes:

```bash
# Quick test (3 broadcasts)
python naver_search_crawler.py "https://shoppinglive.naver.com/search/lives?query=설화수" --json --limit 3

# Full test (50 broadcasts)
./test_search_crawler.sh
```

Expected output:
- ✅ Found 100+ cards
- ✅ Titles extracted (not "Untitled")
- ✅ Thumbnails extracted (URLs present)
- ✅ Status extracted ("ongoing", "ended", or "upcoming")
