"""
Schema validator for broadcast data before database insertion
"""

from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Validate data against database schema requirements"""

    @staticmethod
    def validate_broadcast(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate broadcast record against schema

        Args:
            data: Broadcast data dictionary

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        required_fields = {
            'id': (int, 'Broadcast ID must be an integer'),
            'replay_url': (str, 'Replay URL must be a string'),
            'livebridge_url': (str, 'Livebridge URL must be a string'),
            'title': (str, 'Title must be a string'),
            'brand_name': (str, 'Brand name must be a string'),
        }

        for field, (expected_type, error_msg) in required_fields.items():
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
            elif not isinstance(data[field], expected_type):
                errors.append(f"{error_msg} (got {type(data[field]).__name__})")

        # Validate URL formats
        if data.get('replay_url') and not data['replay_url'].startswith('http'):
            errors.append("Replay URL must start with http:// or https://")

        if data.get('broadcast_url') and not data['broadcast_url'].startswith('http'):
            errors.append("Broadcast URL must start with http:// or https://")

        if data.get('livebridge_url') and not data['livebridge_url'].startswith('http'):
            errors.append("Livebridge URL must start with http:// or https://")

        # Validate numeric constraints
        if data.get('id') and data['id'] <= 0:
            errors.append("Broadcast ID must be positive")

        # Validate string lengths
        if data.get('title') and len(data['title']) > 500:
            errors.append("Title is too long (max 500 characters)")

        if data.get('brand_name') and len(data['brand_name']) > 200:
            errors.append("Brand name is too long (max 200 characters)")

        return len(errors) == 0, errors

    @staticmethod
    def validate_product(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate product record against schema

        Args:
            data: Product data dictionary

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        if not data.get('broadcast_id'):
            errors.append("Missing required field: broadcast_id")
        elif not isinstance(data['broadcast_id'], int):
            errors.append("broadcast_id must be an integer")

        if not data.get('name'):
            errors.append("Missing required field: name")
        elif not isinstance(data['name'], str):
            errors.append("Product name must be a string")

        # Validate numeric constraints
        numeric_fields = {
            'discount_rate': (0, 100),
            'discounted_price': (0, None),
            'original_price': (0, None),
            'stock': (0, None),
            'review_count': (0, None),
            'delivery_fee': (0, None),
        }

        for field, (min_val, max_val) in numeric_fields.items():
            value = data.get(field)
            if value is not None:
                if not isinstance(value, (int, float)):
                    errors.append(f"{field} must be numeric (got {type(value).__name__})")
                elif value < min_val:
                    errors.append(f"{field} must be >= {min_val}")
                elif max_val is not None and value > max_val:
                    errors.append(f"{field} must be <= {max_val}")

        # Validate URLs
        if data.get('image_url') and not data['image_url'].startswith('http'):
            errors.append("Image URL must start with http:// or https://")

        if data.get('link_url') and not data['link_url'].startswith('http'):
            errors.append("Link URL must start with http:// or https://")

        return len(errors) == 0, errors

    @staticmethod
    def validate_coupon(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate coupon record against schema

        Args:
            data: Coupon data dictionary

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        if not data.get('broadcast_id'):
            errors.append("Missing required field: broadcast_id")

        if not data.get('title'):
            errors.append("Missing required field: title")

        # Validate numeric constraints
        numeric_fields = ['benefit_value', 'min_order_amount', 'max_discount_amount']

        for field in numeric_fields:
            value = data.get(field)
            if value is not None and not isinstance(value, (int, float)):
                errors.append(f"{field} must be numeric")
            if value is not None and value < 0:
                errors.append(f"{field} must be non-negative")

        return len(errors) == 0, errors

    @staticmethod
    def validate_benefit(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate benefit record against schema

        Args:
            data: Benefit data dictionary

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        if not data.get('broadcast_id'):
            errors.append("Missing required field: broadcast_id")

        if not data.get('message'):
            errors.append("Missing required field: message")

        return len(errors) == 0, errors

    @staticmethod
    def validate_chat_message(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate chat message record against schema

        Args:
            data: Chat message data dictionary

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        if not data.get('broadcast_id'):
            errors.append("Missing required field: broadcast_id")

        if not data.get('message'):
            errors.append("Missing required field: message")

        return len(errors) == 0, errors

    @staticmethod
    def validate_metadata(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate crawl metadata record against schema

        Args:
            data: Metadata data dictionary

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        # Required fields
        if not data.get('broadcast_id'):
            errors.append("Missing required field: broadcast_id")

        if not data.get('source_url'):
            errors.append("Missing required field: source_url")

        if not data.get('crawled_at'):
            errors.append("Missing required field: crawled_at")

        # Validate source URL
        if data.get('source_url') and not data['source_url'].startswith('http'):
            errors.append("Source URL must start with http:// or https://")

        # Validate extraction method
        valid_methods = ['API', 'JSON', 'HYBRID']
        if data.get('extraction_method') and data['extraction_method'] not in valid_methods:
            errors.append(f"extraction_method must be one of: {', '.join(valid_methods)}")

        # Validate URL type
        valid_types = ['replays', 'lives', 'shortclips']
        if data.get('url_type') and data['url_type'] not in valid_types:
            errors.append(f"url_type must be one of: {', '.join(valid_types)}")

        return len(errors) == 0, errors

    @classmethod
    def validate_all(cls, transformed_data: Dict[str, Any]) -> Tuple[bool, Dict[str, List[str]]]:
        """
        Validate all transformed data at once

        Args:
            transformed_data: Dictionary with all transformed data
                (broadcast, products, coupons, benefits, chat, metadata)

        Returns:
            Tuple[bool, Dict[str, List[str]]]: (is_valid, dict_of_errors_by_type)
        """
        all_errors = {}

        # Validate broadcast
        valid, errors = cls.validate_broadcast(transformed_data.get('broadcast', {}))
        if errors:
            all_errors['broadcast'] = errors

        # Validate products
        for i, product in enumerate(transformed_data.get('products', [])):
            valid, errors = cls.validate_product(product)
            if errors:
                all_errors[f'product_{i}'] = errors

        # Validate coupons
        for i, coupon in enumerate(transformed_data.get('coupons', [])):
            valid, errors = cls.validate_coupon(coupon)
            if errors:
                all_errors[f'coupon_{i}'] = errors

        # Validate benefits
        for i, benefit in enumerate(transformed_data.get('benefits', [])):
            valid, errors = cls.validate_benefit(benefit)
            if errors:
                all_errors[f'benefit_{i}'] = errors

        # Validate chat messages
        for i, message in enumerate(transformed_data.get('chat', [])):
            valid, errors = cls.validate_chat_message(message)
            if errors:
                all_errors[f'chat_{i}'] = errors

        # Validate metadata
        valid, errors = cls.validate_metadata(transformed_data.get('metadata', {}))
        if errors:
            all_errors['metadata'] = errors

        return len(all_errors) == 0, all_errors
