"""
Replays Crawler
Crawler for /replays/ URLs using API interception + DOM extraction
"""

import asyncio
import logging
import re
from typing import Dict, Any, List

from crawlers.base_crawler import BaseCrawler
from extractors.api_extractor import APIExtractor

logger = logging.getLogger(__name__)


class ReplaysCrawler(BaseCrawler):
    """Crawler for /replays/ URLs using API interception"""

    def get_extraction_method(self) -> str:
        return "API"

    def get_url_type(self) -> str:
        return "replays"

    async def extract_data(self, url: str) -> Dict[str, Any]:
        """
        Extract data from replays URL using API interception

        Args:
            url: The replays URL to crawl

        Returns:
            Dict containing broadcast data
        """
        errors = []
        warnings = []

        # Setup API extractor
        api_extractor = APIExtractor()
        await api_extractor.setup_interception(self.page)

        # Navigate to page
        logger.info(f"Navigating to {url}")
        await self.page.goto(url, wait_until='networkidle')
        logger.info("Page loaded, waiting for APIs...")

        # Optimization #3: Smart wait for required APIs instead of fixed 30s
        # Wait for main broadcast API first (required)
        await api_extractor.wait_for_required_apis(['broadcast'], max_wait=10.0)

        # Wait for optional APIs (coupons, benefits) with smart timeout
        # These are not critical, but we give them enough time to be captured
        logger.info("Waiting for optional APIs (coupons, benefits)...")
        await api_extractor.wait_for_optional_apis(
            ['coupons', 'benefits'],
            max_wait=15.0,
            min_wait=3.0  # Wait at least 3s even if some APIs are captured
        )

        # Check what APIs were captured
        captured_apis = api_extractor.get_captured_apis()
        logger.info(f"Captured APIs: {captured_apis}")

        # Extract main broadcast data
        broadcast_api_data = api_extractor.get_broadcast_data()
        if not broadcast_api_data:
            self._add_error(errors, "APIError", "Failed to capture main broadcast API")
            raise Exception("Failed to capture main broadcast API")

        # Extract broadcast fields
        broadcast_data = self._extract_broadcast_fields(broadcast_api_data)

        # Extract products: Try DOM first (gets all 64), fallback to API (only 30)
        api_products = broadcast_data.get('products', [])
        total_product_count = broadcast_api_data.get('productCount', len(api_products))

        if total_product_count > len(api_products):
            logger.info(f"API has {len(api_products)}/{total_product_count} products - extracting from DOM...")
            dom_products = await self._extract_products_from_dom()

            if len(dom_products) > len(api_products):
                logger.info(f"✓ DOM extraction successful: {len(dom_products)} products (vs API: {len(api_products)})")
                broadcast_data['products'] = dom_products
                broadcast_data['products_source'] = 'DOM'
            else:
                logger.warning(f"DOM extraction got {len(dom_products)} products, using API data ({len(api_products)})")
                broadcast_data['products_source'] = 'API'
                self._add_warning(
                    warnings,
                    "products",
                    f"Only {len(api_products)}/{total_product_count} products available. Naver API limit.",
                    len(api_products)
                )
        else:
            broadcast_data['products_source'] = 'API'

        # Extract coupons
        coupons = api_extractor.get_coupons()
        if coupons:
            broadcast_data['coupons'] = self._extract_coupons(coupons)
        else:
            self._add_warning(warnings, "coupons", "No coupons available", [])
            broadcast_data['coupons'] = []

        # Extract benefits
        benefits = api_extractor.get_benefits()
        if benefits:
            broadcast_data['live_benefits'] = self._extract_benefits(benefits)
        else:
            self._add_warning(warnings, "live_benefits", "No benefits available", [])
            broadcast_data['live_benefits'] = []

        # Extract comments with pagination (100 per page, keep odd indices for storage optimization)
        logger.info("Fetching all comments with pagination...")
        all_comments = await api_extractor.fetch_all_comments_paginated(
            broadcast_id=broadcast_api_data.get('id'),
            page_size=100,
            keep_odd_only=True  # Keep only odd indices (~50%) to reduce DB storage for demo
        )
        if all_comments:
            broadcast_data['live_chat'] = self._extract_comments(all_comments)
        else:
            self._add_warning(warnings, "live_chat", "No comments available", [])
            broadcast_data['live_chat'] = []

        # Add errors and warnings
        if errors:
            broadcast_data['_errors'] = errors
        if warnings:
            broadcast_data['_warnings'] = warnings

        # Log extraction summary
        logger.info(
            f"Extracted {len(broadcast_data.get('products', []))} products, "
            f"{len(broadcast_data.get('coupons', []))} coupons, "
            f"{len(broadcast_data.get('live_benefits', []))} benefits, "
            f"{len(broadcast_data.get('live_chat', []))} comments"
        )

        return broadcast_data

    def _extract_broadcast_fields(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract broadcast fields from API data"""
        broadcast_id = api_data.get('id')

        return {
            'broadcast_id': broadcast_id,
            'replay_url': api_data.get('broadcastReplayEndUrl'),
            'broadcast_url': api_data.get('broadcastEndUrl'),
            'livebridge_url': self.construct_livebridge_url(broadcast_id) if broadcast_id else None,
            'title': api_data.get('title'),
            'brand_name': api_data.get('nickname'),
            'description': api_data.get('description'),
            'broadcast_date': api_data.get('startDate'),
            'broadcast_end_date': api_data.get('endDate'),
            'expected_start_date': api_data.get('expectedStartDate'),
            'status': api_data.get('status'),
            'stand_by_image': api_data.get('standByImage'),
            'products': self._extract_products(api_data.get('shoppingProducts', []))
        }

    def _extract_products(self, products: list) -> list:
        """Extract product information"""
        extracted_products = []

        for product in products:
            # Get price information
            discounted_price = product.get('discountedSalePrice') or product.get('price')
            price = product.get('price')
            discount_rate = product.get('discountRate', 0)

            # Calculate original price if we have discount rate
            original_price = None
            if discounted_price and discount_rate > 0:
                # original_price = discounted_price / (1 - discount_rate/100)
                original_price = int(discounted_price / (1 - discount_rate / 100))
            elif price:
                original_price = price

            extracted_products.append({
                'product_id': product.get('key') or product.get('productNo'),
                'name': product.get('name'),
                'brand_name': product.get('brandName'),
                'discount_rate': discount_rate,
                'discounted_price': discounted_price,
                'original_price': original_price,
                'stock': product.get('stock'),
                'image': product.get('image'),
                'link': product.get('link') or product.get('productEndUrl'),
                'review_count': product.get('reviewCount'),
                'delivery_fee': product.get('deliveryFee')
            })

        return extracted_products

    def _extract_coupons(self, coupons: list) -> list:
        """Extract coupon information"""
        extracted_coupons = []

        for coupon in coupons:
            extracted_coupons.append({
                'title': coupon.get('benefitPolicyName'),
                'benefit_type': coupon.get('benefitTargetType'),
                'benefit_unit': coupon.get('benefitUnit'),
                'benefit_value': coupon.get('benefitValue'),
                'min_order_amount': coupon.get('minOrderAmount'),
                'max_discount_amount': coupon.get('maxDiscountAmount'),
                'valid_start': coupon.get('validPeriodStartDate'),
                'valid_end': coupon.get('validPeriodEndDate')
            })

        return extracted_coupons

    def _extract_benefits(self, benefits: list) -> list:
        """Extract benefit information"""
        extracted_benefits = []

        for benefit in benefits:
            extracted_benefits.append({
                'id': benefit.get('id'),
                'message': benefit.get('message'),
                'detail': benefit.get('detailMessage'),
                'type': benefit.get('type')
            })

        return extracted_benefits

    def _extract_comments(self, comments: list) -> list:
        """Extract comment information"""
        extracted_comments = []

        for comment in comments:
            extracted_comments.append({
                'nickname': comment.get('nickname'),
                'message': comment.get('message'),
                'created_at': comment.get('createdAt'),
                'comment_type': comment.get('commentType')
            })

        return extracted_comments

    async def _extract_products_from_dom(self) -> List[Dict[str, Any]]:
        """
        Extract ALL products from DOM (gets 64 vs API's 30)

        Products are lazy-loaded in wa_product_modal_tabpanel div.
        Requires aggressive scrolling to trigger lazy loading of all items.

        Returns:
            List of product dicts extracted from DOM
        """
        try:
            logger.info("Extracting products from DOM...")

            # Try to open product tab/modal if it exists
            # Wait a bit for page to fully render first
            await asyncio.sleep(3)

            try:
                # Look for product tab/button (Korean: 상품)
                # Try multiple strategies
                product_triggers = [
                    '#wa_product_modal_tab',  # Specific ID
                    'button#wa_product_modal_tab',
                    '[id*="product"][role="tab"]',
                    'button:has-text("상품")',
                    '[aria-label*="상품"]',
                    'text=상품'
                ]

                tab_clicked = False
                for trigger in product_triggers:
                    try:
                        element = await self.page.wait_for_selector(trigger, timeout=2000, state='visible')
                        if element:
                            await element.click()
                            logger.info(f"✓ Clicked product tab: {trigger}")
                            await asyncio.sleep(3)  # Wait longer for products to load
                            tab_clicked = True
                            break
                    except Exception as e:
                        logger.debug(f"Trigger {trigger} failed: {e}")
                        continue

                if not tab_clicked:
                    logger.warning("Could not click product tab, products might not load")
            except Exception as e:
                logger.warning(f"Exception while trying to click product tab: {e}")
                pass  # Product panel might already be visible

            # Wait for product panel to appear
            try:
                await self.page.wait_for_selector(
                    '#wa_product_modal_tabpanel',
                    timeout=10000,
                    state='attached'
                )
                logger.info("✓ Product panel found in DOM")
            except:
                logger.warning("Product panel not found, trying alternative selectors")

            # Wait for initial products to render
            try:
                await self.page.wait_for_selector(
                    '[class*="ProductList_item"], [class*="ProductListItem_wrap"]',
                    timeout=10000,
                    state='attached'
                )
                logger.info("✓ Product elements detected in DOM")
            except:
                logger.warning("Product elements not found in DOM within timeout")
                return []

            # Initial wait for first batch to render
            await asyncio.sleep(2)

            # Aggressive scrolling to trigger lazy loading of ALL 64 products
            logger.info("Scrolling aggressively to trigger lazy loading of all products...")
            await self.page.evaluate("""
                async () => {
                    const panel = document.querySelector('#wa_product_modal_tabpanel')
                               || document.querySelector('[class*="ProductList"]');

                    if (panel) {
                        // Scroll multiple times with delays to trigger lazy load
                        for (let i = 0; i < 20; i++) {
                            panel.scrollTop = panel.scrollHeight;
                            await new Promise(resolve => setTimeout(resolve, 500));

                            // Log progress every 5 scrolls
                            if (i % 5 === 0) {
                                const count = document.querySelectorAll('[class*="ProductList_item"]').length;
                                console.log(`[Scroll ${i}] Products loaded: ${count}`);
                            }
                        }

                        // Final count
                        const finalCount = document.querySelectorAll('[class*="ProductList_item"]').length;
                        console.log(`[Final] Total products loaded: ${finalCount}`);
                    }
                }
            """)

            # Wait for lazy load to complete
            await asyncio.sleep(2)

            # Log count before extraction
            element_count = await self.page.evaluate('''
                document.querySelectorAll('[class*="ProductList_item"]').length
            ''')
            logger.info(f"Elements visible before extraction: {element_count}")

            # Extract products from DOM using correct selectors
            result = await self.page.evaluate("""
                () => {
                    const debug = {};

                    // Check global count first
                    debug.globalCount = document.querySelectorAll('[class*="ProductList_item"]').length;

                    // Search globally in document (products are in ModalContentScroll_inner, not directly in panel)
                    // The products appear after clicking the product tab
                    let elements = document.querySelectorAll('[class*="ProductList_item"]');
                    debug.elementsFound = elements.length;

                    if (elements.length === 0) {
                        elements = document.querySelectorAll('[class*="ProductListItem_wrap"]');
                        debug.usedFallback = true;
                        debug.elementsFound = elements.length;
                    }

                    const products = [];

                    elements.forEach((el, idx) => {
                        try {
                            // Extract product data using the correct class names
                            const nameEl = el.querySelector('[class*="ProductTitle"]');
                            const discountEl = el.querySelector('[class*="DiscountPrice_discount"]');
                            const priceEl = el.querySelector('[class*="DiscountPrice_price"]');
                            const imgEl = el.querySelector('img');
                            const linkEl = el.querySelector('a');

                            const name = nameEl?.textContent?.trim();
                            const link = linkEl?.href;

                            // Extract product ID from link (channelProductNo parameter)
                            let productId = null;
                            if (link) {
                                const match = link.match(/channelProductNo=(\\d+)/);
                                productId = match ? match[1] : null;
                            }

                            // Extract discount rate (e.g., "23%" -> 23)
                            const discountText = discountEl?.textContent?.trim() || '';
                            const discountRate = parseInt(discountText.replace(/[^0-9]/g, '')) || null;

                            // Extract discounted price (e.g., "100,100원" -> 100100)
                            const priceText = priceEl?.textContent?.trim() || '';
                            const price = parseInt(priceText.replace(/[^0-9]/g, '')) || null;

                            // Calculate original price if we have discount
                            let originalPrice = null;
                            if (price && discountRate) {
                                originalPrice = Math.round(price / (1 - discountRate / 100));
                            }

                            // Only add products with valid name and link
                            if (name && link) {
                                products.push({
                                    product_id: productId,
                                    name: name,
                                    link: link,
                                    image: imgEl?.src,
                                    discounted_price: price,
                                    discount_rate: discountRate,
                                    original_price: originalPrice
                                });
                            }
                        } catch (err) {
                            console.error('Error extracting product:', err);
                        }
                    });

                    debug.productsExtracted = products.length;

                    return {
                        debug: debug,
                        products: products
                    };
                }
            """)

            # Log debug info
            logger.info(f"Debug: globalCount={result['debug']['globalCount']}, " +
                       f"elementsFound={result['debug']['elementsFound']}, " +
                       f"extracted={result['debug']['productsExtracted']}")

            products = result['products']

            # Remove duplicates based on product_id or link
            seen = set()
            unique_products = []
            duplicates = 0

            for product in products:
                # Use product_id as unique key, fallback to link
                key = product.get('product_id') or product.get('link')
                if key and key not in seen:
                    seen.add(key)
                    unique_products.append(product)
                else:
                    duplicates += 1

            if duplicates > 0:
                logger.info(f"Removed {duplicates} duplicate products ({len(products)} → {len(unique_products)})")

            logger.info(f"✓ Extracted {len(unique_products)} unique products from DOM")
            return unique_products

        except Exception as e:
            logger.error(f"Failed to extract products from DOM: {e}")
            return []
