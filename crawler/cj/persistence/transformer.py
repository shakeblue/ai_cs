"""
Data transformer for converting crawler JSON to database schema
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transform crawler JSON format to database-ready format"""

    @staticmethod
    def transform_broadcast(crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform broadcast data from crawler JSON to DB schema

        Args:
            crawler_data: Complete crawler output with metadata and broadcast sections

        Returns:
            Dict: Broadcast data ready for database insertion
        """
        broadcast = crawler_data.get('broadcast', {})
        metadata = crawler_data.get('metadata', {})

        return {
            'id': broadcast.get('broadcast_id'),
            'replay_url': broadcast.get('replay_url'),
            'broadcast_url': broadcast.get('broadcast_url'),
            'livebridge_url': broadcast.get('livebridge_url'),
            'title': broadcast.get('title', ''),
            'brand_name': broadcast.get('brand_name', ''),
            'description': broadcast.get('description'),
            'broadcast_date': broadcast.get('broadcast_date'),
            'broadcast_end_date': broadcast.get('broadcast_end_date'),
            'expected_start_date': broadcast.get('expected_start_date'),
            'status': broadcast.get('status'),
            'stand_by_image': broadcast.get('stand_by_image'),
            'broadcast_type': metadata.get('url_type'),
            'raw_data': crawler_data  # Store complete original JSON
        }

    @staticmethod
    def transform_products(broadcast_id: int, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform products data from crawler JSON to DB schema

        Args:
            broadcast_id: Broadcast ID
            products: List of product dictionaries from crawler

        Returns:
            List[Dict]: Products data ready for database insertion
        """
        transformed_products = []

        for product in products:
            # Handle both 'image' and 'image_url' field names
            image_url = product.get('image') or product.get('image_url')

            # Handle both 'link' and 'link_url' field names
            link_url = product.get('link') or product.get('link_url')

            transformed_product = {
                'broadcast_id': broadcast_id,
                'product_id': str(product['product_id']) if product.get('product_id') else None,
                'name': product.get('name', ''),
                'brand_name': product.get('brand_name'),
                'discount_rate': product.get('discount_rate'),
                'discounted_price': product.get('discounted_price'),
                'original_price': product.get('original_price'),
                'stock': product.get('stock'),
                'image_url': image_url,
                'link_url': link_url,
                'review_count': product.get('review_count'),
                'delivery_fee': product.get('delivery_fee'),
                'raw_data': product  # Store complete original product data
            }

            transformed_products.append(transformed_product)

        return transformed_products

    @staticmethod
    def transform_coupons(broadcast_id: int, coupons: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform coupons data from crawler JSON to DB schema

        Args:
            broadcast_id: Broadcast ID
            coupons: List of coupon dictionaries from crawler

        Returns:
            List[Dict]: Coupons data ready for database insertion
        """
        transformed_coupons = []

        for coupon in coupons:
            transformed_coupon = {
                'broadcast_id': broadcast_id,
                'title': coupon.get('title', ''),
                'benefit_type': coupon.get('benefit_type'),
                'benefit_unit': coupon.get('benefit_unit'),
                'benefit_value': coupon.get('benefit_value'),
                'min_order_amount': coupon.get('min_order_amount'),
                'max_discount_amount': coupon.get('max_discount_amount'),
                'valid_start': coupon.get('valid_start'),
                'valid_end': coupon.get('valid_end'),
                'raw_data': coupon  # Store complete original coupon data
            }

            transformed_coupons.append(transformed_coupon)

        return transformed_coupons

    @staticmethod
    def transform_benefits(broadcast_id: int, benefits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform benefits data from crawler JSON to DB schema

        Args:
            broadcast_id: Broadcast ID
            benefits: List of benefit dictionaries from crawler

        Returns:
            List[Dict]: Benefits data ready for database insertion
        """
        transformed_benefits = []

        for benefit in benefits:
            # Handle both 'id' and 'benefit_id' field names
            benefit_id = benefit.get('id') or benefit.get('benefit_id')

            # Handle both 'type' and 'benefit_type' field names
            benefit_type = benefit.get('type') or benefit.get('benefit_type')

            transformed_benefit = {
                'broadcast_id': broadcast_id,
                'benefit_id': str(benefit_id) if benefit_id else None,
                'message': benefit.get('message', ''),
                'detail': benefit.get('detail'),
                'benefit_type': benefit_type,
                'raw_data': benefit  # Store complete original benefit data
            }

            transformed_benefits.append(transformed_benefit)

        return transformed_benefits

    @staticmethod
    def transform_chat(broadcast_id: int, chat_messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform chat messages from crawler JSON to DB schema

        Args:
            broadcast_id: Broadcast ID
            chat_messages: List of chat message dictionaries from crawler

        Returns:
            List[Dict]: Chat messages ready for database insertion
        """
        transformed_chat = []

        for message in chat_messages:
            transformed_message = {
                'broadcast_id': broadcast_id,
                'nickname': message.get('nickname'),
                'message': message.get('message', ''),
                'created_at_source': message.get('created_at'),
                'comment_type': message.get('comment_type'),
                'raw_data': message  # Store complete original message data
            }

            transformed_chat.append(transformed_message)

        return transformed_chat

    @staticmethod
    def transform_metadata(crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform crawl metadata from crawler JSON to DB schema

        Args:
            crawler_data: Complete crawler output with metadata section

        Returns:
            Dict: Metadata ready for database insertion
        """
        metadata = crawler_data.get('metadata', {})
        broadcast = crawler_data.get('broadcast', {})

        return {
            'broadcast_id': broadcast.get('broadcast_id'),
            'source_url': metadata.get('source_url', ''),
            'extraction_method': metadata.get('extraction_method'),
            'url_type': metadata.get('url_type'),
            'crawler_version': metadata.get('crawler_version'),
            'errors': metadata.get('errors', []),
            'warnings': metadata.get('warnings', []),
            'crawled_at': metadata.get('crawled_at'),
            'status': 'success' if not metadata.get('errors') else 'partial',
            'error_message': None
        }

    @classmethod
    def transform_all(cls, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform complete crawler output to database-ready format

        This is a convenience method that transforms all data at once.

        Args:
            crawler_data: Complete crawler output

        Returns:
            Dict containing all transformed data:
                - broadcast: Broadcast data
                - products: List of products
                - coupons: List of coupons
                - benefits: List of benefits
                - chat: List of chat messages
                - metadata: Crawl metadata
        """
        broadcast_data = crawler_data.get('broadcast', {})
        broadcast_id = broadcast_data.get('broadcast_id')

        if not broadcast_id:
            raise ValueError("Missing broadcast_id in crawler data")

        return {
            'broadcast': cls.transform_broadcast(crawler_data),
            'products': cls.transform_products(
                broadcast_id,
                broadcast_data.get('products', [])
            ),
            'coupons': cls.transform_coupons(
                broadcast_id,
                broadcast_data.get('coupons', [])
            ),
            'benefits': cls.transform_benefits(
                broadcast_id,
                broadcast_data.get('live_benefits', [])
            ),
            'chat': cls.transform_chat(
                broadcast_id,
                broadcast_data.get('live_chat', [])
            ),
            'metadata': cls.transform_metadata(crawler_data)
        }

    @staticmethod
    def clean_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove keys with None values from dictionary

        This is useful for optional fields where None should not be inserted.

        Args:
            data: Dictionary to clean

        Returns:
            Dict: Dictionary with None values removed
        """
        return {k: v for k, v in data.items() if v is not None}
