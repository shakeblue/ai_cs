"""
Extract broadcast data from lives URL using HTML parsing
"""

import asyncio
import json
from pathlib import Path
from playwright.async_api import async_playwright

OUTPUT_DIR = Path("cj/live_debug_output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

async def extract_lives_html(url):
    """Extract all possible data from lives URL HTML"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            ignore_https_errors=True
        )

        page = await context.new_page()

        print(f"\n{'='*80}")
        print(f"EXTRACTING DATA FROM LIVES URL HTML")
        print(f"URL: {url}")
        print(f"{'='*80}\n")

        print("Loading page...")
        await page.goto(url, wait_until='networkidle')
        await asyncio.sleep(5)

        extracted_data = {}

        print("\n1. Extracting from meta tags...\n")

        # Meta tags
        meta_selectors = {
            'title': 'meta[property="og:title"]',
            'description': 'meta[property="og:description"]',
            'image': 'meta[property="og:image"]',
        }

        for field, selector in meta_selectors.items():
            elem = await page.query_selector(selector)
            if elem:
                content = await elem.get_attribute('content')
                extracted_data[f'meta_{field}'] = content
                print(f"   ✓ {field}: {content[:80]}...")

        print("\n2. Extracting products...\n")

        # Products
        product_items = await page.query_selector_all('[class*="ProductList_item"]')
        products = []

        for item in product_items:
            try:
                # Product title
                title_elem = await item.query_selector('[class*="ProductListItem_title"]')
                title = await title_elem.text_content() if title_elem else None

                # Discount rate
                discount_elem = await item.query_selector('[class*="DiscountPrice_discount"]')
                discount_text = await discount_elem.text_content() if discount_elem else None

                # Price
                price_elem = await item.query_selector('[class*="DiscountPrice_price"]')
                price_text = await price_elem.text_content() if price_elem else None

                # Product link (to get product ID)
                link_elem = await item.query_selector('a[href*="/products/"]')
                link = await link_elem.get_attribute('href') if link_elem else None

                # Image
                img_elem = await item.query_selector('img')
                image = await img_elem.get_attribute('src') if img_elem else None

                product = {
                    'name': title.strip() if title else None,
                    'discount_rate': discount_text.strip() if discount_text else None,
                    'price': price_text.strip() if price_text else None,
                    'link': link,
                    'image': image
                }

                products.append(product)
                print(f"   ✓ Product: {product['name'][:60] if product['name'] else 'N/A'}...")

            except Exception as e:
                print(f"   ✗ Error extracting product: {e}")

        extracted_data['products'] = products
        print(f"\n   Total products extracted: {len(products)}")

        print("\n3. Extracting comments...\n")

        # Comments
        comment_nicknames = await page.query_selector_all('[class*="NormalComment_nickname"]')
        comment_texts = await page.query_selector_all('[class*="NormalComment_comment"]')

        comments = []
        for i in range(min(len(comment_nicknames), len(comment_texts))):
            try:
                nickname = await comment_nicknames[i].text_content()
                text = await comment_texts[i].text_content()
                comments.append({
                    'nickname': nickname.strip() if nickname else None,
                    'message': text.strip() if text else None
                })
            except:
                pass

        extracted_data['comments'] = comments[:50]  # Limit to 50
        print(f"   ✓ Total comments extracted: {len(comments)}")
        if comments:
            print(f"   Sample: {comments[0]['nickname']}: {comments[0]['message'][:40]}...")

        print("\n4. Extracting broadcast title and brand...\n")

        # Broadcast title
        title_selectors = [
            '[class*="IntroductionModalTitle"]',
            '[class*="LiveTitle"]',
            'h1',
            '[class*="BroadcastTitle"]'
        ]

        for selector in title_selectors:
            elem = await page.query_selector(selector)
            if elem:
                title_text = await elem.text_content()
                if title_text and len(title_text.strip()) > 5:
                    extracted_data['broadcast_title'] = title_text.strip()
                    print(f"   ✓ Title: {title_text.strip()[:80]}...")
                    break

        # Brand name
        brand_selectors = [
            '[class*="IntroductionProfile_name"]',
            '[class*="BrandName"]',
            '[class*="ProfileName"]'
        ]

        for selector in brand_selectors:
            elem = await page.query_selector(selector)
            if elem:
                brand_text = await elem.text_content()
                if brand_text and len(brand_text.strip()) > 0:
                    extracted_data['brand_name'] = brand_text.strip()
                    print(f"   ✓ Brand: {brand_text.strip()}")
                    break

        print("\n5. Extracting broadcast status and time...\n")

        # Status/time
        status_selectors = [
            '[class*="LiveStatus"]',
            '[class*="BroadcastStatus"]',
            '[class*="LiveIntroductionList_state"]'
        ]

        for selector in status_selectors:
            elem = await page.query_selector(selector)
            if elem:
                status_text = await elem.text_content()
                if status_text:
                    extracted_data['status_time'] = status_text.strip()
                    print(f"   ✓ Status: {status_text.strip()}")
                    break

        print("\n6. Extracting coupons and benefits...\n")

        # Coupons
        coupon_elems = await page.query_selector_all('[class*="CouponButton"]')
        coupons = []
        for elem in coupon_elems:
            try:
                text = await elem.text_content()
                if text:
                    coupons.append(text.strip())
            except:
                pass

        extracted_data['coupons'] = coupons
        print(f"   Coupons found: {len(coupons)}")
        for coupon in coupons:
            print(f"   ✓ {coupon[:60]}...")

        # Benefits
        benefit_elems = await page.query_selector_all('[class*="BenefitBanner"]')
        benefits = []
        for elem in benefit_elems:
            try:
                text = await elem.text_content()
                if text:
                    benefits.append(text.strip())
            except:
                pass

        extracted_data['benefits'] = benefits
        print(f"   Benefits found: {len(benefits)}")
        for benefit in benefits:
            print(f"   ✓ {benefit[:60]}...")

        # Save extracted data
        output_file = OUTPUT_DIR / "lives_html_extraction.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*80}")
        print("EXTRACTION SUMMARY")
        print(f"{'='*80}\n")

        summary = {
            'Meta tags': len([k for k in extracted_data.keys() if k.startswith('meta_')]),
            'Products': len(extracted_data.get('products', [])),
            'Comments': len(extracted_data.get('comments', [])),
            'Coupons': len(extracted_data.get('coupons', [])),
            'Benefits': len(extracted_data.get('benefits', [])),
            'Broadcast title': '✓' if extracted_data.get('broadcast_title') else '✗',
            'Brand name': '✓' if extracted_data.get('brand_name') else '✗',
        }

        for field, value in summary.items():
            print(f"{field:20}: {value}")

        print(f"\nFull extraction saved to: {output_file}")

        # Compare with API approach
        print(f"\n{'='*80}")
        print("COMPARISON: HTML vs API (from previous investigation)")
        print(f"{'='*80}\n")

        comparison_table = [
            ("Field", "HTML", "API", "Recommendation"),
            ("-" * 20, "-" * 10, "-" * 10, "-" * 20),
            ("Broadcast Title", "✓" if extracted_data.get('broadcast_title') else "✗", "✗", "HTML or Meta"),
            ("Brand Name", "✓" if extracted_data.get('brand_name') else "✗", "✗", "HTML or Meta"),
            ("Products", str(len(extracted_data.get('products', []))), "0", "HTML"),
            ("Comments", str(len(extracted_data.get('comments', []))), "0", "HTML"),
            ("Coupons", str(len(extracted_data.get('coupons', []))), "0 (API exists but empty)", "HTML or API"),
            ("Benefits", str(len(extracted_data.get('benefits', []))), "5 (API has data)", "API"),
        ]

        for row in comparison_table:
            print(f"{row[0]:20} | {row[1]:10} | {row[2]:10} | {row[3]:20}")

        print("\n✓ CONCLUSION FOR LIVES URLs:")
        print("  Use HYBRID approach:")
        print("  - Meta tags: title, description")
        print("  - HTML parsing: products, comments, brand name")
        print("  - API interception: benefits (and possibly coupons)")

        await browser.close()

if __name__ == "__main__":
    import sys
    url = sys.argv[1] if len(sys.argv) > 1 else "https://view.shoppinglive.naver.com/lives/1810235?tr=lim"
    asyncio.run(extract_lives_html(url))
