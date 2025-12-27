#!/usr/bin/env python3
"""
Quick test script for API-First approach implementation
Tests that search crawler can extract URLs quickly without timeouts
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from naver_search_crawler import NaverSearchCrawler
import time

def test_api_first_approach():
    """Test that search crawler works with API-First approach"""

    print("=" * 80)
    print("API-FIRST APPROACH TEST")
    print("=" * 80)
    print()

    # Test URL
    search_url = "https://shoppinglive.naver.com/search/lives?query=이니스프리"

    print(f"🔍 Testing search crawler with API-First approach")
    print(f"   URL: {search_url}")
    print(f"   Limit: 5 broadcasts")
    print()

    # Create crawler
    crawler = NaverSearchCrawler(headless=True)

    # Measure time
    start_time = time.time()

    try:
        # Execute crawl
        print("⏳ Starting search crawl...")
        broadcasts = crawler.crawl_search_results(search_url, limit=5)

        # Calculate duration
        duration = time.time() - start_time

        print()
        print("=" * 80)
        print("RESULTS")
        print("=" * 80)
        print()
        print(f"✅ Success! Found {len(broadcasts)} broadcasts")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print()

        # Analyze results
        if broadcasts:
            print("📊 Sample Results:")
            print("-" * 80)

            for idx, broadcast in enumerate(broadcasts, 1):
                print(f"\n[{idx}] {broadcast.get('external_id', 'N/A')}")
                print(f"    URL: {broadcast.get('url', 'N/A')}")
                print(f"    Type: {broadcast.get('event_type', 'N/A')}")
                print(f"    Title: {broadcast.get('title', 'None (expected - will be from API)')}")
                print(f"    Thumbnail: {broadcast.get('thumbnail', 'None (expected - will be from API)')}")
                print(f"    Status: {broadcast.get('status', 'None (expected - will be from API)')}")

            print()
            print("=" * 80)
            print("VALIDATION")
            print("=" * 80)
            print()

            # Validate API-First approach
            urls_ok = all(b.get('url') for b in broadcasts)
            types_ok = all(b.get('event_type') for b in broadcasts)
            titles_none = all(b.get('title') is None for b in broadcasts)

            print(f"✅ All URLs extracted: {urls_ok}")
            print(f"✅ All event types determined: {types_ok}")
            print(f"✅ All titles are None (as expected): {titles_none}")
            print()

            if duration < 60:
                print(f"✅ Duration < 60s: PASS ({duration:.2f}s)")
            else:
                print(f"⚠️  Duration >= 60s: SLOW ({duration:.2f}s)")

            print()

            if urls_ok and types_ok and titles_none and duration < 60:
                print("🎉 API-FIRST APPROACH TEST: PASSED!")
                print()
                print("Next step: Run full crawler to verify detail crawlers populate metadata")
                return True
            else:
                print("❌ API-FIRST APPROACH TEST: FAILED")
                return False
        else:
            print("⚠️  No broadcasts found - check search URL or selectors")
            return False

    except Exception as e:
        print()
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        crawler.close_driver()

if __name__ == "__main__":
    success = test_api_first_approach()
    sys.exit(0 if success else 1)
