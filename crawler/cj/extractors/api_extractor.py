"""
API Extractor
Intercepts and extracts data from API responses during page load
"""

import asyncio
import json
import logging
import httpx
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class APIExtractor:
    """Extract data from intercepted API responses"""

    def __init__(self):
        """Initialize APIExtractor"""
        self.api_data: Dict[str, Any] = {}
        self.response_lock = asyncio.Lock()

    async def setup_interception(self, page):
        """
        Setup API response interception

        Args:
            page: Playwright page object
        """
        page.on('response', self._handle_response)
        logger.info("API interception setup complete")

    async def _handle_response(self, response):
        """
        Handle intercepted API responses

        Args:
            response: Playwright response object
        """
        try:
            url = response.url

            # Debug: log all URLs
            if 'naver.com' in url or 'apis' in url:
                logger.debug(f"Intercepted URL: {url}")

            # Check if this is an API we're interested in
            if not self._is_target_api(url):
                return

            logger.info(f"Found target API: {url}")

            # Skip non-JSON responses
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                logger.debug(f"Skipping non-JSON response from {url} (content-type: {content_type})")
                return

            # Parse response body
            try:
                body = await response.json()
            except Exception as e:
                logger.debug(f"Failed to parse JSON from {url}: {e}")
                return

            # Store data based on API type
            async with self.response_lock:
                await self._store_api_data(url, body)

        except Exception as e:
            logger.debug(f"Error handling response: {e}")

    def _is_target_api(self, url: str) -> bool:
        """
        Check if URL is a target API we want to intercept

        Args:
            url: The API URL

        Returns:
            True if this is a target API
        """
        target_patterns = [
            '/v1/broadcast/',
            '/v2/broadcast/',
            '/v1/shortclip/',
            '/broadcast-benefits',
            '/shopping-app/benefit',
            '/coupons',
            '/replays/comments'
        ]

        return any(pattern in url for pattern in target_patterns)

    async def _store_api_data(self, url: str, body: Any):
        """
        Store API data based on URL pattern

        Args:
            url: The API URL
            body: The response body
        """
        # Main broadcast API: /v1/broadcast/{id}
        if '/v1/broadcast/' in url and 'needTimeMachine' in url:
            self.api_data['broadcast'] = body
            logger.info(f"✓ Stored broadcast API data from {url}")

        # Coupons API: /v2/broadcast/{id}/coupons
        elif '/v2/broadcast/' in url and '/coupons' in url:
            self.api_data['coupons'] = body
            logger.info(f"✓ Stored coupons API data from {url}")

        # Benefits API: /v1/broadcast/{id}/broadcast-benefits (list of benefits)
        elif '/broadcast-benefits' in url:
            self.api_data['benefits'] = body
            logger.info(f"✓ Stored benefits API data from {url}")

        # Shopping app benefit API: /shopping-app/benefit (banner/notice info - different from live benefits)
        elif '/shopping-app/benefit' in url:
            self.api_data['shopping_app_benefit'] = body
            logger.debug(f"✓ Stored shopping app benefit data from {url}")

        # Comments API: /v1/broadcast/{id}/replays/comments
        elif '/replays/comments' in url:
            self.api_data['comments'] = body
            logger.info(f"✓ Stored comments API data from {url}")

        # Shortclip API: /v1/shortclip/{id}
        elif '/v1/shortclip/' in url:
            self.api_data['shortclip'] = body
            logger.info(f"✓ Stored shortclip API data from {url}")

    def get_broadcast_data(self) -> Optional[Dict[str, Any]]:
        """
        Get main broadcast data from API

        Returns:
            Broadcast data dict, or None if not available
        """
        return self.api_data.get('broadcast')

    def get_coupons(self) -> List[Dict[str, Any]]:
        """
        Get coupons from API

        Returns:
            List of coupon dicts, empty list if not available
        """
        coupons_data = self.api_data.get('coupons', {})
        return coupons_data.get('coupons', [])

    def get_benefits(self) -> List[Dict[str, Any]]:
        """
        Get broadcast benefits from API

        Returns:
            List of benefit dicts, empty list if not available
        """
        benefits_data = self.api_data.get('benefits', [])
        # Benefits API returns array directly
        if isinstance(benefits_data, list):
            return benefits_data
        return []

    def get_comments(self) -> List[Dict[str, Any]]:
        """
        Get comments from API

        Returns:
            List of comment dicts, empty list if not available
        """
        comments_data = self.api_data.get('comments', {})
        return comments_data.get('comments', [])

    def get_shortclip_data(self) -> Optional[Dict[str, Any]]:
        """
        Get shortclip data from API

        Returns:
            Shortclip data dict, or None if not available
        """
        return self.api_data.get('shortclip')

    def has_data(self) -> bool:
        """
        Check if any API data has been captured

        Returns:
            True if at least one API response was captured
        """
        return len(self.api_data) > 0

    def get_captured_apis(self) -> List[str]:
        """
        Get list of APIs that were successfully captured

        Returns:
            List of API names
        """
        return list(self.api_data.keys())

    async def wait_for_required_apis(
        self,
        required_apis: List[str],
        max_wait: float = 30.0,
        check_interval: float = 0.5
    ) -> bool:
        """
        Smart wait for required APIs to be captured
        Optimization #3: Instead of fixed 30s wait, check if APIs are ready

        Args:
            required_apis: List of required API keys (e.g., ['broadcast', 'coupons'])
            max_wait: Maximum time to wait in seconds (default: 30)
            check_interval: How often to check in seconds (default: 0.5)

        Returns:
            True if all required APIs captured, False if timeout

        Example:
            >>> await api_extractor.wait_for_required_apis(['broadcast', 'coupons'], max_wait=30)
        """
        elapsed = 0.0
        start_time = asyncio.get_event_loop().time()

        logger.info(f"Waiting for required APIs: {required_apis} (max {max_wait}s)")

        while elapsed < max_wait:
            # Check if all required APIs are captured
            captured = self.get_captured_apis()
            missing = [api for api in required_apis if api not in captured]

            if not missing:
                logger.info(f"✓ All required APIs captured in {elapsed:.1f}s: {captured}")
                return True

            # Log progress
            if elapsed > 0 and int(elapsed) % 5 == 0:
                logger.info(f"Still waiting for: {missing} (elapsed: {elapsed:.1f}s)")

            # Wait and check again
            await asyncio.sleep(check_interval)
            elapsed = asyncio.get_event_loop().time() - start_time

        # Timeout
        captured = self.get_captured_apis()
        missing = [api for api in required_apis if api not in captured]
        logger.warning(
            f"Timeout after {max_wait}s. Captured: {captured}, Missing: {missing}"
        )
        return False

    async def wait_for_any_data(
        self,
        max_wait: float = 10.0,
        check_interval: float = 0.5
    ) -> bool:
        """
        Wait for at least some API data to be captured

        Args:
            max_wait: Maximum time to wait in seconds
            check_interval: How often to check in seconds

        Returns:
            True if any data captured, False if timeout
        """
        elapsed = 0.0
        start_time = asyncio.get_event_loop().time()

        while elapsed < max_wait:
            if self.has_data():
                logger.info(f"✓ API data captured in {elapsed:.1f}s")
                return True

            await asyncio.sleep(check_interval)
            elapsed = asyncio.get_event_loop().time() - start_time

        logger.warning(f"No API data captured after {max_wait}s")
        return False

    async def wait_for_optional_apis(
        self,
        optional_apis: List[str],
        max_wait: float = 15.0,
        min_wait: float = 3.0,
        check_interval: float = 0.5
    ) -> List[str]:
        """
        Smart wait for optional APIs (not all required to be present)
        Waits at least min_wait seconds, up to max_wait seconds
        Returns early if all optional APIs are captured after min_wait

        Args:
            optional_apis: List of optional API keys (e.g., ['coupons', 'benefits'])
            max_wait: Maximum time to wait in seconds (default: 15)
            min_wait: Minimum time to wait in seconds (default: 3)
            check_interval: How often to check in seconds (default: 0.5)

        Returns:
            List of APIs that were captured

        Example:
            >>> captured = await api_extractor.wait_for_optional_apis(
            ...     ['coupons', 'benefits'],
            ...     max_wait=15.0,
            ...     min_wait=3.0
            ... )
            >>> print(f"Captured: {captured}")
        """
        elapsed = 0.0
        start_time = asyncio.get_event_loop().time()

        logger.info(
            f"Waiting for optional APIs: {optional_apis} "
            f"(min: {min_wait}s, max: {max_wait}s)"
        )

        while elapsed < max_wait:
            # Check which optional APIs are captured
            captured = self.get_captured_apis()
            captured_optional = [api for api in optional_apis if api in captured]
            missing = [api for api in optional_apis if api not in captured]

            # If we've waited at least min_wait and all optional APIs are captured, return
            if elapsed >= min_wait and not missing:
                logger.info(
                    f"✓ All optional APIs captured in {elapsed:.1f}s: {captured_optional}"
                )
                return captured_optional

            # Log progress every 3 seconds
            if elapsed > 0 and int(elapsed) % 3 == 0 and elapsed < max_wait - check_interval:
                if captured_optional:
                    logger.info(
                        f"Progress: {len(captured_optional)}/{len(optional_apis)} "
                        f"APIs captured: {captured_optional} (elapsed: {elapsed:.1f}s)"
                    )
                else:
                    logger.info(f"Still waiting for optional APIs (elapsed: {elapsed:.1f}s)")

            # Wait and check again
            await asyncio.sleep(check_interval)
            elapsed = asyncio.get_event_loop().time() - start_time

        # Timeout or completed
        captured = self.get_captured_apis()
        captured_optional = [api for api in optional_apis if api in captured]
        missing = [api for api in optional_apis if api not in captured]

        if captured_optional:
            logger.info(
                f"✓ Optional APIs captured ({len(captured_optional)}/{len(optional_apis)}): "
                f"{captured_optional} after {elapsed:.1f}s"
            )
            if missing:
                logger.info(f"  Missing optional APIs (not critical): {missing}")
        else:
            logger.warning(
                f"No optional APIs captured after {max_wait}s. "
                f"This is OK if the broadcast has no {'/'.join(optional_apis)}."
            )

        return captured_optional

    async def fetch_all_comments_paginated(
        self,
        broadcast_id: int,
        page_size: int = 100,
        keep_odd_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch ALL comments using pagination with direct API calls
        For demo purposes, keeps only odd-indexed comments (50% of total) to reduce storage

        Args:
            broadcast_id: The broadcast ID
            page_size: Number of comments per page (default: 100)
            keep_odd_only: If True, keeps only odd-indexed comments to save storage (default: True)

        Returns:
            List of all comments (or 50% if keep_odd_only=True)

        Example:
            >>> comments = await api_extractor.fetch_all_comments_paginated(1776510, page_size=100)
        """
        all_comments = []
        url = f"https://apis.naver.com/selectiveweb/live_commerce_web/v1/broadcast/{broadcast_id}/replays/comments"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': f'https://view.shoppinglive.naver.com/replays/{broadcast_id}'
        }

        params = {'size': page_size}
        page_num = 1

        logger.info(f"Fetching comments with pagination (page_size={page_size}, keep_odd_only={keep_odd_only})...")

        try:
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                while True:
                    # Fetch page
                    response = await client.get(url, headers=headers, params=params)

                    if response.status_code != 200:
                        logger.warning(f"Failed to fetch comments page {page_num}: {response.status_code}")
                        break

                    data = response.json()
                    comments = data.get('comments', [])
                    has_next = data.get('hasNext', False)

                    if not comments:
                        logger.info(f"No more comments on page {page_num}")
                        break

                    # Add comments to collection
                    all_comments.extend(comments)
                    logger.info(f"✓ Page {page_num}: fetched {len(comments)} comments (total: {len(all_comments)})")

                    # Check if there are more pages
                    if not has_next:
                        logger.info(f"✓ No more pages (hasNext=False)")
                        break

                    # Set pagination cursors for next page
                    params['lastCommentNo'] = data.get('lastCommentNo')
                    params['lastCreatedAtMilli'] = data.get('lastCreatedAtMilli')
                    page_num += 1

                    # Safety limit: max 50 pages (5000 comments with page_size=100)
                    if page_num > 50:
                        logger.warning(f"Reached safety limit of 50 pages, stopping pagination")
                        break

        except Exception as e:
            logger.error(f"Error fetching paginated comments: {e}")

        # Filter to odd indices for storage optimization (demo mode)
        if keep_odd_only and all_comments:
            original_count = len(all_comments)
            # Keep comments at odd indices: 1, 3, 5, 7, ... (roughly 50%)
            all_comments = [comment for idx, comment in enumerate(all_comments) if idx % 2 == 1]
            logger.info(f"✓ Filtered to odd indices: {len(all_comments)}/{original_count} comments ({len(all_comments)/original_count*100:.1f}%)")

        logger.info(f"✓ Total comments fetched: {len(all_comments)}")
        return all_comments
