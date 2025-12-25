#!/usr/bin/env python3
"""
Standalone Crawler for Scheduled Execution
------------------------------------------
This script crawls Naver Shopping Live events for a specific brand
and stores results in Supabase database.

Usage:
    python standalone_crawler.py --brand-id <uuid>
    python standalone_crawler.py --brand-name "Sulwhasoo"
    python standalone_crawler.py --brand-name "Sulwhasoo" --verbose

Design Reference:
    docs/ai/design/feature-scheduled-crawler.md
"""

import argparse
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, List

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db_client import get_db_client, SupabaseClient
from crawler_utils import (
    construct_search_url,
    validate_brand_platform,
    get_time_range_config,
    format_execution_summary
)

# Import existing crawlers
try:
    from naver_search_crawler import NaverSearchCrawler
except ImportError as e:
    print(f"⚠️ Warning: Could not import naver_search_crawler: {e}")
    NaverSearchCrawler = None

try:
    import asyncio
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    from crawlers.replays_crawler import ReplaysCrawler
    from crawlers.lives_crawler import LivesCrawler
    from utils.url_detector import URLDetector, URLType
    from persistence import BroadcastSaver
    BROADCAST_CRAWLER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Warning: Could not import broadcast crawlers: {e}")
    BROADCAST_CRAWLER_AVAILABLE = False
    ReplaysCrawler = None
    LivesCrawler = None
    URLDetector = None
    URLType = None
    BroadcastSaver = None


class StandaloneCrawler:
    """
    Standalone crawler that orchestrates the crawling process
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the standalone crawler

        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.db: SupabaseClient = get_db_client()
        self.execution_id: Optional[str] = None
        self.start_time: Optional[datetime] = None

    def log(self, message: str, force: bool = False):
        """Log message (respects verbose flag)"""
        if self.verbose or force:
            print(message)

    def load_brand_config(self, brand_id: Optional[str] = None, brand_name: Optional[str] = None) -> tuple[Dict, Dict, Dict]:
        """
        Load brand, platform, and crawler configuration from database

        Args:
            brand_id: Brand UUID (optional)
            brand_name: Brand name (optional)

        Returns:
            Tuple of (brand, platform, config)

        Raises:
            ValueError: If brand not found or configuration invalid
        """
        self.log("📦 Loading configuration from database...")

        # Load brand
        if brand_id:
            brand = self.db.get_brand_by_id(brand_id)
            if not brand:
                raise ValueError(f"Brand not found with ID: {brand_id}")
        elif brand_name:
            brand = self.db.get_brand_by_name(brand_name)
            if not brand:
                raise ValueError(f"Brand not found with name: {brand_name}")
        else:
            raise ValueError("Must provide either brand_id or brand_name")

        self.log(f"  ✅ Brand: {brand['name']} (ID: {brand['id']})")

        # Load platform
        platform = self.db.get_platform_by_id(brand['platform_id'])
        if not platform:
            raise ValueError(f"Platform not found with ID: {brand['platform_id']}")

        self.log(f"  ✅ Platform: {platform['name']} (ID: {platform['id']})")

        # Validate brand and platform
        is_valid, error_message = validate_brand_platform(brand, platform)
        if not is_valid:
            raise ValueError(f"Configuration validation failed: {error_message}")

        self.log(f"  ✅ Validation passed")

        # Load crawler config
        config = self.db.get_all_config()
        self.log(f"  ✅ Config loaded: {len(config)} entries")

        return brand, platform, config

    def create_execution_record(self, brand: Dict, platform: Dict, trigger_type: str = 'manual') -> str:
        """
        Create crawler execution record in database

        Args:
            brand: Brand dictionary
            platform: Platform dictionary
            trigger_type: 'scheduled' or 'manual'

        Returns:
            Execution ID
        """
        self.log(f"📝 Creating execution record (trigger: {trigger_type})...")

        execution = self.db.create_execution(
            brand_id=brand['id'],
            platform_id=platform['id'],
            trigger_type=trigger_type
        )

        self.execution_id = execution['id']
        self.log(f"  ✅ Execution created: {self.execution_id}", force=True)

        return self.execution_id

    def update_execution_status(self, status: str, items_found: int = 0, error_message: Optional[str] = None):
        """
        Update execution status in database

        Args:
            status: 'running', 'success', or 'failed'
            items_found: Number of events found
            error_message: Error message if failed
        """
        if not self.execution_id:
            self.log("⚠️ No execution ID, skipping status update")
            return

        self.db.update_execution_status(
            execution_id=self.execution_id,
            status=status,
            items_found=items_found,
            error_message=error_message
        )

        status_emoji = {'running': '⏳', 'success': '✅', 'failed': '❌'}.get(status, '❓')
        self.log(f"  {status_emoji} Execution status: {status.upper()}", force=True)

    def execute_search_crawler(self, search_url: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Execute the search crawler to find broadcasts

        Args:
            search_url: Constructed search URL
            limit: Maximum number of broadcasts to retrieve

        Returns:
            List of broadcast dictionaries
        """
        self.log(f"🔍 Executing search crawler...")
        self.log(f"  URL: {search_url}")
        self.log(f"  Limit: {limit} broadcasts")

        if not NaverSearchCrawler:
            self.log("  ❌ NaverSearchCrawler not available")
            return []

        try:
            # Create crawler instance
            crawler = NaverSearchCrawler(headless=True)

            # Execute crawl
            self.log("  ⏳ Crawling search results...")
            broadcasts = crawler.crawl_search_results(search_url, limit=limit)

            # Close crawler
            crawler.close_driver()

            self.log(f"  ✅ Found {len(broadcasts)} broadcasts", force=True)
            return broadcasts

        except Exception as e:
            self.log(f"  ❌ Search crawler failed: {e}")
            raise

    def execute_broadcast_crawler(self, broadcast_url: str) -> Optional[Dict[str, Any]]:
        """
        Execute the broadcast detail crawler

        Args:
            broadcast_url: Broadcast URL

        Returns:
            Broadcast detail dictionary or None
        """
        self.log(f"  🔍 Crawling broadcast: {broadcast_url}")

        if not BROADCAST_CRAWLER_AVAILABLE:
            self.log("    ⚠️ Broadcast crawler not available")
            return None

        try:
            # Detect URL type
            url_type = URLDetector.detect(broadcast_url)
            self.log(f"    URL type: {url_type.value}")

            # Create appropriate crawler
            if url_type == URLType.REPLAYS:
                crawler = ReplaysCrawler(headless=True)
            elif url_type == URLType.LIVES:
                crawler = LivesCrawler(headless=True)
            else:
                self.log(f"    ⚠️ Unsupported URL type: {url_type.value}")
                return None

            # Execute async crawl
            async def crawl_async():
                return await crawler.crawl(broadcast_url)

            result = asyncio.run(crawl_async())
            self.log(f"    ✅ Crawled broadcast successfully")

            return result

        except Exception as e:
            self.log(f"    ❌ Broadcast crawler failed: {e}")
            # Don't raise - continue with other broadcasts
            return None

    def store_broadcasts(self, broadcasts: List[Dict[str, Any]]) -> int:
        """
        Store broadcasts in database using BroadcastSaver

        Args:
            broadcasts: List of broadcast dictionaries (from broadcast crawler)

        Returns:
            Number of broadcasts stored successfully
        """
        if not broadcasts:
            self.log("  ℹ️ No broadcasts to store")
            return 0

        if not BroadcastSaver:
            self.log("  ❌ BroadcastSaver not available")
            return 0

        self.log(f"💾 Storing {len(broadcasts)} broadcasts...")

        saver = BroadcastSaver()
        successful = 0
        failed = 0

        for broadcast in broadcasts:
            try:
                # Use BroadcastSaver to save the complete broadcast data
                result = saver.save_from_dict(broadcast)

                if result['status'] == 'success':
                    successful += 1
                    broadcast_id = result.get('broadcast_id', 'unknown')
                    records = result.get('records_saved', {})

                    self.log(f"  ✅ Broadcast {broadcast_id}:", force=True)
                    self.log(f"     Products: {records.get('products', 0)}")
                    self.log(f"     Coupons: {records.get('coupons', 0)}")
                    self.log(f"     Benefits: {records.get('benefits', 0)}")
                    self.log(f"     Chat: {records.get('chat', 0)}")
                else:
                    failed += 1
                    error = result.get('error', 'Unknown error')
                    self.log(f"  ❌ Failed to save broadcast: {error}")

            except Exception as e:
                failed += 1
                self.log(f"  ❌ Error saving broadcast: {e}")
                import traceback
                if self.verbose:
                    traceback.print_exc()

        self.log(f"  📊 Summary: {successful} successful, {failed} failed", force=True)
        return successful

    def run(self, brand_id: Optional[str] = None, brand_name: Optional[str] = None, trigger_type: str = 'manual', limit: int = 50) -> int:
        """
        Main execution flow

        Args:
            brand_id: Brand UUID (optional)
            brand_name: Brand name (optional)
            trigger_type: 'scheduled' or 'manual'
            limit: Maximum number of broadcasts to crawl

        Returns:
            Number of events found (0 on failure)
        """
        self.start_time = datetime.now()

        print("=" * 70)
        print("🚀 Standalone Crawler - Starting Execution")
        print("=" * 70)

        try:
            # Step 1: Load configuration
            brand, platform, config = self.load_brand_config(brand_id, brand_name)

            # Step 2: Create execution record
            self.create_execution_record(brand, platform, trigger_type)

            # Step 3: Update status to running
            self.update_execution_status('running')

            # Step 4: Construct search URL
            search_url = construct_search_url(platform, brand)
            self.log(f"🔗 Search URL: {search_url}", force=True)

            # Step 5: Execute search crawler
            broadcasts = self.execute_search_crawler(search_url, limit=limit)
            self.log(f"📊 Found {len(broadcasts)} broadcasts")

            # Step 6: Execute broadcast detail crawler for each broadcast
            broadcast_details = []
            for broadcast in broadcasts:
                broadcast_url = broadcast.get('url')
                if broadcast_url:
                    detail = self.execute_broadcast_crawler(broadcast_url)
                    if detail:
                        broadcast_details.append(detail)

            # Step 7: Store broadcasts in database
            items_found = self.store_broadcasts(broadcast_details)

            # Step 8: Update execution status to success
            self.update_execution_status('success', items_found=items_found)

            # Step 9: Print summary
            end_time = datetime.now()
            summary = format_execution_summary(
                brand_name=brand['name'],
                items_found=items_found,
                start_time=self.start_time,
                end_time=end_time,
                status='success'
            )
            print("\n" + "=" * 70)
            print(summary)
            print("=" * 70)

            return items_found

        except Exception as e:
            # Handle errors
            error_message = str(e)
            self.log(f"❌ Error: {error_message}", force=True)

            # Update execution status to failed
            if self.execution_id:
                self.update_execution_status('failed', error_message=error_message)

            # Print summary
            if self.start_time:
                end_time = datetime.now()
                summary = format_execution_summary(
                    brand_name=brand.get('name', 'Unknown') if 'brand' in locals() else 'Unknown',
                    items_found=0,
                    start_time=self.start_time,
                    end_time=end_time,
                    status='failed'
                )
                print("\n" + "=" * 70)
                print(summary)
                print(f"   Error: {error_message}")
                print("=" * 70)

            # Re-raise for exit code
            raise


def main():
    """
    Main entry point for CLI
    """
    parser = argparse.ArgumentParser(
        description='Standalone crawler for Naver Shopping Live events',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python standalone_crawler.py --brand-id "uuid-here"
  python standalone_crawler.py --brand-name "Sulwhasoo"
  python standalone_crawler.py --brand-name "Innisfree" --verbose
  python standalone_crawler.py --brand-name "Sulwhasoo" --trigger scheduled

For GitHub Actions:
  python standalone_crawler.py --brand-name "$BRAND_NAME" --trigger scheduled
        """
    )

    parser.add_argument(
        '--brand-id',
        type=str,
        help='Brand UUID from database'
    )

    parser.add_argument(
        '--brand-name',
        type=str,
        help='Brand name (alternative to brand-id)'
    )

    parser.add_argument(
        '--trigger',
        type=str,
        choices=['manual', 'scheduled'],
        default='manual',
        help='Trigger type (default: manual)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of broadcasts to crawl (default: 50)'
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.brand_id and not args.brand_name:
        parser.error('Must provide either --brand-id or --brand-name')

    if args.brand_id and args.brand_name:
        parser.error('Cannot provide both --brand-id and --brand-name')

    # Run crawler
    try:
        crawler = StandaloneCrawler(verbose=args.verbose)
        items_found = crawler.run(
            brand_id=args.brand_id,
            brand_name=args.brand_name,
            trigger_type=args.trigger,
            limit=args.limit
        )

        # Exit with success
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ Crawler failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
