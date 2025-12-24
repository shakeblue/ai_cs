"""
URL Type Detector
Detects the type of Naver Shopping Live URL (replays, lives, or shortclips)
"""

from enum import Enum
from typing import Optional


class URLType(Enum):
    """Enum for different URL types"""
    REPLAYS = "replays"
    LIVES = "lives"
    SHORTCLIPS = "shortclips"


class URLDetector:
    """Detects the type of Naver Shopping Live URL"""

    @staticmethod
    def detect(url: str) -> URLType:
        """
        Detect URL type from URL string

        Args:
            url: The URL to analyze

        Returns:
            URLType enum value

        Raises:
            ValueError: If URL type cannot be determined
        """
        url_lower = url.lower()

        if '/replays/' in url_lower:
            return URLType.REPLAYS
        elif '/lives/' in url_lower:
            return URLType.LIVES
        elif '/shortclips/' in url_lower:
            return URLType.SHORTCLIPS
        else:
            raise ValueError(
                f"Invalid URL: Cannot determine type. "
                f"URL must contain '/replays/', '/lives/', or '/shortclips/'. "
                f"Got: {url}"
            )

    @staticmethod
    def extract_id(url: str) -> Optional[int]:
        """
        Extract broadcast/shortclip ID from URL

        Args:
            url: The URL to analyze

        Returns:
            The extracted ID, or None if not found
        """
        import re

        # Pattern to match ID in URL
        # Examples:
        # - /replays/1776510
        # - /lives/1810235?tr=lim
        # - /shortclips/9797637?tr=sclim
        pattern = r'/(replays|lives|shortclips)/(\d+)'
        match = re.search(pattern, url)

        if match:
            return int(match.group(2))

        return None
