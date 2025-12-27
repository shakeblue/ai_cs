"""
Lives Crawler
Crawler for /lives/ URLs using hybrid approach (embedded JSON + API interception)
"""

import asyncio
import logging
from typing import Dict, Any, List

from crawlers.base_crawler import BaseCrawler
from extractors.json_extractor import JSONExtractor
from extractors.api_extractor import APIExtractor

logger = logging.getLogger(__name__)


class LivesCrawler(BaseCrawler):
    """Crawler for /lives/ URLs using hybrid approach"""

    def get_extraction_method(self) -> str:
        return "HYBRID"

    def get_url_type(self) -> str:
        return "lives"

    async def extract_data(self, url: str) -> Dict[str, Any]:
        """
        Extract data from lives URL using hybrid approach (embedded JSON + API interception)

        Args:
            url: The lives URL to crawl

        Returns:
            Dict containing broadcast data
        """
        errors = []
        warnings = []

        # Setup API extractor BEFORE navigation
        api_extractor = APIExtractor()
        await api_extractor.setup_interception(self.page)

        # Navigate to page
        logger.info(f"Navigating to {url}")
        await self.page.goto(url, wait_until='domcontentloaded')
        logger.info("Page loaded, extracting data...")

        # Optimization #3: Smart wait for optional APIs (lives use embedded JSON for main data)
        # Wait for optional APIs (coupons, benefits) with smart timeout
        logger.info("Waiting for optional APIs (coupons, benefits)...")
        await api_extractor.wait_for_optional_apis(
            ['coupons', 'benefits'],
            max_wait=15.0,
            min_wait=3.0  # Wait at least 3s even if some APIs are captured
        )

        # Check what APIs were captured
        captured_apis = api_extractor.get_captured_apis()
        logger.info(f"Captured APIs: {captured_apis}")

        # Get HTML content for embedded JSON extraction
        html = await self.page.content()

        # Extract embedded JSON as primary data source
        json_data = JSONExtractor.extract_broadcast_json(html)
        if not json_data:
            self._add_error(errors, "JSONError", "Failed to extract embedded broadcast JSON")
            raise Exception("Failed to extract embedded broadcast JSON from HTML")

        # Extract broadcast fields from JSON
        broadcast_data = self._extract_broadcast_fields(json_data)

        # Extract products: Try multiple sources (API > DOM > JSON)
        json_products = broadcast_data.get('products', [])
        total_product_count = json_data.get('productCount', len(json_products))

        if total_product_count > len(json_products):
            logger.info(f"JSON has {len(json_products)}/{total_product_count} products - fetching via API pagination...")

            # Try to fetch all products via direct API pagination
            broadcast_id = json_data.get('id')
            api_products_raw = await self._fetch_all_products_via_api(broadcast_id, total_product_count)
            api_products = self._extract_products(api_products_raw) if api_products_raw else []

            # If API pagination successful, use it; otherwise fall back to DOM
            if api_products and len(api_products) >= total_product_count * 0.9:  # At least 90% of expected
                logger.info(f"✓ API pagination successful: {len(api_products)}/{total_product_count} products")
                broadcast_data['products'] = api_products  # Already transformed by _extract_products above
                broadcast_data['products_source'] = 'API'
            else:
                # Fallback to DOM extraction
                logger.info(f"API pagination incomplete ({len(api_products)} products), trying DOM extraction...")
                dom_products = await self._extract_products_from_dom()

                if len(dom_products) > len(api_products):
                    logger.info(f"✓ DOM extraction successful: {len(dom_products)} products")
                    broadcast_data['products'] = dom_products
                    broadcast_data['products_source'] = 'DOM'
                elif api_products:
                    broadcast_data['products'] = api_products  # Already transformed
                    broadcast_data['products_source'] = 'API'
                else:
                    logger.warning(f"Using JSON data ({len(json_products)} products)")
                    broadcast_data['products_source'] = 'JSON'
                    self._add_warning(
                        warnings,
                        "products",
                        f"Only {len(json_products)}/{total_product_count} products available.",
                        len(json_products)
                    )
        else:
            broadcast_data['products_source'] = 'JSON'

        # Extract coupons from API (if available)
        coupons = api_extractor.get_coupons()
        if coupons:
            broadcast_data['coupons'] = self._extract_coupons(coupons)
        else:
            self._add_warning(warnings, "coupons", "No coupons available", [])
            broadcast_data['coupons'] = []

        # Extract benefits from API (if available)
        benefits = api_extractor.get_benefits()
        if benefits:
            broadcast_data['live_benefits'] = self._extract_benefits(benefits)
        else:
            self._add_warning(warnings, "live_benefits", "No benefits available", [])
            broadcast_data['live_benefits'] = []

        # Extract comments with pagination (100 per page, keep odd indices for storage optimization)
        logger.info("Fetching all comments with pagination...")
        all_comments = await api_extractor.fetch_all_comments_paginated(
            broadcast_id=broadcast_data.get('broadcast_id'),
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

    def _extract_broadcast_fields(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract broadcast fields from JSON data"""
        broadcast_id = json_data.get('id')

        return {
            'broadcast_id': broadcast_id,
            'replay_url': json_data.get('broadcastReplayEndUrl') or self._construct_replay_url(broadcast_id),
            'broadcast_url': json_data.get('broadcastEndUrl') or self._construct_broadcast_url(broadcast_id),
            'livebridge_url': self.construct_livebridge_url(broadcast_id) if broadcast_id else None,
            'title': json_data.get('title'),
            'brand_name': json_data.get('nickname'),
            'description': json_data.get('description'),
            'broadcast_date': json_data.get('startDate'),
            'broadcast_end_date': json_data.get('endDate'),
            'expected_start_date': json_data.get('expectedStartDate'),
            'status': json_data.get('status'),
            'stand_by_image': json_data.get('standByImage'),
            'products': self._extract_products(json_data.get('shoppingProducts', []))
        }

    def _construct_replay_url(self, broadcast_id: int) -> str:
        """Construct replay URL from broadcast ID"""
        if broadcast_id:
            return f"https://view.shoppinglive.naver.com/replays/{broadcast_id}"
        return None

    def _construct_broadcast_url(self, broadcast_id: int) -> str:
        """Construct broadcast URL from broadcast ID"""
        if broadcast_id:
            return f"https://view.shoppinglive.naver.com/lives/{broadcast_id}?tr=lim"
        return None

    def _extract_products(self, products: list) -> list:
        """Extract product information with deduplication"""
        extracted_products = []
        seen_ids = set()

        for product in products:
            # Get product ID for deduplication
            product_id = product.get('key') or product.get('productNo')

            # Skip duplicates
            if product_id and product_id in seen_ids:
                continue
            if product_id:
                seen_ids.add(product_id)

            # Get price information
            discounted_price = product.get('discountedSalePrice') or product.get('price')
            price = product.get('price')
            discount_rate = product.get('discountRate', 0)

            # Calculate original price if we have discount rate
            original_price = None
            if discounted_price and discount_rate > 0:
                original_price = int(discounted_price / (1 - discount_rate / 100))
            elif price:
                original_price = price

            extracted_products.append({
                'product_id': product_id,
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
                'detail': benefit.get('detailMessage') or benefit.get('detail'),
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
        Extract products from DOM

        Returns:
            List of product dicts extracted from DOM
        """
        try:
            logger.info("Extracting products from DOM...")

            # Wait for page to fully render
            await asyncio.sleep(3)

            # Try to click main product tab/button (Korean: 상품)
            try:
                product_triggers = [
                    '#wa_product_modal_tab',
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
                            logger.info(f"✓ Clicked main product tab: {trigger}")
                            await asyncio.sleep(3)
                            tab_clicked = True
                            break
                    except Exception as e:
                        logger.debug(f"Trigger {trigger} failed: {e}")
                        continue

                if not tab_clicked:
                    logger.warning("Could not click main product tab")
            except Exception as e:
                logger.warning(f"Exception while clicking main product tab: {e}")

            # Extract from currently visible product panel
            return await self._extract_from_current_panel()

        except Exception as e:
            logger.error(f"Failed to extract products from DOM: {e}")
            return []

    async def _extract_from_current_panel(self) -> List[Dict[str, Any]]:
        """
        Extract products from the currently visible product panel

        Returns:
            List of product dicts
        """
        try:
            # Wait for products to appear
            try:
                await self.page.wait_for_selector(
                    '[class*="ProductList_item"], [class*="ProductListItem_wrap"]',
                    timeout=5000,
                    state='attached'
                )
            except:
                logger.debug("No products found in current panel")
                return []

            await asyncio.sleep(1)

            # Aggressive scrolling to trigger all lazy-loaded products (paginated API)
            # Products are loaded in pages of 30, so need to scroll enough to trigger all pages
            await self.page.evaluate("""
                async () => {
                    const panel = document.querySelector('#wa_product_modal_tabpanel')
                               || document.querySelector('[class*="ProductList"]');

                    if (panel) {
                        let prevCount = 0;
                        let stableCount = 0;

                        // Scroll up to 50 times or until product count stabilizes
                        for (let i = 0; i < 50; i++) {
                            panel.scrollTop = panel.scrollHeight;
                            await new Promise(resolve => setTimeout(resolve, 400));

                            // Check if product count has stabilized
                            const currentCount = document.querySelectorAll('[class*="ProductList_item"]').length;
                            if (currentCount === prevCount) {
                                stableCount++;
                                if (stableCount >= 5) {  // Stop if count stable for 5 iterations
                                    console.log(`Product count stabilized at ${currentCount} after ${i+1} scrolls`);
                                    break;
                                }
                            } else {
                                stableCount = 0;
                            }
                            prevCount = currentCount;
                        }
                    }
                }
            """)

            await asyncio.sleep(2)

            # Extract products
            result = await self.page.evaluate("""
                () => {
                    let elements = document.querySelectorAll('[class*="ProductList_item"]');
                    const products = [];

                    elements.forEach((el) => {
                        try {
                            const nameEl = el.querySelector('[class*="ProductTitle"]');
                            const discountEl = el.querySelector('[class*="DiscountPrice_discount"]');
                            const priceEl = el.querySelector('[class*="DiscountPrice_price"]');
                            const imgEl = el.querySelector('img');
                            const linkEl = el.querySelector('a');

                            const name = nameEl?.textContent?.trim();
                            const link = linkEl?.href;

                            if (name && link) {
                                let productId = null;
                                if (link) {
                                    const match = link.match(/channelProductNo=(\\d+)/);
                                    productId = match ? match[1] : null;
                                }

                                const discountRate = parseInt(discountEl?.textContent?.replace(/[^0-9]/g, '') || '') || null;
                                const price = parseInt(priceEl?.textContent?.replace(/[^0-9]/g, '') || '') || null;
                                const originalPrice = (price && discountRate) ? Math.round(price / (1 - discountRate / 100)) : null;

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
                        } catch (err) {}
                    });

                    return products;
                }
            """)

            return result

        except Exception as e:
            logger.debug(f"Failed to extract from current panel: {e}")
            return []

    async def _fetch_all_products_via_api(self, broadcast_id: int, expected_count: int) -> List[Dict[str, Any]]:
        """
        Fetch all products via direct API pagination

        Args:
            broadcast_id: The broadcast ID
            expected_count: Expected total product count

        Returns:
            List of raw product dicts from all API pages
        """
        try:
            # Get cookies from current page context
            cookies = await self.page.context.cookies()
            cookie_dict = {c['name']: c['value'] for c in cookies}

            # Use httpx for direct API requests
            import httpx

            all_products = []
            page_num = 0

            async with httpx.AsyncClient(verify=False) as client:
                while True:
                    api_url = (
                        f"https://apis.naver.com/live_commerce_web/viewer_api_web/v1/broadcast/{broadcast_id}/products"
                        f"?attachmentType=MAIN&categoryId=-1&page={page_num}&size=30&tr=lim"
                    )

                    try:
                        response = await client.get(
                            api_url,
                            cookies=cookie_dict,
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                                'Referer': f'https://view.shoppinglive.naver.com/lives/{broadcast_id}'
                            },
                            timeout=15.0
                        )

                        if response.status_code != 200:
                            logger.warning(f"API request failed with status {response.status_code} on page {page_num}")
                            break

                        data = response.json()
                        products = data.get('list', [])
                        total_pages = data.get('totalPage', 0)

                        logger.debug(f"Fetched page {page_num}: {len(products)} products (total pages: {total_pages})")

                        if not products:
                            break

                        all_products.extend(products)

                        # Check if we've fetched all pages
                        if total_pages and page_num >= total_pages - 1:
                            break

                        page_num += 1
                        await asyncio.sleep(0.3)  # Rate limiting

                    except Exception as e:
                        logger.debug(f"Error fetching page {page_num}: {e}")
                        break

            logger.info(f"✓ Fetched {len(all_products)} products from {page_num + 1} API pages")
            return all_products

        except Exception as e:
            logger.error(f"Failed to fetch products via API: {e}")
            return []
