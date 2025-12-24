"""
ShortClips Crawler
Crawler for /shortclips/ URLs using hybrid approach (JSON or API)
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from crawlers.base_crawler import BaseCrawler
from extractors.json_extractor import JSONExtractor
from extractors.api_extractor import APIExtractor

logger = logging.getLogger(__name__)


class ShortClipsCrawler(BaseCrawler):
    """Crawler for /shortclips/ URLs using hybrid approach"""

    def get_extraction_method(self) -> str:
        return "HYBRID"

    def get_url_type(self) -> str:
        return "shortclips"

    async def _extract_shortclip_from_window(self) -> Optional[Dict[str, Any]]:
        """
        Extract window.__shortclip data using JavaScript evaluation

        Returns:
            Shortclip data dict, or None if not found
        """
        try:
            shortclip_data = await self.page.evaluate("""
                () => {
                    if (typeof window.__shortclip === 'string') {
                        try {
                            return JSON.parse(window.__shortclip);
                        } catch (e) {
                            console.error('Failed to parse __shortclip:', e);
                            return null;
                        }
                    } else if (typeof window.__shortclip === 'object' && window.__shortclip !== null) {
                        return window.__shortclip;
                    }
                    return null;
                }
            """)
            return shortclip_data
        except Exception as e:
            logger.debug(f"Failed to extract window.__shortclip: {e}")
            return None

    async def extract_data(self, url: str) -> Dict[str, Any]:
        """
        Extract data from shortclips URL using hybrid approach

        Args:
            url: The shortclips URL to crawl

        Returns:
            Dict containing broadcast data
        """
        errors = []
        warnings = []

        # Navigate to page
        logger.info(f"Navigating to {url}")
        await self.page.goto(url, wait_until='domcontentloaded')
        logger.info("Page loaded, trying to extract window.__shortclip...")

        # Wait a bit for JavaScript to execute
        await asyncio.sleep(2)

        # Try extracting window.__shortclip using JavaScript evaluation (most reliable)
        shortclip_data = await self._extract_shortclip_from_window()

        if shortclip_data:
            logger.info("Successfully extracted shortclip data from window.__shortclip")
            broadcast_data = self._extract_from_shortclip_json(shortclip_data)
        else:
            # Try HTML parsing as fallback
            logger.info("window.__shortclip not found, trying HTML parsing...")
            html = await self.page.content()
            json_data = JSONExtractor.extract_shortclip_json(html)

            if json_data:
                logger.info("Successfully extracted shortclip data from HTML parsing")
                broadcast_data = self._extract_from_shortclip_json(json_data)
            else:
                # Last resort: API interception
                logger.info("Embedded JSON not found, falling back to API interception...")
                broadcast_data = await self._extract_from_api(url, errors, warnings)

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

    def _extract_from_shortclip_json(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from shortclip JSON

        Args:
            json_data: The shortclip JSON data from window.__shortclip

        Returns:
            Broadcast data dict
        """
        # Extract shortclip ID (can be used as broadcast_id)
        shortclip_id = json_data.get('shortclipId')

        # Extract broadcast URL from shortclip data
        broadcast_url = json_data.get('broadcastLinkUrl')

        # Try to extract broadcast_id from the broadcast URL
        broadcast_id = None
        if broadcast_url:
            import re
            match = re.search(r'/(?:lives|replays)/(\d+)', broadcast_url)
            if match:
                broadcast_id = int(match.group(1))

        # If no broadcast_id found, use shortclip_id as fallback
        if not broadcast_id:
            broadcast_id = shortclip_id

        return {
            'broadcast_id': broadcast_id,
            'shortclip_id': shortclip_id,
            'replay_url': self._construct_replay_url(broadcast_id) if broadcast_id else None,
            'broadcast_url': broadcast_url or (self._construct_broadcast_url(broadcast_id) if broadcast_id else None),
            'livebridge_url': self.construct_livebridge_url(broadcast_id) if broadcast_id else None,
            'title': json_data.get('title'),
            'brand_name': json_data.get('channelName'),
            'description': json_data.get('description'),
            'broadcast_date': json_data.get('expectedExposeAt'),  # Use expected expose time for shortclips
            'broadcast_end_date': None,  # Not available in shortclip JSON
            'expected_start_date': json_data.get('expectedExposeAt'),
            'stand_by_image': json_data.get('thumbnailUrl') or json_data.get('standByImage'),
            'status': json_data.get('status'),
            'products': self._extract_shortclip_products(json_data.get('products', [])),
            'coupons': [],  # Usually not in shortclip JSON
            'live_benefits': [],  # Usually not in shortclip JSON
            'live_chat': [],  # Not available for shortclips
            'channel_id': json_data.get('channelId'),
            'channel_image_url': json_data.get('channelImageUrl'),
            'channel_link_url': json_data.get('channelLinkUrl'),
            'broadcaster_id': json_data.get('broadcasterId'),
            'vid': json_data.get('vid'),
            'vod_media_url': json_data.get('vodMediaUrl')
        }

    async def _extract_from_api(self, url: str, errors: list, warnings: list) -> Dict[str, Any]:
        """
        Extract data from API interception

        Args:
            url: The URL to reload and intercept
            errors: Errors list to append to
            warnings: Warnings list to append to

        Returns:
            Broadcast data dict
        """
        # Setup API extractor
        api_extractor = APIExtractor()
        await api_extractor.setup_interception(self.page)

        # Reload page with API interception
        await self.page.reload(wait_until='networkidle')
        logger.info("Page reloaded, waiting for APIs...")

        # Wait for APIs
        await asyncio.sleep(5)

        # Get shortclip data from API
        shortclip_data = api_extractor.get_shortclip_data()

        if not shortclip_data:
            self._add_error(errors, "APIError", "Failed to capture shortclip API")
            raise Exception("Failed to extract shortclip data from both JSON and API")

        # Extract broadcast from shortclip API
        broadcast = shortclip_data.get('broadcast', {})
        broadcast_id = broadcast.get('id')

        return {
            'broadcast_id': broadcast_id,
            'replay_url': broadcast.get('broadcastReplayEndUrl') or self._construct_replay_url(broadcast_id),
            'broadcast_url': broadcast.get('broadcastEndUrl') or self._construct_broadcast_url(broadcast_id),
            'livebridge_url': self.construct_livebridge_url(broadcast_id) if broadcast_id else None,
            'title': broadcast.get('title'),
            'brand_name': broadcast.get('nickname'),
            'description': broadcast.get('description'),
            'broadcast_date': broadcast.get('startDate'),
            'broadcast_end_date': broadcast.get('endDate'),
            'expected_start_date': broadcast.get('expectedStartDate'),
            'status': broadcast.get('status'),
            'products': self._extract_products(broadcast.get('shoppingProducts', [])),
            'coupons': [],
            'live_benefits': [],
            'live_chat': []
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
        """Extract product information (from API data)"""
        extracted_products = []

        for product in products:
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

    def _extract_shortclip_products(self, products: list) -> list:
        """Extract product information from shortclip JSON structure"""
        extracted_products = []

        for product in products:
            # Get price information
            discounted_price = product.get('price')
            original_price = product.get('originalPrice')
            discount_rate = product.get('discountRate', 0)

            # Calculate original price if not available but discount rate exists
            if not original_price and discounted_price and discount_rate > 0:
                original_price = int(discounted_price / (1 - discount_rate / 100))

            extracted_products.append({
                'product_id': product.get('productNo'),
                'name': product.get('name'),
                'brand_name': product.get('brandName'),
                'discount_rate': discount_rate,
                'discounted_price': discounted_price,
                'original_price': original_price,
                'stock': product.get('stock'),
                'image': product.get('imageUrl'),
                'link': product.get('productBridgeUrl'),
                'review_count': product.get('reviewCount'),
                'delivery_fee': product.get('deliveryFee'),
                'status': product.get('status'),
                'represent': product.get('represent'),
                'introducing': product.get('introducing'),
                'category': product.get('category'),
                'arrival_guarantee': product.get('arrivalGuarantee')
            })

        return extracted_products
