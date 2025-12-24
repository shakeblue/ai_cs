#!/usr/bin/env python3
"""
Advanced Naver Crawler with Multiple Anti-Detection Strategies
Bypasses rate limiting through multiple approaches
"""

import requests
import os
import time
import random
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class AdvancedNaverCrawler:
    """Advanced crawler with anti-detection measures"""

    def __init__(self, output_dir='naver_images', strategy='aggressive'):
        self.output_dir = output_dir
        self.strategy = strategy  # 'gentle', 'moderate', 'aggressive'
        self.session = None
        self._init_session()

        # Strategy-based delays (min, max) in seconds
        self.delay_strategies = {
            'gentle': (3, 7),      # Very slow, most human-like
            'moderate': (2, 4),    # Balanced
            'aggressive': (1, 2)   # Faster, but still safe
        }

    def _init_session(self):
        """Initialize session with advanced anti-detection"""
        self.session = requests.Session()

        # Realistic browser headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        })

    def _human_delay(self, action="action"):
        """Random delay based on strategy"""
        min_delay, max_delay = self.delay_strategies[self.strategy]
        delay = random.uniform(min_delay, max_delay)
        print(f"    ⏱ Human delay ({action}): {delay:.1f}s")
        time.sleep(delay)

    def _rotate_user_agent(self):
        """Rotate user agent to avoid detection"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]
        self.session.headers['User-Agent'] = random.choice(user_agents)

    def fetch_page_with_retry(self, url: str, max_retries=5) -> Optional[str]:
        """Fetch page with exponential backoff and retry logic"""

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    # Exponential backoff
                    backoff = (2 ** attempt) * random.uniform(1, 3)
                    print(f"\n🔄 Retry {attempt + 1}/{max_retries}")
                    print(f"    ⏱ Backoff delay: {backoff:.1f}s")
                    time.sleep(backoff)
                    # Rotate user agent on retry
                    self._rotate_user_agent()
                    # Reinitialize session
                    self._init_session()

                print(f"\n📄 Fetching page...")
                print(f"    URL: {url}")

                # Initial delay before request
                if attempt == 0:
                    self._human_delay("initial request")

                # Make request with cookies and referer
                response = self.session.get(
                    url,
                    timeout=30,
                    allow_redirects=True,
                    verify=False,
                    headers={
                        'Referer': 'https://brand.naver.com/'
                    }
                )

                # Check response
                if response.status_code == 200:
                    print(f"    ✓ Success! Status: {response.status_code}")
                    print(f"    ✓ Content size: {len(response.content):,} bytes")
                    return response.text

                elif response.status_code == 429:
                    print(f"    ⚠ Rate limit detected (429)")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        print(f"    ✗ Max retries exceeded")
                        return None

                elif response.status_code == 403:
                    print(f"    ⚠ Forbidden (403) - Detection possible")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return None

                else:
                    print(f"    ⚠ Unexpected status: {response.status_code}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return None

            except requests.exceptions.Timeout:
                print(f"    ⚠ Request timeout")
                if attempt < max_retries - 1:
                    continue
                return None

            except requests.exceptions.RequestException as e:
                print(f"    ⚠ Request error: {e}")
                if attempt < max_retries - 1:
                    continue
                return None

        return None

    def extract_images(self, html: str, target_class='se-main-container') -> List[str]:
        """Extract image URLs from HTML"""
        try:
            print(f"\n🔍 Extracting images from class: {target_class}")

            soup = BeautifulSoup(html, 'html.parser')

            # Find target div
            target_divs = soup.find_all('div', class_=lambda c: c and target_class in c)

            if not target_divs:
                print(f"    ⚠ Target div not found, searching entire page")
                target_divs = [soup]
            else:
                print(f"    ✓ Found {len(target_divs)} target div(s)")

            image_urls = []

            for div in target_divs:
                imgs = div.find_all('img')
                print(f"    ✓ Found {len(imgs)} image tags")

                for img in imgs:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')

                    if src:
                        # Skip small images
                        if any(skip in src.lower() for skip in ['icon', 'logo', 'btn', 'arrow', 'blank']):
                            continue

                        # Make absolute URL
                        if not src.startswith('http'):
                            src = urljoin('https://brand.naver.com/', src)

                        # Check valid image
                        if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '?type=w']):
                            if src not in image_urls:
                                image_urls.append(src)

            print(f"    ✓ Extracted {len(image_urls)} unique image URLs")
            return image_urls

        except Exception as e:
            print(f"    ✗ Error extracting images: {e}")
            return []

    def download_images(self, image_urls: List[str], brand_name='brand') -> List[str]:
        """Download images with anti-detection measures"""
        Path(self.output_dir).mkdir(exist_ok=True)

        print(f"\n{'='*70}")
        print(f"Downloading {len(image_urls)} images")
        print(f"Strategy: {self.strategy.upper()}")
        print(f"{'='*70}\n")

        downloaded = []

        for idx, url in enumerate(image_urls, 1):
            try:
                # Human delay between downloads
                if idx > 1:
                    self._human_delay(f"image {idx}")

                # Occasionally rotate user agent
                if idx % 3 == 0:
                    self._rotate_user_agent()
                    print(f"    🔄 Rotated user agent")

                print(f"[{idx}/{len(image_urls)}] Downloading...")
                print(f"    URL: {url[:80]}...")

                response = self.session.get(
                    url,
                    timeout=30,
                    verify=False,
                    headers={
                        'Referer': 'https://brand.naver.com/'
                    }
                )
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

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"    ⚠ Rate limit on image download!")
                    print(f"    💡 Increasing delay...")
                    time.sleep(random.uniform(5, 10))
                else:
                    print(f"    ✗ HTTP error: {e}")

            except Exception as e:
                print(f"    ✗ Download failed: {e}")

        print(f"\n✓ Downloaded {len(downloaded)}/{len(image_urls)} images\n")
        return downloaded

    def crawl(self, url: str, target_class='se-main-container') -> Dict:
        """Main crawling function"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║          Advanced Naver Crawler (Anti-Detection)                 ║
╚══════════════════════════════════════════════════════════════════╝

URL: {url}
Target Class: {target_class}
Strategy: {self.strategy.upper()}
        """)

        # Extract brand name from URL
        brand_name = 'brand'
        if '/brand.naver.com/' in url:
            parts = url.split('/')
            if len(parts) > 3:
                brand_name = parts[3]

        print(f"Brand: {brand_name}\n")

        # Fetch page
        html = self.fetch_page_with_retry(url)
        if not html:
            return {
                'success': False,
                'error': 'Failed to fetch page after retries',
                'downloaded_images': []
            }

        # Extract images
        image_urls = self.extract_images(html, target_class)
        if not image_urls:
            return {
                'success': False,
                'error': 'No images found',
                'downloaded_images': []
            }

        # Download images
        downloaded = self.download_images(image_urls, brand_name)

        return {
            'success': True,
            'brand_name': brand_name,
            'url': url,
            'image_urls': image_urls,
            'downloaded_images': downloaded,
            'count': len(downloaded)
        }


def main():
    """Test the crawler"""
    import sys

    # Test URL
    url = 'https://brand.naver.com/iope/shoppingstory/detail?id=5002337684'

    # You can change strategy: 'gentle', 'moderate', 'aggressive'
    strategy = sys.argv[1] if len(sys.argv) > 1 else 'moderate'

    print(f"\nUsing strategy: {strategy}")
    print(f"Available strategies: gentle (slow), moderate (balanced), aggressive (fast)\n")

    crawler = AdvancedNaverCrawler(strategy=strategy)
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
