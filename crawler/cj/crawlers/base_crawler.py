"""
Base Crawler
Abstract base class for all crawlers
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from playwright.async_api import async_playwright, Browser, Page

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """Abstract base class for all crawlers"""

    CRAWLER_VERSION = "1.0.0"

    def __init__(self, headless: bool = True):
        """
        Initialize BaseCrawler

        Args:
            headless: Whether to run browser in headless mode
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None

    @abstractmethod
    async def extract_data(self, url: str) -> Dict[str, Any]:
        """
        Extract broadcast data from URL
        Must be implemented by subclasses

        Args:
            url: The URL to crawl

        Returns:
            Dict containing broadcast data

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        pass

    @abstractmethod
    def get_extraction_method(self) -> str:
        """
        Get the extraction method name
        Must be implemented by subclasses

        Returns:
            Extraction method name (e.g., "API", "JSON", "HYBRID")
        """
        pass

    @abstractmethod
    def get_url_type(self) -> str:
        """
        Get the URL type this crawler handles
        Must be implemented by subclasses

        Returns:
            URL type name (e.g., "replays", "lives", "shortclips")
        """
        pass

    async def crawl(self, url: str) -> Dict[str, Any]:
        """
        Main crawl method with browser lifecycle management

        Args:
            url: The URL to crawl

        Returns:
            Complete crawl result with metadata and broadcast data

        Raises:
            Exception: If crawl fails
        """
        logger.info(f"Starting crawler for URL: {url}")
        logger.info(f"Detected URL type: {self.get_url_type()}")

        try:
            # Launch browser
            await self._launch_browser()

            # Extract data (implemented by subclass)
            broadcast_data = await self.extract_data(url)

            # Build complete result
            result = self._build_result(url, broadcast_data)

            logger.info("Crawl completed successfully")
            return result

        except Exception as e:
            logger.error(f"Crawl failed: {e}")
            raise

        finally:
            # Always close browser
            await self._close_browser()

    async def _launch_browser(self):
        """Launch Playwright browser"""
        logger.info(f"Launching browser in {'headless' if self.headless else 'headful'} mode")

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)

        # Create new context with SSL certificate errors ignored
        context = await self.browser.new_context(
            ignore_https_errors=True,
            extra_http_headers={
                "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
            }
        )
        self.page = await context.new_page()

        logger.info("Browser launched successfully")

    async def _close_browser(self):
        """Close Playwright browser"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

        logger.info("Browser closed")

    def _build_result(self, source_url: str, broadcast_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Build complete result with metadata

        Args:
            source_url: The source URL that was crawled
            broadcast_data: The extracted broadcast data

        Returns:
            Complete result dict with metadata and broadcast data
        """
        metadata = {
            "crawled_at": datetime.utcnow().isoformat() + "Z",
            "source_url": source_url,
            "extraction_method": self.get_extraction_method(),
            "url_type": self.get_url_type(),
            "crawler_version": self.CRAWLER_VERSION,
            "errors": [],
            "warnings": []
        }

        # Add any errors/warnings from broadcast_data
        if "_errors" in broadcast_data:
            metadata["errors"] = broadcast_data.pop("_errors")
        if "_warnings" in broadcast_data:
            metadata["warnings"] = broadcast_data.pop("_warnings")

        return {
            "metadata": metadata,
            "broadcast": broadcast_data
        }

    def construct_livebridge_url(self, broadcast_id: int) -> str:
        """
        Construct livebridge URL from broadcast ID

        Args:
            broadcast_id: The broadcast ID

        Returns:
            Livebridge URL
        """
        return f"https://shoppinglive.naver.com/livebridge/{broadcast_id}"

    def _add_error(self, errors: list, error_type: str, message: str, **kwargs):
        """
        Add error to errors list

        Args:
            errors: List to add error to
            error_type: Type of error
            message: Error message
            **kwargs: Additional error details
        """
        error = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": error_type,
            "message": message,
            **kwargs
        }
        errors.append(error)
        logger.error(f"{error_type}: {message}")

    def _add_warning(self, warnings: list, field: str, message: str, fallback_value: Any = None):
        """
        Add warning to warnings list

        Args:
            warnings: List to add warning to
            field: Field that has warning
            message: Warning message
            fallback_value: Fallback value used
        """
        warning = {
            "field": field,
            "message": message
        }
        if fallback_value is not None:
            warning["fallback_value"] = fallback_value

        warnings.append(warning)
        logger.warning(f"Warning for {field}: {message}")
