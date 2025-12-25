#!/usr/bin/env python3
"""
Naver Shopping Live Search Crawler
Crawls search results page and extracts broadcast URLs

Usage:
    python naver_search_crawler.py <search_url> [--limit LIMIT] [--json]

Example:
    python naver_search_crawler.py "https://shoppinglive.naver.com/search/lives?query=설화수"
    python naver_search_crawler.py "https://shoppinglive.naver.com/search/lives?query=설화수" --limit 10 --json
"""

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class NaverSearchCrawler:
    """Crawler for Naver Shopping Live search results"""

    def __init__(self, headless=True):
        """Initialize crawler"""
        self.headless = headless
        self.driver = None

    def setup_driver(self):
        """Setup Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')

        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)

    def close_driver(self):
        """Close WebDriver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

    def crawl_search_results(self, search_url, limit=50):
        """
        Crawl search results page and extract broadcast information

        Args:
            search_url: Search URL to crawl
            limit: Maximum number of broadcasts to extract

        Returns:
            List of broadcast dictionaries
        """
        broadcasts = []

        try:
            self.setup_driver()
            logger.info(f"Accessing search URL: {search_url}")

            # Navigate to search page
            self.driver.get(search_url)
            time.sleep(3)  # Wait for initial load

            # Scroll to load more results
            self.scroll_to_load_more(max_scrolls=5)

            # Extract broadcast cards
            broadcasts = self.extract_broadcasts(limit=limit)

            logger.info(f"Found {len(broadcasts)} broadcasts")

        except Exception as e:
            logger.error(f"Error crawling search results: {e}")
            raise

        finally:
            self.close_driver()

        return broadcasts

    def scroll_to_load_more(self, max_scrolls=5):
        """Scroll page to load more results"""
        for i in range(max_scrolls):
            # Scroll to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)

            # Check if "더보기" (Load More) button exists and click it
            try:
                load_more_button = self.driver.find_element(By.CSS_SELECTOR, ".more_button, .load_more, button[class*='more']")
                if load_more_button.is_displayed():
                    load_more_button.click()
                    time.sleep(2)
                    logger.info("Clicked load more button")
            except NoSuchElementException:
                pass  # No load more button

    def extract_broadcasts(self, limit=50):
        """
        Extract broadcast information from search results

        Returns:
            List of broadcast dictionaries
        """
        broadcasts = []

        try:
            # Find all broadcast cards (various possible selectors)
            card_selectors = [
                ".live_card",
                ".ProductLive_live_card__",
                "[class*='live_card']",
                "[class*='LiveCard']",
                ".live-card",
                "a[href*='/lives/']",
                "a[href*='/replays/']",
                "a[href*='/shortclips/']",
            ]

            cards = []
            for selector in card_selectors:
                try:
                    found_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found_cards:
                        cards = found_cards
                        logger.info(f"Found {len(cards)} cards using selector: {selector}")
                        break
                except:
                    continue

            if not cards:
                logger.warning("No broadcast cards found")
                return []

            # Extract information from each card
            for idx, card in enumerate(cards[:limit]):
                try:
                    broadcast = self.extract_broadcast_info(card, idx)
                    if broadcast:
                        broadcasts.append(broadcast)
                except Exception as e:
                    logger.warning(f"Failed to extract card {idx}: {e}")
                    continue

        except Exception as e:
            logger.error(f"Error extracting broadcasts: {e}")

        return broadcasts

    def extract_broadcast_info(self, card, index):
        """Extract information from a single broadcast card"""
        try:
            # Extract URL (required)
            url = self.extract_url(card)
            if not url:
                return None

            # Extract external ID from URL
            external_id = self.extract_external_id_from_url(url)

            # Extract title
            title = self.extract_title(card)

            # Extract thumbnail
            thumbnail = self.extract_thumbnail(card)

            # Determine event type from URL
            event_type = self.determine_event_type(url)

            # Extract status (live, replay, upcoming)
            status = self.extract_status(card)

            # Extract date information if available
            date_info = self.extract_date_info(card)

            broadcast = {
                'external_id': external_id,
                'url': url,
                'title': title,
                'thumbnail': thumbnail,
                'event_type': event_type,
                'status': status,
                'start_date': date_info.get('start_date'),
                'extracted_at': datetime.now().isoformat(),
                'index': index,
            }

            return broadcast

        except Exception as e:
            logger.warning(f"Failed to extract broadcast info: {e}")
            return None

    def extract_url(self, card):
        """Extract URL from card"""
        try:
            # Try to find link element
            link = card.find_element(By.CSS_SELECTOR, "a")
            url = link.get_attribute("href")
            if url and ('lives' in url or 'replays' in url or 'shortclips' in url or 'livebridge' in url):
                return url
        except:
            pass

        # If card itself is a link
        try:
            url = card.get_attribute("href")
            if url and ('lives' in url or 'replays' in url or 'shortclips' in url or 'livebridge' in url):
                return url
        except:
            pass

        return None

    def extract_external_id_from_url(self, url):
        """Extract external ID from URL"""
        if not url:
            return None

        # Extract ID from URL patterns:
        # /lives/12345 -> 12345
        # /replays/67890 -> 67890
        # /shortclips/11111 -> 11111
        # /livebridge/22222 -> 22222
        import re
        match = re.search(r'/(lives|replays|shortclips|livebridge)/(\d+)', url)
        if match:
            type_prefix = match.group(1)
            id_num = match.group(2)
            return f"{type_prefix}_{id_num}"

        return None

    def extract_title(self, card):
        """Extract title from card"""
        title_selectors = [
            ".live_title",
            ".ProductLive_live_title__",
            "[class*='live_title']",
            "[class*='title']",
            "h3",
            "h2",
        ]

        for selector in title_selectors:
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, selector)
                title = title_elem.text.strip()
                if title:
                    return title
            except:
                continue

        return "Untitled"

    def extract_thumbnail(self, card):
        """Extract thumbnail URL from card"""
        try:
            img = card.find_element(By.CSS_SELECTOR, "img")
            return img.get_attribute("src")
        except:
            return None

    def determine_event_type(self, url):
        """Determine event type from URL"""
        if '/lives/' in url:
            return 'live'
        elif '/replays/' in url:
            return 'replay'
        elif '/shortclips/' in url:
            return 'shortclip'
        elif '/livebridge/' in url:
            return 'livebridge'
        return None

    def extract_status(self, card):
        """Extract broadcast status (live, upcoming, ended)"""
        try:
            # Look for status badge
            badge_selectors = [".badge", ".live_badge", "[class*='badge']", ".status"]

            for selector in badge_selectors:
                try:
                    badge = card.find_element(By.CSS_SELECTOR, selector)
                    badge_text = badge.text.upper()

                    if "LIVE" in badge_text or "라이브" in badge_text:
                        return "ongoing"
                    elif "예정" in badge_text or "UPCOMING" in badge_text:
                        return "upcoming"
                    elif "종료" in badge_text or "ENDED" in badge_text:
                        return "ended"
                except:
                    continue

        except:
            pass

        # Default: if it's a replay, mark as ended
        return None

    def extract_date_info(self, card):
        """Extract date information from card"""
        date_info = {
            'start_date': None,
        }

        try:
            # Look for date elements
            date_selectors = [".date", ".time", "[class*='date']", "[class*='time']"]

            for selector in date_selectors:
                try:
                    date_elem = card.find_element(By.CSS_SELECTOR, selector)
                    date_text = date_elem.text.strip()

                    if date_text:
                        # Try to parse date (format: "2025-12-25 15:00" or similar)
                        # For now, store as string; parsing can be done later
                        date_info['start_date'] = date_text
                        break
                except:
                    continue

        except:
            pass

        return date_info


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Crawl Naver Shopping Live search results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('search_url', type=str, help='Search URL to crawl')
    parser.add_argument('--limit', type=int, default=50, help='Maximum number of broadcasts to extract (default: 50)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    parser.add_argument('--headful', action='store_true', help='Run browser in headful mode (with GUI)')

    args = parser.parse_args()

    # Create crawler
    crawler = NaverSearchCrawler(headless=not args.headful)

    try:
        # Crawl search results
        broadcasts = crawler.crawl_search_results(args.search_url, limit=args.limit)

        # Output results
        if args.json:
            # Output as JSON for programmatic consumption
            output = {
                'success': True,
                'count': len(broadcasts),
                'broadcasts': broadcasts,
                'search_url': args.search_url,
                'crawled_at': datetime.now().isoformat(),
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            # Human-readable output
            print(f"\n✅ Found {len(broadcasts)} broadcasts from search results")
            print("=" * 80)
            for idx, broadcast in enumerate(broadcasts, 1):
                print(f"\n[{idx}] {broadcast['title']}")
                print(f"    Type: {broadcast['event_type']} | Status: {broadcast['status']}")
                print(f"    URL: {broadcast['url']}")

    except Exception as e:
        logger.error(f"Crawler failed: {e}")
        if args.json:
            output = {
                'success': False,
                'error': str(e),
                'search_url': args.search_url,
            }
            print(json.dumps(output, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
