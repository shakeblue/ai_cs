#!/usr/bin/env python3
"""
Command-line interface for the Livebridge Crawler
Extracts data from Naver Shopping Live livebridge pages and saves to Supabase

Usage:
    python run_livebridge_crawler.py <url> [--save-json] [--no-llm] [--no-supabase]

Examples:
    # Save to Supabase only (default)
    python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510

    # Save to both Supabase and JSON file
    python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --save-json

    # Skip Supabase, only save JSON
    python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --save-json --no-supabase

    # Skip LLM extraction (faster but less complete)
    python run_livebridge_crawler.py https://shoppinglive.naver.com/livebridge/1776510 --no-llm
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from crawlers.livebridge_crawler import LivebridgeCrawler
from vision_extractor import VisionProvider


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Crawl Naver Shopping Live livebridge pages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    # Required arguments
    parser.add_argument('url', type=str, help='Livebridge URL to crawl')

    # Optional arguments
    parser.add_argument(
        '--save-json',
        action='store_true',
        help='Save JSON output file in addition to Supabase (default: False)'
    )

    parser.add_argument(
        '--no-llm',
        action='store_true',
        help='Disable LLM image extraction (faster but less complete)'
    )

    parser.add_argument(
        '--no-supabase',
        action='store_true',
        help='Disable Supabase storage (only save JSON if --save-json is specified)'
    )

    parser.add_argument(
        '--vision-provider',
        type=str,
        choices=['gpt-4o-mini', 'claude-haiku', 'gemini-flash'],
        default='gpt-4o-mini',
        help='Vision LLM provider to use (default: gpt-4o-mini)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Directory to save JSON output (default: output)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Validate URL
    if not args.url.startswith('https://shoppinglive.naver.com/livebridge/'):
        logger.error("Invalid livebridge URL. Must start with: https://shoppinglive.naver.com/livebridge/")
        sys.exit(1)

    # Map provider string to enum
    provider_map = {
        'gpt-4o-mini': VisionProvider.GPT_4O_MINI,
        'claude-haiku': VisionProvider.CLAUDE_HAIKU,
        'gemini-flash': VisionProvider.GEMINI_FLASH
    }
    vision_provider = provider_map[args.vision_provider]

    # Initialize crawler
    logger.info("="*70)
    logger.info("Livebridge Crawler - Phase 2 (Supabase Integration)")
    logger.info("="*70)
    logger.info(f"URL: {args.url}")
    logger.info(f"Save JSON: {args.save_json}")
    logger.info(f"Use LLM: {not args.no_llm}")
    logger.info(f"Use Supabase: {not args.no_supabase}")
    if not args.no_llm:
        logger.info(f"Vision Provider: {args.vision_provider}")
    logger.info("="*70)

    try:
        crawler = LivebridgeCrawler(
            use_llm=not args.no_llm,
            vision_provider=vision_provider,
            use_supabase=not args.no_supabase
        )

        # Crawl the livebridge page
        result = await crawler.crawl(args.url)

        logger.info("\n" + "="*70)
        logger.info("CRAWL RESULT SUMMARY")
        logger.info("="*70)
        logger.info(f"Title: {result.get('title')}")
        logger.info(f"Brand: {result.get('brand_name')}")
        logger.info(f"Live Date: {result.get('live_datetime')}")
        logger.info(f"Special Coupons: {len(result.get('special_coupons', []))}")
        logger.info(f"Products: {len(result.get('products', []))}")
        logger.info(f"Live Benefits: {len(result.get('live_benefits', []))}")
        logger.info(f"Benefits by Amount: {len(result.get('benefits_by_amount', []))}")
        logger.info(f"Simple Coupons: {len(result.get('coupons', []))}")
        logger.info("="*70)

        # Save to Supabase (default)
        livebridge_id = None
        if not args.no_supabase:
            logger.info("\nSaving to Supabase...")
            livebridge_id = crawler.save_to_supabase(result)
            if livebridge_id:
                logger.info(f"✓ Saved to Supabase with ID: {livebridge_id}")
            else:
                logger.error("✗ Failed to save to Supabase")

        # Save to JSON (optional)
        if args.save_json:
            output_dir = Path(__file__).parent / args.output_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            # Use livebridge_id for filename if available, otherwise extract from URL
            if livebridge_id:
                filename = f"livebridge_{livebridge_id}_optimized.json"
            else:
                url_id = args.url.split('/')[-1]
                filename = f"livebridge_{url_id}_optimized.json"

            output_file = output_dir / filename

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            logger.info(f"✓ JSON saved to: {output_file}")

        logger.info("\n" + "="*70)
        logger.info("CRAWL COMPLETED SUCCESSFULLY")
        logger.info("="*70)

    except KeyboardInterrupt:
        logger.info("\n\nCrawl interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"\n\nCrawl failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
