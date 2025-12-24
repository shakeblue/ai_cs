#!/usr/bin/env python3
"""
Test script for livebridge crawler with LLM extraction
"""

import asyncio
import logging
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from crawlers.livebridge_crawler import LivebridgeCrawler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Test the livebridge crawler"""

    # Test URL
    test_url = 'https://shoppinglive.naver.com/livebridge/1776510'

    print("="*70)
    print("LIVEBRIDGE CRAWLER TEST")
    print("="*70)
    print(f"URL: {test_url}")
    print(f"OpenAI API Key: {'✓ Set' if os.getenv('OPENAI_API_KEY') else '✗ Not set'}")
    print("="*70)
    print()

    # Create crawler with LLM enabled
    crawler = LivebridgeCrawler(use_llm=True)

    try:
        # Run crawl
        result = await crawler.crawl(test_url)

        # Print summary
        print("\n" + "="*70)
        print("CRAWL RESULT SUMMARY")
        print("="*70)
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Brand: {result['brand_name']}")
        print(f"Live Date/Time: {result['live_datetime']}")
        print()
        print("Extracted Data:")
        print(f"  - Special Coupons: {len(result['special_coupons'])}")
        print(f"  - Normal Coupons: {len(result['coupons'])}")
        print(f"  - Live Benefits: {len(result['live_benefits'])}")
        print(f"  - Benefits by Amount: {len(result['benefits_by_amount'])}")
        print(f"  - Products: {len(result['products'])}")
        print("="*70)

        # Save to JSON
        output_dir = Path(__file__).parent / 'output'
        output_dir.mkdir(exist_ok=True)

        # Extract broadcast ID from URL
        broadcast_id = result['url'].split('/')[-1]
        output_file = output_dir / f"livebridge_{broadcast_id}_optimized.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✓ Output saved to: {output_file}")

        # Print sample extracted content
        if result['special_coupons']:
            print("\nSample Special Coupons:")
            for coupon in result['special_coupons'][:2]:
                print(f"  - {json.dumps(coupon, ensure_ascii=False, indent=4)}")

        if result['coupons']:
            print("\nSample Normal Coupons:")
            for coupon in result['coupons'][:2]:
                print(f"  - {json.dumps(coupon, ensure_ascii=False, indent=4)}")

        if result['products']:
            print("\nSample Products:")
            for product in result['products'][:2]:
                print(f"  - {json.dumps(product, ensure_ascii=False, indent=4)}")

        print("\n✓ Test completed successfully!")
        return 0

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
