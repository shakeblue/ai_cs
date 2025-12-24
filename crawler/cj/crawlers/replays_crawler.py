"""
Replays Crawler
Crawler for /replays/ URLs using API interception
"""

import asyncio
import logging
from typing import Dict, Any

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

        # Wait longer for late-loading APIs (coupons, benefits, comments) and for async response handlers to complete
        await asyncio.sleep(30)

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

        # Extract comments
        comments = api_extractor.get_comments()
        if comments:
            broadcast_data['live_chat'] = self._extract_comments(comments)
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
