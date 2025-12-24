"""
Prototype crawler to demonstrate final JSON output structure
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright
from datetime import datetime

OUTPUT_DIR = Path("cj/prototype_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class PrototypeCrawler:
    def __init__(self, max_broadcasts=2):  # Using 2 for quick demo
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
                        import re
                        if re.search(r'/v\d+/broadcast/\d+\?', url) and not any(x in url for x in ['/coupons', '/comments', '/benefits', '/lounge', '/counts', '/extras', '/events', '/watched', '/custom-banner', '/benefit-banner', '/replays', '/shopping-app', '/showhosts']):
                            self.api_data['broadcast'] = body
                            print(f"   [DEBUG] Captured main broadcast API")
                        # Coupons
                        elif '/coupons' in url:
                            self.api_data['coupons'] = body
                            print(f"   [DEBUG] Captured coupons API")
                        # Comments
                        elif '/comments' in url:
                            self.api_data['comments'] = body
                            print(f"   [DEBUG] Captured comments API")
                        # Benefits
                        elif '/broadcast-benefits' in url:
                            self.api_data['broadcast_benefits'] = body
                            print(f"   [DEBUG] Captured benefits API")
                        elif '/benefit-banner' in url:
                            self.api_data['benefit_banner'] = body
                        # Video pager
                        elif '/video-pager/' in url:
                            self.api_data['video_pager'] = body
                            print(f"   [DEBUG] Captured video-pager API")
                        # Extras
                        elif '/extras' in url:
                            self.api_data['extras'] = body
                            print(f"   [DEBUG] Captured extras API")
        except Exception as e:
            print(f"   [ERROR] {e}")

    def _extract_broadcast_data(self, broadcast_id):
        """Extract data from captured API responses"""

        # Main broadcast info
        broadcast = self.api_data.get('broadcast', {})

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

        # Video pager (for navigation)
        pager_data = self.api_data.get('video_pager', {})

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

            # Coupons - extract key info
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
                for c in coupons
            ],

            # Products - extract key info
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
                for p in products[:5]  # Limit to first 5 for demo
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

            # Comments - sample first 10
            "live_chat": [
                {
                    "nickname": c.get('nickname'),
                    "message": c.get('message'),
                    "created_at": c.get('createdAt'),
                    "comment_type": c.get('commentType')
                }
                for c in comments[:10]  # Limit to first 10 for demo
            ],

            # Video pager info
            "related_broadcasts": {
                "prev_content_count": len(pager_data.get('prevPager', {}).get('contents', [])),
                "current": pager_data.get('current', {})
            }
        }

    async def crawl(self, start_url):
        """Crawl broadcasts starting from a replay URL"""

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Use visible browser
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                ignore_https_errors=True
            )

            all_broadcasts = []

            print(f"\n{'='*80}")
            print(f"PROTOTYPE CRAWLER - Extracting {self.max_broadcasts} broadcasts")
            print(f"{'='*80}\n")

            # Extract broadcast ID from URL
            broadcast_id = start_url.split('/')[-1].split('?')[0]

            # Crawl first broadcast
            page = await context.new_page()
            page.on('response', self._handle_response)

            print(f"1. Crawling initial broadcast: {broadcast_id}...")
            await page.goto(start_url, wait_until='networkidle')
            print(f"   Waiting for all APIs to load...")
            await asyncio.sleep(3)

            # Scroll to trigger more API calls
            print(f"   Scrolling to trigger more content...")
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(2)
            await page.evaluate('window.scrollTo(0, 0)')  # Scroll back up
            await asyncio.sleep(3)

            # Extract data
            print(f"   [DEBUG] Captured APIs: {list(self.api_data.keys())}")
            broadcast_data = self._extract_broadcast_data(broadcast_id)
            all_broadcasts.append(broadcast_data)
            print(f"   ✓ Extracted: {broadcast_data['title']}")

            # Get video pager to find more broadcasts
            pager_api_key = f"v2/video-pager/{broadcast_id}"
            pager_data = self.api_data.get(pager_api_key, {})
            prev_contents = pager_data.get('prevPager', {}).get('contents', [])

            print(f"\n2. Found {len(prev_contents)} related broadcasts/clips in video-pager")

            # Crawl additional broadcasts from video-pager
            crawled_count = 1
            for content in prev_contents:
                if crawled_count >= self.max_broadcasts:
                    break

                content_id = content.get('id')
                content_type = content.get('videoContentType')
                link_url = content.get('linkUrl')

                if not link_url:
                    continue

                print(f"\n{crawled_count + 1}. Crawling {content_type}: {content_id}...")

                # Reset API data for next broadcast
                self.api_data = {}

                # Navigate to new broadcast
                await page.goto(link_url, wait_until='networkidle')
                await asyncio.sleep(2)

                # Extract data
                try:
                    broadcast_data = self._extract_broadcast_data(content_id)
                    all_broadcasts.append(broadcast_data)
                    print(f"   ✓ Extracted: {broadcast_data.get('title', 'N/A')}")
                    crawled_count += 1
                except Exception as e:
                    print(f"   ✗ Failed: {e}")
                    continue

            await browser.close()

            # Save to JSON
            output_file = OUTPUT_DIR / f"replay_data_{broadcast_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_data = {
                "metadata": {
                    "crawled_at": datetime.now().isoformat(),
                    "start_url": start_url,
                    "total_broadcasts": len(all_broadcasts),
                    "max_broadcasts": self.max_broadcasts
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
            print(f"\nJSON structure preview:")
            print(json.dumps(output_data, ensure_ascii=False, indent=2)[:1500])
            print(f"\n... (see full output in {output_file})")

if __name__ == "__main__":
    crawler = PrototypeCrawler(max_broadcasts=2)  # Demo with 2 broadcasts
    asyncio.run(crawler.crawl("https://view.shoppinglive.naver.com/replays/1776510"))
