"""
Supabase client wrapper for broadcast crawler
"""

import os
import logging
import ssl
import urllib3
from typing import Optional

# Disable SSL warnings (for development)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Monkey-patch httpx to disable SSL verification (for development)
try:
    import httpx
    original_httpx_client_init = httpx.Client.__init__

    def patched_httpx_client_init(self, *args, **kwargs):
        kwargs['verify'] = False
        return original_httpx_client_init(self, *args, **kwargs)

    httpx.Client.__init__ = patched_httpx_client_init
except ImportError:
    pass  # httpx not available

from supabase import create_client, Client

from .config import SupabaseConfig

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Manages Supabase database connection for broadcast crawler

    This is a separate client from the existing supabase_client.py
    which handles live_broadcasts schema. This client is specifically
    for the broadcasts schema (Phase 3).
    """

    def __init__(self, config: Optional[SupabaseConfig] = None):
        """
        Initialize Supabase client

        Args:
            config: SupabaseConfig instance. If None, loads from environment.
        """
        self.config = config or SupabaseConfig.from_env()
        self.config.validate()
        self._client: Optional[Client] = None

    @property
    def client(self) -> Client:
        """
        Get or create Supabase client instance (lazy initialization)

        Returns:
            Client: Supabase client instance
        """
        if self._client is None:
            self.connect()
        return self._client

    def connect(self) -> Client:
        """
        Establish connection to Supabase

        Returns:
            Client: Supabase client instance
        """
        try:
            # Disable SSL verification for development
            os.environ['HTTPX_VERIFY_SSL'] = '0'
            os.environ['REQUESTS_CA_BUNDLE'] = ''
            os.environ['CURL_CA_BUNDLE'] = ''

            self._client = create_client(self.config.url, self.config.key)
            logger.info("Successfully connected to Supabase")
            return self._client
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            raise

    def disconnect(self):
        """
        Close connection to Supabase

        Note: Supabase Python client doesn't require explicit disconnect,
        but this method is provided for consistency and future-proofing.
        """
        self._client = None
        logger.info("Disconnected from Supabase")

    def test_connection(self) -> bool:
        """
        Test database connection by querying broadcasts table

        Returns:
            bool: True if connection is successful

        Raises:
            Exception: If connection test fails
        """
        try:
            # Try to query the broadcasts table (will fail if table doesn't exist)
            result = self.client.table('broadcasts').select('id').limit(1).execute()
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
