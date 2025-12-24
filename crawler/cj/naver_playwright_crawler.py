#!/usr/bin/env python3
"""
Naver Playwright Crawler with Stealth Mode
Uses Playwright with anti-detection to bypass rate limiting
"""

import asyncio
import os
import time
import random
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright, Page
from playwright_stealth import Stealth
import requests


class NaverPlaywrightCrawler:
    """Playwright-based crawler with stealth mode"""

    def __init__(self, output_dir='naver_playwright_images', headless=True, strategy='moderate'):
        self.output_dir = output_dir
        self.headless = headless
        self.strategy = strategy

        # Strategy-based delays
        self.delay_strategies = {
            'gentle': (3, 7),      # Very slow, most human-like
            'moderate': (2, 4),    # Balanced
            'aggressive': (1, 2)   # Faster
        }

    def _human_delay(self, action="action"):
        """Human-like delay"""
        min_delay, max_delay = self.delay_strategies[self.strategy]
        delay = random.uniform(min_delay, max_delay)
        print(f"    ⏱ Human delay ({action}): {delay:.1f}s")
        time.sleep(delay)

    async def _scroll_page_slowly(self, page: Page):
        """Scroll page with human-like behavior"""
        print("    🖱 Scrolling page like human...")

        # Get page height
        page_height = await page.evaluate("document.body.scrollHeight")

        # Scroll in random chunks
        current_position = 0
        while current_position < page_height:
            # Random scroll amount
            scroll_amount = random.randint(300, 600)
            current_position += scroll_amount

            await page.evaluate(f"window.scrollTo(0, {current_position})")
            await asyncio.sleep(random.uniform(0.5, 1.2))

            # Sometimes scroll back a bit (human behavior)
            if random.random() < 0.2:
                back_scroll = random.randint(50, 150)
                current_position -= back_scroll
                await page.evaluate(f"window.scrollTo(0, {current_position})")
                await asyncio.sleep(random.uniform(0.3, 0.6))

            # Update page height (for dynamic content)
            page_height = await page.evaluate("document.body.scrollHeight")

        # Scroll to top
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)
        print("    ✓ Scrolling complete")

    async def _random_mouse_movements(self, page: Page):
        """Make random mouse movements to mimic human"""
        print("    🖱 Simulating mouse movements...")

        for _ in range(random.randint(2, 4)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.2, 0.5))

        print("    ✓ Mouse movements complete")

    async def _extract_images(self, page: Page, target_class='se-main-container') -> List[str]:
        """Extract image URLs from page"""
        print(f"\n🔍 Extracting images from class: {target_class}")

        try:
            # Wait for target div or timeout
            try:
                await page.wait_for_selector(f".{target_class}", timeout=10000)
                print(f"    ✓ Found target div: {target_class}")
            except:
                print(f"    ⚠ Target div not found, using entire page")

            # Scroll to trigger lazy loading
            await self._scroll_page_slowly(page)

            # Wait for images to load
            await asyncio.sleep(2)

            # Extract all image URLs
            image_urls = await page.evaluate("""
                (targetClass) => {
                    const images = [];
                    const targetDiv = document.querySelector('.' + targetClass) || document.body;
                    const imgElements = targetDiv.querySelectorAll('img');

                    imgElements.forEach(img => {
                        const src = img.src || img.getAttribute('data-src') || img.getAttribute('data-lazy-src');

                        if (src && src.startsWith('http')) {
                            // Skip small images
                            if (src.toLowerCase().includes('icon') ||
                                src.toLowerCase().includes('logo') ||
                                src.toLowerCase().includes('btn') ||
                                src.toLowerCase().includes('arrow') ||
                                src.toLowerCase().includes('blank')) {
                                return;
                            }

                            // Check if valid image
                            if (src.includes('.jpg') || src.includes('.jpeg') ||
                                src.includes('.png') || src.includes('.webp') ||
                                src.includes('.gif') || src.includes('?type=w')) {
                                images.push(src);
                            }
                        }
                    });

                    // Remove duplicates
                    return [...new Set(images)];
                }
            """, target_class)

            print(f"    ✓ Extracted {len(image_urls)} unique image URLs")
            return image_urls

        except Exception as e:
            print(f"    ✗ Error extracting images: {e}")
            return []

    def _download_images(self, image_urls: List[str], brand_name='brand') -> List[str]:
        """Download images using requests"""
        Path(self.output_dir).mkdir(exist_ok=True)

        print(f"\n{'='*70}")
        print(f"Downloading {len(image_urls)} images")
        print(f"{'='*70}\n")

        downloaded = []
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://brand.naver.com/'
        })

        for idx, url in enumerate(image_urls, 1):
            try:
                # Human delay
                if idx > 1:
                    self._human_delay(f"image {idx}")

                print(f"[{idx}/{len(image_urls)}] Downloading...")
                print(f"    URL: {url[:80]}...")

                response = session.get(url, timeout=30, verify=False)
                response.raise_for_status()

                # Determine extension
                ext = '.jpg'
                content_type = response.headers.get('Content-Type', '')
                if 'png' in content_type:
                    ext = '.png'
                elif 'webp' in content_type:
                    ext = '.webp'
                elif 'gif' in content_type:
                    ext = '.gif'

                filename = f"{self.output_dir}/{brand_name}_{idx:03d}{ext}"

                with open(filename, 'wb') as f:
                    f.write(response.content)

                size_kb = len(response.content) / 1024
                downloaded.append(filename)
                print(f"    ✓ Saved: {filename} ({size_kb:.1f} KB)")

            except Exception as e:
                print(f"    ✗ Download failed: {e}")

        print(f"\n✓ Downloaded {len(downloaded)}/{len(image_urls)} images\n")
        return downloaded

    async def crawl(self, url: str, target_class='se-main-container') -> Dict:
        """Main crawling function"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║        Playwright Stealth Crawler (Advanced Anti-Detection)      ║
╚══════════════════════════════════════════════════════════════════╝

URL: {url}
Target Class: {target_class}
Strategy: {self.strategy.upper()}
Headless: {self.headless}
        """)

        # Extract brand name
        brand_name = 'brand'
        if '/brand.naver.com/' in url:
            parts = url.split('/')
            if len(parts) > 3:
                brand_name = parts[3]

        print(f"Brand: {brand_name}\n")

        async with async_playwright() as p:
            try:
                # Launch browser with stealth mode
                print("🚀 Launching browser with stealth mode...")

                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process'
                    ]
                )

                # Create context with realistic settings
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='ko-KR',
                    timezone_id='Asia/Seoul',
                    ignore_https_errors=True,
                    extra_http_headers={
                        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    }
                )

                page = await context.new_page()

                # Apply stealth mode
                stealth = Stealth()
                await stealth.apply_stealth_async(page)

                print("    ✓ Browser launched with stealth mode")

                # Navigate to page
                print(f"\n📄 Navigating to page...")
                await page.goto(url, wait_until='networkidle', timeout=60000)
                print(f"    ✓ Page loaded")

                # Human-like delay
                self._human_delay("after page load")

                # Random mouse movements
                await self._random_mouse_movements(page)

                # Extract images
                image_urls = await self._extract_images(page, target_class)

                # Close browser
                await browser.close()

                if not image_urls:
                    return {
                        'success': False,
                        'error': 'No images found',
                        'downloaded_images': []
                    }

                # Download images
                downloaded = self._download_images(image_urls, brand_name)

                return {
                    'success': True,
                    'brand_name': brand_name,
                    'url': url,
                    'image_urls': image_urls,
                    'downloaded_images': downloaded,
                    'count': len(downloaded)
                }

            except Exception as e:
                print(f"\n✗ Crawling failed: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'downloaded_images': []
                }


async def main():
    """Test the crawler"""
    import sys

    # Test URL
    url = 'https://brand.naver.com/iope/shoppingstory/detail?id=5002337684'

    # Strategy: gentle, moderate, aggressive
    strategy = sys.argv[1] if len(sys.argv) > 1 else 'moderate'
    headless = '--visible' not in sys.argv

    print(f"\nStrategy: {strategy}")
    print(f"Headless: {headless}")
    print(f"Available strategies: gentle (slow), moderate (balanced), aggressive (fast)\n")

    crawler = NaverPlaywrightCrawler(strategy=strategy, headless=headless)
    result = await crawler.crawl(url)

    if result['success']:
        print(f"\n✅ Success!")
        print(f"   Downloaded: {result['count']} images")
        print(f"   Location: {crawler.output_dir}/")
    else:
        print(f"\n❌ Failed: {result['error']}")


if __name__ == '__main__':
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Run async main
    asyncio.run(main())
