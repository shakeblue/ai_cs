#!/usr/bin/env python3
"""Simple debug script to check shopping story page structure"""

import asyncio
import re
from playwright.async_api import async_playwright


async def debug_shopping_story_page(brand_code: str):
    """Debug shopping story page to see its structure"""

    url = f"https://brand.naver.com/{brand_code}/shoppingstory/list"
    print(f"Debugging URL: {url}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            ignore_https_errors=True
        )
        page = await context.new_page()

        try:
            print("Navigating to page...")
            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            except Exception as e:
                print(f"⚠ Initial load warning: {e}")
                print("  Trying to continue anyway...")

            print("✓ Page loaded, waiting for dynamic content...")
            await asyncio.sleep(5)  # Give more time for JS to load

            # Get full page content
            content = await page.content()

            # Save to file for inspection
            output_file = f"debug_shopping_story_{brand_code}.html"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✓ Page content saved to: {output_file}")
            print(f"  Total length: {len(content)} characters\n")

            # Search for different patterns
            print("="*70)
            print("SEARCHING FOR PATTERNS")
            print("="*70)

            patterns = {
                'shoppingstory (case insensitive)': r'shoppingstory',
                'detail?id': r'detail\?id',
                'any href with "story"': r'href=["\']([^"\']*story[^"\']+)["\']',
                'any href with "detail"': r'href=["\']([^"\']*detail[^"\']+)["\']',
                'any href with "shopping"': r'href=["\']([^"\']*shopping[^"\']+)["\']',
            }

            for desc, pattern in patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                print(f"\n{desc}: {len(matches)} matches")
                if matches:
                    for match in matches[:5]:
                        print(f"  - {match}")
                    if len(matches) > 5:
                        print(f"  ... and {len(matches) - 5} more")

            # Check all links
            print(f"\n{'='*70}")
            print("ALL LINKS ON PAGE")
            print("="*70)
            all_links = re.findall(r'href=["\']([^"\']+)["\']', content)
            print(f"Total links found: {len(all_links)}\n")

            # Group links by type
            link_groups = {
                'story/detail links': [],
                'product links': [],
                'category links': [],
                'other links': []
            }

            for link in all_links:
                if 'story' in link.lower() or 'detail' in link.lower():
                    link_groups['story/detail links'].append(link)
                elif 'product' in link.lower():
                    link_groups['product links'].append(link)
                elif 'category' in link.lower():
                    link_groups['category links'].append(link)
                else:
                    link_groups['other links'].append(link)

            for group_name, links in link_groups.items():
                if links:
                    print(f"\n{group_name}: {len(links)}")
                    for link in links[:10]:
                        print(f"  - {link}")
                    if len(links) > 10:
                        print(f"  ... and {len(links) - 10} more")

            # Look for specific elements
            print(f"\n{'='*70}")
            print("LOOKING FOR SPECIFIC ELEMENTS")
            print("="*70)

            # Check for article/card elements
            article_patterns = [
                r'<article[^>]*>',
                r'<div[^>]*class="[^"]*card[^"]*"',
                r'<div[^>]*class="[^"]*item[^"]*"',
                r'<div[^>]*class="[^"]*story[^"]*"',
            ]

            for pattern in article_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"\nPattern {pattern}: {len(matches)} matches")
                    for match in matches[:3]:
                        print(f"  - {match}")

            # Take a screenshot
            screenshot_file = f"debug_shopping_story_{brand_code}.png"
            await page.screenshot(path=screenshot_file, full_page=True)
            print(f"\n✓ Screenshot saved to: {screenshot_file}")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()


if __name__ == '__main__':
    import sys

    brand_code = sys.argv[1] if len(sys.argv) > 1 else 'IOPE'
    print(f"Debugging brand: {brand_code}\n")

    asyncio.run(debug_shopping_story_page(brand_code))
