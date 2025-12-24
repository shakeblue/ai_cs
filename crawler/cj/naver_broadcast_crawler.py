#!/usr/bin/env python3
"""
Naver Shopping Live Broadcast Crawler
Main entry point for crawling Naver Shopping Live broadcasts

Usage:
    python naver_broadcast_crawler.py <URL> [--headful] [--output-dir OUTPUT_DIR] [--save-to-db]

Example:
    python naver_broadcast_crawler.py https://view.shoppinglive.naver.com/replays/1776510
    python naver_broadcast_crawler.py https://view.shoppinglive.naver.com/lives/1810235?tr=lim --headful
    python naver_broadcast_crawler.py https://view.shoppinglive.naver.com/shortclips/9797637?tr=sclim --output-dir ./my_output
    python naver_broadcast_crawler.py https://view.shoppinglive.naver.com/replays/1776510 --save-to-db
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from crawlers.replays_crawler import ReplaysCrawler
from crawlers.lives_crawler import LivesCrawler
from crawlers.shortclips_crawler import ShortClipsCrawler
from utils.url_detector import URLDetector, URLType
from utils.output_writer import OutputWriter

# Import persistence layer (optional - only if saving to DB)
try:
    from persistence import BroadcastSaver
    PERSISTENCE_AVAILABLE = True
except ImportError:
    PERSISTENCE_AVAILABLE = False
    BroadcastSaver = None


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class CrawlerFactory:
    """Factory for creating appropriate crawler based on URL type"""

    @staticmethod
    def create_crawler(url: str, headless: bool = True):
        """
        Create crawler instance based on URL type

        Args:
            url: The URL to crawl
            headless: Whether to run browser in headless mode

        Returns:
            Appropriate crawler instance

        Raises:
            ValueError: If URL type is invalid
        """
        url_type = URLDetector.detect(url)

        if url_type == URLType.REPLAYS:
            return ReplaysCrawler(headless=headless)
        elif url_type == URLType.LIVES:
            return LivesCrawler(headless=headless)
        elif url_type == URLType.SHORTCLIPS:
            return ShortClipsCrawler(headless=headless)
        else:
            raise ValueError(f"Unknown URL type: {url_type}")


async def main():
    """Main entry point"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Crawl Naver Shopping Live broadcasts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://view.shoppinglive.naver.com/replays/1776510
  %(prog)s https://view.shoppinglive.naver.com/lives/1810235?tr=lim --headful
  %(prog)s https://view.shoppinglive.naver.com/shortclips/9797637?tr=sclim --output-dir ./output
        """
    )

    parser.add_argument(
        'url',
        help='Naver Shopping Live URL to crawl (replays, lives, or shortclips)'
    )

    parser.add_argument(
        '--headful',
        action='store_true',
        help='Run browser in headful mode (default: headless)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory for JSON files (default: output)'
    )

    parser.add_argument(
        '--save-to-db',
        action='store_true',
        help='Save crawled data to Supabase database (requires .env configuration)'
    )

    parser.add_argument(
        '--db-only',
        action='store_true',
        help='Save to database only, skip JSON file output'
    )

    args = parser.parse_args()

    # Validate URL and extract ID
    try:
        url_type = URLDetector.detect(args.url)
        broadcast_id = URLDetector.extract_id(args.url)

        if not broadcast_id:
            logger.error("Could not extract broadcast ID from URL")
            return 1

        logger.info(f"Detected URL type: {url_type.value}")
        logger.info(f"Broadcast ID: {broadcast_id}")

    except ValueError as e:
        logger.error(f"Invalid URL: {e}")
        return 2

    # Create crawler
    try:
        crawler = CrawlerFactory.create_crawler(args.url, headless=not args.headful)
    except ValueError as e:
        logger.error(f"Failed to create crawler: {e}")
        return 2

    # Perform crawl
    try:
        result = await crawler.crawl(args.url)
    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        return 1

    # Write output to JSON file (unless --db-only)
    output_file = None
    if not args.db_only:
        try:
            output_dir = Path(__file__).parent / args.output_dir
            writer = OutputWriter(output_dir)

            # Validate output
            if not writer.validate_output(result):
                logger.warning("Output validation failed, but continuing to write file")

            output_file = writer.write(result, broadcast_id)
            logger.info(f"✓ Output file: {output_file}")

        except Exception as e:
            logger.error(f"Failed to write output: {e}")
            if not args.save_to_db:
                # If not saving to DB, this is a fatal error
                return 1
            # Otherwise, continue to try DB save

    # Save to database if requested
    db_result = None
    if args.save_to_db or args.db_only:
        if not PERSISTENCE_AVAILABLE:
            logger.error("✗ Persistence layer not available. Please install dependencies.")
            logger.error("  Run: pip install -r requirements.txt")
            return 1

        try:
            logger.info("Saving to database...")
            saver = BroadcastSaver()

            # Save from the result dictionary directly
            db_result = saver.save_from_dict(result)

            if db_result['status'] == 'success':
                logger.info(f"✓ Database save successful!")
                logger.info(f"  Broadcast ID: {db_result['broadcast_id']}")
                logger.info(f"  Products: {db_result['records_saved']['products']}")
                logger.info(f"  Coupons: {db_result['records_saved']['coupons']}")
                logger.info(f"  Benefits: {db_result['records_saved']['benefits']}")
                logger.info(f"  Chat messages: {db_result['records_saved']['chat']}")
                logger.info(f"  Duration: {db_result['duration_seconds']}s")
            else:
                error_msg = db_result.get('error', 'Unknown error')
                error_type = db_result.get('error_type', 'Error')
                logger.error(f"✗ Database save failed ({error_type}): {error_msg}")

                if 'validation_errors' in db_result:
                    logger.error("  Validation errors:")
                    for key, errors in db_result['validation_errors'].items():
                        logger.error(f"    {key}: {errors}")

                # Check if it's a "table not found" error
                if 'broadcasts' in error_msg and ('does not exist' in error_msg or 'PGRST205' in error_msg):
                    logger.error("")
                    logger.error("  ⚠ HINT: Database tables not created!")
                    logger.error("  Run the database schema script in Supabase SQL Editor:")
                    logger.error("  File: /home/long/ai_cs/crawler/cj/database_schema.sql")
                    logger.error("  See: INTEGRATION_GUIDE.md for instructions")
                    logger.error("")

                # Don't fail completely if file was saved successfully
                if not output_file:
                    return 1

        except Exception as e:
            logger.error(f"✗ Database save failed with exception: {e}")
            import traceback
            traceback.print_exc()

            # Don't fail completely if file was saved successfully
            if not output_file:
                return 1

    # Summary
    logger.info("="*60)
    logger.info("Crawl completed successfully!")
    if output_file:
        logger.info(f"  JSON file: {output_file}")
    if db_result and db_result['status'] == 'success':
        logger.info(f"  Database: Saved broadcast {db_result['broadcast_id']}")
    logger.info("="*60)

    return 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Crawl interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
