#!/usr/bin/env python3
"""
Brand Shopping Story Crawler
Loops through brands and crawls their shopping story pages using vision pipeline
"""

import asyncio
import json
import os
import sys
import re
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

from vision_pipeline import VisionPipeline
from vision_extractor import VisionProvider


class BrandShoppingStoryCrawler:
    """Crawls shopping stories for multiple brands"""

    def __init__(
        self,
        brands_file: str = '../config/brands.json',
        vision_provider: VisionProvider = VisionProvider.GPT_4O_MINI,
        crawler_strategy: str = 'gentle',
        max_brands: int = 10,
        headless: bool = True
    ):
        """
        Initialize crawler

        Args:
            brands_file: Path to brands.json file
            vision_provider: Vision LLM provider for pipeline
            crawler_strategy: Crawler strategy (gentle, moderate, aggressive)
            max_brands: Maximum number of brands to process
            headless: Run browser in headless mode
        """
        self.brands_file = brands_file
        self.vision_provider = vision_provider
        self.crawler_strategy = crawler_strategy
        self.max_brands = max_brands
        self.headless = headless

        # Statistics
        self.stats = {
            'brands_processed': 0,
            'shopping_stories_found': 0,
            'shopping_stories_processed': 0,
            'successes': 0,
            'failures': 0,
            'total_cost': 0.0
        }

    def load_brands(self) -> List[Dict]:
        """Load brands from JSON file"""
        brands_path = Path(__file__).parent / self.brands_file

        if not brands_path.exists():
            raise FileNotFoundError(f"Brands file not found: {brands_path}")

        with open(brands_path, 'r', encoding='utf-8') as f:
            brands = json.load(f)

        return brands[:self.max_brands]

    async def get_shopping_story_links(self, brand_code: str) -> List[str]:
        """
        Get all shopping story detail links for a brand

        Args:
            brand_code: Brand code (e.g., 'sulwhasoo')

        Returns:
            List of shopping story detail URLs
        """
        # Use lowercase brand code
        brand_code_lower = brand_code.lower()
        shopping_story_list_url = f"https://brand.naver.com/{brand_code_lower}/shoppingstory/list"

        print(f"\n{'='*70}")
        print(f"Searching shopping stories: {brand_code}")
        print(f"URL: {shopping_story_list_url}")
        print(f"{'='*70}\n")

        story_links = []

        try:
            async with async_playwright() as p:
                # Launch browser
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    ignore_https_errors=True  # Bypass SSL errors
                )
                page = await context.new_page()

                # Navigate to shopping story list
                try:
                    # Use domcontentloaded instead of networkidle for better reliability
                    # Increased timeout for gentle strategy
                    timeout = 90000 if self.crawler_strategy == 'gentle' else 30000
                    await page.goto(shopping_story_list_url, wait_until='domcontentloaded', timeout=timeout)

                    # Wait for dynamic content - longer for gentle strategy
                    wait_time = 8 if self.crawler_strategy == 'gentle' else 3
                    await asyncio.sleep(wait_time)

                    # Get page content
                    content = await page.content()

                    # Extract shopping story detail links
                    # Pattern: href="/brand_code/shoppingstory/detail?id=XXXXX&amp;page=1"
                    import html

                    # Find all href attributes containing shoppingstory/detail
                    pattern = r'href=["\']([^"\']*shoppingstory/detail\?id=[^"\']+)["\']'
                    matches = re.findall(pattern, content, re.IGNORECASE)

                    # Normalize URLs and decode HTML entities
                    for match in matches:
                        # Decode HTML entities (&amp; -> &)
                        decoded_match = html.unescape(match)

                        # Remove leading slash if present
                        link = decoded_match.lstrip('/')

                        # Build full URL
                        if not link.startswith('http'):
                            # If link doesn't include brand code, add it
                            if not link.startswith(brand_code_lower):
                                full_url = f"https://brand.naver.com/{brand_code_lower}/{link}"
                            else:
                                full_url = f"https://brand.naver.com/{link}"
                        else:
                            full_url = link

                        # Remove duplicate page parameter if present and normalize
                        # Only keep the ID parameter for uniqueness
                        if 'detail?id=' in full_url:
                            base_url = full_url.split('&')[0]  # Keep only the ID part
                            if base_url not in story_links:
                                story_links.append(full_url)  # Keep original URL with page param

                    print(f"✓ Found {len(story_links)} shopping stories for {brand_code}")
                    for i, link in enumerate(story_links, 1):
                        print(f"  {i}. {link}")

                except PlaywrightTimeout:
                    print(f"⚠ Timeout loading shopping story list for {brand_code}")
                except Exception as e:
                    print(f"⚠ Error loading page for {brand_code}: {e}")
                    import traceback
                    traceback.print_exc()

                finally:
                    await browser.close()

        except Exception as e:
            print(f"❌ Browser error for {brand_code}: {e}")
            import traceback
            traceback.print_exc()

        return story_links

    async def process_brand(self, brand: Dict) -> Dict:
        """
        Process all shopping stories for a brand

        Args:
            brand: Brand dictionary with 'code' and 'name'

        Returns:
            Processing results
        """
        brand_code = brand['code']
        brand_name = brand['name']

        print(f"\n{'#'*70}")
        print(f"# Processing Brand: {brand_name} ({brand_code})")
        print(f"{'#'*70}\n")

        results = {
            'brand_code': brand_code,
            'brand_name': brand_name,
            'stories_found': 0,
            'stories_processed': 0,
            'successes': 0,
            'failures': 0,
            'cost': 0.0,
            'errors': []
        }

        # Get shopping story links
        story_links = await self.get_shopping_story_links(brand_code)
        results['stories_found'] = len(story_links)
        self.stats['shopping_stories_found'] += len(story_links)

        if not story_links:
            print(f"⚠ No shopping stories found for {brand_name}")
            return results

        # Process each shopping story
        pipeline = VisionPipeline(
            vision_provider=self.vision_provider,
            crawler_strategy=self.crawler_strategy
        )

        for i, story_url in enumerate(story_links, 1):
            print(f"\n{'-'*70}")
            print(f"Processing story {i}/{len(story_links)} for {brand_name}")
            print(f"URL: {story_url}")
            print(f"{'-'*70}\n")

            try:
                # Create output directory for this brand
                output_dir = f"shopping_story_images/{brand_code}"
                os.makedirs(output_dir, exist_ok=True)

                # Run vision pipeline
                result = await pipeline.process_event_url(story_url, output_dir)

                results['stories_processed'] += 1
                self.stats['shopping_stories_processed'] += 1

                if result['success']:
                    results['successes'] += 1
                    results['cost'] += result.get('cost', 0.0)
                    self.stats['successes'] += 1
                    self.stats['total_cost'] += result.get('cost', 0.0)
                    print(f"✓ Success: Story {i} processed (Cost: ${result.get('cost', 0):.6f})")
                else:
                    results['failures'] += 1
                    self.stats['failures'] += 1
                    error_msg = result.get('error', 'Unknown error')
                    results['errors'].append({
                        'url': story_url,
                        'error': error_msg
                    })
                    print(f"✗ Failed: Story {i} - {error_msg}")

            except KeyboardInterrupt:
                print("\n⚠️  Interrupted by user")
                raise
            except Exception as e:
                results['failures'] += 1
                self.stats['failures'] += 1
                results['errors'].append({
                    'url': story_url,
                    'error': str(e)
                })
                print(f"❌ Error processing story {i}: {e}")

            # Add delay between stories for gentle strategy to avoid rate limiting
            if i < len(story_links) and self.crawler_strategy == 'gentle':
                delay = 15
                print(f"\n⏱ Waiting {delay}s before next story (gentle strategy)...")
                await asyncio.sleep(delay)

        self.stats['brands_processed'] += 1

        return results

    async def run(self) -> Dict:
        """
        Run the crawler for all brands

        Returns:
            Overall statistics
        """
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║          Brand Shopping Story Crawler                            ║
║                                                                  ║
║  Loops through brands and processes shopping stories             ║
║  using the Vision Pipeline                                       ║
╚══════════════════════════════════════════════════════════════════╝
        """)

        # Load brands
        brands = self.load_brands()
        print(f"\n📋 Loaded {len(brands)} brands:")
        for brand in brands:
            print(f"  - {brand['name']} ({brand['code']})")

        # Process each brand
        brand_results = []

        try:
            for i, brand in enumerate(brands, 1):
                print(f"\n\n{'='*70}")
                print(f"BRAND {i}/{len(brands)}")
                print(f"{'='*70}")

                result = await self.process_brand(brand)
                brand_results.append(result)

                # Show progress
                print(f"\n📊 Progress: {i}/{len(brands)} brands completed")
                print(f"   Stories found: {self.stats['shopping_stories_found']}")
                print(f"   Stories processed: {self.stats['shopping_stories_processed']}")
                print(f"   Successes: {self.stats['successes']}")
                print(f"   Failures: {self.stats['failures']}")
                print(f"   Total cost: ${self.stats['total_cost']:.6f}")

        except KeyboardInterrupt:
            print("\n\n⚠️  Crawler interrupted by user")

        # Final summary
        print(f"\n\n{'='*70}")
        print("FINAL SUMMARY")
        print(f"{'='*70}\n")

        print(f"Brands processed: {self.stats['brands_processed']}/{len(brands)}")
        print(f"Shopping stories found: {self.stats['shopping_stories_found']}")
        print(f"Shopping stories processed: {self.stats['shopping_stories_processed']}")
        print(f"Successes: {self.stats['successes']}")
        print(f"Failures: {self.stats['failures']}")
        print(f"Total cost: ${self.stats['total_cost']:.6f}")

        # Save results
        results_file = 'shopping_story_results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump({
                'stats': self.stats,
                'brand_results': brand_results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Results saved to: {results_file}")

        return self.stats


async def main():
    """Main function"""
    import argparse
    from dotenv import load_dotenv

    # Load environment variables
    load_dotenv()

    parser = argparse.ArgumentParser(
        description='Crawl shopping stories for multiple brands',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all 10 brands using GPT-4o Mini:
  python brand_shopping_story_crawler.py

  # Process only 3 brands using Claude:
  python brand_shopping_story_crawler.py --max-brands 3 --provider claude

  # Process with custom brands file:
  python brand_shopping_story_crawler.py --brands-file /path/to/brands.json
        """
    )

    parser.add_argument(
        '--brands-file',
        default='../config/brands.json',
        help='Path to brands JSON file (default: ../config/brands.json)'
    )
    parser.add_argument(
        '--provider',
        choices=['claude', 'gpt', 'gemini'],
        default='gpt',
        help='Vision LLM provider (default: gpt)'
    )
    parser.add_argument(
        '--crawler',
        choices=['gentle', 'moderate', 'aggressive'],
        default='gentle',
        help='Crawler strategy (default: gentle)'
    )
    parser.add_argument(
        '--max-brands',
        type=int,
        default=10,
        help='Maximum number of brands to process (default: 10)'
    )
    parser.add_argument(
        '--show-browser',
        action='store_true',
        help='Show browser (non-headless mode)'
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
  Brands file:      {args.brands_file}
  Max brands:       {args.max_brands}
  Vision provider:  {args.provider} ({vision_provider.value})
  Crawler strategy: {args.crawler}
  Headless:         {not args.show_browser}
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

    # Run crawler
    crawler = BrandShoppingStoryCrawler(
        brands_file=args.brands_file,
        vision_provider=vision_provider,
        crawler_strategy=args.crawler,
        max_brands=args.max_brands,
        headless=not args.show_browser
    )

    stats = await crawler.run()

    # Return exit code based on results
    if stats['successes'] > 0:
        print("\n✓ Crawler completed with some successes")
        return 0
    else:
        print("\n✗ Crawler completed with no successes")
        return 1


if __name__ == '__main__':
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Run crawler
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
