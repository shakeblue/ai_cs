#!/usr/bin/env python3
"""
Crawl multiple broadcasts and save to database

This script combines crawling and database saving in one operation.
It can read URLs from a file or accept them as command-line arguments.

Usage:
    python scripts/crawl_and_save.py <URL1> <URL2> ...
    python scripts/crawl_and_save.py --urls-file urls.txt
    python scripts/crawl_and_save.py --urls-file urls.txt --headful
"""

import sys
import argparse
import asyncio
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from naver_broadcast_crawler import CrawlerFactory
from utils.url_detector import URLDetector
from persistence import BroadcastSaver


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


async def crawl_and_save_url(url: str, headless: bool, saver: BroadcastSaver) -> dict:
    """
    Crawl a single URL and save to database

    Args:
        url: Broadcast URL
        headless: Run browser in headless mode
        saver: BroadcastSaver instance

    Returns:
        Dict with result status
    """
    logger = logging.getLogger(__name__)

    try:
        # Detect URL type and extract ID
        url_type = URLDetector.detect(url)
        broadcast_id = URLDetector.extract_id(url)

        logger.info(f"\n{'='*60}")
        logger.info(f"Crawling: {url}")
        logger.info(f"Type: {url_type.value}, ID: {broadcast_id}")
        logger.info('='*60)

        # Create crawler
        crawler = CrawlerFactory.create_crawler(url, headless=headless)

        # Crawl
        logger.info("Starting crawl...")
        crawler_data = await crawler.crawl(url)

        logger.info("✓ Crawl completed")

        # Save to database
        logger.info("Saving to database...")
        db_result = saver.save_from_dict(crawler_data)

        if db_result['status'] == 'success':
            logger.info(f"✓ Database save successful!")
            logger.info(f"  Products: {db_result['records_saved']['products']}")
            logger.info(f"  Coupons: {db_result['records_saved']['coupons']}")
            logger.info(f"  Benefits: {db_result['records_saved']['benefits']}")
            logger.info(f"  Chat: {db_result['records_saved']['chat']}")
            logger.info(f"  Duration: {db_result['duration_seconds']}s")

            return {
                'status': 'success',
                'url': url,
                'broadcast_id': broadcast_id,
                'db_result': db_result
            }
        else:
            logger.error(f"✗ Database save failed: {db_result.get('error')}")
            return {
                'status': 'error',
                'url': url,
                'broadcast_id': broadcast_id,
                'error': db_result.get('error')
            }

    except Exception as e:
        logger.error(f"✗ Failed to crawl {url}: {e}")
        import traceback
        traceback.print_exc()

        return {
            'status': 'error',
            'url': url,
            'error': str(e)
        }


async def crawl_and_save_multiple(urls: list, headless: bool = True) -> dict:
    """
    Crawl multiple URLs and save to database

    Args:
        urls: List of URLs to crawl
        headless: Run browser in headless mode

    Returns:
        Dict with batch statistics
    """
    logger = logging.getLogger(__name__)

    # Initialize saver once for all operations
    saver = BroadcastSaver()

    # Test connection first
    logger.info("Testing database connection...")
    if not saver.test_connection():
        logger.error("✗ Database connection failed!")
        return {
            'total': len(urls),
            'successful': 0,
            'failed': len(urls),
            'results': []
        }

    logger.info("✓ Database connection successful\n")

    # Crawl each URL sequentially (to avoid overwhelming the server)
    results = []
    successful = 0
    failed = 0

    for i, url in enumerate(urls, 1):
        logger.info(f"Progress: {i}/{len(urls)}")

        result = await crawl_and_save_url(url, headless, saver)
        results.append(result)

        if result['status'] == 'success':
            successful += 1
        else:
            failed += 1

        # Small delay between requests to be respectful
        if i < len(urls):
            await asyncio.sleep(2)

    return {
        'total': len(urls),
        'successful': successful,
        'failed': failed,
        'results': results
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Crawl multiple Naver Shopping Live broadcasts and save to database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Crawl multiple URLs
  python scripts/crawl_and_save.py \\
      https://view.shoppinglive.naver.com/replays/1776510 \\
      https://view.shoppinglive.naver.com/lives/1810235

  # Crawl URLs from file
  python scripts/crawl_and_save.py --urls-file urls.txt

  # With headful browser
  python scripts/crawl_and_save.py --urls-file urls.txt --headful

URL file format (one URL per line):
  https://view.shoppinglive.naver.com/replays/1776510
  https://view.shoppinglive.naver.com/lives/1810235
  https://view.shoppinglive.naver.com/shortclips/9797637
        """
    )

    parser.add_argument(
        'urls',
        nargs='*',
        help='URLs to crawl'
    )

    parser.add_argument(
        '--urls-file',
        type=str,
        help='File containing URLs (one per line)'
    )

    parser.add_argument(
        '--headful',
        action='store_true',
        help='Run browser in headful mode (default: headless)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Collect URLs
    urls = []

    # From command line arguments
    if args.urls:
        urls.extend(args.urls)

    # From file
    if args.urls_file:
        urls_file = Path(args.urls_file)

        if not urls_file.exists():
            logger.error(f"✗ URLs file not found: {urls_file}")
            return 1

        with open(urls_file, 'r') as f:
            file_urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            urls.extend(file_urls)

    # Validate we have URLs
    if not urls:
        parser.print_help()
        print("\nError: No URLs provided. Use URLs as arguments or --urls-file")
        return 1

    logger.info(f"Found {len(urls)} URLs to crawl")

    # Run crawler
    try:
        result = asyncio.run(crawl_and_save_multiple(urls, headless=not args.headful))

        # Display summary
        print("\n" + "="*60)
        print("CRAWL AND SAVE SUMMARY")
        print("="*60)
        print(f"Total URLs: {result['total']}")
        print(f"✓ Successful: {result['successful']}")
        print(f"✗ Failed: {result['failed']}")

        if result['successful'] > 0:
            success_rate = (result['successful'] / result['total']) * 100
            print(f"\nSuccess rate: {success_rate:.1f}%")

        print("\nDetails:")
        for res in result['results']:
            if res['status'] == 'success':
                print(f"  ✓ Broadcast {res['broadcast_id']}")
            else:
                broadcast_id = res.get('broadcast_id', 'unknown')
                error = res.get('error', 'Unknown error')
                print(f"  ✗ Broadcast {broadcast_id}: {error}")

        print("="*60)

        # Return exit code
        if result['failed'] == 0:
            return 0
        elif result['successful'] > 0:
            return 2  # Partial success
        else:
            return 1  # Complete failure

    except KeyboardInterrupt:
        logger.info("\nCrawl interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"\n✗ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
