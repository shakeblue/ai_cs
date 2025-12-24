# Livebridge API Documentation

## Overview
REST API endpoints for accessing Naver Shopping Live livebridge promotional data stored in Supabase.

## Base URL
```
http://localhost:3001/api/livebridge
```

## Endpoints

### 1. Get All Livebridges (Paginated)

**GET** `/api/livebridge`

Get a paginated list of all livebridge records.

#### Query Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | integer | 1 | Page number |
| `limit` | integer | 20 | Items per page |
| `sort` | string | 'date_desc' | Sort order (date_desc, date_asc, title_asc, title_desc) |

#### Example Request
```bash
curl http://localhost:3001/api/livebridge?page=1&limit=10&sort=date_desc
```

#### Example Response
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "url": "https://shoppinglive.naver.com/livebridge/1776510",
      "live_datetime": "2025-12-03T20:00:00+00:00",
      "title": "[강세일]베스트 어워즈💙특집 라이브(~40%+트리플 혜택)",
      "brand_name": "아이오페",
      "created_at": "2025-12-24T10:30:00+00:00",
      "updated_at": "2025-12-24T10:30:00+00:00",
      "livebridge_products": [{"id": 1}, {"id": 2}],
      "livebridge_coupons": [{"id": 1}, {"id": 2}, {"id": 3}]
    }
  ],
  "pagination": {
    "currentPage": 1,
    "totalPages": 5,
    "totalItems": 42,
    "itemsPerPage": 10,
    "hasNextPage": true,
    "hasPrevPage": false
  }
}
```

---

### 2. Get Livebridge by ID

**GET** `/api/livebridge/:id`

Get complete livebridge data including all related records (coupons, products, benefits).

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Livebridge ID |

#### Example Request
```bash
curl http://localhost:3001/api/livebridge/1
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "id": 1,
    "url": "https://shoppinglive.naver.com/livebridge/1776510",
    "live_datetime": "2025-12-03T20:00:00+00:00",
    "title": "[강세일]베스트 어워즈💙특집 라이브(~40%+트리플 혜택)",
    "brand_name": "아이오페",
    "created_at": "2025-12-24T10:30:00+00:00",
    "updated_at": "2025-12-24T10:30:00+00:00",
    "special_coupons": [
      {
        "id": 1,
        "livebridge_id": 1,
        "coupon_name": "샘플링 시크릿혜택_슈바_7천원",
        "coupon_type": "NEWS",
        "benefit_unit": "FIX",
        "benefit_value": 7000,
        "min_order_amount": 90000,
        "max_discount_amount": null,
        "coupon_kind": "PRODUCT",
        "valid_period_start": "2025-12-15T00:00:00+09:00",
        "valid_period_end": "2025-12-31T23:59:59.999+09:00",
        "availability_status": "ISSUABLE",
        "benefit_status": "ON",
        "provider_name": "아이오페",
        "source": "API"
      }
    ],
    "products": [
      {
        "id": 1,
        "livebridge_id": 1,
        "image": "https://shop-phinf.pstatic.net/...",
        "name": "아이오페 NEW 6세대 슈퍼바이탈 크림 50ml",
        "discount_rate": 23,
        "discount_price": 100100
      }
    ],
    "live_benefits": [
      "N+스토어 강세일"
    ],
    "benefits_by_amount": [
      "라이브 특가 UP TO 40%",
      "구매인증(해시태그+주문번호) 시 신세계백화점 5천원 모바일 상품권 증정(20명)",
      "전 구매 고객 사은품: NEW 멀티 비타민 10% 겔 마스크팩 증정"
    ],
    "coupons": [
      "첫 구매/라운지 쿠폰 3천원 (7만 원 이상 구매 시)",
      "첫 구매/라운지 쿠폰 2천원 (4만 원 이상 구매 시)"
    ]
  }
}
```

---

### 3. Get Livebridge by URL

**GET** `/api/livebridge/url/:encodedUrl`

Get livebridge data by its original URL (URL must be URL-encoded).

#### Path Parameters
| Parameter | Type | Description |
|-----------|------|-------------|
| `encodedUrl` | string | URL-encoded livebridge URL |

#### Example Request
```bash
# URL-encode the livebridge URL first
curl "http://localhost:3001/api/livebridge/url/https%3A%2F%2Fshoppinglive.naver.com%2Flivebridge%2F1776510"
```

#### JavaScript Example
```javascript
const livebridgeUrl = 'https://shoppinglive.naver.com/livebridge/1776510';
const encodedUrl = encodeURIComponent(livebridgeUrl);

fetch(`http://localhost:3001/api/livebridge/url/${encodedUrl}`)
  .then(res => res.json())
  .then(data => console.log(data));
```

#### Example Response
Same structure as "Get Livebridge by ID"

---

### 4. Get Livebridge Statistics

**GET** `/api/livebridge/stats`

Get statistics and summary information about livebridge data.

#### Example Request
```bash
curl http://localhost:3001/api/livebridge/stats
```

#### Example Response
```json
{
  "success": true,
  "data": {
    "total": 42,
    "byBrand": {
      "아이오페": 5,
      "설화수": 3,
      "이니스프리": 8
    },
    "recent": [
      {
        "id": 42,
        "title": "최신 라이브 방송",
        "brand_name": "아이오페",
        "live_datetime": "2025-12-24T20:00:00+00:00",
        "created_at": "2025-12-24T12:00:00+00:00"
      }
    ]
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "message": "Invalid livebridge ID"
}
```

### 404 Not Found
```json
{
  "success": false,
  "message": "Livebridge not found"
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "message": "Failed to fetch livebridge data",
  "error": "Error message details"
}
```

---

## Data Model

### Main Livebridge Object
```typescript
{
  id: number;
  url: string;
  live_datetime: string;  // ISO 8601 format
  title: string;
  brand_name: string;
  created_at: string;
  updated_at: string;
}
```

### Special Coupon Object
```typescript
{
  id: number;
  livebridge_id: number;
  coupon_name: string;
  coupon_type: string;  // "NEWS", "LIVE", etc.
  benefit_unit: string;  // "FIX", "PERCENT"
  benefit_value: number;
  min_order_amount: number | null;
  max_discount_amount: number | null;
  coupon_kind: string;  // "PRODUCT", "ORDER"
  valid_period_start: string | null;
  valid_period_end: string | null;
  availability_status: string | null;
  benefit_status: string | null;
  provider_name: string;
  source: string;  // "API"
}
```

### Product Object
```typescript
{
  id: number;
  livebridge_id: number;
  image: string;  // Image URL
  name: string;
  discount_rate: number;
  discount_price: number;
}
```

### Arrays
- `live_benefits`: `string[]`
- `benefits_by_amount`: `string[]`
- `coupons`: `string[]`

---

## Testing the API

### Using cURL
```bash
# Get all livebridges
curl http://localhost:3001/api/livebridge

# Get specific livebridge
curl http://localhost:3001/api/livebridge/1

# Get by URL
curl "http://localhost:3001/api/livebridge/url/$(echo -n 'https://shoppinglive.naver.com/livebridge/1776510' | jq -sRr @uri)"

# Get stats
curl http://localhost:3001/api/livebridge/stats
```

### Using JavaScript (Fetch)
```javascript
// Get all livebridges with pagination
async function getLivebridges(page = 1, limit = 20) {
  const response = await fetch(
    `http://localhost:3001/api/livebridge?page=${page}&limit=${limit}`
  );
  return response.json();
}

// Get specific livebridge
async function getLivebridge(id) {
  const response = await fetch(`http://localhost:3001/api/livebridge/${id}`);
  return response.json();
}

// Get by URL
async function getLivebridgeByUrl(url) {
  const encodedUrl = encodeURIComponent(url);
  const response = await fetch(
    `http://localhost:3001/api/livebridge/url/${encodedUrl}`
  );
  return response.json();
}
```

### Using Postman
Import the following collection:

1. **GET All Livebridges**
   - URL: `http://localhost:3001/api/livebridge?page=1&limit=10`
   - Method: GET

2. **GET Livebridge by ID**
   - URL: `http://localhost:3001/api/livebridge/1`
   - Method: GET

3. **GET Livebridge by URL**
   - URL: `http://localhost:3001/api/livebridge/url/https%3A%2F%2Fshoppinglive.naver.com%2Flivebridge%2F1776510`
   - Method: GET

4. **GET Statistics**
   - URL: `http://localhost:3001/api/livebridge/stats`
   - Method: GET

---

## Integration with Frontend

### React Example
```jsx
import React, { useState, useEffect } from 'react';

function LivebridgeDetail({ livebridgeId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/livebridge/${livebridgeId}`)
      .then(res => res.json())
      .then(result => {
        if (result.success) {
          setData(result.data);
        } else {
          setError(result.message);
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [livebridgeId]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!data) return null;

  return (
    <div>
      <h2>{data.title}</h2>
      <p>Brand: {data.brand_name}</p>

      {/* Special Coupons */}
      {data.special_coupons?.length > 0 && (
        <div>
          <h3>Special Coupons</h3>
          {data.special_coupons.map(coupon => (
            <div key={coupon.id}>
              <p>{coupon.coupon_name}</p>
              <p>{coupon.benefit_value} {coupon.benefit_unit}</p>
            </div>
          ))}
        </div>
      )}

      {/* Products */}
      {data.products?.length > 0 && (
        <div>
          <h3>Products</h3>
          {data.products.map(product => (
            <div key={product.id}>
              <img src={product.image} alt={product.name} />
              <p>{product.name}</p>
              <p>{product.discount_rate}% OFF - {product.discount_price}원</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Related Documentation

- **Database Schema**: `/home/long/ai_cs/database/create_livebridge_tables.sql`
- **Service Layer**: `/home/long/ai_cs/backend/src/services/livebridgeService.js`
- **Routes**: `/home/long/ai_cs/backend/src/routes/livebridgeRoutes.js`
- **Requirements**: `/home/long/ai_cs/docs/ai/requirements/feature-naver-livebridge-data-extraction.md`
- **Design**: `/home/long/ai_cs/docs/ai/design/feature-naver-livebridge-data-extraction.md`
