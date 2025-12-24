#!/usr/bin/env python3
"""
Naver Brand Page Image Crawler
Downloads images from a specific div class on Naver Brand pages
"""

import requests
import os
import re
import time
import random
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict


class NaverBrandImageCrawler:
    """Crawler for Naver Brand page images"""

    def __init__(self, output_dir='naver_brand_images', delay_min=2, delay_max=5):
        self.output_dir = output_dir
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.session = requests.Session()

        # Rotate user agents to avoid detection
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        ]

        self._update_headers()

    def _update_headers(self):
        """Update session headers with random user agent"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Referer': 'https://brand.naver.com/',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })

    def _delay(self, message="Rate limiting delay"):
        """Add random delay to avoid rate limiting"""
        delay = random.uniform(self.delay_min, self.delay_max)
        print(f"    ⏱ {message}: {delay:.1f}초 대기 중...")
        time.sleep(delay)

    def extract_page_info(self, url: str) -> Dict[str, str]:
        """Extract brand name and page ID from URL"""
        info = {
            'url': url,
            'brand_name': None,
            'page_id': None
        }

        # Parse URL: https://brand.naver.com/iope/shoppingstory/detail?id=5002337684&page=1
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.split('/')
            if len(path_parts) >= 2:
                info['brand_name'] = path_parts[1]

            # Extract ID from query string
            query_params = dict(param.split('=') for param in parsed.query.split('&') if '=' in param)
            info['page_id'] = query_params.get('id')

        except Exception as e:
            print(f"    ⚠ URL 파싱 실패: {e}")

        return info

    def fetch_page(self, url: str, max_retries=3) -> str:
        """Fetch HTML content from URL with retry logic"""

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"\n🔄 재시도 {attempt + 1}/{max_retries}")
                    # Exponential backoff
                    backoff_delay = (2 ** attempt) * random.uniform(1, 3)
                    print(f"    ⏱ 백오프 대기: {backoff_delay:.1f}초")
                    time.sleep(backoff_delay)
                    # Rotate user agent
                    self._update_headers()

                print(f"\n📄 페이지 가져오는 중: {url}")

                # Add initial delay before first request
                if attempt == 0:
                    self._delay("초기 요청 전 대기")

                response = self.session.get(url, timeout=30, verify=False)
                response.raise_for_status()

                print(f"    ✓ 상태 코드: {response.status_code}")
                print(f"    ✓ 콘텐츠 크기: {len(response.content)} bytes")

                return response.text

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"    ⚠ 요청 제한 감지 (429) - 재시도 대기 중...")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        print(f"    ✗ 최대 재시도 횟수 초과")
                        return None
                else:
                    print(f"    ✗ HTTP 오류: {e}")
                    return None
            except Exception as e:
                print(f"    ✗ 페이지 가져오기 실패: {e}")
                if attempt < max_retries - 1:
                    continue
                return None

        return None

    def extract_images_from_div(self, html: str, target_class: str = 'se-main-container') -> List[str]:
        """Extract image URLs from specific div class"""
        try:
            print(f"\n🔍 이미지 추출 중 (div class='{target_class}')")

            soup = BeautifulSoup(html, 'html.parser')

            # Find the target div
            target_divs = soup.find_all('div', class_=lambda c: c and target_class in c)

            if not target_divs:
                print(f"    ⚠ '{target_class}' 클래스를 가진 div를 찾을 수 없습니다")
                # Fallback: try to find all images on the page
                print("    → 페이지의 모든 이미지 검색으로 전환")
                target_divs = [soup]
            else:
                print(f"    ✓ {len(target_divs)}개의 대상 div 발견")

            image_urls = []

            for div in target_divs:
                # Find all img tags
                imgs = div.find_all('img')
                print(f"    ✓ div에서 {len(imgs)}개의 이미지 태그 발견")

                for img in imgs:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')

                    if src:
                        # Skip small images (icons, placeholders, etc.)
                        if any(skip in src.lower() for skip in ['icon', 'logo', 'btn', 'arrow', 'blank']):
                            continue

                        # Convert relative URLs to absolute
                        if not src.startswith('http'):
                            src = urljoin('https://brand.naver.com/', src)

                        # Check if it's a valid image URL
                        if any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '?type=w']):
                            if src not in image_urls:
                                image_urls.append(src)

            print(f"    ✓ 총 {len(image_urls)}개의 고유 이미지 URL 추출")

            return image_urls

        except Exception as e:
            print(f"    ✗ 이미지 추출 실패: {e}")
            return []

    def download_images(self, image_urls: List[str], brand_name: str = 'brand') -> List[str]:
        """Download images from URLs with rate limiting"""
        Path(self.output_dir).mkdir(exist_ok=True)

        print(f"\n{'='*70}")
        print(f"이미지 다운로드 시작 ({len(image_urls)}개)")
        print(f"{'='*70}\n")

        downloaded = []

        for idx, url in enumerate(image_urls, 1):
            try:
                # Add delay between downloads to avoid rate limiting
                if idx > 1:
                    self._delay(f"이미지 {idx} 다운로드 전 대기")

                print(f"[{idx}/{len(image_urls)}] 다운로드 중...")
                print(f"    URL: {url[:80]}...")

                response = self.session.get(url, timeout=30, verify=False)
                response.raise_for_status()

                # Determine file extension
                ext = '.jpg'
                content_type = response.headers.get('Content-Type', '')
                if 'png' in content_type:
                    ext = '.png'
                elif 'webp' in content_type:
                    ext = '.webp'
                elif 'gif' in content_type:
                    ext = '.gif'

                # Generate filename
                filename = f"{self.output_dir}/{brand_name}_{idx:03d}{ext}"

                with open(filename, 'wb') as f:
                    f.write(response.content)

                size_kb = len(response.content) / 1024
                downloaded.append(filename)
                print(f"    ✓ 저장: {filename} ({size_kb:.1f} KB)")

            except Exception as e:
                print(f"    ✗ 다운로드 실패: {e}")

        print(f"\n{'='*70}")
        print(f"✓ 다운로드 완료: {len(downloaded)}/{len(image_urls)}개")
        print(f"{'='*70}\n")

        return downloaded

    def crawl(self, url: str, target_class: str = 'se-main-container') -> Dict:
        """Main crawling function"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║          Naver Brand 이미지 크롤러                                 ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        # Extract page info
        page_info = self.extract_page_info(url)
        brand_name = page_info['brand_name'] or 'brand'

        print(f"브랜드: {brand_name}")
        print(f"페이지 ID: {page_info['page_id']}")
        print(f"대상 div 클래스: {target_class}")

        # Fetch page
        html = self.fetch_page(url)
        if not html:
            return {
                'success': False,
                'error': 'Failed to fetch page',
                'downloaded_images': []
            }

        # Extract image URLs
        image_urls = self.extract_images_from_div(html, target_class)
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
            'page_info': page_info,
            'image_urls': image_urls,
            'downloaded_images': downloaded,
            'count': len(downloaded)
        }


def main():
    """Main function for testing"""
    # Test URL
    url = 'https://brand.naver.com/iope/shoppingstory/detail?id=5002337684&page=1'
    target_class = 'se-main-container'

    crawler = NaverBrandImageCrawler()
    result = crawler.crawl(url, target_class)

    if result['success']:
        print(f"\n✅ 크롤링 성공!")
        print(f"   이미지 개수: {result['count']}")
        print(f"   저장 위치: {crawler.output_dir}/")
    else:
        print(f"\n❌ 크롤링 실패: {result['error']}")


if __name__ == '__main__':
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
