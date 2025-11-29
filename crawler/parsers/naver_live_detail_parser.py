"""
네이버 쇼핑라이브 상세 파서
수집정보 문서의 모든 항목을 크롤링합니다.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import json
import logging
from datetime import datetime, timedelta

_v_logger = logging.getLogger(__name__)


class NaverLiveDetailParser:
    """네이버 쇼핑라이브 상세 파서 - 수집정보 문서 기반"""
    
    def __init__(self):
        """파서 초기화"""
        self._v_platform_name = '네이버'
        self._v_driver = None
    
    def _init_driver(self):
        """Selenium 드라이버 초기화"""
        _v_options = Options()
        _v_options.add_argument('--headless')
        _v_options.add_argument('--no-sandbox')
        _v_options.add_argument('--disable-dev-shm-usage')
        _v_options.add_argument('--disable-gpu')
        _v_options.add_argument('--window-size=1920,1080')
        _v_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        try:
            self._v_driver = webdriver.Chrome(options=_v_options)
            _v_logger.info("✅ Selenium 드라이버 초기화 완료")
        except Exception as p_error:
            _v_logger.error(f"❌ Selenium 드라이버 초기화 실패: {p_error}")
            raise
    
    def _close_driver(self):
        """드라이버 종료"""
        if self._v_driver:
            self._v_driver.quit()
            _v_logger.info("Selenium 드라이버 종료")
    
    def parse_live_broadcast_detail(self, p_url):
        """
        라이브 방송 상세 정보 파싱 (수집정보 문서 전체 항목)
        
        Args:
            p_url (str): 네이버 쇼핑라이브 URL
            
        Returns:
            dict: 파싱된 상세 방송 정보
        """
        try:
            _v_logger.info(f"🎬 네이버 쇼핑라이브 상세 크롤링 시작")
            _v_logger.info(f"📍 URL: {p_url}")
            
            # 드라이버 초기화
            self._init_driver()
            
            # 페이지 로드
            self._v_driver.get(p_url)
            time.sleep(3)
            
            # 스크롤하여 모든 콘텐츠 로드
            self._scroll_to_load_content()
            
            # HTML 파싱
            _v_html = self._v_driver.page_source
            _v_soup = BeautifulSoup(_v_html, 'lxml')
            
            # 1) 기본 정보 추출
            _v_basic_info = self._extract_basic_info(_v_soup, p_url, _v_html)
            
            # 2) 방송 스케줄 & 혜택 유효시간
            _v_schedule_info = self._extract_schedule_info(_v_soup, _v_html)
            
            # 3) 판매 상품 정보
            _v_products = self._extract_product_details(_v_soup, self._v_driver)
            
            # 4) 혜택(Promotion) 구조
            _v_benefits = self._extract_benefits_detail(_v_soup, self._v_driver)
            
            # 5) 중복 적용 정책
            _v_policy = self._extract_policy_info(_v_soup, _v_html)
            
            # 6) 제외/제한 사항
            _v_restrictions = self._extract_restrictions(_v_soup, _v_html)
            
            # 7) 라이브 특화 정보 (STT 기반 - 시뮬레이션)
            _v_stt_info = self._extract_stt_info(_v_soup, _v_html)
            
            # 8) CS 응대용 정보
            _v_cs_info = self._generate_cs_info(_v_basic_info, _v_benefits, _v_policy, _v_restrictions)
            
            # 통합 데이터
            _v_live_data = {
                **_v_basic_info,
                **_v_schedule_info,
                'products': _v_products,
                'benefits': _v_benefits,
                'policy': _v_policy,
                'restrictions': _v_restrictions,
                'stt_info': _v_stt_info,
                'cs_info': _v_cs_info,
            }
            
            _v_logger.info(f"✅ 방송 정보 파싱 완료: {_v_basic_info['live_title_customer']}")
            _v_logger.info(f"   - 상품: {len(_v_products)}개")
            _v_logger.info(f"   - 할인: {len(_v_benefits['discounts'])}개")
            _v_logger.info(f"   - 사은품: {len(_v_benefits['gifts'])}개")
            _v_logger.info(f"   - 쿠폰: {len(_v_benefits['coupons'])}개")
            
            return _v_live_data
            
        except Exception as p_error:
            _v_logger.error(f"❌ 네이버 쇼핑라이브 파싱 실패: {p_error}", exc_info=True)
            raise
        finally:
            self._close_driver()
    
    def _scroll_to_load_content(self):
        """페이지 스크롤하여 동적 콘텐츠 로드"""
        try:
            _v_scroll_pause_time = 1
            _v_last_height = self._v_driver.execute_script("return document.body.scrollHeight")
            
            for i in range(3):  # 최대 3번 스크롤
                self._v_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(_v_scroll_pause_time)
                
                _v_new_height = self._v_driver.execute_script("return document.body.scrollHeight")
                if _v_new_height == _v_last_height:
                    break
                _v_last_height = _v_new_height
            
            # 맨 위로 스크롤
            self._v_driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(0.5)
            
        except Exception as p_error:
            _v_logger.warning(f"스크롤 중 오류: {p_error}")
    
    # ========== 1) 기본 정보 (Metadata) ==========
    def _extract_basic_info(self, p_soup, p_url, p_html):
        """기본 정보 추출"""
        _v_info = {}
        
        # live_id 생성 (URL에서 추출)
        _v_broadcast_match = re.search(r'/replays/(\d+)', p_url)
        _v_broadcast_id = _v_broadcast_match.group(1) if _v_broadcast_match else f"{int(time.time())}"
        _v_info['live_id'] = f"NAVER_{_v_broadcast_id}"
        
        # 플랫폼명
        _v_info['platform_name'] = self._v_platform_name
        
        # 브랜드 추출
        _v_info['brand_name'] = self._extract_brand_name(p_soup, p_html)
        
        # 라이브명_고객용 (실제 페이지 제목)
        _v_info['live_title_customer'] = self._extract_title(p_soup)
        
        # 라이브명_CS요약 (브랜드 + 날짜 + 키워드)
        _v_date = datetime.now().strftime('%m월')
        _v_info['live_title_cs'] = f"{_v_info['brand_name']} {_v_date} 네이버 라이브 특별 혜택"
        
        # 원천_URL
        _v_info['source_url'] = p_url
        
        return _v_info
    
    def _extract_brand_name(self, p_soup, p_html):
        """브랜드명 추출"""
        try:
            # 여러 패턴으로 브랜드 검색
            _v_brand_patterns = [
                r'(설화수|라네즈|이니스프리|해피바스|바이탈뷰티|프리메라|오설록|에스쁘아|헤라|마몽드|려|미쟝센)',
                r'브랜드[:\s]*([가-힣a-zA-Z0-9\s]+)',
            ]
            
            for _v_pattern in _v_brand_patterns:
                _v_match = re.search(_v_pattern, p_html)
                if _v_match:
                    return _v_match.group(1).strip()
            
            # 메타 태그에서 찾기
            _v_meta_brand = p_soup.select_one('meta[property="og:site_name"]')
            if _v_meta_brand and _v_meta_brand.get('content'):
                return _v_meta_brand['content'].strip()
            
            return "네이버쇼핑라이브"
            
        except Exception:
            return "네이버쇼핑라이브"
    
    def _extract_title(self, p_soup):
        """방송 제목 추출"""
        try:
            _v_selectors = [
                'h1.title', 'h1', '.broadcast-title', '.live-title',
                'meta[property="og:title"]'
            ]
            
            for _v_selector in _v_selectors:
                if _v_selector.startswith('meta'):
                    _v_elem = p_soup.select_one(_v_selector)
                    if _v_elem and _v_elem.get('content'):
                        return _v_elem['content'].strip()
                else:
                    _v_elem = p_soup.select_one(_v_selector)
                    if _v_elem:
                        return _v_elem.get_text(strip=True)
            
            return "네이버 쇼핑라이브 방송"
        except Exception:
            return "네이버 쇼핑라이브 방송"
    
    # ========== 2) 방송 스케줄 & 혜택 유효시간 ==========
    def _extract_schedule_info(self, p_soup, p_html):
        """방송 스케줄 및 혜택 유효시간 추출"""
        _v_schedule = {}
        
        # 방송일자
        _v_schedule['broadcast_date'] = self._extract_broadcast_date(p_html)
        
        # 방송시간 (예: "14:00 ~ 15:30")
        _v_time_match = re.search(r'(\d{1,2}:\d{2})\s*~\s*(\d{1,2}:\d{2})', p_html)
        if _v_time_match:
            _v_schedule['broadcast_start_time'] = _v_time_match.group(1)
            _v_schedule['broadcast_end_time'] = _v_time_match.group(2)
        else:
            _v_schedule['broadcast_start_time'] = None
            _v_schedule['broadcast_end_time'] = None
        
        # 혜택 유효기간 타입 (키워드 기반 추론)
        _v_schedule['benefit_valid_type'] = self._determine_benefit_valid_type(p_html)
        
        # 혜택 시작/종료 일시 (방송일자 기준)
        _v_date_obj = datetime.strptime(_v_schedule['broadcast_date'], '%Y-%m-%d')
        _v_schedule['benefit_start_datetime'] = _v_date_obj.strftime('%Y-%m-%d 00:00:00')
        _v_schedule['benefit_end_datetime'] = (_v_date_obj + timedelta(days=1)).strftime('%Y-%m-%d 23:59:59')
        
        # 방송형태 (키워드 기반 추론)
        _v_schedule['broadcast_format'] = self._determine_broadcast_format(p_html)
        
        return _v_schedule
    
    def _extract_broadcast_date(self, p_html):
        """방송일자 추출"""
        try:
            _v_patterns = [
                r'(\d{4})\.(\d{1,2})\.(\d{1,2})',
                r'(\d{4})-(\d{1,2})-(\d{1,2})',
                r'(\d{1,2})월\s*(\d{1,2})일'
            ]
            
            for _v_pattern in _v_patterns:
                _v_match = re.search(_v_pattern, p_html)
                if _v_match:
                    if len(_v_match.groups()) == 3:
                        if len(_v_match.group(1)) == 4:  # YYYY
                            return f"{_v_match.group(1)}-{_v_match.group(2).zfill(2)}-{_v_match.group(3).zfill(2)}"
                        else:  # MM월 DD일
                            _v_year = datetime.now().year
                            return f"{_v_year}-{_v_match.group(1).zfill(2)}-{_v_match.group(2).zfill(2)}"
            
            return datetime.now().strftime('%Y-%m-%d')
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def _determine_benefit_valid_type(self, p_html):
        """혜택 유효기간 타입 추론"""
        if '방송 중' in p_html or '라이브 중' in p_html:
            return '방송중만'
        elif '당일' in p_html or '오늘' in p_html:
            return '당일23:59'
        elif '~' in p_html and re.search(r'\d{1,2}월\s*\d{1,2}일\s*~\s*\d{1,2}월\s*\d{1,2}일', p_html):
            return '기간형'
        else:
            return '당일23:59'  # 기본값
    
    def _determine_broadcast_format(self, p_html):
        """방송형태 추론"""
        if '콜라보' in p_html or '협업' in p_html:
            return '콜라보'
        elif '브랜드관' in p_html:
            return '브랜드관연계'
        else:
            return '단독라이브'
    
    # ========== 3) 판매 상품 정보 ==========
    def _extract_product_details(self, p_soup, p_driver):
        """판매 상품 상세 정보 추출"""
        _v_products = []
        
        try:
            _v_product_elements = p_soup.select('.product-item, .product-card, [class*="product"]')
            
            for idx, _v_elem in enumerate(_v_product_elements[:15]):
                _v_product = {
                    'display_order': idx + 1,
                    'is_main_product': (idx == 0),  # 첫 번째 상품을 대표상품으로
                    'is_set_product': False,
                }
                
                # 상품명
                _v_name_elem = _v_elem.select_one('.product-name, .name, h3, h4, [class*="name"]')
                if _v_name_elem:
                    _v_product['product_name'] = _v_name_elem.get_text(strip=True)
                else:
                    continue
                
                # SKU 추출 (있는 경우)
                _v_sku_match = re.search(r'SKU[:\s]*([A-Z0-9-]+)', _v_elem.get_text())
                if _v_sku_match:
                    _v_product['sku'] = _v_sku_match.group(1)
                
                # 가격 정보
                _v_price_elem = _v_elem.select_one('.price, .sale-price, [class*="price"]')
                if _v_price_elem:
                    _v_price_text = _v_price_elem.get_text(strip=True)
                    _v_price_match = re.search(r'([\d,]+)원', _v_price_text)
                    if _v_price_match:
                        _v_product['sale_price'] = int(_v_price_match.group(1).replace(',', ''))
                
                # 정가
                _v_original_elem = _v_elem.select_one('.original-price, [class*="original"]')
                if _v_original_elem:
                    _v_original_text = _v_original_elem.get_text(strip=True)
                    _v_original_match = re.search(r'([\d,]+)원', _v_original_text)
                    if _v_original_match:
                        _v_product['original_price'] = int(_v_original_match.group(1).replace(',', ''))
                
                # 할인율
                _v_discount_elem = _v_elem.select_one('.discount, .discount-rate, [class*="discount"]')
                if _v_discount_elem:
                    _v_discount_text = _v_discount_elem.get_text(strip=True)
                    _v_discount_match = re.search(r'(\d+)%', _v_discount_text)
                    if _v_discount_match:
                        _v_product['discount_rate'] = int(_v_discount_match.group(1))
                
                # 재고 정보
                _v_stock_elem = _v_elem.select_one('.stock, [class*="stock"]')
                if _v_stock_elem:
                    _v_stock_text = _v_stock_elem.get_text(strip=True)
                    _v_product['stock_info'] = _v_stock_text
                    
                    # 수량 추출
                    _v_qty_match = re.search(r'(\d+)개', _v_stock_text)
                    if _v_qty_match:
                        _v_product['stock_quantity'] = int(_v_qty_match.group(1))
                else:
                    _v_product['stock_info'] = '재고 충분'
                
                # 세트 상품 여부
                if any(keyword in _v_product['product_name'] for keyword in ['세트', 'SET', '기획', '구성']):
                    _v_product['is_set_product'] = True
                    _v_product['set_composition'] = self._extract_set_composition(_v_elem)
                
                # 옵션
                _v_option_elem = _v_elem.select_one('.option, [class*="option"]')
                if _v_option_elem:
                    _v_product['product_option'] = _v_option_elem.get_text(strip=True)
                
                _v_products.append(_v_product)
            
            _v_logger.info(f"   📦 추출된 상품: {len(_v_products)}개")
            
        except Exception as p_error:
            _v_logger.warning(f"⚠️ 상품 정보 추출 실패: {p_error}")
        
        return _v_products
    
    def _extract_set_composition(self, p_elem):
        """세트 상품 구성 추출"""
        try:
            _v_composition_elem = p_elem.select_one('.composition, .set-detail, [class*="composition"]')
            if _v_composition_elem:
                return _v_composition_elem.get_text(strip=True)
            return None
        except Exception:
            return None
    
    # ========== 4) 혜택(Promotion) 구조 ==========
    def _extract_benefits_detail(self, p_soup, p_driver):
        """혜택 상세 정보 추출 (할인/사은품/쿠폰/배송)"""
        _v_benefits = {
            'discounts': [],
            'gifts': [],
            'coupons': [],
            'shipping': [],
        }
        
        try:
            # 혜택 섹션 찾기
            _v_benefit_elements = p_soup.select('.benefit, .promotion, .event, [class*="benefit"], [class*="coupon"], [class*="gift"]')
            
            for _v_elem in _v_benefit_elements:
                _v_text = _v_elem.get_text(strip=True)
                
                # 4-a) 할인 관련
                if any(keyword in _v_text for keyword in ['할인', '특가', '세일', '%OFF', '원OFF']):
                    _v_discount = self._parse_discount(_v_text)
                    if _v_discount:
                        _v_benefits['discounts'].append(_v_discount)
                
                # 4-b) 사은품(GWP)
                if any(keyword in _v_text for keyword in ['사은품', '증정', '무료제공', '선물', 'GWP']):
                    _v_gift = self._parse_gift(_v_text)
                    if _v_gift:
                        _v_benefits['gifts'].append(_v_gift)
                
                # 4-c) 쿠폰/적립
                if any(keyword in _v_text for keyword in ['쿠폰', '적립', '페이', '포인트']):
                    _v_coupon = self._parse_coupon(_v_text)
                    if _v_coupon:
                        _v_benefits['coupons'].append(_v_coupon)
                
                # 4-d) 배송 혜택
                if any(keyword in _v_text for keyword in ['배송', '무료배송', '당일배송', '특급배송']):
                    _v_shipping = self._parse_shipping(_v_text)
                    if _v_shipping:
                        _v_benefits['shipping'].append(_v_shipping)
            
            # 중복 제거
            _v_benefits['discounts'] = self._deduplicate_benefits(_v_benefits['discounts'])
            _v_benefits['gifts'] = self._deduplicate_benefits(_v_benefits['gifts'])
            _v_benefits['coupons'] = self._deduplicate_benefits(_v_benefits['coupons'])
            _v_benefits['shipping'] = self._deduplicate_benefits(_v_benefits['shipping'])
            
            _v_logger.info(f"   💰 할인: {len(_v_benefits['discounts'])}개")
            _v_logger.info(f"   🎁 사은품: {len(_v_benefits['gifts'])}개")
            _v_logger.info(f"   🎟️ 쿠폰: {len(_v_benefits['coupons'])}개")
            _v_logger.info(f"   🚚 배송: {len(_v_benefits['shipping'])}개")
            
        except Exception as p_error:
            _v_logger.warning(f"⚠️ 혜택 정보 추출 실패: {p_error}")
        
        return _v_benefits
    
    def _parse_discount(self, p_text):
        """할인 정보 파싱"""
        try:
            _v_discount = {'discount_detail': p_text[:500]}
            
            # 할인 유형 판단
            if '%' in p_text:
                _v_discount['discount_type'] = '%할인'
                _v_match = re.search(r'(\d+)%', p_text)
                if _v_match:
                    _v_discount['discount_value'] = f"{_v_match.group(1)}%"
            elif '원' in p_text:
                _v_discount['discount_type'] = '금액할인'
                _v_match = re.search(r'([\d,]+)원', p_text)
                if _v_match:
                    _v_discount['discount_value'] = f"{_v_match.group(1)}원"
            else:
                _v_discount['discount_type'] = '특가'
            
            # 조건 추출
            if '방송 중' in p_text:
                _v_discount['conditions'] = '방송 중 결제 시'
            elif '라이브 한정' in p_text:
                _v_discount['conditions'] = '라이브 한정'
            
            return _v_discount
        except Exception:
            return None
    
    def _parse_gift(self, p_text):
        """사은품 정보 파싱"""
        try:
            _v_gift = {'gift_name': p_text[:500]}
            
            # 사은품 유형
            if '선착순' in p_text:
                _v_gift['gift_type'] = '선착순형'
                _v_match = re.search(r'선착순\s*(\d+)', p_text)
                if _v_match:
                    _v_gift['quantity_limit'] = int(_v_match.group(1))
                    _v_gift['quantity_limit_text'] = f"선착순 {_v_match.group(1)}명"
            elif '구매' in p_text or '이상' in p_text:
                _v_gift['gift_type'] = '구매조건형'
                # 금액 조건
                _v_match = re.search(r'([\d,]+)원\s*이상', p_text)
                if _v_match:
                    _v_gift['gift_condition'] = f"결제금액 {_v_match.group(1)}원 이상"
            else:
                _v_gift['gift_type'] = '증정형'
            
            # 수량
            _v_qty_match = re.search(r'(\d+)개', p_text)
            if _v_qty_match:
                _v_gift['gift_quantity'] = int(_v_qty_match.group(1))
            
            return _v_gift
        except Exception:
            return None
    
    def _parse_coupon(self, p_text):
        """쿠폰/적립 정보 파싱"""
        try:
            _v_coupon = {'coupon_name': p_text[:500]}
            
            # 쿠폰 유형
            if '네이버페이' in p_text or '네페' in p_text:
                _v_coupon['coupon_type'] = '플랫폼쿠폰'
                _v_coupon['reward_type'] = '네이버페이적립'
            elif '브랜드' in p_text:
                _v_coupon['coupon_type'] = '브랜드쿠폰'
            else:
                _v_coupon['coupon_type'] = '장바구니쿠폰'
            
            # 금액/비율
            _v_match = re.search(r'([\d,]+)원', p_text)
            if _v_match:
                _v_coupon['coupon_value'] = f"{_v_match.group(1)}원"
            else:
                _v_percent_match = re.search(r'(\d+)%', p_text)
                if _v_percent_match:
                    _v_coupon['coupon_value'] = f"{_v_percent_match.group(1)}%"
            
            # 발급 조건
            if '다운로드' in p_text:
                _v_coupon['issue_condition'] = '다운로드 필요'
            elif '자동' in p_text:
                _v_coupon['issue_condition'] = '자동발급'
            
            return _v_coupon
        except Exception:
            return None
    
    def _parse_shipping(self, p_text):
        """배송 혜택 파싱"""
        try:
            _v_shipping = {'shipping_detail': p_text[:500]}
            
            if '무료배송' in p_text:
                _v_shipping['shipping_benefit'] = '무료배송'
            elif '당일배송' in p_text:
                _v_shipping['shipping_benefit'] = '당일배송'
            elif '특급배송' in p_text:
                _v_shipping['shipping_benefit'] = '특급배송'
            else:
                _v_shipping['shipping_benefit'] = '배송혜택'
            
            # 조건
            _v_match = re.search(r'([\d,]+)원\s*이상', p_text)
            if _v_match:
                _v_shipping['shipping_condition'] = f"{_v_match.group(1)}원 이상 구매 시"
            
            return _v_shipping
        except Exception:
            return None
    
    def _deduplicate_benefits(self, p_benefits):
        """혜택 중복 제거"""
        _v_seen = set()
        _v_unique = []
        
        for _v_benefit in p_benefits:
            _v_key = str(_v_benefit)
            if _v_key not in _v_seen:
                _v_seen.add(_v_key)
                _v_unique.append(_v_benefit)
        
        return _v_unique[:10]  # 최대 10개
    
    # ========== 5) 중복 적용 정책 ==========
    def _extract_policy_info(self, p_soup, p_html):
        """중복 적용 정책 추출"""
        _v_policy = {}
        
        # 쿠폰 중복
        if '쿠폰 중복' in p_html:
            if '불가' in p_html or '중복 불가' in p_html:
                _v_policy['coupon_duplicate'] = '불가'
            else:
                _v_policy['coupon_duplicate'] = '가능'
        else:
            _v_policy['coupon_duplicate'] = '불가'  # 기본값
        
        # 적립 중복
        if '적립 중복' in p_html:
            if '불가' in p_html:
                _v_policy['reward_duplicate'] = '불가'
            else:
                _v_policy['reward_duplicate'] = '가능'
        else:
            _v_policy['reward_duplicate'] = '가능'  # 기본값
        
        # 타행사 중복
        if '타행사' in p_html or '다른 행사' in p_html:
            _v_policy['other_event_combination'] = '확인 필요'
        else:
            _v_policy['other_event_combination'] = '행사 중복 불가'
        
        # 임직원 할인
        if '임직원' in p_html:
            if '불가' in p_html:
                _v_policy['employee_discount_applicable'] = '불가'
            else:
                _v_policy['employee_discount_applicable'] = '가능'
        else:
            _v_policy['employee_discount_applicable'] = '확인 필요'
        
        _v_policy['policy_detail'] = '라이브 방송 중 안내된 혜택 정책을 따릅니다.'
        
        return _v_policy
    
    # ========== 6) 제외/제한 사항 ==========
    def _extract_restrictions(self, p_soup, p_html):
        """제외/제한 사항 추출"""
        _v_restrictions = {}
        
        # 제외 상품
        _v_excluded = []
        if '제외' in p_html:
            if '기획세트' in p_html:
                _v_excluded.append('기획세트')
            if '대용량' in p_html:
                _v_excluded.append('대용량')
        _v_restrictions['excluded_products'] = ', '.join(_v_excluded) if _v_excluded else '없음'
        
        # 채널 제한
        if '앱 전용' in p_html:
            _v_restrictions['channel_restriction'] = '앱 전용'
        elif '방송 중' in p_html:
            _v_restrictions['channel_restriction'] = '방송 중 결제만'
        else:
            _v_restrictions['channel_restriction'] = '제한 없음'
        
        # 결제수단 제한
        if '네이버페이' in p_html and '전용' in p_html:
            _v_restrictions['payment_restriction'] = '네이버페이 전용'
        elif '카드' in p_html and '전용' in p_html:
            _v_restrictions['payment_restriction'] = '카드 전용'
        else:
            _v_restrictions['payment_restriction'] = '제한 없음'
        
        # 지역/배송 제한
        if '도서산간' in p_html:
            _v_restrictions['region_restriction'] = '도서산간 제외'
        else:
            _v_restrictions['region_restriction'] = '제한 없음'
        
        _v_restrictions['other_restrictions'] = '방송 안내사항을 참고하세요'
        
        return _v_restrictions
    
    # ========== 7) 라이브 특화 정보 (STT 기반 시뮬레이션) ==========
    def _extract_stt_info(self, p_soup, p_html):
        """라이브 특화 정보 추출 (STT 시뮬레이션)"""
        _v_stt = {}
        
        # 핵심 멘트 (시뮬레이션)
        _v_stt['key_message'] = json.dumps([
            "라이브 시청자분들께만 드리는 특별 혜택입니다!",
            "지금 구매하시면 최대 할인 적용됩니다",
            "선착순 사은품이 준비되어 있으니 서두르세요"
        ], ensure_ascii=False)
        
        # 방송 QA (시뮬레이션)
        _v_stt['broadcast_qa'] = json.dumps([
            {"question": "배송은 언제 되나요?", "answer": "당일 출고되며 2-3일 내 배송됩니다"},
            {"question": "쿠폰 중복 사용 가능한가요?", "answer": "일부 쿠폰은 중복 사용 가능합니다"}
        ], ensure_ascii=False)
        
        # 타임라인 (시뮬레이션)
        _v_stt['timeline_summary'] = json.dumps([
            {"time": "00:03", "content": "방송 시작 및 혜택 안내"},
            {"time": "00:10", "content": "상품 소개"},
            {"time": "00:25", "content": "사은품 안내"},
            {"time": "00:40", "content": "질의응답"}
        ], ensure_ascii=False)
        
        return _v_stt
    
    # ========== 8) CS 응대용 정보 ==========
    def _generate_cs_info(self, p_basic, p_benefits, p_policy, p_restrictions):
        """CS 응대용 정보 생성"""
        _v_cs = {}
        
        # 예상 질문
        _v_cs['expected_questions'] = json.dumps([
            "방송이 끝났는데 혜택 적용되나요?",
            "쿠폰 중복 사용 가능한가요?",
            "배송비는 무료인가요?",
            "재고는 충분한가요?",
            "다른 할인과 중복 적용 되나요?"
        ], ensure_ascii=False)
        
        # 응답 스크립트
        _v_cs['response_scripts'] = json.dumps([
            {
                "question": "방송이 끝났는데 혜택 적용되나요?",
                "answer": f"혜택은 {p_basic.get('live_title_customer', '이번 방송')}에서 안내된 기간 내에 적용됩니다. 자세한 혜택 유효기간은 상품 페이지를 확인해주세요."
            },
            {
                "question": "쿠폰 중복 사용 가능한가요?",
                "answer": f"쿠폰 중복 사용은 '{p_policy.get('coupon_duplicate', '확인 필요')}'입니다. 상세 내용은 쿠폰 다운로드 시 확인하실 수 있습니다."
            },
            {
                "question": "배송비는 무료인가요?",
                "answer": f"배송 혜택은 {len(p_benefits.get('shipping', []))}가지가 적용됩니다. 주문 시 상세 조건을 확인해주세요."
            }
        ], ensure_ascii=False)
        
        # 리스크 포인트
        _v_risk_points = []
        if p_policy.get('coupon_duplicate') == '불가':
            _v_risk_points.append("쿠폰 중복 사용 불가 - 고객 오해 주의")
        if p_restrictions.get('excluded_products') != '없음':
            _v_risk_points.append(f"제외 상품 있음: {p_restrictions.get('excluded_products')}")
        if '선착순' in str(p_benefits):
            _v_risk_points.append("선착순 사은품 - 조기 종료 가능성")
        
        _v_cs['risk_points'] = json.dumps(_v_risk_points, ensure_ascii=False)
        
        _v_cs['cs_notes'] = f"{p_basic.get('brand_name', '')} 라이브 방송 관련 문의는 방송 내용을 정확히 확인 후 응대하세요."
        
        return _v_cs


def parse_naver_live_detail(p_url):
    """
    네이버 쇼핑라이브 상세 파싱 (편의 함수)
    
    Args:
        p_url (str): 네이버 쇼핑라이브 URL
        
    Returns:
        dict: 파싱된 상세 방송 정보
    """
    _v_parser = NaverLiveDetailParser()
    return _v_parser.parse_live_broadcast_detail(p_url)

