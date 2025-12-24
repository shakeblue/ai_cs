"""
Configuration for Supabase connection
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class SupabaseConfig:
    """Configuration for Supabase database connection"""

    url: str
    key: str

    @classmethod
    def from_env(cls) -> 'SupabaseConfig':
        """
        Load configuration from environment variables

        Environment variables required:
            - SUPABASE_URL: Supabase project URL
            - SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY: Supabase API key

        Returns:
            SupabaseConfig: Configuration instance

        Raises:
            ValueError: If required environment variables are missing
        """
        url = os.getenv('SUPABASE_URL')
        # Try service key first (for server-side operations), fallback to anon key
        key = os.getenv('SUPABASE_SERVICE_KEY') or os.getenv('SUPABASE_ANON_KEY')

        if not url:
            raise ValueError(
                "SUPABASE_URL environment variable is required. "
                "Please set it in your .env file or environment."
            )

        if not key:
            raise ValueError(
                "SUPABASE_SERVICE_KEY or SUPABASE_ANON_KEY environment variable is required. "
                "Please set it in your .env file or environment."
            )

        return cls(url=url, key=key)

    def validate(self) -> bool:
        """
        Validate configuration

        Returns:
            bool: True if configuration is valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.url:
            raise ValueError("Supabase URL is required")

        if not self.url.startswith('https://'):
            raise ValueError("Supabase URL must start with https://")

        if not self.key:
            raise ValueError("Supabase API key is required")

        if len(self.key) < 20:
            raise ValueError("Supabase API key appears to be invalid (too short)")

        return True
