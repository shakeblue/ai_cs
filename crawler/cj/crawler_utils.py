"""
Utility functions for the standalone crawler
"""

import urllib.parse
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


def construct_search_url(platform: Dict[str, Any], brand: Dict[str, Any]) -> str:
    """
    Construct search URL from platform URL pattern and brand search text

    Args:
        platform: Platform dictionary with 'url_pattern' field
        brand: Brand dictionary with 'search_text' field

    Returns:
        Constructed search URL

    Example:
        platform = {'url_pattern': 'https://example.com/search?q={query}'}
        brand = {'search_text': '설화수'}
        result = 'https://example.com/search?q=%EC%84%A4%ED%99%94%EC%88%98'
    """
    url_pattern = platform.get('url_pattern')
    search_text = brand.get('search_text')

    if not url_pattern:
        raise ValueError("Platform missing 'url_pattern' field")

    if not search_text:
        raise ValueError("Brand missing 'search_text' field")

    if '{query}' not in url_pattern:
        raise ValueError(f"URL pattern missing {{query}} placeholder: {url_pattern}")

    # URL-encode the search text
    encoded_query = urllib.parse.quote(search_text)

    # Replace {query} with encoded search text
    search_url = url_pattern.replace('{query}', encoded_query)

    return search_url


def get_time_range_config(config: Dict[str, str]) -> tuple[datetime, datetime]:
    """
    Get time range for filtering events based on configuration

    Args:
        config: Configuration dictionary with 'past_days_range' and 'future_days_range'

    Returns:
        Tuple of (start_date, end_date)

    Example:
        config = {'past_days_range': '7', 'future_days_range': '14'}
        Returns: (7 days ago, 14 days from now)
    """
    past_days = int(config.get('past_days_range', '7'))
    future_days = int(config.get('future_days_range', '14'))

    now = datetime.now()
    start_date = now - timedelta(days=past_days)
    end_date = now + timedelta(days=future_days)

    return start_date, end_date


def validate_brand_platform(brand: Dict[str, Any], platform: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate that brand and platform are active and properly configured

    Args:
        brand: Brand dictionary
        platform: Platform dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check platform status
    if platform.get('status') != 'active':
        return False, f"Platform '{platform.get('name')}' is not active (status: {platform.get('status')})"

    # Check brand status
    if brand.get('status') != 'active':
        return False, f"Brand '{brand.get('name')}' is not active (status: {brand.get('status')})"

    # Check platform has URL pattern
    if not platform.get('url_pattern'):
        return False, f"Platform '{platform.get('name')}' missing url_pattern"

    # Check brand has search text
    if not brand.get('search_text'):
        return False, f"Brand '{brand.get('name')}' missing search_text"

    # Check brand belongs to this platform
    if brand.get('platform_id') != platform.get('id'):
        return False, f"Brand '{brand.get('name')}' does not belong to platform '{platform.get('name')}'"

    return True, None


def extract_broadcast_id_from_url(url: str) -> Optional[str]:
    """
    Extract broadcast ID from Naver Shopping Live URL

    Args:
        url: Broadcast URL

    Returns:
        Broadcast ID or None

    Examples:
        'https://view.shoppinglive.naver.com/lives/1776510' -> '1776510'
        'https://view.shoppinglive.naver.com/replays/1776510' -> '1776510'
    """
    # URL format: https://view.shoppinglive.naver.com/{lives|replays}/{id}
    parts = url.rstrip('/').split('/')
    if len(parts) >= 2:
        return parts[-1]
    return None


def format_execution_summary(
    brand_name: str,
    items_found: int,
    start_time: datetime,
    end_time: datetime,
    status: str
) -> str:
    """
    Format a summary message for crawler execution

    Args:
        brand_name: Name of the brand
        items_found: Number of events found
        start_time: Execution start time
        end_time: Execution end time
        status: Execution status

    Returns:
        Formatted summary string
    """
    duration = (end_time - start_time).total_seconds()

    status_emoji = {
        'success': '✅',
        'failed': '❌',
        'running': '⏳',
        'pending': '🔄'
    }.get(status, '❓')

    return (
        f"{status_emoji} Crawl {status.upper()}: {brand_name}\n"
        f"   Events found: {items_found}\n"
        f"   Duration: {duration:.1f}s\n"
        f"   Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%H:%M:%S')}"
    )


# ==========================================
# Test functions
# ==========================================

def test_url_construction():
    """Test URL construction function"""
    print("Testing URL construction...")

    # Test case 1: Normal case
    platform = {
        'url_pattern': 'https://shoppinglive.naver.com/search/lives?query={query}',
        'name': 'Naver Shopping Live'
    }
    brand = {
        'search_text': '설화수',
        'name': 'Sulwhasoo'
    }

    url = construct_search_url(platform, brand)
    expected = 'https://shoppinglive.naver.com/search/lives?query=%EC%84%A4%ED%99%94%EC%88%98'

    assert url == expected, f"Expected {expected}, got {url}"
    print(f"✅ Test 1 passed: {url}")

    # Test case 2: English search text
    brand2 = {'search_text': 'Innisfree', 'name': 'Innisfree'}
    url2 = construct_search_url(platform, brand2)
    expected2 = 'https://shoppinglive.naver.com/search/lives?query=Innisfree'

    assert url2 == expected2, f"Expected {expected2}, got {url2}"
    print(f"✅ Test 2 passed: {url2}")

    # Test case 3: Search text with spaces
    brand3 = {'search_text': '설화수 크림', 'name': 'Sulwhasoo Cream'}
    url3 = construct_search_url(platform, brand3)
    print(f"✅ Test 3 passed: {url3}")

    print("✅ All URL construction tests passed!")


def test_validate_brand_platform():
    """Test validation function"""
    print("\nTesting brand/platform validation...")

    platform = {
        'id': 'platform-1',
        'name': 'Test Platform',
        'status': 'active',
        'url_pattern': 'https://example.com/search?q={query}'
    }

    brand = {
        'id': 'brand-1',
        'name': 'Test Brand',
        'status': 'active',
        'search_text': 'test',
        'platform_id': 'platform-1'
    }

    # Test case 1: Valid brand and platform
    is_valid, error = validate_brand_platform(brand, platform)
    assert is_valid == True, f"Should be valid, got error: {error}"
    print("✅ Test 1 passed: Valid brand and platform")

    # Test case 2: Inactive platform
    platform2 = {**platform, 'status': 'inactive'}
    is_valid, error = validate_brand_platform(brand, platform2)
    assert is_valid == False, "Should be invalid (inactive platform)"
    assert 'not active' in error, f"Wrong error message: {error}"
    print("✅ Test 2 passed: Inactive platform detected")

    # Test case 3: Inactive brand
    brand2 = {**brand, 'status': 'inactive'}
    is_valid, error = validate_brand_platform(brand2, platform)
    assert is_valid == False, "Should be invalid (inactive brand)"
    print("✅ Test 3 passed: Inactive brand detected")

    print("✅ All validation tests passed!")


def test_broadcast_id_extraction():
    """Test broadcast ID extraction"""
    print("\nTesting broadcast ID extraction...")

    test_cases = [
        ('https://view.shoppinglive.naver.com/lives/1776510', '1776510'),
        ('https://view.shoppinglive.naver.com/replays/1776510', '1776510'),
        ('https://view.shoppinglive.naver.com/lives/123456/', '123456'),
    ]

    for url, expected in test_cases:
        result = extract_broadcast_id_from_url(url)
        assert result == expected, f"Expected {expected}, got {result} for URL {url}"
        print(f"✅ Extracted {result} from {url}")

    print("✅ All broadcast ID extraction tests passed!")


if __name__ == '__main__':
    test_url_construction()
    test_validate_brand_platform()
    test_broadcast_id_extraction()
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)
