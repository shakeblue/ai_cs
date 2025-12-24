#!/usr/bin/env python3
"""
Naver Brand Selenium Crawler
Uses real browser to bypass bot detection and mimic human behavior
"""

import os
import time
import random
from pathlib import Path
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests


class NaverSeleniumCrawler:
    """Selenium-based crawler that mimics human behavior"""

    def __init__(self, output_dir='naver_selenium_images', headless=True):
        self.output_dir = output_dir
        self.headless = headless
        self.driver = None

    def _setup_driver(self):
        """Setup Chrome driver with human-like settings"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless=new')

        # Anti-detection settings
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # Realistic browser settings
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')

        # User agent
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        try:
            # Try webdriver-manager first (auto-downloads driver)
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✓ Chrome driver initialized with webdriver-manager")
            except:
                # Fallback to system ChromeDriver
                self.driver = webdriver.Chrome(options=chrome_options)
                print("✓ Chrome driver initialized from system")

            # Additional anti-detection
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        except Exception as e:
            print(f"✗ Failed to initialize Chrome driver: {e}")
            print("\nInstall ChromeDriver:")
            print("  macOS: brew install chromedriver")
            print("  Ubuntu: sudo apt-get install chromium-chromedriver")
            print("  Or: pip install webdriver-manager (auto-install)")
            raise

    def _human_delay(self, min_sec=1, max_sec=3, action="action"):
        """Simulate human-like delay"""
        delay = random.uniform(min_sec, max_sec)
        print(f"    ⏱ Human delay ({action}): {delay:.1f}s")
        time.sleep(delay)

    def _scroll_slowly(self):
        """Mimic human scrolling behavior"""
        print("    🖱 Scrolling page like human...")

        # Get page height
        total_height = self.driver.execute_script("return document.body.scrollHeight")

        # Scroll in chunks
        current_position = 0
        chunk_size = random.randint(300, 500)

        while current_position < total_height:
            # Random scroll chunk
            scroll_amount = random.randint(chunk_size - 100, chunk_size + 100)
            current_position += scroll_amount

            self.driver.execute_script(f"window.scrollTo(0, {current_position});")

            # Random pause like human
            time.sleep(random.uniform(0.3, 0.8))

            # Sometimes scroll back a bit (human behavior)
            if random.random() < 0.2:
                back_scroll = random.randint(50, 150)
                current_position -= back_scroll
                self.driver.execute_script(f"window.scrollTo(0, {current_position});")
                time.sleep(random.uniform(0.2, 0.5))

        # Scroll to top
        self.driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        print("    ✓ Scrolling complete")

    def _extract_images_with_lazy_load(self, target_class='se-main-container'):
        """Extract images while triggering lazy loading"""
        print(f"\n🔍 Extracting images from div class='{target_class}'")

        try:
            # Wait for page to load
            wait = WebDriverWait(self.driver, 10)

            # Find target div
            try:
                target_div = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, target_class))
                )
                print(f"    ✓ Found target div: {target_class}")
            except TimeoutException:
                print(f"    ⚠ Target div '{target_class}' not found, using entire page")
                target_div = self.driver.find_element(By.TAG_NAME, 'body')

            # Scroll to trigger lazy loading
            self._scroll_slowly()
            self._human_delay(2, 4, "waiting for lazy load")

            # Find all images
            img_elements = target_div.find_elements(By.TAG_NAME, 'img')
            print(f"    ✓ Found {len(img_elements)} image elements")

            # Extract image URLs
            image_urls = []
            for img in img_elements:
                src = img.get_attribute('src') or img.get_attribute('data-src')

                if src and src.startswith('http'):
                    # Skip small icons
                    if any(skip in src.lower() for skip in ['icon', 'logo', 'btn', 'arrow', 'blank']):
                        continue

                    # Check if it's a valid image
                    if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '?type=w']):
                        if src not in image_urls:
                            image_urls.append(src)

            print(f"    ✓ Extracted {len(image_urls)} unique image URLs")
            return image_urls

        except Exception as e:
            print(f"    ✗ Error extracting images: {e}")
            return []

    def _download_images(self, image_urls: List[str], brand_name='brand') -> List[str]:
        """Download images using requests (faster than Selenium)"""
        Path(self.output_dir).mkdir(exist_ok=True)

        print(f"\n{'='*70}")
        print(f"Downloading {len(image_urls)} images")
        print(f"{'='*70}\n")

        downloaded = []
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://brand.naver.com/'
        })

        for idx, url in enumerate(image_urls, 1):
            try:
                print(f"[{idx}/{len(image_urls)}] Downloading...")
                print(f"    URL: {url[:80]}...")

                # Human-like delay between downloads
                if idx > 1:
                    time.sleep(random.uniform(1, 2))

                response = session.get(url, timeout=30, verify=False)
                response.raise_for_status()

                # Determine extension
                ext = '.jpg'
                content_type = response.headers.get('Content-Type', '')
                if 'png' in content_type:
                    ext = '.png'
                elif 'webp' in content_type:
                    ext = '.webp'

                filename = f"{self.output_dir}/{brand_name}_{idx:03d}{ext}"

                with open(filename, 'wb') as f:
                    f.write(response.content)

                size_kb = len(response.content) / 1024
                downloaded.append(filename)
                print(f"    ✓ Saved: {filename} ({size_kb:.1f} KB)")

            except Exception as e:
                print(f"    ✗ Failed: {e}")

        print(f"\n✓ Downloaded {len(downloaded)}/{len(image_urls)} images\n")
        return downloaded

    def crawl(self, url: str, target_class='se-main-container') -> Dict:
        """Main crawling function"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║          Naver Selenium Crawler (Human-like Behavior)            ║
╚══════════════════════════════════════════════════════════════════╝

URL: {url}
Target Div: {target_class}
Mode: {'Headless' if self.headless else 'Visible Browser'}
        """)

        try:
            # Setup driver
            self._setup_driver()

            # Visit page with human delay
            print(f"\n📄 Opening page...")
            self.driver.get(url)
            self._human_delay(3, 5, "initial page load")

            # Extract brand info from URL
            brand_name = 'brand'
            if '/brand.naver.com/' in url:
                parts = url.split('/')
                if len(parts) > 3:
                    brand_name = parts[3]

            print(f"    ✓ Brand: {brand_name}")

            # Extract images with lazy loading
            image_urls = self._extract_images_with_lazy_load(target_class)

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
                'page_info': {'brand_name': brand_name, 'url': url},
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

        finally:
            # Close browser
            if self.driver:
                print("\n🔒 Closing browser...")
                self.driver.quit()

    def crawl_with_screenshots(self, url: str, target_class='se-main-container',
                               save_screenshot=True) -> Dict:
        """Crawl and optionally save screenshot for debugging"""
        result = self.crawl(url, target_class)

        if save_screenshot and self.driver:
            try:
                screenshot_path = f"{self.output_dir}/page_screenshot.png"
                self.driver.save_screenshot(screenshot_path)
                print(f"    📸 Screenshot saved: {screenshot_path}")
                result['screenshot'] = screenshot_path
            except:
                pass

        return result


def main():
    """Test the Selenium crawler"""
    url = 'https://brand.naver.com/iope/shoppingstory/detail?id=5002337684'

    # Run crawler
    crawler = NaverSeleniumCrawler(headless=True)
    result = crawler.crawl(url)

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

    main()
