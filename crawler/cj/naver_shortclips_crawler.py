#!/usr/bin/env python3
"""
Naver Shopping Live Short Clips Crawler
Extracts promotional information from shopping live short clips
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


class NaverShortClipsCrawler:
    """Crawler for Naver Shopping Live Short Clips"""

    def __init__(self, output_dir='crawler/cj/shortclips_data', headless=True, max_clips=5):
        self.output_dir = output_dir
        self.headless = headless
        self.max_clips = max_clips
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

    def _human_delay(self, min_delay=1, max_delay=3):
        """Human-like delay"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)

    async def _wait_for_content_load(self, page: Page, timeout=5000):
        """Wait for content to load after navigation"""
        await asyncio.sleep(random.uniform(1, 2))
        try:
            # Wait for any of the key elements to be visible
            await page.wait_for_selector('[class*="IntroductionProfile_name_"]', timeout=timeout, state='visible')
        except:
            print("    ⚠ Timeout waiting for content, proceeding anyway...")

    async def _extract_clip_data(self, page: Page, clip_index: int) -> Dict:
        """Extract all data from current clip"""
        print(f"\n📋 Extracting data from clip #{clip_index + 1}...")

        data = {
            'clip_index': clip_index + 1,
            'timestamp': datetime.now().isoformat(),
            'url': page.url
        }

        try:
            # Extract Information Title
            try:
                title = await page.evaluate("""
                    () => {
                        const titleEl = document.querySelector('[class*="IntroductionModalTitle_wrap_"]');
                        return titleEl ? titleEl.textContent.trim() : null;
                    }
                """)
                data['information_title'] = title
                data['accurate_broadcast_title'] = title
                print(f"    ✓ Title: {title}")
            except Exception as e:
                print(f"    ⚠ Could not extract title: {e}")
                data['information_title'] = None
                data['accurate_broadcast_title'] = None

            # Extract Broadcast URL
            try:
                broadcast_url = await page.evaluate("""
                    () => {
                        const linkEl = document.querySelector('a[class*="LiveIntroductionList_link_"]');
                        return linkEl ? linkEl.href : null;
                    }
                """)
                data['broadcast_url'] = broadcast_url
                print(f"    ✓ Broadcast URL: {broadcast_url}")
            except Exception as e:
                print(f"    ⚠ Could not extract broadcast URL: {e}")
                data['broadcast_url'] = None

            # Extract Brand Name
            try:
                brand_name = await page.evaluate("""
                    () => {
                        const brandEl = document.querySelector('strong[class*="IntroductionProfile_name_"]');
                        return brandEl ? brandEl.textContent.trim() : null;
                    }
                """)
                data['brand_name'] = brand_name
                print(f"    ✓ Brand: {brand_name}")
            except Exception as e:
                print(f"    ⚠ Could not extract brand name: {e}")
                data['brand_name'] = None

            # Extract Broadcast Date and Time
            try:
                broadcast_datetime = await page.evaluate("""
                    () => {
                        const stateEl = document.querySelector('div[class*="LiveIntroductionList_state_"]');
                        const timeEl = document.querySelector('[class*="LiveStatusTime_wrap_"]');

                        let dateTime = '';
                        if (stateEl) dateTime += stateEl.textContent.trim();
                        if (timeEl) dateTime += ' ' + timeEl.textContent.trim();

                        return dateTime.trim() || null;
                    }
                """)
                data['broadcast_datetime'] = broadcast_datetime
                print(f"    ✓ Date/Time: {broadcast_datetime}")
            except Exception as e:
                print(f"    ⚠ Could not extract date/time: {e}")
                data['broadcast_datetime'] = None

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
                print(f"    ✓ Coupons: {len(coupons) if coupons else 0} found")
            except Exception as e:
                print(f"    ⚠ Could not extract coupons: {e}")
                data['coupons'] = None

            # Extract Products
            try:
                products = await page.evaluate("""
                    () => {
                        const productEls = document.querySelectorAll('[class*="ProductList_item_"]');
                        const products = [];

                        productEls.forEach(el => {
                            const titleEl = el.querySelector('[class*="ProductListItem_title_"]');
                            const discountWrap = el.querySelector('[class*="DiscountPrice_wrap_"]');

                            const product = {};

                            if (titleEl) {
                                product.title = titleEl.textContent.trim();
                            }

                            if (discountWrap) {
                                const discountEl = discountWrap.querySelector('[class*="DiscountPrice_discount_"]');
                                const priceEl = discountWrap.querySelector('[class*="DiscountPrice_price_"]');

                                if (discountEl) {
                                    product.discount = discountEl.textContent.trim();
                                }
                                if (priceEl) {
                                    product.price = priceEl.textContent.trim();
                                }
                            }

                            if (Object.keys(product).length > 0) {
                                products.push(product);
                            }
                        });

                        return products.length > 0 ? products : null;
                    }
                """)
                data['products'] = products
                print(f"    ✓ Products: {len(products) if products else 0} found")
            except Exception as e:
                print(f"    ⚠ Could not extract products: {e}")
                data['products'] = None

            # Extract Live Introduction
            try:
                live_intro = await page.evaluate("""
                    () => {
                        const introEl = document.querySelector('a[class*="LiveIntroductionList_link_"]');
                        return introEl ? introEl.textContent.trim() : null;
                    }
                """)
                data['live_introduction'] = live_intro
                print(f"    ✓ Live Intro: {live_intro[:50] if live_intro else None}...")
            except Exception as e:
                print(f"    ⚠ Could not extract live introduction: {e}")
                data['live_introduction'] = None

            # Extract Benefits
            try:
                benefits = await page.evaluate("""
                    () => {
                        const benefitEls = document.querySelectorAll('[class*="BenefitFullBanner_title_"]');
                        const benefits = [];

                        benefitEls.forEach(el => {
                            const text = el.textContent.trim();
                            if (text) benefits.push(text);
                        });

                        return benefits.length > 0 ? benefits : null;
                    }
                """)
                data['benefits'] = benefits
                print(f"    ✓ Benefits: {len(benefits) if benefits else 0} found")
            except Exception as e:
                print(f"    ⚠ Could not extract benefits: {e}")
                data['benefits'] = None

            # Extract Live Chat Comments
            try:
                comments = await page.evaluate("""
                    () => {
                        const commentEls = document.querySelectorAll('[class*="CommentList_inner_"] [role="presentation"]');
                        const comments = [];

                        commentEls.forEach(el => {
                            const nicknameEl = el.querySelector('[class*="NormalComment_nickname_"]');
                            const commentEl = el.querySelector('[class*="NormalComment_comment_"]');

                            if (nicknameEl && commentEl) {
                                comments.push({
                                    nickname: nicknameEl.textContent.trim(),
                                    comment: commentEl.textContent.trim()
                                });
                            }
                        });

                        return comments.length > 0 ? comments : null;
                    }
                """)
                data['live_chat'] = comments
                print(f"    ✓ Chat Comments: {len(comments) if comments else 0} found")
            except Exception as e:
                print(f"    ⚠ Could not extract chat comments: {e}")
                data['live_chat'] = None

            # Extract FAQ
            try:
                faq = await page.evaluate("""
                    () => {
                        const qnaEls = document.querySelectorAll('[class*="LiveQnaList_wrap_"]');
                        const faqs = [];

                        qnaEls.forEach(el => {
                            const questionEl = el.querySelector('.question');
                            const answerEl = el.querySelector('.answer');

                            if (questionEl && answerEl) {
                                faqs.push({
                                    question: questionEl.textContent.trim(),
                                    answer: answerEl.textContent.trim()
                                });
                            }
                        });

                        return faqs.length > 0 ? faqs : null;
                    }
                """)
                data['faq'] = faq
                print(f"    ✓ FAQ: {len(faq) if faq else 0} found")
            except Exception as e:
                print(f"    ⚠ Could not extract FAQ: {e}")
                data['faq'] = None

            print(f"    ✅ Data extraction complete for clip #{clip_index + 1}")
            return data

        except Exception as e:
            print(f"    ❌ Error extracting clip data: {e}")
            return data

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
║      Naver Shopping Live Short Clips Crawler                     ║
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

    crawler = NaverShortClipsCrawler(max_clips=max_clips, headless=headless)
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
