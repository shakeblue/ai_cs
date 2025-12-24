#!/usr/bin/env python3
"""
Naver Shopping Live Short Clips Crawler V2
Extracts data from window.__shortclip JavaScript object
"""

import asyncio
import json
import os
import time
import random
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page


class NaverShortClipsCrawlerV2:
    """Crawler for Naver Shopping Live Short Clips - using JavaScript data extraction"""

    def __init__(self, output_dir='cj/shortclips_data', headless=True, max_clips=5):
        self.output_dir = output_dir
        self.headless = headless
        self.max_clips = max_clips
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    async def _wait_for_content_load(self, page: Page, timeout=5000):
        """Wait for content to load after navigation"""
        await asyncio.sleep(random.uniform(1, 2))
        try:
            # Wait for the JavaScript data to be available
            await page.wait_for_function("window.__shortclip !== undefined", timeout=timeout)
        except:
            print("    ⚠ Timeout waiting for __shortclip data, proceeding anyway...")

    async def _extract_clip_data(self, page: Page, clip_index: int) -> Dict:
        """Extract all data from window.__shortclip JavaScript object"""
        print(f"\n📋 Extracting data from clip #{clip_index + 1}...")

        data = {
            'clip_index': clip_index + 1,
            'timestamp': datetime.now().isoformat(),
            'url': page.url
        }

        try:
            # Extract the __shortclip JavaScript object
            shortclip_data = await page.evaluate("""
                () => {
                    if (typeof window.__shortclip === 'string') {
                        try {
                            return JSON.parse(window.__shortclip);
                        } catch (e) {
                            console.error('Failed to parse __shortclip:', e);
                            return null;
                        }
                    } else if (typeof window.__shortclip === 'object') {
                        return window.__shortclip;
                    }
                    return null;
                }
            """)

            if not shortclip_data:
                print("    ⚠ Could not extract __shortclip data")
                return data

            # Extract basic information
            data['shortclip_id'] = shortclip_data.get('shortclipId')
            data['status'] = shortclip_data.get('status')
            data['title'] = shortclip_data.get('title')
            data['description'] = shortclip_data.get('description')

            # Brand information
            data['brand_name'] = shortclip_data.get('channelName')
            data['channel_id'] = shortclip_data.get('channelId')
            data['channel_image_url'] = shortclip_data.get('channelImageUrl')
            data['channel_link_url'] = shortclip_data.get('channelLinkUrl')

            # Broadcast information
            data['broadcast_url'] = shortclip_data.get('broadcastLinkUrl')
            data['broadcaster_id'] = shortclip_data.get('broadcasterId')
            data['expected_expose_at'] = shortclip_data.get('expectedExposeAt')

            # Media information
            data['stand_by_image_url'] = shortclip_data.get('standByImageUrl')
            data['vid'] = shortclip_data.get('vid')
            data['vod_media_url'] = shortclip_data.get('vodMediaUrl')

            # Products information
            products = shortclip_data.get('products', [])
            if products:
                data['products'] = []
                for product in products:
                    product_info = {
                        'product_no': product.get('productNo'),
                        'name': product.get('name'),
                        'price': product.get('price'),
                        'discount_rate': product.get('discountRate'),
                        'stock': product.get('stock'),
                        'image_url': product.get('imageUrl'),
                        'product_bridge_url': product.get('productBridgeUrl'),
                        'status': product.get('liveProductStatus'),
                        'represent': product.get('represent'),
                        'introducing': product.get('introducing'),
                        'category': product.get('rightLayerCategoryName'),
                        'delivery_fee': product.get('deliveryFee'),
                        'arrival_guarantee': product.get('arrivalGuarantee')
                    }
                    data['products'].append(product_info)

            print(f"    ✓ Title: {data['title']}")
            print(f"    ✓ Brand: {data['brand_name']}")
            print(f"    ✓ Products: {len(products)} found")
            print(f"    ✓ Status: {data['status']}")

            # Try to extract additional UI elements (coupons, benefits, comments, etc.)
            await self._extract_ui_elements(page, data)

            print(f"    ✅ Data extraction complete for clip #{clip_index + 1}")
            return data

        except Exception as e:
            print(f"    ❌ Error extracting clip data: {e}")
            import traceback
            traceback.print_exc()
            return data

    async def _extract_ui_elements(self, page: Page, data: Dict):
        """Extract additional UI elements like coupons, benefits, comments"""

        # Extract Coupons
        try:
            coupons = await page.evaluate("""
                () => {
                    const couponEls = document.querySelectorAll('[class*="CouponButton_content_"]');
                    const coupons = [];

                    couponEls.forEach(el => {
                        const textEl = el.querySelector('[class*="CouponButton_text_"]');
                        if (textEl) {
                            coupons.push(textEl.textContent.trim());
                        }
                    });

                    return coupons.length > 0 ? coupons : null;
                }
            """)
            data['coupons'] = coupons
            if coupons:
                print(f"    ✓ Coupons: {len(coupons)} found")
        except Exception as e:
            data['coupons'] = None

        # Extract Benefits
        try:
            benefits = await page.evaluate("""
                () => {
                    const benefitEls = document.querySelectorAll('[class*="Benefit"][class*="title"]');
                    const benefits = [];

                    benefitEls.forEach(el => {
                        const text = el.textContent.trim();
                        if (text && text.length > 2) benefits.push(text);
                    });

                    return benefits.length > 0 ? benefits : null;
                }
            """)
            data['benefits'] = benefits
            if benefits:
                print(f"    ✓ Benefits: {len(benefits)} found")
        except Exception as e:
            data['benefits'] = None

        # Extract Live Chat Comments
        try:
            comments = await page.evaluate("""
                () => {
                    const commentEls = document.querySelectorAll('[class*="Comment"]');
                    const comments = [];

                    commentEls.forEach(el => {
                        const nicknameEl = el.querySelector('[class*="nickname"]');
                        const commentEl = el.querySelector('[class*="comment"]');

                        if (nicknameEl && commentEl) {
                            comments.push({
                                nickname: nicknameEl.textContent.trim(),
                                comment: commentEl.textContent.trim()
                            });
                        }
                    });

                    return comments.length > 0 ? comments.slice(0, 20) : null;  // Limit to 20
                }
            """)
            data['live_chat'] = comments
            if comments:
                print(f"    ✓ Chat Comments: {len(comments)} found")
        except Exception as e:
            data['live_chat'] = None

    async def _swipe_to_next_clip(self, page: Page) -> bool:
        """Simulate swipe to next clip"""
        print("\n👆 Swiping to next clip...")

        try:
            # Get viewport size
            viewport = page.viewport_size
            center_x = viewport['width'] // 2
            center_y = viewport['height'] // 2

            # Simulate swipe up (drag from center to top)
            await page.mouse.move(center_x, center_y)
            await page.mouse.down()
            await asyncio.sleep(random.uniform(0.1, 0.3))
            await page.mouse.move(center_x, center_y - 400, steps=10)
            await page.mouse.up()

            # Wait for content to update
            await asyncio.sleep(random.uniform(1.5, 2.5))

            print("    ✓ Swipe complete")
            return True

        except Exception as e:
            print(f"    ✗ Swipe failed: {e}")
            return False

    async def crawl(self, url: str) -> Dict:
        """Main crawling function"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║      Naver Shopping Live Short Clips Crawler V2                  ║
╚══════════════════════════════════════════════════════════════════╝

URL: {url}
Max Clips: {self.max_clips}
Headless: {self.headless}
        """)

        all_clips_data = []

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
                    viewport={'width': 414, 'height': 896},  # Mobile viewport for short clips
                    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                    locale='ko-KR',
                    timezone_id='Asia/Seoul',
                    has_touch=True,  # Enable touch events
                    is_mobile=True,
                    ignore_https_errors=True  # Ignore SSL certificate errors
                )

                page = await context.new_page()
                print("    ✓ Browser launched")

                # Navigate to page
                print(f"\n📄 Navigating to page...")
                await page.goto(url, wait_until='networkidle', timeout=60000)
                print(f"    ✓ Page loaded")

                # Wait for initial content
                await self._wait_for_content_load(page)

                # Extract data from multiple clips
                for i in range(self.max_clips):
                    print(f"\n{'='*70}")
                    print(f"Processing Clip {i + 1}/{self.max_clips}")
                    print(f"{'='*70}")

                    # Extract current clip data
                    clip_data = await self._extract_clip_data(page, i)
                    all_clips_data.append(clip_data)

                    # If not the last clip, swipe to next
                    if i < self.max_clips - 1:
                        success = await self._swipe_to_next_clip(page)
                        if not success:
                            print(f"    ⚠ Could not swipe to next clip, stopping at {i + 1} clips")
                            break

                        # Wait for new content to load
                        await self._wait_for_content_load(page)

                # Close browser
                await browser.close()

                # Save results
                output_file = f"{self.output_dir}/shortclips_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_clips_data, f, ensure_ascii=False, indent=2)

                print(f"\n{'='*70}")
                print(f"✅ Crawling Complete!")
                print(f"{'='*70}")
                print(f"Total clips extracted: {len(all_clips_data)}")
                print(f"Data saved to: {output_file}")

                return {
                    'success': True,
                    'clips_count': len(all_clips_data),
                    'data': all_clips_data,
                    'output_file': output_file
                }

            except Exception as e:
                print(f"\n❌ Crawling failed: {e}")
                import traceback
                traceback.print_exc()

                return {
                    'success': False,
                    'error': str(e),
                    'clips_count': len(all_clips_data),
                    'data': all_clips_data
                }


async def main():
    """Test the crawler"""
    import sys

    # Default URL
    default_url = 'https://view.shoppinglive.naver.com/shortclips/9588115?fm=store&offFeature=contentLayer&sn=ltlim&swipe=%7B%22sortType%22%3A%22LATEST%22%2C%22pagerType%22%3A%22ALL%22%2C%22channelId%22%3A62163%2C%22referrerType%22%3A%22STORE%22%2C%22referrerKey%22%3A%2262163%22%7D&tr=sclim'

    # Parse arguments
    url = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else default_url
    max_clips = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 5
    headless = '--visible' not in sys.argv

    print(f"\nURL: {url}")
    print(f"Max Clips: {max_clips}")
    print(f"Headless: {headless}\n")

    crawler = NaverShortClipsCrawlerV2(max_clips=max_clips, headless=headless)
    result = await crawler.crawl(url)

    if result['success']:
        print(f"\n✅ Success!")
        print(f"   Extracted {result['clips_count']} clips")
        print(f"   Saved to: {result['output_file']}")
    else:
        print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")
        if result['clips_count'] > 0:
            print(f"   Partially extracted {result['clips_count']} clips before failure")


if __name__ == '__main__':
    # Run async main
    asyncio.run(main())
