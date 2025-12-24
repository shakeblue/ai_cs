# Naver Shopping Live - Data Source Analysis

**Date:** 2025-12-23
**Question:** How does lives URL generate its HTML? Where does the data come from?

---

## Answer: Lives URLs Use Server-Side JSON Embedding

Lives URLs **embed all broadcast data as JSON** in the initial server HTML response:

```html
<!-- Initial server response (11,139 characters) -->
<script type="text/javascript">
  window.__viewerConfig.broadcast = '{"id":1810235, "title":"💘래피즈 연말&크리스마스 선물 UPTO 38%💘", "nickname":"REPIZ", "shoppingProducts":[...], ...}';
</script>

<script defer src="viewer.js"></script>
```

**Then JavaScript renders the UI:**
1. Server sends HTML with embedded JSON (11KB)
2. Browser loads `viewer.js` (JavaScript framework)
3. `viewer.js` parses `window.__viewerConfig.broadcast` JSON
4. JavaScript renders product cards, comments, etc. into DOM
5. Final rendered HTML: 170KB (15x growth!)

**This is different from API-based loading!**

---

## Comparison: All Three URL Types

### 1. Replays URLs (`/replays/{id}`)

**Data Source:** ✅ **API Responses** (fetched client-side)

**Flow:**
```
1. Server → Minimal HTML (5KB, no data)
2. Browser loads JavaScript
3. JavaScript → Fetch APIs:
   - /v1/broadcast/{id} → broadcast data, products (20+)
   - /v2/broadcast/{id}/coupons → 11 coupons
   - /v1/broadcast/{id}/broadcast-benefits → 4 benefits
   - /v1/broadcast/{id}/replays/comments → 100 comments
4. JavaScript renders UI from API data
```

**Why this approach?**
- Replays have LOTS of data (100 comments, 20+ products)
- Embedding would make initial HTML too large
- APIs allow lazy loading and pagination

---

### 2. Lives URLs (`/lives/{id}`)

**Data Source:** ⚠️ **Embedded JSON** (server-side rendered) + **Partial APIs**

**Flow:**
```
1. Server → HTML with embedded JSON (11KB):
   window.__viewerConfig.broadcast = '{
     "id": 1810235,
     "title": "💘래피즈 연말&크리스마스 선물 UPTO 38%💘",
     "nickname": "REPIZ",
     "shoppingProducts": [
       {"name": "래피즈 원더 피치...", "price": 269000, "discountRate": 22, ...},
       {"name": "래피즈 테이블형...", "price": 299000, "discountRate": 36, ...}
     ],
     "status": "BLOCK",
     "startDate": "2025-12-23T13:00:03.227",
     ...
   }'

2. Browser loads JavaScript
3. JavaScript parses embedded JSON
4. JavaScript renders UI (products, title, etc.)
5. OPTIONAL: Fetch additional APIs:
   - /v1/broadcast/{id}/broadcast-benefits → benefits
   - /v3/broadcast/{id}/extras → view/like counts
```

**Embedded Data Includes:**
- Broadcast ID, title, description
- Brand name (`nickname`)
- Products array (2-5 products typically)
- Status, dates, video info
- Brand profile URL, brand store URL

**Additional APIs (optional):**
- Benefits (not in embedded data)
- View/like counts (real-time stats)
- Comments (for active live broadcasts)

**Why this approach?**
- Lives have LESS data than replays (fewer products, no comment history)
- Faster initial page load (data already in HTML)
- Reduces server load (no API calls needed for basic display)
- Better for SEO (data in initial HTML)

---

### 3. ShortClips URLs (`/shortclips/{id}`)

**Data Source:** ⚠️ **Embedded JSON** (server-side rendered) + **API Response**

**Flow:**
```
1. Server → HTML with embedded JSON (similar to lives)
   window.__viewerConfig.shortclip = '{...}'

2. Browser loads JavaScript
3. JavaScript → Also fetches API:
   - /v1/shortclip/{id} → full shortclip data (products, brand, etc.)

4. JavaScript renders UI
```

**Why hybrid approach?**
- ShortClips can have API for full data
- Also supports direct SEO-friendly HTML
- Best of both worlds

---

## Technical Investigation Results

### Lives URL (`https://view.shoppinglive.naver.com/lives/1810235`)

| Metric | Value | Source |
|--------|-------|--------|
| **Initial server HTML size** | 11,139 characters | Server response |
| **Final rendered HTML size** | 170,342 characters | After JavaScript |
| **HTML size growth** | 1429% (15x) | JavaScript rendering |
| **Products in embedded JSON** | 2 products | `window.__viewerConfig.broadcast.shoppingProducts[]` |
| **Product details in JSON** | Full (name, price, discount, stock, brand, image, link) | Embedded JSON |
| **Brand name** | "REPIZ" | `window.__viewerConfig.broadcast.nickname` |
| **Broadcast title** | "💘래피즈 연말&크리스마스 선물 UPTO 38%💘" | `window.__viewerConfig.broadcast.title` |

### Embedded JSON Structure

```json
{
  "id": 1810235,
  "title": "💘래피즈 연말&크리스마스 선물 UPTO 38%💘",
  "nickname": "REPIZ",
  "profileUrl": "http://shop1.phinf.naver.net/.../image.png",
  "status": "BLOCK",
  "startDate": "2025-12-23T13:00:03.227",
  "endDate": "2025-12-23T14:00:16.069",
  "broadcastEndUrl": "https://view.shoppinglive.naver.com/lives/1810235?tr=lim",
  "broadcasterEndUrl": "https://shoppinglive.naver.com/channels/222152",
  "description": "오직 방송중에만 최대 혜택!",
  "shoppingProducts": [
    {
      "key": "11260582263",
      "name": "래피즈 원더 피치 모션 칼로리 바이크...",
      "image": "https://shop-phinf.pstatic.net/.../image.png",
      "brandName": "래피즈",
      "mallName": "REPIZ",
      "link": "https://product.shoppinglive.naver.com/bridge/v4/product/...",
      "price": 269000,
      "discountRate": 22,
      "stock": 538,
      "status": "SALE",
      "arrivalGuarantee": true,
      "freeDelivery": true
    },
    {
      "key": "11614107612",
      "name": "래피즈 테이블형 원더 피치 칼로리 바이크...",
      "price": 299000,
      "discountRate": 36,
      "stock": 203,
      ...
    }
  ],
  "productCount": 2,
  "categoryComponent": {
    "categories": [{"name": "헬스사이클", "id": "50001603", "primary": true}],
    "brandName": "래피즈"
  },
  "likeEffectIconUrls": [...],
  "externalServiceIds": ["shoppinglive", "shoppingliveuser"]
}
```

---

## Crawler Implementation Implications

### Option 1: Parse Embedded JSON (FASTEST for Lives)

**For Lives URLs:**
```python
async def extract_lives(url):
    html = await page.content()

    # Extract embedded JSON
    match = re.search(r'window\.__viewerConfig\.broadcast\s*=\s*\'(.+?)\';', html)
    if match:
        json_str = match.group(1)
        broadcast_data = json.loads(json_str)

        return {
            'broadcast_id': broadcast_data['id'],
            'title': broadcast_data['title'],
            'brand_name': broadcast_data['nickname'],
            'products': broadcast_data['shoppingProducts'],
            'status': broadcast_data['status'],
            'dates': {
                'start': broadcast_data['startDate'],
                'end': broadcast_data['endDate']
            }
        }
```

**Advantages:**
- ✅ **Fastest** - no waiting for JavaScript or APIs
- ✅ **Most reliable** - data guaranteed to be in initial HTML
- ✅ **Complete** - has all product details (name, price, discount, stock, etc.)
- ✅ **No API rate limits** - pure HTML parsing

**Disadvantages:**
- ⚠️ Missing benefits (need API: `/v1/broadcast/{id}/broadcast-benefits`)
- ⚠️ Missing view/like counts (need API: `/v3/broadcast/{id}/extras`)
- ⚠️ Missing comments (only in HTML if broadcast is active)

---

### Option 2: Hybrid (JSON + APIs)

```python
async def extract_lives_hybrid(url):
    # 1. Parse embedded JSON for core data
    json_data = extract_embedded_json(html)

    # 2. Intercept additional APIs
    api_data = {
        'benefits': await extract_api('/broadcast-benefits'),
        'extras': await extract_api('/extras')
    }

    # 3. Merge
    return merge(json_data, api_data)
```

**Advantages:**
- ✅ Complete data (JSON + APIs)
- ✅ Faster than pure HTML parsing

---

### Option 3: Pure HTML Parsing (SLOWEST)

```python
async def extract_lives_html(url):
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(5)  # Wait for JavaScript

    # Parse rendered HTML elements
    products = await page.query_selector_all('[class*="ProductList_item"]')
    ...
```

**Disadvantages:**
- ✗ Slowest (wait for JavaScript rendering)
- ✗ Less reliable (depends on HTML structure)
- ✗ Incomplete (only visible products, limited data)

---

## Final Recommendation

### For Lives URLs: **Parse Embedded JSON** ✅

Use the embedded `window.__viewerConfig.broadcast` JSON for core data:
- Broadcast title, brand name, products, dates, status
- Much faster than waiting for JavaScript rendering
- More complete than HTML parsing (has full product details)
- More reliable than HTML structure matching

**Optionally add APIs for:**
- Benefits (`/v1/broadcast/{id}/broadcast-benefits`)
- View/like counts (`/v3/broadcast/{id}/extras`)

### For Replays URLs: **Pure API Interception** ✅

- No embedded JSON
- APIs have MORE data than would fit in HTML (100 comments, 20+ products)
- Wait 8-10 seconds for all APIs to load

### For ShortClips URLs: **Either JSON or API** ✅

- Has embedded JSON (like lives)
- Also has comprehensive API (`/v1/shortclip/{id}`)
- Choose based on which is easier to implement

---

## Summary Table

| Feature | Replays | Lives | ShortClips |
|---------|---------|-------|------------|
| **Data in Initial HTML** | ❌ No (5KB) | ✅ Yes (11KB JSON) | ✅ Yes (JSON) |
| **Data Source** | APIs only | Embedded JSON | JSON + API |
| **Main API Called** | ✅ `/v1/broadcast/{id}` | ❌ Not called | ✅ `/v1/shortclip/{id}` |
| **Products Count** | 20+ (from API) | 2-5 (from JSON) | Multiple (from API or JSON) |
| **Comments** | 100 (from API) | 0 (need active broadcast) | 0 |
| **Best Extraction Method** | API interception | **Parse embedded JSON** | API or JSON |
| **Speed** | Moderate (8-10s wait) | **Fastest** (instant) | Fast |
| **Completeness** | ✅ Most complete | ⚠️ Core data only | ✅ Complete |

**Winner for Lives:** Parse `window.__viewerConfig.broadcast` JSON string! 🏆
