"""
High-level interface for saving broadcast data to Supabase
"""

import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .config import SupabaseConfig
from .client import SupabaseClient
from .upserter import DatabaseUpserter

logger = logging.getLogger(__name__)


class BroadcastSaver:
    """
    High-level interface for saving broadcast data

    This is the main entry point for saving crawler data to Supabase.
    It provides simple methods for saving from files or dictionaries.

    Example usage:
        >>> saver = BroadcastSaver()
        >>> result = saver.save_from_json_file('broadcast_1776510.json')
        >>> print(result['status'])
        'success'
    """

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None
    ):
        """
        Initialize BroadcastSaver

        Args:
            supabase_url: Supabase project URL (optional, loads from env if not provided)
            supabase_key: Supabase API key (optional, loads from env if not provided)
        """
        if supabase_url and supabase_key:
            config = SupabaseConfig(url=supabase_url, key=supabase_key)
        else:
            config = SupabaseConfig.from_env()

        self.client = SupabaseClient(config)
        self.upserter = DatabaseUpserter(self.client)

        logger.info("BroadcastSaver initialized")

    def save_from_json_file(self, json_file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Save broadcast data from JSON file

        Args:
            json_file_path: Path to crawler output JSON file

        Returns:
            Dict with save status and statistics

        Example:
            >>> saver = BroadcastSaver()
            >>> result = saver.save_from_json_file('output/broadcast_1776510.json')
            >>> if result['status'] == 'success':
            ...     print(f"Saved {result['broadcast_id']}")
        """
        json_file_path = Path(json_file_path)

        if not json_file_path.exists():
            logger.error(f"File not found: {json_file_path}")
            return {
                'status': 'error',
                'error': f'File not found: {json_file_path}'
            }

        logger.info(f"Loading data from {json_file_path}")

        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                crawler_data = json.load(f)

            return self.save_from_dict(crawler_data)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {json_file_path}: {e}")
            return {
                'status': 'error',
                'error': f'Invalid JSON: {e}'
            }
        except Exception as e:
            logger.error(f"Failed to load file {json_file_path}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def save_from_dict(self, crawler_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save broadcast data from dictionary

        Args:
            crawler_data: Crawler output as dictionary

        Returns:
            Dict with save status and statistics

        Example:
            >>> saver = BroadcastSaver()
            >>> data = {...}  # crawler output
            >>> result = saver.save_from_dict(data)
        """
        return self.upserter.upsert_broadcast_data(crawler_data)

    def save_multiple(
        self,
        sources: List[Union[str, Path, Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Save multiple broadcasts from files or dictionaries

        Args:
            sources: List of file paths or dictionaries

        Returns:
            Dict with batch statistics

        Example:
            >>> saver = BroadcastSaver()
            >>> files = ['broadcast_1.json', 'broadcast_2.json']
            >>> result = saver.save_multiple(files)
            >>> print(f"Saved {result['successful']}/{result['total']}")
        """
        crawler_data_list = []

        for source in sources:
            if isinstance(source, dict):
                # Already a dictionary
                crawler_data_list.append(source)
            else:
                # Load from file
                source_path = Path(source)

                if not source_path.exists():
                    logger.warning(f"Skipping non-existent file: {source_path}")
                    continue

                try:
                    with open(source_path, 'r', encoding='utf-8') as f:
                        crawler_data = json.load(f)
                        crawler_data_list.append(crawler_data)
                except Exception as e:
                    logger.error(f"Failed to load {source_path}: {e}")
                    continue

        if not crawler_data_list:
            logger.error("No valid data to save")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'results': []
            }

        return self.upserter.upsert_batch(crawler_data_list)

    def save_from_directory(
        self,
        directory: Union[str, Path],
        pattern: str = 'broadcast_*.json'
    ) -> Dict[str, Any]:
        """
        Save all broadcast JSON files from a directory

        Args:
            directory: Directory containing JSON files
            pattern: Glob pattern for matching files (default: 'broadcast_*.json')

        Returns:
            Dict with batch statistics

        Example:
            >>> saver = BroadcastSaver()
            >>> result = saver.save_from_directory('output/')
            >>> print(f"Processed {result['total']} broadcasts")
        """
        directory = Path(directory)

        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'results': [],
                'error': f'Directory not found: {directory}'
            }

        # Find all matching files
        json_files = list(directory.glob(pattern))

        if not json_files:
            logger.warning(f"No files matching '{pattern}' found in {directory}")
            return {
                'total': 0,
                'successful': 0,
                'failed': 0,
                'results': []
            }

        logger.info(f"Found {len(json_files)} files matching '{pattern}' in {directory}")

        return self.save_multiple(json_files)

    def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            bool: True if connection is successful

        Example:
            >>> saver = BroadcastSaver()
            >>> if saver.test_connection():
            ...     print("Connected!")
        """
        try:
            return self.client.test_connection()
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.client.disconnect()


# Convenience function for one-off saves
def save_broadcast(
    json_file_path: Union[str, Path],
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to save a single broadcast

    This is a simple one-liner for saving a broadcast without
    creating a BroadcastSaver instance manually.

    Args:
        json_file_path: Path to broadcast JSON file
        supabase_url: Supabase URL (optional, loads from env)
        supabase_key: Supabase key (optional, loads from env)

    Returns:
        Dict with save status and statistics

    Example:
        >>> from persistence import save_broadcast
        >>> result = save_broadcast('broadcast_1776510.json')
        >>> print(result['status'])
    """
    with BroadcastSaver(supabase_url, supabase_key) as saver:
        return saver.save_from_json_file(json_file_path)
