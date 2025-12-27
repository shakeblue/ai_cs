#!/usr/bin/env python3
"""
Naver Shopping Live Livebridge Crawler
Extracts data from livebridge pages (promotional landing pages for upcoming broadcasts)

Example URLs:
    https://shoppinglive.naver.com/livebridge/1776510
"""

import json
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import sys
import requests
import urllib3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from vision_extractor import VisionExtractor, VisionProvider
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False
    print("⚠ Vision extractor not available")

# Supabase client
try:
    from supabase import create_client, Client
    import httpx
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("⚠ Supabase client not available. Install with: pip install supabase")

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

logger = logging.getLogger(__name__)


class LivebridgeCrawler:
    """Crawler for Naver Shopping Live livebridge pages"""

    def __init__(self, use_llm: bool = True, vision_provider: VisionProvider = None, use_supabase: bool = True):
        """
        Initialize the livebridge crawler

        Args:
            use_llm: Whether to use LLM for image extraction (default: True)
            vision_provider: Vision LLM provider to use (default: GPT_4O_MINI)
            use_supabase: Whether to save data to Supabase (default: True)
        """
        self.use_llm = use_llm and VISION_AVAILABLE
        self.use_supabase = use_supabase and SUPABASE_AVAILABLE

        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for Naver
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        })

        # Initialize vision extractor if enabled
        if self.use_llm:
            try:
                provider = vision_provider if vision_provider else VisionProvider.GPT_4O_MINI
                self.vision_extractor = VisionExtractor(provider=provider)
                logger.info("✓ Vision extractor initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize vision extractor: {e}")
                self.use_llm = False

        # Initialize Supabase client if enabled
        if self.use_supabase:
            try:
                supabase_url = os.getenv("SUPABASE_URL")
                supabase_key = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_ANON_KEY")

                if not supabase_url or not supabase_key:
                    logger.warning("SUPABASE_URL or SUPABASE_SECRET_KEY not found in environment")
                    self.use_supabase = False
                else:
                    # Create Supabase client
                    self.supabase: Client = create_client(supabase_url, supabase_key)
                    # Create httpx client with SSL verification disabled and override
                    http_client = httpx.Client(verify=False)
                    self.supabase.postgrest.session = http_client
                    logger.info("✓ Supabase client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Supabase client: {e}")
                self.use_supabase = False

    async def crawl(self, url: str) -> Dict:
        """
        Crawl a livebridge URL and extract all data

        Args:
            url: Livebridge URL to crawl

        Returns:
            Dictionary with extracted data
        """
        logger.info(f"Starting livebridge crawl: {url}")

        try:
            # Step 1: Fetch the page
            html = self._fetch_page(url)
            if not html:
                raise Exception("Failed to fetch page")

            # Step 2: Extract __NEXT_DATA__
            next_data = self._extract_next_data(html)
            if not next_data:
                raise Exception("Failed to extract __NEXT_DATA__")

            # Step 3: Parse bridge info
            bridge_info = self._parse_bridge_info(next_data)
            if not bridge_info:
                raise Exception("Failed to parse bridge info")

            # Step 4: Extract image URLs from contentsJson
            images = self._extract_images(bridge_info)

            # Step 5: Extract products from API
            broadcast_id = bridge_info.get('broadcastId')
            products = self._extract_products_from_api(broadcast_id) if broadcast_id else []

            # Step 6: Extract special coupons from API
            special_coupons = self._extract_coupons_from_api(broadcast_id) if broadcast_id else []

            # Step 7: Extract content from images using LLM (if enabled)
            extracted_content = {
                'live_benefits': [],
                'benefits_by_amount': [],
                'coupons': [],  # Normal coupons from images
                'special_coupons': special_coupons,  # Special coupons from API
                'products': products  # Use products from API
            }

            if self.use_llm and images:
                logger.info(f"Extracting content from {len(images)} images using LLM...")
                llm_content = await self._extract_image_content(images)
                # Merge LLM extracted benefits and normal coupons
                extracted_content['live_benefits'] = llm_content.get('live_benefits', [])
                extracted_content['benefits_by_amount'] = llm_content.get('benefits_by_amount', [])
                extracted_content['coupons'] = llm_content.get('coupons', [])
            else:
                logger.info("Skipping LLM extraction (disabled or no images)")

            # Step 8: Build output structure
            result = self._build_output(url, bridge_info, images, extracted_content)

            logger.info(f"Successfully crawled livebridge: {bridge_info.get('broadcastId')}")
            return result

        except Exception as e:
            logger.error(f"Crawl failed: {e}")
            raise

    def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch the livebridge page HTML with retry logic"""
        max_retries = 3
        timeout = 30  # Increased timeout

        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching (attempt {attempt + 1}/{max_retries}): {url}")
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()

                logger.info(f"Page fetched: {len(response.text)} bytes")
                return response.text

            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch page after {max_retries} attempts")
                    return None

        return None

    def _extract_next_data(self, html: str) -> Optional[Dict]:
        """Extract __NEXT_DATA__ from HTML"""
        try:
            # Look for <script id="__NEXT_DATA__">...</script>
            pattern = r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>'
            matches = re.findall(pattern, html, re.DOTALL)

            if not matches:
                logger.error("__NEXT_DATA__ not found in HTML")
                return None

            # Parse JSON
            data = json.loads(matches[0])
            logger.info("Successfully extracted __NEXT_DATA__")
            return data

        except Exception as e:
            logger.error(f"Failed to extract __NEXT_DATA__: {e}")
            return None

    def _parse_bridge_info(self, next_data: Dict) -> Optional[Dict]:
        """Parse bridgeInfo from __NEXT_DATA__"""
        try:
            # Navigate to bridgeInfo
            page_props = next_data.get('props', {}).get('pageProps', {})
            recoil_state = page_props.get('initialRecoilState', {})
            bridge_info = recoil_state.get('bridgeInfo', {})

            if not bridge_info:
                logger.error("bridgeInfo not found in __NEXT_DATA__")
                return None

            logger.info(f"Found bridgeInfo for broadcast: {bridge_info.get('broadcastId')}")
            return bridge_info

        except Exception as e:
            logger.error(f"Failed to parse bridgeInfo: {e}")
            return None

    def _extract_images(self, bridge_info: Dict) -> List[Dict]:
        """Extract image URLs from contentsJson.components"""
        images = []

        try:
            contents_json = bridge_info.get('contentsJson', {})
            document = contents_json.get('document', {})
            components = document.get('components', [])

            logger.info(f"Found {len(components)} components in contentsJson")

            for idx, component in enumerate(components):
                # Only process image components
                if component.get('@ctype') != 'image':
                    continue

                image_data = {
                    'id': component.get('id', ''),
                    'url': component.get('src', ''),
                    'filename': component.get('fileName', ''),
                    'link': component.get('link', ''),
                    'width': component.get('width', 0),
                    'height': component.get('height', 0),
                    'file_size': component.get('fileSize', 0),
                    'position': idx
                }

                images.append(image_data)

            logger.info(f"Extracted {len(images)} images from components")
            return images

        except Exception as e:
            logger.error(f"Failed to extract images: {e}")
            return []

    def _extract_products_from_api(self, broadcast_id: int) -> List[Dict]:
        """Extract products from Naver Shopping Live API with pagination support"""
        products = []

        try:
            # API endpoint for products
            api_url = f'https://apis.naver.com/selectiveweb/live_commerce_web/v1/broadcast-bridge/{broadcast_id}/products'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json',
                'Referer': f'https://shoppinglive.naver.com/livebridge/{broadcast_id}',
                'apigw-routing-key': 'real-home-api',
            }

            # Fetch ALL MAIN products with pagination
            logger.info(f"Fetching MAIN products from API (with pagination)...")
            page = 0
            total_main = 0
            while True:
                params_main = {'attachmentType': 'MAIN', 'page': page, 'size': 20}
                response_main = self.session.get(api_url, headers=headers, params=params_main, timeout=10)

                if response_main.status_code == 200:
                    data_main = response_main.json()
                    main_products = data_main.get('list', [])

                    if not main_products:
                        # No more products, exit pagination loop
                        break

                    logger.info(f"Page {page}: Found {len(main_products)} MAIN products")
                    total_main += len(main_products)

                    for product in main_products:
                        products.append({
                            'product_id': str(product.get('productNo') or product.get('key')),
                            'product_name': product.get('productName') or product.get('name'),
                            'brand_name': product.get('brandName'),
                            'price': product.get('price'),
                            'sale_price': product.get('salePrice'),
                            'discounted_price': product.get('discountedSalePrice'),
                            'discount_rate': product.get('discountRate'),
                            'product_url': product.get('productEndUrl'),
                            'bridge_url': product.get('productBridgeUrl'),
                            'image_url': product.get('image'),
                            'stock': product.get('stock'),
                            'status': product.get('status'),
                            'is_represent': product.get('represent', False),
                            'badges': self._extract_product_badges(product),
                            'attachment_type': 'MAIN',
                            'source': 'API'
                        })

                    # Check if there are more pages using totalCount
                    total_count = data_main.get('totalCount')
                    if total_count and total_main >= total_count:
                        # Collected all products based on totalCount
                        break
                    if len(main_products) < 20:
                        # Last page has fewer items than page size
                        break

                    page += 1
                else:
                    logger.warning(f"Failed to fetch MAIN products page {page}: {response_main.status_code}")
                    break

            logger.info(f"Total MAIN products: {total_main}")

            # Fetch ALL SUB products with pagination
            logger.info(f"Fetching SUB products from API (with pagination)...")
            page = 0
            total_sub = 0
            while True:
                params_sub = {'attachmentType': 'SUB', 'page': page, 'size': 20}
                response_sub = self.session.get(api_url, headers=headers, params=params_sub, timeout=10)

                if response_sub.status_code == 200:
                    data_sub = response_sub.json()
                    sub_products = data_sub.get('list', [])

                    if not sub_products:
                        # No more products, exit pagination loop
                        break

                    logger.info(f"Page {page}: Found {len(sub_products)} SUB products")
                    total_sub += len(sub_products)

                    for product in sub_products:
                        products.append({
                            'product_id': str(product.get('productNo') or product.get('key')),
                            'product_name': product.get('productName') or product.get('name'),
                            'brand_name': product.get('brandName'),
                            'price': product.get('price'),
                            'sale_price': product.get('salePrice'),
                            'discounted_price': product.get('discountedSalePrice'),
                            'discount_rate': product.get('discountRate'),
                            'product_url': product.get('productEndUrl'),
                            'bridge_url': product.get('productBridgeUrl'),
                            'image_url': product.get('image'),
                            'stock': product.get('stock'),
                            'status': product.get('status'),
                            'is_represent': product.get('represent', False),
                            'badges': self._extract_product_badges(product),
                            'attachment_type': 'SUB',
                            'source': 'API'
                        })

                    # Check if there are more pages using totalCount
                    total_count = data_sub.get('totalCount')
                    if total_count and total_sub >= total_count:
                        # Collected all products based on totalCount
                        break
                    if len(sub_products) < 20:
                        # Last page has fewer items than page size
                        break

                    page += 1
                else:
                    logger.warning(f"Failed to fetch SUB products page {page}: {response_sub.status_code}")
                    break

            logger.info(f"Total SUB products: {total_sub}")
            logger.info(f"Total products extracted: {len(products)} (MAIN: {total_main}, SUB: {total_sub})")
            return products

        except Exception as e:
            logger.error(f"Failed to extract products from API: {e}")
            return []

    def _extract_coupons_from_api(self, broadcast_id: int) -> List[Dict]:
        """Extract special coupons from Naver Shopping Live API"""
        try:
            api_url = f'https://apis.naver.com/selectiveweb/live_commerce_web/v3/broadcast/{broadcast_id}/coupons'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': f'https://shoppinglive.naver.com/livebridge/{broadcast_id}',
                'apigw-routing-key': 'real-home-api',
                'x-external-service-id': 'shoppinglive',
            }

            params = {'liveCoupon': 'true'}

            logger.info(f"Fetching coupons from API...")
            response = self.session.get(api_url, headers=headers, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                coupons_list = data.get('coupons', [])
                logger.info(f"Found {len(coupons_list)} special coupons")

                coupons = []
                for coupon in coupons_list:
                    coupons.append({
                        'coupon_name': coupon.get('benefitPolicyName'),
                        'coupon_type': coupon.get('benefitTargetType'),  # NEWS, LIVE, etc.
                        'benefit_unit': coupon.get('benefitUnit'),  # FIX or PERCENT
                        'benefit_value': coupon.get('benefitValue'),
                        'min_order_amount': coupon.get('minOrderAmount'),
                        'max_discount_amount': coupon.get('maxDiscountAmount'),
                        'coupon_kind': coupon.get('couponKind'),  # PRODUCT or ORDER
                        'valid_period_start': coupon.get('validPeriodStartDate'),
                        'valid_period_end': coupon.get('validPeriodEndDate'),
                        'availability_status': coupon.get('availabilityStatus'),
                        'benefit_status': coupon.get('benefitStatusDisplay'),
                        'provider_name': coupon.get('couponProviderName'),
                        'source': 'API'
                    })

                return coupons
            else:
                logger.warning(f"Failed to fetch coupons: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Failed to extract coupons from API: {e}")
            return []

    def _extract_product_badges(self, product: Dict) -> List[str]:
        """Extract badges from product data"""
        badges = []

        if product.get('todayDispatch'):
            badges.append('오늘출발')
        if product.get('freeDelivery'):
            badges.append('무료배송')
        if product.get('arrivalGuarantee'):
            badges.append('네이버 배송')
        if product.get('arrivalGuaranteeHope'):
            badges.append('네이버 희망일 배송')
        if product.get('isNpaySaving'):
            badges.append('네이버페이 적립')

        return badges

    async def _extract_image_content(self, images: List[Dict]) -> Dict:
        """
        Extract content from images using vision LLM

        Args:
            images: List of image dictionaries with URLs

        Returns:
            Dict with extracted content (benefits, coupons, products)
        """
        result = {
            'live_benefits': [],
            'benefits_by_amount': [],
            'coupons': [],
            'products': []
        }

        # Download images to temp directory for processing
        temp_dir = Path(__file__).parent.parent / 'output' / 'temp_images'
        temp_dir.mkdir(parents=True, exist_ok=True)

        downloaded_images = []

        for idx, img in enumerate(images):
            try:
                # Download image
                response = self.session.get(img['url'], timeout=10)
                response.raise_for_status()

                # Save to temp file
                filename = f"image_{idx}_{img['filename']}"
                filepath = temp_dir / filename

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                downloaded_images.append({
                    'path': str(filepath),
                    'filename': img['filename'],
                    'url': img['url']
                })

                logger.info(f"Downloaded: {img['filename']}")

            except Exception as e:
                logger.error(f"Failed to download image {img['url']}: {e}")
                continue

        if not downloaded_images:
            logger.warning("No images downloaded for LLM extraction")
            return result

        # Extract from all images using vision LLM
        # Note: vision_extractor uses its own built-in prompt for event extraction
        try:
            logger.info(f"Processing {len(downloaded_images)} images with vision LLM...")
            image_paths = [img['path'] for img in downloaded_images]

            extracted = self.vision_extractor.extract_from_images(image_paths)

            if extracted:
                logger.info(f"LLM extraction successful")

                # Map vision extractor output to our format
                if 'live_benefits' in extracted:
                    result['live_benefits'].extend(extracted['live_benefits'])

                if 'benefits_by_purchase_amount' in extracted:
                    result['benefits_by_amount'].extend(extracted['benefits_by_purchase_amount'])

                if 'coupon_benefits' in extracted:
                    # Convert coupon strings to structured format
                    for coupon_text in extracted['coupon_benefits']:
                        result['coupons'].append({
                            'text': coupon_text,
                            'confidence': 0.85
                        })

            else:
                logger.warning("Vision extractor returned no data")

        except Exception as e:
            logger.error(f"Vision extraction failed: {e}")
            import traceback
            traceback.print_exc()

        # Cleanup temp files
        for img_info in downloaded_images:
            try:
                Path(img_info['path']).unlink()
            except:
                pass

        logger.info(f"Extraction complete: {len(result['live_benefits'])} benefits, "
                   f"{len(result['coupons'])} coupons, {len(result['products'])} products")

        return result

    def _create_benefits_prompt(self) -> str:
        """Create prompt for extracting benefits from images"""
        return """이 이미지에서 라이브 방송 혜택 정보를 추출해주세요.

다음 정보를 JSON 형식으로 추출하세요:
1. live_benefits: 라이브 특별 혜택 리스트 (예: "라이브 한정 20% 할인", "특별 사은품 증정")
2. benefits_by_amount: 구매 금액별 혜택 (예: "5만원 이상 구매시 파우치 증정", "10만원 이상 무료배송")

응답 형식 (JSON만 출력):
{
  "live_benefits": ["혜택1", "혜택2"],
  "benefits_by_amount": ["금액별혜택1", "금액별혜택2"]
}
"""

    def _create_coupons_prompt(self) -> str:
        """Create prompt for extracting coupon information"""
        return """이 이미지에서 쿠폰 정보를 추출해주세요.

다음 정보를 JSON 형식으로 추출하세요:
- coupon_name: 쿠폰 이름
- discount_amount: 할인 금액 또는 비율 (예: "5,000원 할인", "10% 할인")
- min_purchase: 최소 구매 금액 (있는 경우)
- conditions: 쿠폰 사용 조건
- expiry: 유효기간 (있는 경우)

응답 형식 (JSON 배열):
[
  {
    "coupon_name": "이름",
    "discount_amount": "할인액",
    "conditions": "조건",
    "confidence": 0.9
  }
]
"""

    def _create_products_prompt(self) -> str:
        """Create prompt for extracting product information"""
        return """이 이미지에서 상품 정보를 추출해주세요.

다음 정보를 JSON 형식으로 추출하세요:
- product_name: 상품명
- discount_rate: 할인율 (예: "40%")
- discount_price: 할인가 (예: "15,900원")
- original_price: 정가 (있는 경우)

응답 형식 (JSON 배열):
[
  {
    "product_name": "상품명",
    "discount_rate": "할인율",
    "discount_price": "할인가",
    "original_price": "정가",
    "confidence": 0.9
  }
]
"""

    def _create_generic_prompt(self) -> str:
        """Create generic extraction prompt for unknown image types"""
        return """이 이미지에서 프로모션 정보를 추출해주세요.

혜택, 쿠폰, 상품 정보 등을 찾아서 JSON 형식으로 추출하세요.
"""

    def _categorize_extraction(self, extracted_data: Dict, result: Dict, extraction_type: str):
        """Categorize extracted data into appropriate result fields"""
        if not extracted_data:
            return

        # Handle different extraction types
        if extraction_type == 'benefits':
            if 'live_benefits' in extracted_data:
                result['live_benefits'].extend(extracted_data['live_benefits'])
            if 'benefits_by_amount' in extracted_data:
                result['benefits_by_amount'].extend(extracted_data['benefits_by_amount'])

        elif extraction_type == 'coupons':
            if isinstance(extracted_data, list):
                result['coupons'].extend(extracted_data)
            elif 'coupons' in extracted_data:
                result['coupons'].extend(extracted_data['coupons'])

        elif extraction_type == 'products':
            if isinstance(extracted_data, list):
                result['products'].extend(extracted_data)
            elif 'products' in extracted_data:
                result['products'].extend(extracted_data['products'])

    def _build_output(self, url: str, bridge_info: Dict, images: List[Dict],
                      extracted_content: Dict) -> Dict:
        """Build the final output structure (optimized)"""

        # Parse expected start date
        expected_start_date = bridge_info.get('expectedStartDate', '')
        if expected_start_date:
            try:
                # Already in ISO format, just validate
                datetime.fromisoformat(expected_start_date.replace('Z', '+00:00'))
            except:
                logger.warning(f"Invalid date format: {expected_start_date}")

        # Simplify products - keep only essential fields
        simplified_products = []
        for product in extracted_content.get('products', []):
            simplified_products.append({
                'image': product.get('image_url'),
                'name': product.get('product_name'),
                'discount_rate': product.get('discount_rate'),
                'discount_price': product.get('discounted_price')
            })

        # Extract brand name with fallback chain
        all_products = extracted_content.get('products', [])
        brand_name = (
            # Priority 1: Product brand from first product (most accurate)
            (all_products[0].get('brand_name') if all_products else None) or
            # Priority 2: Broadcaster nickname (fallback)
            bridge_info.get('nickname')
        )

        # Extract mall name and broadcaster name
        broadcaster_name = bridge_info.get('nickname')

        # Simplify coupons - remove confidence field
        simplified_coupons = []
        for coupon in extracted_content.get('coupons', []):
            if isinstance(coupon, dict):
                # Remove confidence field, keep only text
                simplified_coupons.append(coupon.get('text', coupon))
            else:
                simplified_coupons.append(coupon)

        # Build optimized output with only essential fields
        result = {
            'url': url,
            'live_datetime': expected_start_date,
            'title': bridge_info.get('broadcastTitle') or bridge_info.get('title'),
            'brand_name': brand_name,
            'broadcaster_name': broadcaster_name,
            'special_coupons': extracted_content.get('special_coupons', []),
            'products': simplified_products,
            'live_benefits': extracted_content.get('live_benefits', []),
            'benefits_by_amount': extracted_content.get('benefits_by_amount', []),
            'coupons': simplified_coupons
        }

        return result

    def save_to_supabase(self, data: Dict) -> Optional[int]:
        """
        Save extracted livebridge data to Supabase

        Args:
            data: Extracted livebridge data dictionary

        Returns:
            The livebridge_id if successful, None otherwise
        """
        if not self.use_supabase:
            logger.warning("Supabase not available, skipping database save")
            return None

        try:
            logger.info("Saving data to Supabase...")

            # 1. Upsert main livebridge record
            main_data = {
                "url": data["url"],
                "live_datetime": data.get("live_datetime"),
                "title": data["title"],
                "brand_name": data.get("brand_name")
            }

            result = self.supabase.table("livebridge")\
                .upsert(main_data, on_conflict="url")\
                .execute()

            if not result.data:
                logger.error("Failed to insert main livebridge record")
                return None

            livebridge_id = result.data[0]["id"]
            logger.info(f"✓ Main record saved (ID: {livebridge_id})")

            # 2. Delete existing related records (for update case)
            logger.info("Cleaning up existing related records...")
            self.supabase.table("livebridge_coupons").delete().eq("livebridge_id", livebridge_id).execute()
            self.supabase.table("livebridge_products").delete().eq("livebridge_id", livebridge_id).execute()
            self.supabase.table("livebridge_live_benefits").delete().eq("livebridge_id", livebridge_id).execute()
            self.supabase.table("livebridge_benefits_by_amount").delete().eq("livebridge_id", livebridge_id).execute()
            self.supabase.table("livebridge_simple_coupons").delete().eq("livebridge_id", livebridge_id).execute()

            # 3. Insert special coupons
            if data.get("special_coupons"):
                coupons = [
                    {**coupon, "livebridge_id": livebridge_id}
                    for coupon in data["special_coupons"]
                ]
                self.supabase.table("livebridge_coupons").insert(coupons).execute()
                logger.info(f"✓ Inserted {len(coupons)} special coupons")

            # 4. Insert products
            if data.get("products"):
                products = [
                    {**product, "livebridge_id": livebridge_id}
                    for product in data["products"]
                ]
                self.supabase.table("livebridge_products").insert(products).execute()
                logger.info(f"✓ Inserted {len(products)} products")

            # 5. Insert live benefits
            if data.get("live_benefits"):
                benefits = [
                    {"livebridge_id": livebridge_id, "benefit_text": benefit}
                    for benefit in data["live_benefits"]
                ]
                self.supabase.table("livebridge_live_benefits").insert(benefits).execute()
                logger.info(f"✓ Inserted {len(benefits)} live benefits")

            # 6. Insert benefits by amount
            if data.get("benefits_by_amount"):
                benefits = [
                    {"livebridge_id": livebridge_id, "benefit_text": benefit}
                    for benefit in data["benefits_by_amount"]
                ]
                self.supabase.table("livebridge_benefits_by_amount").insert(benefits).execute()
                logger.info(f"✓ Inserted {len(benefits)} benefits by amount")

            # 7. Insert simple coupons
            if data.get("coupons"):
                coupons = [
                    {"livebridge_id": livebridge_id, "coupon_text": coupon}
                    for coupon in data["coupons"]
                ]
                self.supabase.table("livebridge_simple_coupons").insert(coupons).execute()
                logger.info(f"✓ Inserted {len(coupons)} simple coupons")

            logger.info(f"✓ Successfully saved all data to Supabase (ID: {livebridge_id})")
            return livebridge_id

        except Exception as e:
            logger.error(f"Failed to save to Supabase: {e}")
            import traceback
            traceback.print_exc()
            return None


async def main():
    """Test the crawler"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )

    # Test URL
    test_url = 'https://shoppinglive.naver.com/livebridge/1776510'

    crawler = LivebridgeCrawler()
    result = await crawler.crawl(test_url)

    # Print summary
    print("\n" + "="*70)
    print("CRAWL RESULT SUMMARY")
    print("="*70)
    print(f"Broadcast ID: {result['metadata']['broadcast_id']}")
    print(f"Title: {result['broadcast_info']['title']}")
    print(f"Brand: {result['broadcast_info']['brand_name']}")
    print(f"Start Date: {result['broadcast_info']['expected_start_date']}")
    print(f"Images Found: {len(result['images'])}")
    print("="*70)

    # Save to JSON
    import os
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(
        output_dir,
        f"livebridge_{result['metadata']['broadcast_id']}.json"
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Output saved to: {output_file}")


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
