#!/usr/bin/env python3
"""
Extract products from BridgeProductSection using Playwright
"""

import asyncio
from playwright.async_api import async_playwright
import re
import json


async def extract_bridge_products(url: str):
    """Extract products from livebridge page"""

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            ignore_https_errors=True,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        try:
            print(f"Loading: {url}")
            await page.goto(url, wait_until='networkidle')
            await page.wait_for_timeout(2000)

            # Scroll to ensure products are loaded
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await page.wait_for_timeout(1000)

            # Extract products from BridgeProductSection
            products = await page.evaluate("""
                () => {
                    const productSection = document.querySelector('[class*="BridgeProductSection_card_wrap"]');
                    if (!productSection) return [];

                    // Find all product items - they are direct children divs
                    const productCards = Array.from(productSection.children).filter(child =>
                        child.classList.contains('ProductWrapper_wrap_eCUt9') ||
                        child.className.includes('VerticalCardList_item') ||
                        child.querySelector('a[href*="channelProductNo"]')
                    );
                    const products = [];

                    productCards.forEach(card => {
                        // Find the product link
                        const link = card.querySelector('a[href*="channelProductNo"]');
                        if (!link) return;

                        const href = link.href;

                        // Extract channelProductNo from URL
                        const match = href.match(/channelProductNo=(\\d+)/);
                        const productNo = match ? match[1] : null;

                        if (!productNo) return;

                        // Get all text content and parse it
                        const textContent = link.textContent || '';

                        // Extract product name (first substantial text)
                        const lines = textContent.split('\\n').map(l => l.trim()).filter(l => l);
                        const name = lines[0] || null;

                        // Extract discount rate (look for %)
                        const discountMatch = textContent.match(/(\\d+)%할인/);
                        const discount = discountMatch ? discountMatch[1] + '%' : null;

                        // Extract price (look for 원)
                        const priceMatches = textContent.match(/([\\d,]+)원/g);
                        const price = priceMatches ? priceMatches[0] : null;

                        // Extract image
                        const img = card.querySelector('img');
                        const imageUrl = img ? img.src : null;

                        // Extract badges
                        const badgeTexts = [];
                        if (textContent.includes('네이버 배송')) badgeTexts.push('네이버 배송');
                        if (textContent.includes('무료배송')) badgeTexts.push('무료배송');
                        if (textContent.includes('오늘출발')) badgeTexts.push('오늘출발');

                        products.push({
                            product_id: productNo,
                            product_url: href,
                            name: name,
                            discount_rate: discount,
                            price: price,
                            image_url: imageUrl,
                            badges: badgeTexts,
                            source: 'BridgeProductSection_HTML'
                        });
                    });

                    return products;
                }
            """)

            print(f"\n✓ Extracted {len(products)} products from BridgeProductSection")

            for i, product in enumerate(products, 1):
                print(f"\nProduct {i}:")
                print(f"  ID: {product['product_id']}")
                print(f"  Name: {product.get('name', 'N/A')}")
                print(f"  Discount: {product.get('discount_rate', 'N/A')}")
                print(f"  Price: {product.get('price', 'N/A')}")
                print(f"  Badges: {', '.join(product.get('badges', []))}")
                print(f"  URL: {product['product_url'][:100]}...")

            return products

        finally:
            await browser.close()


if __name__ == '__main__':
    url = 'https://shoppinglive.naver.com/livebridge/1776510'
    products = asyncio.run(extract_bridge_products(url))

    # Save to JSON
    with open('output/bridge_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Saved to: output/bridge_products.json")
