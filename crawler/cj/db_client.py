"""
Database client for Supabase connection
Handles connection initialization, retry logic, and SSL configuration
"""

import os
import sys
import ssl
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from supabase import create_client, Client
import warnings
import urllib3

# Disable SSL warnings for development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


class SupabaseClient:
    """
    Supabase database client with connection management and retry logic
    """

    def __init__(self):
        """Initialize Supabase client"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_SECRET_KEY') or os.getenv('SUPABASE_SERVICE_KEY')

        if not self.url or not self.key:
            raise ValueError(
                "Missing Supabase credentials. Set SUPABASE_URL and "
                "SUPABASE_SECRET_KEY in .env file"
            )

        self.client: Optional[Client] = None
        self._connect()

    def _connect(self):
        """Establish connection to Supabase with SSL handling"""
        try:
            # Create httpx client with SSL verification disabled for development
            # TODO: Use proper SSL certificates in production
            import httpx

            # Create custom HTTP client with SSL verification disabled
            http_client = httpx.Client(verify=False, timeout=30.0)

            # Create Supabase client
            self.client = create_client(self.url, self.key)

            # Replace the default httpx client with our custom one
            # This allows us to disable SSL verification
            self.client.postgrest.session = http_client

            print(f"✅ Connected to Supabase: {self.url}")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            raise

    def reconnect(self):
        """Reconnect to Supabase"""
        self._connect()

    def execute_with_retry(self, operation, max_retries=3, base_delay=1):
        """
        Execute a database operation with exponential backoff retry

        Args:
            operation: Function to execute
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for exponential backoff

        Returns:
            Result of the operation

        Raises:
            Exception: If all retries fail
        """
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise

                delay = base_delay * (2 ** attempt)
                print(f"⚠️ Operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"   Retrying in {delay}s...")
                time.sleep(delay)

    # ==========================================
    # Platform Operations
    # ==========================================

    def get_platform_by_id(self, platform_id: str) -> Optional[Dict[str, Any]]:
        """Get platform by ID"""
        def operation():
            result = self.client.table('platforms').select('*').eq('id', platform_id).execute()
            return result.data[0] if result.data else None

        return self.execute_with_retry(operation)

    def get_platform_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get platform by name"""
        def operation():
            result = self.client.table('platforms').select('*').eq('name', name).execute()
            return result.data[0] if result.data else None

        return self.execute_with_retry(operation)

    # ==========================================
    # Brand Operations
    # ==========================================

    def get_brand_by_id(self, brand_id: str) -> Optional[Dict[str, Any]]:
        """Get brand by ID"""
        def operation():
            result = self.client.table('brands').select('*').eq('id', brand_id).execute()
            return result.data[0] if result.data else None

        return self.execute_with_retry(operation)

    def get_brand_by_name(self, name: str, platform_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get brand by name (optionally filtered by platform)"""
        def operation():
            query = self.client.table('brands').select('*').eq('name', name)
            if platform_id:
                query = query.eq('platform_id', platform_id)
            result = query.execute()
            return result.data[0] if result.data else None

        return self.execute_with_retry(operation)

    def get_active_brands(self, platform_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all active brands (optionally filtered by platform)"""
        def operation():
            query = self.client.table('brands').select('*').eq('status', 'active')
            if platform_id:
                query = query.eq('platform_id', platform_id)
            result = query.execute()
            return result.data

        return self.execute_with_retry(operation)

    # ==========================================
    # Crawler Execution Operations
    # ==========================================

    def create_execution(
        self,
        brand_id: str,
        platform_id: str,
        trigger_type: str = 'manual'
    ) -> Dict[str, Any]:
        """
        Create a new crawler execution record

        Args:
            brand_id: Brand UUID
            platform_id: Platform UUID
            trigger_type: 'scheduled' or 'manual'

        Returns:
            Created execution record
        """
        def operation():
            execution_data = {
                'brand_id': brand_id,
                'platform_id': platform_id,
                'trigger_type': trigger_type,
                'status': 'pending'
            }
            result = self.client.table('crawler_executions').insert(execution_data).execute()
            return result.data[0]

        return self.execute_with_retry(operation)

    def update_execution_status(
        self,
        execution_id: str,
        status: str,
        items_found: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """
        Update crawler execution status

        Args:
            execution_id: Execution UUID
            status: 'pending', 'running', 'success', or 'failed'
            items_found: Number of events found (optional)
            error_message: Error message if status is 'failed' (optional)
        """
        def operation():
            update_data = {'status': status}

            if status in ['success', 'failed']:
                update_data['completed_at'] = 'now()'

            if items_found is not None:
                update_data['items_found'] = items_found

            if error_message:
                update_data['error_message'] = error_message

            result = self.client.table('crawler_executions').update(update_data).eq('id', execution_id).execute()
            return result.data[0] if result.data else None

        return self.execute_with_retry(operation)

    # ==========================================
    # Event Operations
    # ==========================================

    def upsert_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert or update an event (handles duplicates)

        Args:
            event_data: Event data dictionary with required fields

        Returns:
            Upserted event record
        """
        def operation():
            # Ensure required fields exist
            required_fields = ['external_id', 'brand_id', 'platform_id']
            for field in required_fields:
                if field not in event_data:
                    raise ValueError(f"Missing required field: {field}")

            # Upsert with conflict resolution on (platform_id, external_id)
            result = self.client.table('events').upsert(
                event_data,
                on_conflict='platform_id,external_id'
            ).execute()

            return result.data[0] if result.data else None

        return self.execute_with_retry(operation)

    def upsert_events_bulk(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Bulk insert/update events

        Args:
            events: List of event data dictionaries

        Returns:
            List of upserted event records
        """
        def operation():
            result = self.client.table('events').upsert(
                events,
                on_conflict='platform_id,external_id'
            ).execute()

            return result.data

        return self.execute_with_retry(operation)

    # ==========================================
    # Configuration Operations
    # ==========================================

    def get_config(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value by key"""
        def operation():
            result = self.client.table('crawler_config').select('value').eq('key', key).execute()
            return result.data[0]['value'] if result.data else default

        return self.execute_with_retry(operation)

    def get_all_config(self) -> Dict[str, str]:
        """Get all configuration as a dictionary"""
        def operation():
            result = self.client.table('crawler_config').select('key, value').execute()
            return {row['key']: row['value'] for row in result.data}

        return self.execute_with_retry(operation)


# Singleton instance
_db_client: Optional[SupabaseClient] = None


def get_db_client() -> SupabaseClient:
    """
    Get singleton database client instance

    Returns:
        SupabaseClient instance
    """
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
    return _db_client


def test_connection():
    """Test database connection and print status"""
    print("=" * 60)
    print("Testing Supabase Connection")
    print("=" * 60)

    try:
        db = get_db_client()

        # Test platform query
        platforms = db.execute_with_retry(
            lambda: db.client.table('platforms').select('*').execute()
        )
        print(f"\n✅ Platforms found: {len(platforms.data)}")
        for p in platforms.data:
            print(f"   - {p['name']} ({p['status']})")

        # Test brand query
        brands = db.execute_with_retry(
            lambda: db.client.table('brands').select('*').execute()
        )
        print(f"\n✅ Brands found: {len(brands.data)}")
        for b in brands.data:
            print(f"   - {b['name']} → {b['search_text']} ({b['status']})")

        # Test config query
        config = db.get_all_config()
        print(f"\n✅ Config entries: {len(config)}")
        for key, value in config.items():
            print(f"   - {key}: {value}")

        print("\n" + "=" * 60)
        print("✅ Connection test successful!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    # Run connection test
    test_connection()
