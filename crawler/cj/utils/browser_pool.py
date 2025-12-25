"""
Browser Pool for Reusing Browser Instances
Optimization #2: Browser Instance Pooling
"""

import asyncio
import logging
from typing import Optional, List
from playwright.async_api import async_playwright, Browser, BrowserContext

logger = logging.getLogger(__name__)


class BrowserPool:
    """
    Pool of browser instances for reuse across multiple crawls

    Benefits:
    - Eliminates browser startup overhead (1-2s per instance)
    - Reuses browser contexts for better performance
    - Manages browser lifecycle automatically
    """

    def __init__(self, pool_size: int = 5, headless: bool = True):
        """
        Initialize browser pool

        Args:
            pool_size: Maximum number of concurrent browser contexts
            headless: Whether to run browsers in headless mode
        """
        self.pool_size = pool_size
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.contexts: List[BrowserContext] = []
        self.available_contexts: asyncio.Queue = asyncio.Queue()
        self.lock = asyncio.Lock()
        self._initialized = False

        logger.info(f"BrowserPool initialized with pool_size={pool_size}")

    async def initialize(self):
        """Initialize the browser pool"""
        if self._initialized:
            return

        async with self.lock:
            if self._initialized:
                return

            logger.info("Starting browser pool initialization...")

            # Launch playwright
            self.playwright = await async_playwright().start()

            # Launch single browser instance
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            # Create browser contexts (lightweight)
            for i in range(self.pool_size):
                context = await self.browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                    ignore_https_errors=True,  # Ignore SSL certificate errors
                    extra_http_headers={
                        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
                    }
                )
                self.contexts.append(context)
                await self.available_contexts.put(context)
                logger.info(f"Created browser context {i+1}/{self.pool_size}")

            self._initialized = True
            logger.info("Browser pool initialization complete")

    async def acquire_context(self) -> BrowserContext:
        """
        Acquire a browser context from the pool

        Returns:
            BrowserContext ready for use
        """
        if not self._initialized:
            await self.initialize()

        # Wait for available context
        context = await self.available_contexts.get()
        logger.debug("Browser context acquired from pool")
        return context

    async def release_context(self, context: BrowserContext):
        """
        Release a browser context back to the pool

        Args:
            context: The context to release
        """
        # Clear cookies and storage for clean state
        try:
            await context.clear_cookies()
        except Exception as e:
            logger.warning(f"Failed to clear cookies: {e}")

        # Return to pool
        await self.available_contexts.put(context)
        logger.debug("Browser context released back to pool")

    async def cleanup(self):
        """Clean up all browser resources"""
        if not self._initialized:
            return

        logger.info("Cleaning up browser pool...")

        # Close all contexts
        for context in self.contexts:
            try:
                await context.close()
            except Exception as e:
                logger.warning(f"Error closing context: {e}")

        # Close browser
        if self.browser:
            try:
                await self.browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")

        # Stop playwright
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")

        self._initialized = False
        logger.info("Browser pool cleanup complete")

    async def __aenter__(self):
        """Context manager entry"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.cleanup()
