#!/usr/bin/env python3
"""
Naver Shopping Live Replay Crawler
Extracts data from replay pages using API interception
"""

import asyncio
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page, Response


class NaverReplayCrawler:
    """Crawler for Naver Shopping Live Replay pages"""

    def __init__(self, output_dir='cj/replay_data', headless=True, max_replays=5):
        self.output_dir = output_dir
        self.headless = headless
        self.max_replays = max_replays
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        self.api_data = {}

    async def _handle_api_response(self, response: Response):
        """Capture API responses"""
        url = response.url

        try:
            if response.status == 200:
                content_type = response.headers.get('content-type', '')
                if 'application/json' in content_type:
                    # Capture specific API endpoints
                    if '/broadcast/' in url and '/broadcast/' in url:
                        body = await response.json()

                        # Main broadcast info
                        if re.search(r'/broadcast/\d+\?', url):
                            self.api_data['broadcast'] = body
                        # Products
                        elif '/replays/extras' in url:
                            self.api_data['extras'] = body
                        # Coupons
                        elif '/coupons' in url:
                            self.api_data['coupons'] = body
                        # Comments
                        elif '/comments' in url:
                            self.api_data['comments'] = body
                        # Benefits
                        elif '/benefit-banner' in url:
                            self.api_data['benefit_banner'] = body
                        elif '/broadcast-benefits' in url:
                            self.api_data['broadcast_benefits'] = body
                        # Video pager
                        elif '/video-pager/' in url:
                            self.api_data['video_pager'] = body
                        # Custom banner
                        elif '/custom-banner' in url:
                            self.api_data['custom_banner'] = body
        except Exception as e:
            pass

    async def _extract_replay_data(self, page: Page, replay_index: int) -> Dict:
        """Extract data from captured API responses"""
        print(f"\n📋 Extracting data from replay #{replay_index + 1}...")

        data = {
            'replay_index': replay_index + 1,
            'timestamp': datetime.now().isoformat(),
            'url': page.url
        }

        # Extract from broadcast API
        if 'broadcast' in self.api_data:
            broadcast = self.api_data['broadcast']
            data['broadcast_id'] = broadcast.get('id')
            data['title'] = broadcast.get('title')
            data['description'] = broadcast.get('description')
            data['status'] = broadcast.get('status')
            data['broadcast_type'] = broadcast.get('broadcastType')

            # Brand/Channel info
            data['brand_name'] = broadcast.get('nickname')
            data['channel_id'] = broadcast.get('broadcastOwnerId')
            data['channel_profile_url'] = broadcast.get('profileUrl')
            data['channel_end_url'] = broadcast.get('broadcasterEndUrl')

            # Dates
            data['expected_start_date'] = broadcast.get('expectedStartDate')
            data['start_date'] = broadcast.get('startDate')
            data['end_date'] = broadcast.get('endDate')

            # Media
            data['stand_by_image'] = broadcast.get('standByImage')
            data['vid'] = broadcast.get('vid')
            data['broadcast_replay_url'] = broadcast.get('broadcastReplayEndUrl')
            data['broadcast_live_url'] = broadcast.get('broadcastEndUrl')

            # Products from broadcast
            products = broadcast.get('shoppingProducts', [])
            if products:
                data['products'] = []
                for product in products:
                    product_info = {
                        'key': product.get('key'),
                        'name': product.get('name'),
                        'product_type': product.get('productType'),
                        'represent': product.get('represent'),
                        'mall_name': product.get('mallName'),
                        'image': product.get('image'),
                        'link': product.get('link'),
                        'detail_link': product.get('detailLink')
                    }
                    data['products'].append(product_info)

            print(f"    ✓ Title: {data['title']}")
            print(f"    ✓ Brand: {data['brand_name']}")
            print(f"    ✓ Products: {len(products)} found")

        # Extract from extras API (has more detailed product info)
        if 'extras' in self.api_data:
            extras = self.api_data['extras']
            data['comment_count'] = extras.get('commentCount')
            data['like_total_count'] = extras.get('likeTotalCount')
            data['viewer_total_count'] = extras.get('viewerTotalCount')

            # Detailed products
            replay_products = extras.get('replayProducts', [])
            if replay_products and 'products' not in data:
                data['products'] = []
                for product in replay_products:
                    product_info = {
                        'key': product.get('key'),
                        'name': product.get('name'),
                        'price': product.get('price'),
                        'discount_rate': product.get('discountRate'),
                        'stock': product.get('stock'),
                        'image': product.get('image'),
                        'link': product.get('link'),
                        'status': product.get('status')
                    }
                    data['products'].append(product_info)

            print(f"    ✓ Views: {data.get('viewer_total_count', 0)}")
            print(f"    ✓ Likes: {data.get('like_total_count', 0)}")
            print(f"    ✓ Comments: {data.get('comment_count', 0)}")

        # Extract coupons
        if 'coupons' in self.api_data:
            coupons_data = self.api_data['coupons']
            coupons = coupons_data.get('coupons', [])
            if coupons:
                data['coupons'] = []
                for coupon in coupons:
                    coupon_info = {
                        'name': coupon.get('name'),
                        'discount_amount': coupon.get('discountAmount'),
                        'discount_type': coupon.get('discountType'),
                        'status': coupon.get('status')
                    }
                    data['coupons'].append(coupon_info)
                print(f"    ✓ Coupons: {len(coupons)} found")

        # Extract comments
        if 'comments' in self.api_data:
            comments_data = self.api_data['comments']
            comments = comments_data.get('comments', [])
            if comments:
                data['live_chat'] = []
                for comment in comments[:20]:  # Limit to 20
                    comment_info = {
                        'nickname': comment.get('nickname'),
                        'comment': comment.get('comment'),
                        'created_at': comment.get('createdAt')
                    }
                    data['live_chat'].append(comment_info)
                print(f"    ✓ Chat Comments: {len(data['live_chat'])} captured")

        # Extract benefits
        if 'benefit_banner' in self.api_data:
            benefit = self.api_data['benefit_banner']
            if benefit.get('exposureText'):
                data['benefit_banner'] = {
                    'text': benefit.get('exposureText'),
                    'sub_text': benefit.get('exposureSubText'),
                    'description': benefit.get('exposureDescription'),
                    'link_url': benefit.get('linkUrl')
                }
                print(f"    ✓ Benefit Banner found")

        print(f"    ✅ Data extraction complete for replay #{replay_index + 1}")
        return data

    async def _swipe_to_next_replay(self, page: Page) -> bool:
        """Simulate swipe to next replay"""
        import random
        print("\n👆 Swiping to next replay...")

        try:
            # Clear previous API data
            self.api_data = {}

            # Get viewport size
            viewport = page.viewport_size
            center_x = viewport['width'] // 2
            center_y = viewport['height'] // 2

            # Simulate swipe up
            await page.mouse.move(center_x, center_y)
            await page.mouse.down()
            await asyncio.sleep(random.uniform(0.1, 0.3))
            await page.mouse.move(center_x, center_y - 400, steps=10)
            await page.mouse.up()

            # Wait for content to update
            await asyncio.sleep(random.uniform(2, 3))

            # Wait for API responses to be captured
            await asyncio.sleep(2)

            print("    ✓ Swipe complete")
            return True

        except Exception as e:
            print(f"    ✗ Swipe failed: {e}")
            return False

    async def crawl(self, url: str) -> Dict:
        """Main crawling function"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║      Naver Shopping Live Replay Crawler                          ║
╚══════════════════════════════════════════════════════════════════╝

URL: {url}
Max Replays: {self.max_replays}
Headless: {self.headless}
        """)

        all_replays_data = []

        async with async_playwright() as p:
            try:
                # Launch browser
                print("🚀 Launching browser...")

                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )

                # Create context
                context = await browser.new_context(
                    viewport={'width': 414, 'height': 896},
                    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                    locale='ko-KR',
                    timezone_id='Asia/Seoul',
                    has_touch=True,
                    is_mobile=True,
                    ignore_https_errors=True
                )

                page = await context.new_page()

                # Set up API response handler
                page.on('response', self._handle_api_response)

                print("    ✓ Browser launched")

                # Navigate to page
                print(f"\n📄 Navigating to page...")
                await page.goto(url, wait_until='networkidle', timeout=60000)
                print(f"    ✓ Page loaded")

                # Wait for API responses
                await asyncio.sleep(5)

                # Extract data from multiple replays
                for i in range(self.max_replays):
                    print(f"\n{'='*70}")
                    print(f"Processing Replay {i + 1}/{self.max_replays}")
                    print(f"{'='*70}")

                    # Extract current replay data
                    replay_data = await self._extract_replay_data(page, i)
                    all_replays_data.append(replay_data)

                    # If not the last replay, swipe to next
                    if i < self.max_replays - 1:
                        success = await self._swipe_to_next_replay(page)
                        if not success:
                            print(f"    ⚠ Could not swipe to next replay, stopping at {i + 1} replays")
                            break

                # Close browser
                await browser.close()

                # Save results
                output_file = f"{self.output_dir}/replay_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_replays_data, f, ensure_ascii=False, indent=2)

                print(f"\n{'='*70}")
                print(f"✅ Crawling Complete!")
                print(f"{'='*70}")
                print(f"Total replays extracted: {len(all_replays_data)}")
                print(f"Data saved to: {output_file}")

                return {
                    'success': True,
                    'replays_count': len(all_replays_data),
                    'data': all_replays_data,
                    'output_file': output_file
                }

            except Exception as e:
                print(f"\n❌ Crawling failed: {e}")
                import traceback
                traceback.print_exc()

                return {
                    'success': False,
                    'error': str(e),
                    'replays_count': len(all_replays_data),
                    'data': all_replays_data
                }


async def main():
    """Test the crawler"""
    import sys

    # Default URL
    default_url = 'https://view.shoppinglive.naver.com/replays/1776510?fm=store&offFeature=contentLayer&sn=ltlim&swipe=%7B%22sortType%22%3A%22LATEST%22%2C%22pagerType%22%3A%22ALL%22%2C%22channelId%22%3A62163%2C%22referrerType%22%3A%22STORE%22%2C%22referrerKey%22%3A%2262163%22%7D&tr=ltlim'

    # Parse arguments
    url = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else default_url
    max_replays = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 5
    headless = '--visible' not in sys.argv

    print(f"\nURL: {url}")
    print(f"Max Replays: {max_replays}")
    print(f"Headless: {headless}\n")

    crawler = NaverReplayCrawler(max_replays=max_replays, headless=headless)
    result = await crawler.crawl(url)

    if result['success']:
        print(f"\n✅ Success!")
        print(f"   Extracted {result['replays_count']} replays")
        print(f"   Saved to: {result['output_file']}")
    else:
        print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")
        if result['replays_count'] > 0:
            print(f"   Partially extracted {result['replays_count']} replays before failure")


if __name__ == '__main__':
    # Run async main
    asyncio.run(main())
