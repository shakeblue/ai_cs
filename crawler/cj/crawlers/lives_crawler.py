"""
Lives Crawler
Crawler for /lives/ URLs using hybrid approach (embedded JSON + API interception)
"""

import asyncio
import logging
from typing import Dict, Any

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
