#!/usr/bin/env python3
"""
Complete Naver Event Pipeline - Integrated Version
1. Downloads images using Playwright (bypasses Naver rate limits)
2. Extracts text using OCR.space API
3. Parses event information (with configurable strategy)
4. Saves to Supabase database
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
from naver_event_ocr_extractor import NaverEventOCRExtractor
from extraction_strategy import ExtractionStrategy
from llm_extractor import LLMProvider

# Optional Supabase import
try:
    from save_to_supabase import SupabaseSaver
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠ Supabase integration not available - will save to JSON only")


class NaverEventPipelineIntegrated:
    """Complete integrated pipeline for Naver event extraction"""

    def __init__(self, ocr_api_key: str = "K87899142388957",
                 crawler_strategy='moderate',
                 extraction_strategy: ExtractionStrategy = ExtractionStrategy.AUTO,
                 llm_provider: LLMProvider = None):
        """
        Initialize pipeline

        Args:
            ocr_api_key: OCR.space API key
            crawler_strategy: Crawler strategy (gentle, moderate, aggressive)
            extraction_strategy: Extraction strategy (pattern, semantic, llm, hybrid, auto)
            llm_provider: LLM provider if using LLM strategy
        """
        self.crawler_strategy = crawler_strategy
        self.extraction_strategy = extraction_strategy
        self.llm_provider = llm_provider
        self.ocr_api_key = ocr_api_key

        # Initialize components
        self.crawler = None
        self.ocr_extractor = None
        self.db_saver = None

    async def process_event_url(self, url: str, output_dir: str = 'naver_event_images') -> Dict:
        """
        Process a single event URL through the complete pipeline

        Args:
            url: Naver brand event URL
            output_dir: Directory to save downloaded images

        Returns:
            Dictionary with success status and results
        """
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║         Naver Event Pipeline - Integrated (Full Process)         ║
║                                                                  ║
║  Step 1: Download images (Playwright - bypasses rate limits)    ║
║  Step 2: Extract text (OCR.space API)                           ║
║  Step 3: Parse event information                                ║
║  Step 4: Save to Supabase database                              ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        try:
            # Step 1: Download images with Playwright
            print(f"\n{'='*70}")
            print("STEP 1: Downloading Images with Playwright (Anti-Rate Limit)")
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
                    'error': f"Image download failed: {crawl_result['error']}",
                    'step': 'download'
                }

            brand_name = crawl_result['brand_name']
            image_files = crawl_result['downloaded_images']
            image_urls = crawl_result['image_urls']

            print(f"\n✅ Step 1 Complete: Downloaded {len(image_files)} images")

            # Step 2: Extract text with OCR.space API
            print(f"\n{'='*70}")
            print("STEP 2: Extracting Text with OCR.space API")
            print(f"{'='*70}\n")

            self.ocr_extractor = NaverEventOCRExtractor(
                api_key=self.ocr_api_key,
                delay_min=1,
                delay_max=3,
                strategy=self.extraction_strategy,
                llm_provider=self.llm_provider
            )

            ocr_texts = self.ocr_extractor.extract_all_text(image_files)

            print(f"\n✅ Step 2 Complete: Extracted text from {len([t for t in ocr_texts.values() if t])} images")

            # Step 3: Parse event information
            print(f"\n{'='*70}")
            print("STEP 3: Parsing Event Information")
            print(f"{'='*70}\n")

            event_data = self.ocr_extractor.parse_event_info(ocr_texts, url, brand_name)

            print(f"\n✅ Step 3 Complete: Event information parsed")

            # Step 4: Save to database
            print(f"\n{'='*70}")
            print("STEP 4: Saving to Supabase Database")
            print(f"{'='*70}\n")

            if SUPABASE_AVAILABLE:
                try:
                    self.db_saver = SupabaseSaver()

                    save_result = self.db_saver.save_event(
                        event_data=event_data,
                        image_urls=image_urls,
                        raw_ocr_data=ocr_texts
                    )

                    if save_result['success']:
                        print(f"\n✅ Step 4 Complete: Data saved to database")
                        print(f"   Record ID: {save_result['data'].get('id')}")
                    else:
                        print(f"\n⚠️ Step 4 Warning: Database save failed")
                        print(f"   Error: {save_result['error']}")
                        # Continue anyway - we still have the data

                except Exception as db_error:
                    print(f"\n⚠️ Step 4 Warning: Database connection failed: {db_error}")
                    print(f"   Continuing without database save...")
                    save_result = {
                        'success': False,
                        'error': str(db_error),
                        'data': None
                    }
            else:
                print(f"\n⚠️ Step 4 Skipped: Supabase not available")
                print(f"   Data will be saved to JSON file only")
                save_result = {
                    'success': False,
                    'error': 'Supabase not available',
                    'data': None
                }

            # Save results to JSON file as backup
            output_file = f"{output_dir}/event_data_{brand_name}.json"
            result_data = {
                'event_data': event_data,
                'image_urls': image_urls,
                'raw_ocr_texts': {os.path.basename(k): v for k, v in ocr_texts.items()},
                'metadata': {
                    'url': url,
                    'brand_name': brand_name,
                    'images_downloaded': len(image_files),
                    'crawler_method': 'Playwright Stealth',
                    'ocr_method': 'OCR.space API',
                    'database_saved': save_result['success'],
                    'database_id': save_result.get('data', {}).get('id') if save_result['success'] else None
                }
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)

            print(f"\n{'='*70}")
            print("FINAL RESULTS")
            print(f"{'='*70}\n")
            print(json.dumps(event_data, ensure_ascii=False, indent=2))
            print(f"\n✓ Results saved to: {output_file}")

            if save_result['success']:
                print(f"✓ Database record ID: {save_result['data'].get('id')}")

            print(f"\n{'='*70}")
            print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"{'='*70}\n")

            return {
                'success': True,
                'event_data': event_data,
                'image_urls': image_urls,
                'ocr_texts': ocr_texts,
                'database_result': save_result,
                'output_file': output_file
            }

        except Exception as e:
            print(f"\n❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'error': str(e),
                'step': 'unknown'
            }


async def main():
    """Main execution function"""
    import sys
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    # Configuration
    url = sys.argv[1] if len(sys.argv) > 1 else 'https://brand.naver.com/iope/shoppingstory/detail?id=5002337684'
    strategy = sys.argv[2] if len(sys.argv) > 2 else 'moderate'

    # OCR API key (from env or default)
    ocr_api_key = os.getenv('OCR_SPACE_API_KEY', 'K87899142388957')

    print(f"""
Configuration:
  URL: {url}
  Strategy: {strategy} (gentle/moderate/aggressive)
  OCR API: OCR.space
  Database: Supabase
    """)

    # Create and run pipeline
    pipeline = NaverEventPipelineIntegrated(
        ocr_api_key=ocr_api_key,
        strategy=strategy
    )

    result = await pipeline.process_event_url(url)

    if result['success']:
        print("\n🎉 All steps completed successfully!")
        return 0
    else:
        print(f"\n💥 Pipeline failed at step: {result.get('step', 'unknown')}")
        print(f"   Error: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == '__main__':
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Run pipeline
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
