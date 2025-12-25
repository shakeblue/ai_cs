"""
Crawler Optimization Utilities
"""

from .browser_pool import BrowserPool
from .checkpoint_manager import CheckpointManager
from .url_detector import URLDetector, URLType

__all__ = ['BrowserPool', 'CheckpointManager', 'URLDetector', 'URLType']
