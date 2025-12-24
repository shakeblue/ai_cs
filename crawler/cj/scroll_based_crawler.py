"""
Scroll-based Naver Shopping Live Replay Crawler
Scrolls through broadcasts on a single page to extract multiple broadcasts
"""

import asyncio
import json
import re
from pathlib import Path
from playwright.async_api import async_playwright
from datetime import datetime

OUTPUT_DIR = Path("cj/scroll_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class ScrollBasedCrawler:
    def __init__(self, max_broadcasts=5):
        self.max_broadcasts = max_broadcasts
        self.api_data = {}

    async def _handle_response(self, response):
        """Capture API responses"""
        url = response.url

        try:
            if response.status == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    body = await response.json()

                    # Capture specific API endpoints
                    if '/broadcast/' in url:
                        # Main broadcast info - use regex to match exact pattern
                        if re.search(r'/v\d+/broadcast/\d+\?', url) and not any(x in url for x in ['/coupons', '/comments', '/benefits', '/lounge', '/counts', '/extras', '/events', '/watched', '/custom-banner', '/benefit-banner', '/replays', '/shopping-app', '/showhosts']):
                            self.api_data['broadcast'] = body
                            print(f"      [API] Broadcast info")
                        # Coupons
                        elif '/coupons' in url:
                            self.api_data['coupons'] = body
                            print(f"      [API] Coupons")
                        # Comments
                        elif '/comments' in url:
                            self.api_data['comments'] = body
                            print(f"      [API] Comments")
                        # Benefits
                        elif '/broadcast-benefits' in url:
                            self.api_data['broadcast_benefits'] = body
                            print(f"      [API] Benefits")
                        # Video pager
                        elif '/video-pager/' in url:
                            self.api_data['video_pager'] = body
                        # Extras
                        elif '/extras' in url:
                            self.api_data['extras'] = body
                            print(f"      [API] Extras")
        except Exception as e:
            pass

    def _extract_broadcast_data(self):
        """Extract data from captured API responses"""

        # Main broadcast info
        broadcast = self.api_data.get('broadcast', {})

        if not broadcast:
            return None

        # Coupons
        coupons_data = self.api_data.get('coupons', {})
        coupons = coupons_data.get('coupons', [])

        # Benefits
        benefits = self.api_data.get('broadcast_benefits', [])

        # Comments
        comments_data = self.api_data.get('comments', {})
        comments = comments_data.get('comments', [])

        # Products (from main broadcast API)
        products = broadcast.get('shoppingProducts', [])

        return {
            "broadcast_id": broadcast.get('id'),
            "replay_url": broadcast.get('broadcastReplayEndUrl'),
            "broadcast_url": broadcast.get('broadcastEndUrl'),
            "title": broadcast.get('title'),
            "brand_name": broadcast.get('nickname'),
            "description": broadcast.get('description'),
            "broadcast_date": broadcast.get('startDate'),
            "broadcast_end_date": broadcast.get('endDate'),
            "expected_start_date": broadcast.get('expectedStartDate'),
            "status": broadcast.get('status'),

            # Coupons
            "coupons": [
                {
                    "title": c.get('benefitPolicyName'),
                    "benefit_type": c.get('benefitTargetType'),
                    "benefit_unit": c.get('benefitUnit'),
                    "benefit_value": c.get('benefitValue'),
                    "min_order_amount": c.get('minOrderAmount'),
                    "max_discount_amount": c.get('maxDiscountAmount'),
                    "valid_start": c.get('validPeriodStartDate'),
                    "valid_end": c.get('validPeriodEndDate'),
                    "availability": c.get('availabilityStatus')
                }
                for c in coupons[:10]  # Limit coupons
            ],

            # Products
            "products": [
                {
                    "product_id": p.get('key'),
                    "name": p.get('name'),
                    "brand_name": p.get('brandName'),
                    "discount_rate": p.get('discountRate'),
                    "discounted_price": p.get('discountedSalePrice'),
                    "original_price": p.get('price'),
                    "stock": p.get('stock'),
                    "image": p.get('image'),
                    "link": p.get('link'),
                    "review_count": p.get('reviewCount'),
                    "delivery_fee": p.get('deliveryFee')
                }
                for p in products[:20]  # Limit products
            ],

            # Benefits
            "live_benefits": [
                {
                    "id": b.get('id'),
                    "message": b.get('message'),
                    "detail": b.get('detailMessage'),
                    "type": b.get('type')
                }
                for b in benefits
            ],

            # Comments
            "live_chat": [
                {
                    "nickname": c.get('nickname'),
                    "message": c.get('message'),
                    "created_at": c.get('createdAt'),
                    "comment_type": c.get('commentType')
                }
                for c in comments[:50]  # Limit to first 50 comments
            ]
        }

    async def crawl(self, start_url):
        """Crawl broadcasts by scrolling through the page"""

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                ignore_https_errors=True
            )

            page = await context.new_page()
            page.on('response', self._handle_response)

            all_broadcasts = []

            print(f"\n{'='*80}")
            print(f"SCROLL-BASED CRAWLER - Extracting up to {self.max_broadcasts} broadcasts")
            print(f"{'='*80}\n")

            # Load initial page
            print(f"Loading page: {start_url}")
            await page.goto(start_url, wait_until='networkidle')
            await asyncio.sleep(5)  # Wait longer for all initial APIs

            # Extract broadcasts by scrolling
            for i in range(self.max_broadcasts):
                print(f"\n{i+1}. Extracting broadcast #{i+1}...")

                # Wait for current broadcast APIs to load
                print(f"   Waiting for APIs to load...")
                await asyncio.sleep(4)  # Wait longer for all APIs

                # Extract data
                broadcast_data = self._extract_broadcast_data()

                if broadcast_data:
                    all_broadcasts.append(broadcast_data)
                    print(f"   ✓ Extracted: {broadcast_data['title']}")
                    print(f"      - Products: {len(broadcast_data['products'])}")
                    print(f"      - Coupons: {len(broadcast_data['coupons'])}")
                    print(f"      - Benefits: {len(broadcast_data['live_benefits'])}")
                    print(f"      - Comments: {len(broadcast_data['live_chat'])}")
                else:
                    print(f"   ✗ No broadcast data found")
                    break

                # If this isn't the last one, scroll to next broadcast
                if i < self.max_broadcasts - 1:
                    print(f"   Scrolling to next broadcast...")

                    # Clear API data to capture fresh data for next broadcast
                    self.api_data = {}

                    # Scroll down to load next broadcast
                    await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')

                    # Add 1 second delay between broadcasts (as per requirements)
                    await asyncio.sleep(1)

                    # Wait for new broadcast to load
                    await asyncio.sleep(2)

            await browser.close()

            # Save to JSON
            broadcast_id = start_url.split('/')[-1].split('?')[0]
            output_file = OUTPUT_DIR / f"replay_{broadcast_id}.json"

            output_data = {
                "metadata": {
                    "crawled_at": datetime.now().isoformat(),
                    "start_url": start_url,
                    "total_broadcasts": len(all_broadcasts),
                    "max_broadcasts_requested": self.max_broadcasts
                },
                "broadcasts": all_broadcasts
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print(f"\n{'='*80}")
            print(f"CRAWL COMPLETE!")
            print(f"{'='*80}")
            print(f"Total broadcasts extracted: {len(all_broadcasts)}")
            print(f"Output saved to: {output_file}")
            print(f"\nPreview of JSON structure:")
            print(json.dumps(output_data['metadata'], ensure_ascii=False, indent=2))
            print(f"\nFirst broadcast preview:")
            if all_broadcasts:
                first_broadcast = all_broadcasts[0]
                preview = {
                    "broadcast_id": first_broadcast['broadcast_id'],
                    "title": first_broadcast['title'],
                    "brand_name": first_broadcast['brand_name'],
                    "products_count": len(first_broadcast['products']),
                    "coupons_count": len(first_broadcast['coupons']),
                    "benefits_count": len(first_broadcast['live_benefits']),
                    "comments_count": len(first_broadcast['live_chat'])
                }
                print(json.dumps(preview, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    import sys

    # Default values
    url = "https://view.shoppinglive.naver.com/replays/1776510"
    max_broadcasts = 3  # Test with 3 for demo

    # Parse command line args if provided
    if len(sys.argv) > 1:
        url = sys.argv[1]
    if len(sys.argv) > 2:
        max_broadcasts = int(sys.argv[2])

    print(f"\nStarting crawler...")
    print(f"  URL: {url}")
    print(f"  Max broadcasts: {max_broadcasts}\n")

    crawler = ScrollBasedCrawler(max_broadcasts=max_broadcasts)
    asyncio.run(crawler.crawl(url))
