#!/usr/bin/env python3
"""
Vision-Based Naver Event Pipeline
1. Downloads images using Playwright (bypasses Naver rate limits)
2. Extracts event data DIRECTLY from images using Vision LLMs (NO OCR step)
3. Saves to Supabase database

This pipeline is simpler and potentially more accurate than the OCR-based approach.
"""

import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

# Import components
from naver_playwright_crawler import NaverPlaywrightCrawler
from vision_extractor import VisionExtractor, VisionProvider

# Optional Supabase import
try:
    from save_to_supabase import SupabaseSaver
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠ Supabase integration not available - will save to JSON only")


class VisionPipeline:
    """Vision-based pipeline for Naver event extraction (bypasses OCR)"""

    def __init__(self,
                 vision_provider: VisionProvider = VisionProvider.GPT_4O_MINI,
                 crawler_strategy='moderate'):
        """
        Initialize vision pipeline

        Args:
            vision_provider: Vision LLM provider (Claude/GPT/Gemini)
            crawler_strategy: Crawler strategy (gentle, moderate, aggressive)
        """
        self.vision_provider = vision_provider
        self.crawler_strategy = crawler_strategy

        # Initialize components (lazy loading)
        self.crawler = None
        self.vision_extractor = None
        self.db_saver = None

    async def process_event_url(self, url: str, output_dir: str = 'vision_event_images') -> Dict:
        """
        Process a single event URL through the vision pipeline

        Args:
            url: Naver brand event URL
            output_dir: Directory to save downloaded images

        Returns:
            Dictionary with success status and results
        """
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║            Naver Event Pipeline - Vision-Based (NEW)             ║
║                                                                  ║
║  Step 1: Download images (Playwright - bypasses rate limits)    ║
║  Step 2: Extract data directly from images (Vision LLM)         ║
║  Step 3: Save to Supabase database                              ║
║                                                                  ║
║  ⚡ NO OCR STEP - Simpler & More Accurate                       ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        try:
            # Step 1: Download images with Playwright
            print(f"\n{'='*70}")
            print("STEP 1: Downloading Images with Playwright")
            print(f"{'='*70}\n")

            self.crawler = NaverPlaywrightCrawler(
                output_dir=output_dir,
                strategy=self.crawler_strategy,
                headless=True
            )

            crawl_result = await self.crawler.crawl(url)

            if not crawl_result['success']:
                return {
                    'success': False,
                    'step': 'download',
                    'error': f"Image download failed: {crawl_result['error']}"
                }

            image_paths = crawl_result['downloaded_images']
            brand_name = crawl_result.get('brand_name', 'unknown')

            print(f"\n✓ Downloaded {len(image_paths)} images")
            for img_path in image_paths:
                print(f"  - {img_path}")

            # Step 2: Extract data directly from images using Vision LLM
            print(f"\n{'='*70}")
            print("STEP 2: Vision-Based Extraction (Direct from Images)")
            print(f"{'='*70}\n")

            self.vision_extractor = VisionExtractor(provider=self.vision_provider)

            # Estimate cost
            cost_estimate = self.vision_extractor.estimate_cost(len(image_paths))
            print(f"💰 Estimated cost: ${cost_estimate['total_cost']:.6f}")
            print(f"   Provider: {cost_estimate['provider']}")
            print(f"   Images: {cost_estimate['num_images']} images (${cost_estimate['image_cost']:.6f})")
            print(f"   Text tokens: ${cost_estimate['text_cost']:.6f}")
            print()

            # Extract event information
            event_info = self.vision_extractor.extract_from_images(image_paths, url)

            if not event_info:
                return {
                    'success': False,
                    'step': 'vision_extraction',
                    'error': 'Vision extraction failed - no data returned'
                }

            # Add metadata
            event_info['url'] = url
            event_info['brand_name'] = brand_name
            event_info['extraction_method'] = 'vision_llm'
            event_info['vision_provider'] = self.vision_provider.value

            print("\n✓ Extraction successful:")
            print(json.dumps(event_info, ensure_ascii=False, indent=2))

            # Step 3: Save to database
            print(f"\n{'='*70}")
            print("STEP 3: Saving to Database")
            print(f"{'='*70}\n")

            # Save to local JSON first
            json_output = f"{output_dir}/vision_event_data_{brand_name}.json"
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(event_info, f, ensure_ascii=False, indent=2)
            print(f"✓ Saved to local JSON: {json_output}")

            # Save to Supabase if available
            if SUPABASE_AVAILABLE:
                try:
                    self.db_saver = SupabaseSaver()
                    save_result = self.db_saver.save_event(event_info)

                    if save_result['success']:
                        print(f"✓ Saved to Supabase")
                        if 'record_id' in save_result:
                            print(f"  Record ID: {save_result['record_id']}")
                    else:
                        print(f"⚠ Supabase save failed: {save_result.get('error', 'Unknown error')}")
                except Exception as e:
                    print(f"⚠ Supabase save error: {e}")
            else:
                print("ℹ Supabase not available - skipped database save")

            return {
                'success': True,
                'event_info': event_info,
                'image_count': len(image_paths),
                'cost': cost_estimate['total_cost'],
                'json_file': json_output
            }

        except KeyboardInterrupt:
            print("\n\n⚠️  Pipeline interrupted by user")
            raise
        except Exception as e:
            print(f"\n❌ Pipeline error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'step': 'unknown',
                'error': str(e)
            }


async def main():
    """Main function for testing"""
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description='Run vision-based Naver event pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using GPT-4o Mini (recommended):
  python vision_pipeline.py "https://brand.naver.com/iope/..." --provider gpt

  # Using Claude Haiku (higher accuracy):
  python vision_pipeline.py "https://brand.naver.com/iope/..." --provider claude

  # Using Gemini Flash (fastest):
  python vision_pipeline.py "https://brand.naver.com/iope/..." --provider gemini
        """
    )

    parser.add_argument('url', help='Naver brand event URL')
    parser.add_argument(
        '--provider',
        choices=['claude', 'gpt', 'gemini'],
        default='gpt',
        help='Vision LLM provider (default: gpt)'
    )
    parser.add_argument(
        '--crawler',
        choices=['gentle', 'moderate', 'aggressive'],
        default='moderate',
        help='Crawler strategy (default: moderate)'
    )
    parser.add_argument(
        '--output',
        default='vision_event_images',
        help='Output directory (default: vision_event_images)'
    )

    args = parser.parse_args()

    # Map provider to enum
    provider_map = {
        'claude': VisionProvider.CLAUDE_HAIKU,
        'gpt': VisionProvider.GPT_4O_MINI,
        'gemini': VisionProvider.GEMINI_FLASH,
    }
    vision_provider = provider_map[args.provider]

    # Display configuration
    print(f"""
Configuration:
  URL:              {args.url}
  Vision Provider:  {args.provider} ({vision_provider.value})
  Crawler:          {args.crawler}
  Output:           {args.output}
    """)

    # Check API key
    api_key_map = {
        VisionProvider.CLAUDE_HAIKU: 'ANTHROPIC_API_KEY',
        VisionProvider.GPT_4O_MINI: 'OPENAI_API_KEY',
        VisionProvider.GEMINI_FLASH: 'GOOGLE_API_KEY',
    }
    required_key = api_key_map[vision_provider]

    if not os.getenv(required_key):
        print(f"❌ Error: {required_key} not found in environment")
        print(f"   Please set it in .env file")
        return 1

    # Run pipeline
    pipeline = VisionPipeline(
        vision_provider=vision_provider,
        crawler_strategy=args.crawler
    )

    result = await pipeline.process_event_url(args.url, args.output)

    if result['success']:
        print("\n🎉 Vision pipeline completed successfully!")
        print(f"   Cost: ${result['cost']:.6f}")
        print(f"   Images processed: {result['image_count']}")
        return 0
    else:
        print(f"\n💥 Vision pipeline failed at step: {result.get('step', 'unknown')}")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == '__main__':
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Run pipeline
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
