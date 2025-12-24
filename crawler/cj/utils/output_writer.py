"""
Output Writer
Writes extracted broadcast data to JSON files
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class OutputWriter:
    """Writes extracted data to JSON file"""

    def __init__(self, output_dir: Path):
        """
        Initialize OutputWriter

        Args:
            output_dir: Directory where output files will be saved
        """
        self.output_dir = Path(output_dir)

    def write(self, data: Dict[str, Any], broadcast_id: int) -> Path:
        """
        Write data to JSON file

        Args:
            data: The broadcast data to write
            broadcast_id: The broadcast ID for filename

        Returns:
            Path to the created file

        Raises:
            IOError: If file writing fails
        """
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate output filename
        output_file = self.output_dir / f"broadcast_{broadcast_id}.json"

        try:
            # Write JSON with pretty formatting
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Successfully wrote output to: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Failed to write output file: {e}")
            raise IOError(f"Failed to write output to {output_file}: {e}")

    def validate_output(self, data: Dict[str, Any]) -> bool:
        """
        Validate output data structure

        Args:
            data: The data to validate

        Returns:
            True if valid, False otherwise
        """
        # Check required top-level keys
        if 'metadata' not in data or 'broadcast' not in data:
            logger.warning("Output missing required top-level keys (metadata, broadcast)")
            return False

        # Check required broadcast fields
        broadcast = data.get('broadcast', {})
        required_fields = ['broadcast_id', 'title', 'brand_name']

        for field in required_fields:
            if field not in broadcast or broadcast[field] is None:
                logger.warning(f"Output missing required broadcast field: {field}")
                return False

        return True
