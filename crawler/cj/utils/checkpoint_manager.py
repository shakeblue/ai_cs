"""
Checkpoint Manager for Crawler Resume Capability
Optimization #8: Add Progress Tracking & Resume Capability
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class CheckpointManager:
    """
    Manages crawler checkpoints for resume capability

    Features:
    - Save progress after each chunk
    - Resume from last successful checkpoint
    - Track processed URLs to avoid duplicates
    - Store statistics and errors
    """

    def __init__(self, execution_id: str, checkpoint_dir: str = "crawler/cj/checkpoints"):
        """
        Initialize checkpoint manager

        Args:
            execution_id: Unique execution ID
            checkpoint_dir: Directory to store checkpoint files
        """
        self.execution_id = execution_id
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_file = self.checkpoint_dir / f"checkpoint_{execution_id}.json"

        # Create checkpoint directory if it doesn't exist
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"CheckpointManager initialized for execution {execution_id}")

    def save_checkpoint(
        self,
        processed_urls: List[str],
        total_urls: int,
        items_saved: int,
        current_chunk: int,
        total_chunks: int,
        errors: List[Dict[str, Any]] = None
    ):
        """
        Save checkpoint to disk

        Args:
            processed_urls: List of URLs already processed
            total_urls: Total number of URLs to process
            items_saved: Number of items successfully saved
            current_chunk: Current chunk number
            total_chunks: Total number of chunks
            errors: List of errors encountered
        """
        checkpoint_data = {
            'execution_id': self.execution_id,
            'timestamp': datetime.now().isoformat(),
            'processed_urls': processed_urls,
            'total_urls': total_urls,
            'items_saved': items_saved,
            'current_chunk': current_chunk,
            'total_chunks': total_chunks,
            'progress_percentage': round((len(processed_urls) / total_urls * 100), 2) if total_urls > 0 else 0,
            'errors': errors or []
        }

        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"Checkpoint saved: {len(processed_urls)}/{total_urls} URLs processed "
                f"({checkpoint_data['progress_percentage']}%)"
            )

        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")

    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint from disk

        Returns:
            Checkpoint data dictionary or None if not found
        """
        if not self.checkpoint_file.exists():
            logger.info("No checkpoint found, starting fresh")
            return None

        try:
            with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint_data = json.load(f)

            logger.info(
                f"Checkpoint loaded: {len(checkpoint_data['processed_urls'])}/{checkpoint_data['total_urls']} "
                f"URLs already processed ({checkpoint_data['progress_percentage']}%)"
            )

            return checkpoint_data

        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    def get_processed_urls(self) -> List[str]:
        """
        Get list of already processed URLs

        Returns:
            List of processed URL strings
        """
        checkpoint = self.load_checkpoint()
        if checkpoint:
            return checkpoint.get('processed_urls', [])
        return []

    def should_process_url(self, url: str) -> bool:
        """
        Check if URL should be processed (not in checkpoint)

        Args:
            url: URL to check

        Returns:
            True if URL should be processed, False if already done
        """
        processed = self.get_processed_urls()
        return url not in processed

    def clear_checkpoint(self):
        """Remove checkpoint file (call after successful completion)"""
        if self.checkpoint_file.exists():
            try:
                self.checkpoint_file.unlink()
                logger.info("Checkpoint cleared")
            except Exception as e:
                logger.error(f"Failed to clear checkpoint: {e}")

    def get_resume_info(self) -> Dict[str, Any]:
        """
        Get resume information for display

        Returns:
            Dictionary with resume info
        """
        checkpoint = self.load_checkpoint()
        if not checkpoint:
            return {
                'can_resume': False,
                'message': 'No checkpoint found'
            }

        return {
            'can_resume': True,
            'message': f"Found checkpoint from {checkpoint['timestamp']}",
            'processed': len(checkpoint['processed_urls']),
            'total': checkpoint['total_urls'],
            'progress': checkpoint['progress_percentage'],
            'items_saved': checkpoint.get('items_saved', 0),
            'errors': len(checkpoint.get('errors', []))
        }
