"""
Database upserter with retry logic and transaction support
"""

import time
import logging
from typing import Dict, List, Any, Optional
from functools import wraps
from datetime import datetime

from .client import SupabaseClient
from .transformer import DataTransformer
from .validator import SchemaValidator

logger = logging.getLogger(__name__)


def retry_with_backoff(max_retries=3, base_delay=1):
    """
    Decorator for retry with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubles with each retry)

    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except ConnectionError as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Connection failed after {max_retries} attempts: {e}")
                        raise
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Connection error, retrying in {delay}s... "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(delay)
                except Exception as e:
                    # Don't retry on other exceptions
                    logger.error(f"Error in {func.__name__}: {e}")
                    raise
            return None
        return wrapper
    return decorator


class DatabaseUpserter:
    """Insert/update records in Supabase with error handling and retries"""

    def __init__(self, client: SupabaseClient):
        """
        Initialize database upserter

        Args:
            client: SupabaseClient instance
        """
        self.client = client

    @retry_with_backoff(max_retries=3, base_delay=1)
    def upsert_broadcast(self, broadcast_data: Dict[str, Any]) -> bool:
        """
        Upsert broadcast record

        Args:
            broadcast_data: Broadcast data dictionary

        Returns:
            bool: True if successful

        Raises:
            Exception: If upsert fails after retries
        """
        try:
            response = self.client.client.table('broadcasts').upsert(
                broadcast_data,
                on_conflict='id'
            ).execute()

            if response.data:
                logger.info(f"✓ Broadcast {broadcast_data['id']} upserted successfully")
                return True
            else:
                logger.warning(f"⚠ Broadcast upsert returned no data")
                return False

        except Exception as e:
            logger.error(f"✗ Failed to upsert broadcast {broadcast_data.get('id')}: {e}")
            raise

    @retry_with_backoff(max_retries=3, base_delay=1)
    def delete_child_records(self, broadcast_id: int):
        """
        Delete existing child records for a broadcast

        This ensures a clean slate before inserting new child records.

        Args:
            broadcast_id: Broadcast ID

        Raises:
            Exception: If deletion fails after retries
        """
        try:
            # Delete in reverse dependency order
            self.client.client.table('broadcast_chat').delete().eq('broadcast_id', broadcast_id).execute()
            self.client.client.table('broadcast_benefits').delete().eq('broadcast_id', broadcast_id).execute()
            self.client.client.table('broadcast_coupons').delete().eq('broadcast_id', broadcast_id).execute()
            self.client.client.table('broadcast_products').delete().eq('broadcast_id', broadcast_id).execute()

            logger.debug(f"Deleted existing child records for broadcast {broadcast_id}")

        except Exception as e:
            logger.warning(f"Failed to delete child records for broadcast {broadcast_id}: {e}")
            # Don't raise - continue with insertion even if deletion fails
            # (e.g., first time saving this broadcast)

    @retry_with_backoff(max_retries=3, base_delay=1)
    def insert_products(self, products: List[Dict[str, Any]]) -> int:
        """
        Insert product records

        Args:
            products: List of product dictionaries

        Returns:
            int: Number of products inserted

        Raises:
            Exception: If insertion fails after retries
        """
        if not products:
            logger.debug("No products to insert")
            return 0

        try:
            # Filter out products without product_id (required for unique constraint)
            valid_products = [p for p in products if p.get('product_id')]

            if not valid_products:
                logger.warning(f"All {len(products)} products missing product_id, skipping insertion")
                return 0

            if len(valid_products) < len(products):
                logger.warning(
                    f"Skipping {len(products) - len(valid_products)} products without product_id"
                )

            response = self.client.client.table('broadcast_products').insert(valid_products).execute()

            count = len(response.data) if response.data else 0
            logger.info(f"✓ Inserted {count} products")
            return count

        except Exception as e:
            logger.error(f"✗ Failed to insert products: {e}")
            raise

    @retry_with_backoff(max_retries=3, base_delay=1)
    def insert_coupons(self, coupons: List[Dict[str, Any]]) -> int:
        """
        Insert coupon records

        Args:
            coupons: List of coupon dictionaries

        Returns:
            int: Number of coupons inserted

        Raises:
            Exception: If insertion fails after retries
        """
        if not coupons:
            logger.debug("No coupons to insert")
            return 0

        try:
            response = self.client.client.table('broadcast_coupons').insert(coupons).execute()

            count = len(response.data) if response.data else 0
            logger.info(f"✓ Inserted {count} coupons")
            return count

        except Exception as e:
            logger.error(f"✗ Failed to insert coupons: {e}")
            raise

    @retry_with_backoff(max_retries=3, base_delay=1)
    def insert_benefits(self, benefits: List[Dict[str, Any]]) -> int:
        """
        Insert benefit records

        Args:
            benefits: List of benefit dictionaries

        Returns:
            int: Number of benefits inserted

        Raises:
            Exception: If insertion fails after retries
        """
        if not benefits:
            logger.debug("No benefits to insert")
            return 0

        try:
            response = self.client.client.table('broadcast_benefits').insert(benefits).execute()

            count = len(response.data) if response.data else 0
            logger.info(f"✓ Inserted {count} benefits")
            return count

        except Exception as e:
            logger.error(f"✗ Failed to insert benefits: {e}")
            raise

    @retry_with_backoff(max_retries=3, base_delay=1)
    def insert_chat(self, chat_messages: List[Dict[str, Any]]) -> int:
        """
        Insert chat message records

        Args:
            chat_messages: List of chat message dictionaries

        Returns:
            int: Number of chat messages inserted

        Raises:
            Exception: If insertion fails after retries
        """
        if not chat_messages:
            logger.debug("No chat messages to insert")
            return 0

        try:
            response = self.client.client.table('broadcast_chat').insert(chat_messages).execute()

            count = len(response.data) if response.data else 0
            logger.info(f"✓ Inserted {count} chat messages")
            return count

        except Exception as e:
            logger.error(f"✗ Failed to insert chat messages: {e}")
            raise

    @retry_with_backoff(max_retries=3, base_delay=1)
    def insert_metadata(self, metadata: Dict[str, Any]) -> bool:
        """
        Insert crawl metadata record

        Args:
            metadata: Metadata dictionary

        Returns:
            bool: True if successful

        Raises:
            Exception: If insertion fails after retries
        """
        try:
            response = self.client.client.table('crawl_metadata').insert(metadata).execute()

            if response.data:
                logger.info("✓ Inserted crawl metadata")
                return True
            else:
                logger.warning("⚠ Metadata insertion returned no data")
                return False

        except Exception as e:
            logger.error(f"✗ Failed to insert metadata: {e}")
            raise

    def upsert_broadcast_data(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upsert complete broadcast data (broadcast + all child records)

        This method orchestrates the entire save operation:
        1. Transform crawler data to database format
        2. Validate all data
        3. Upsert broadcast
        4. Delete old child records
        5. Insert new child records
        6. Insert metadata

        Args:
            crawler_data: Complete crawler output JSON

        Returns:
            Dict with status and statistics:
                - status: 'success' or 'error'
                - broadcast_id: Broadcast ID
                - records_saved: Dict with counts of each record type
                - errors: List of errors (if any)
        """
        start_time = time.time()

        try:
            # Transform data
            logger.info("Transforming crawler data to database format...")
            transformed = DataTransformer.transform_all(crawler_data)

            broadcast_id = transformed['broadcast']['id']
            logger.info(f"Processing broadcast {broadcast_id}: {transformed['broadcast'].get('title', '')[:50]}...")

            # Look up brand_id from brand_name
            brand_name = transformed['broadcast'].get('brand_name')
            if brand_name:
                logger.debug(f"Looking up brand_id for brand_name: '{brand_name}'")
                brand = self.client.get_brand_by_name(brand_name)
                if brand:
                    brand_id = brand.get('id')
                    transformed['broadcast']['brand_id'] = brand_id
                    logger.debug(f"✓ Found brand_id: {brand_id} for brand_name: '{brand_name}'")
                else:
                    logger.warning(f"⚠ Brand not found in database: '{brand_name}' - brand_id will be null")
                    transformed['broadcast']['brand_id'] = None
            else:
                logger.warning("⚠ No brand_name extracted - brand_id will be null")
                transformed['broadcast']['brand_id'] = None

            # Validate data
            logger.info("Validating data...")
            valid, errors = SchemaValidator.validate_all(transformed)

            if not valid:
                logger.error(f"Validation errors found: {errors}")
                return {
                    'status': 'error',
                    'broadcast_id': broadcast_id,
                    'error': 'Validation failed',
                    'validation_errors': errors
                }

            # Start saving (this is not a real transaction, but we handle errors per-operation)
            logger.info("Saving data to database...")

            # 1. Upsert broadcast
            logger.debug(f"Upserting broadcast {broadcast_id}...")
            self.upsert_broadcast(transformed['broadcast'])

            # 2. Delete old child records
            self.delete_child_records(broadcast_id)

            # 3. Insert new child records
            products_count = self.insert_products(transformed['products'])
            coupons_count = self.insert_coupons(transformed['coupons'])
            benefits_count = self.insert_benefits(transformed['benefits'])
            chat_count = self.insert_chat(transformed['chat'])

            # 4. Insert metadata
            self.insert_metadata(transformed['metadata'])

            # Calculate duration
            duration = time.time() - start_time

            result = {
                'status': 'success',
                'broadcast_id': broadcast_id,
                'records_saved': {
                    'products': products_count,
                    'coupons': coupons_count,
                    'benefits': benefits_count,
                    'chat': chat_count
                },
                'duration_seconds': round(duration, 2)
            }

            logger.info(f"✓ Successfully saved broadcast {broadcast_id} in {duration:.2f}s")
            logger.info(f"  Products: {products_count}, Coupons: {coupons_count}, "
                       f"Benefits: {benefits_count}, Chat: {chat_count}")

            return result

        except Exception as e:
            # Log error to database if possible
            try:
                error_metadata = {
                    'broadcast_id': crawler_data['broadcast']['broadcast_id'],
                    'source_url': crawler_data['metadata']['source_url'],
                    'crawled_at': crawler_data['metadata']['crawled_at'],
                    'status': 'error',
                    'error_message': str(e)
                }
                self.client.client.table('crawl_metadata').insert(error_metadata).execute()
            except Exception as meta_error:
                logger.warning(f"Failed to save error metadata: {meta_error}")

            logger.error(f"✗ Failed to save broadcast data: {e}")

            # Log the exception traceback for debugging
            import traceback
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")

            return {
                'status': 'error',
                'broadcast_id': crawler_data.get('broadcast', {}).get('broadcast_id'),
                'error': str(e),
                'error_type': type(e).__name__,
                'duration_seconds': round(time.time() - start_time, 2)
            }

    def upsert_batch(self, crawler_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Upsert multiple broadcasts efficiently

        Args:
            crawler_data_list: List of crawler output JSONs

        Returns:
            Dict with batch statistics:
                - total: Total number of broadcasts
                - successful: Number successfully saved
                - failed: Number that failed
                - results: List of individual results
        """
        logger.info(f"Starting batch upsert for {len(crawler_data_list)} broadcasts...")

        results = []
        successful = 0
        failed = 0

        for i, crawler_data in enumerate(crawler_data_list, 1):
            broadcast_id = crawler_data.get('broadcast', {}).get('broadcast_id', 'unknown')
            logger.info(f"Processing broadcast {i}/{len(crawler_data_list)}: {broadcast_id}")

            result = self.upsert_broadcast_data(crawler_data)
            results.append(result)

            if result['status'] == 'success':
                successful += 1
            else:
                failed += 1

        logger.info(f"Batch upsert complete: {successful} successful, {failed} failed")

        return {
            'total': len(crawler_data_list),
            'successful': successful,
            'failed': failed,
            'results': results
        }
