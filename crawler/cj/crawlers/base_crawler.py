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

    def __init__(self, headless: bool = True, external_context=None, crawl_livebridge: bool = False, use_livebridge_llm: bool = True):
        """
        Initialize BaseCrawler

        Args:
            headless: Whether to run browser in headless mode
            external_context: Optional external browser context from pool (for optimization)
            crawl_livebridge: Whether to automatically crawl livebridge page if available (default: False)
            use_livebridge_llm: Whether to use LLM for livebridge extraction (default: True, only used if crawl_livebridge=True)
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.external_context = external_context  # Context provided by browser pool
        self.owns_browser = external_context is None  # Track if we own the browser lifecycle
        self.crawl_livebridge = crawl_livebridge
        self.use_livebridge_llm = use_livebridge_llm

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
        """Launch Playwright browser or use external context from pool"""

        # If external context provided (from browser pool), use it
        if self.external_context:
            logger.info("Using external browser context from pool")
            self.page = await self.external_context.new_page()
            logger.info("Page created from external context")
            return

        # Otherwise, launch our own browser
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
        """Close Playwright browser (only if we own it)"""

        # Always close the page
        if self.page:
            await self.page.close()
            logger.info("Page closed")

        # Only close browser/playwright if we own them (not using external context)
        if self.owns_browser:
            if self.browser:
                await self.browser.close()
                logger.info("Browser closed")
            if self.playwright:
                await self.playwright.stop()
                logger.info("Playwright stopped")
        else:
            logger.info("Using external context - browser will be managed by pool")

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

    @staticmethod
    def check_livebridge_accessible(livebridge_url: str, timeout: int = 5) -> bool:
        """
        Check if a livebridge URL is accessible

        Args:
            livebridge_url: The livebridge URL to check
            timeout: Request timeout in seconds (default: 5)

        Returns:
            True if URL is accessible (status code 200), False otherwise
        """
        import requests
        import urllib3

        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = requests.head(
                livebridge_url,
                timeout=timeout,
                verify=False,
                allow_redirects=True,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
            )

            # If HEAD request doesn't work, try GET
            if response.status_code == 405:  # Method Not Allowed
                response = requests.get(
                    livebridge_url,
                    timeout=timeout,
                    verify=False,
                    allow_redirects=True,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    }
                )

            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Livebridge URL not accessible: {e}")
            return False

    async def _crawl_livebridge_if_available(self, broadcast_id: int) -> Optional[Dict[str, Any]]:
        """
        Crawl livebridge page if available and enabled

        Args:
            broadcast_id: The broadcast ID

        Returns:
            Dict with livebridge data and status, or None if not crawled
        """
        if not self.crawl_livebridge:
            return None

        try:
            # Import here to avoid circular dependency and allow graceful degradation
            from crawlers.livebridge_crawler import LivebridgeCrawler
            from vision_extractor import VisionProvider
        except ImportError as e:
            logger.warning(f"Livebridge crawler not available: {e}")
            return None

        # Construct livebridge URL
        livebridge_url = self.construct_livebridge_url(broadcast_id)
        logger.info(f"Checking livebridge: {livebridge_url}")

        # Check if accessible
        if not self.check_livebridge_accessible(livebridge_url):
            logger.info("✗ Livebridge page not accessible")
            return {'status': 'not_available', 'url': livebridge_url}

        logger.info("✓ Livebridge page accessible, crawling...")

        try:
            # Initialize livebridge crawler
            livebridge_crawler = LivebridgeCrawler(
                use_llm=self.use_livebridge_llm,
                vision_provider=VisionProvider.GPT_4O_MINI if self.use_livebridge_llm else None,
                use_supabase=True
            )

            # Crawl livebridge
            livebridge_data = await livebridge_crawler.crawl(livebridge_url)

            # Save to Supabase
            livebridge_id = livebridge_crawler.save_to_supabase(livebridge_data)

            if livebridge_id:
                logger.info(f"✓ Livebridge saved to Supabase (ID: {livebridge_id})")
                return {
                    'status': 'success',
                    'livebridge_id': livebridge_id,
                    'url': livebridge_url,
                    'records': {
                        'special_coupons': len(livebridge_data.get('special_coupons', [])),
                        'products': len(livebridge_data.get('products', [])),
                        'live_benefits': len(livebridge_data.get('live_benefits', [])),
                        'benefits_by_amount': len(livebridge_data.get('benefits_by_amount', [])),
                        'simple_coupons': len(livebridge_data.get('coupons', []))
                    }
                }
            else:
                logger.error("✗ Failed to save livebridge to Supabase")
                return {'status': 'save_failed', 'url': livebridge_url}

        except Exception as e:
            logger.error(f"✗ Livebridge crawl failed: {e}")
            return {'status': 'error', 'url': livebridge_url, 'error': str(e)}

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
