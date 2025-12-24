"""
네이버 쇼핑라이브 파서
라이브 방송 정보, 상품, 혜택 정보를 추출합니다.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import re
import logging
from datetime import datetime

_v_logger = logging.getLogger(__name__)


class NaverShoppingLiveParser:
    """네이버 쇼핑라이브 파서"""
    
    def __init__(self):
        """파서 초기화"""
        self._v_channel_code = 'NAVER_SHOPPING_LIVE'
        self._v_driver = None
    
    def _init_driver(self):
        """Selenium 드라이버 초기화"""
        _v_options = Options()
        _v_options.add_argument('--headless')  # 헤드리스 모드
        _v_options.add_argument('--no-sandbox')
        _v_options.add_argument('--disable-dev-shm-usage')
        _v_options.add_argument('--disable-gpu')
        _v_options.add_argument('--window-size=1920,1080')
        _v_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        try:
            self._v_driver = webdriver.Chrome(options=_v_options)
            _v_logger.info("Selenium 드라이버 초기화 완료")
        except Exception as p_error:
            _v_logger.error(f"Selenium 드라이버 초기화 실패: {p_error}")
            raise
    
    def _close_driver(self):
        """드라이버 종료"""
        if self._v_driver:
            self._v_driver.quit()
            _v_logger.info("Selenium 드라이버 종료")
    
    def parse_live_broadcast(self, p_url):
        """
        라이브 방송 페이지 파싱
        
        Args:
            p_url (str): 네이버 쇼핑라이브 URL
            
        Returns:
            dict: 파싱된 방송 정보
        """
        try:
            _v_logger.info(f"네이버 쇼핑라이브 크롤링 시작: {p_url}")
            
            # 드라이버 초기화
            self._init_driver()
            
            # 페이지 로드
            self._v_driver.get(p_url)
            time.sleep(3)  # 동적 콘텐츠 로딩 대기
            
            # 페이지 스크롤 (추가 콘텐츠 로드)
            self._v_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # HTML 파싱
            _v_html = self._v_driver.page_source
            _v_soup = BeautifulSoup(_v_html, 'lxml')
            
            # 방송 정보 추출
            _v_broadcast_data = {
                'url': p_url,
                'broadcast_date': self._extract_broadcast_date(_v_soup, _v_html),
                'title': self._extract_title(_v_soup),
                'products': self._extract_products(_v_soup, self._v_driver),
                'benefits': self._extract_benefits(_v_soup, self._v_driver),
                'channel_info': self._extract_channel_info(_v_soup),
            }
            
            _v_logger.info(f"방송 정보 파싱 완료: {_v_broadcast_data['title']}")
            
            return _v_broadcast_data
            
        except Exception as p_error:
            _v_logger.error(f"네이버 쇼핑라이브 파싱 실패: {p_error}")
            raise
        finally:
            self._close_driver()
    
    def _extract_broadcast_date(self, p_soup, p_html):
        """방송일자 추출"""
        try:
            # 여러 패턴으로 방송일자 검색
            
            # 패턴 1: "YYYY.MM.DD" 형식
            _v_date_match = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})', p_html)
            if _v_date_match:
                _v_year = _v_date_match.group(1)
                _v_month = _v_date_match.group(2).zfill(2)
                _v_day = _v_date_match.group(3).zfill(2)
                return f"{_v_year}-{_v_month}-{_v_day}"
            
            # 패턴 2: "MM월 DD일" 형식
            _v_korean_date = re.search(r'(\d{1,2})월\s*(\d{1,2})일', p_html)
            if _v_korean_date:
                _v_current_year = datetime.now().year
                _v_month = _v_korean_date.group(1).zfill(2)
                _v_day = _v_korean_date.group(2).zfill(2)
                return f"{_v_current_year}-{_v_month}-{_v_day}"
            
            # 기본값: 오늘 날짜
            return datetime.now().strftime('%Y-%m-%d')
            
        except Exception as p_error:
            _v_logger.warning(f"방송일자 추출 실패: {p_error}")
            return datetime.now().strftime('%Y-%m-%d')
    
    def _extract_title(self, p_soup):
        """방송 제목 추출"""
        try:
            # 여러 선택자로 제목 검색
            _v_title_selectors = [
                'h1.title',
                'h1',
                '.broadcast-title',
                '.live-title',
                'meta[property="og:title"]',
            ]
            
            for _v_selector in _v_title_selectors:
                if _v_selector.startswith('meta'):
                    _v_elem = p_soup.select_one(_v_selector)
                    if _v_elem and _v_elem.get('content'):
                        return _v_elem['content'].strip()
                else:
                    _v_elem = p_soup.select_one(_v_selector)
                    if _v_elem:
                        return _v_elem.get_text(strip=True)
            
            # 기본 제목
            return "네이버 쇼핑라이브 방송"
            
        except Exception as p_error:
            _v_logger.warning(f"제목 추출 실패: {p_error}")
            return "네이버 쇼핑라이브 방송"
    
    def _extract_products(self, p_soup, p_driver):
        """판매 상품 정보 추출"""
        _v_products = []
        
        try:
            # 상품 요소 찾기
            _v_product_elements = p_soup.select('.product-item, .product-card, [class*="product"]')
            
            for _v_elem in _v_product_elements[:10]:  # 최대 10개
                _v_product = {}
                
                # 상품명
                _v_name_elem = _v_elem.select_one('.product-name, .name, h3, h4')
                if _v_name_elem:
                    _v_product['name'] = _v_name_elem.get_text(strip=True)
                
                # 가격
                _v_price_elem = _v_elem.select_one('.price, .sale-price, [class*="price"]')
                if _v_price_elem:
                    _v_price_text = _v_price_elem.get_text(strip=True)
                    _v_price_match = re.search(r'([\d,]+)원', _v_price_text)
                    if _v_price_match:
                        _v_product['price'] = _v_price_match.group(1).replace(',', '')
                
                # 할인율
                _v_discount_elem = _v_elem.select_one('.discount, .discount-rate, [class*="discount"]')
                if _v_discount_elem:
                    _v_discount_text = _v_discount_elem.get_text(strip=True)
                    _v_discount_match = re.search(r'(\d+)%', _v_discount_text)
                    if _v_discount_match:
                        _v_product['discount_rate'] = _v_discount_match.group(1)
                
                # 재고 정보
                _v_stock_elem = _v_elem.select_one('.stock, [class*="stock"]')
                if _v_stock_elem:
                    _v_stock_text = _v_stock_elem.get_text(strip=True)
                    _v_product['stock_info'] = _v_stock_text
                
                if _v_product.get('name'):
                    _v_products.append(_v_product)
            
            _v_logger.info(f"추출된 상품 수: {len(_v_products)}개")
            
        except Exception as p_error:
            _v_logger.warning(f"상품 정보 추출 실패: {p_error}")
        
        return _v_products
    
    def _extract_benefits(self, p_soup, p_driver):
        """혜택 정보 추출 (할인, 사은품, 쿠폰, 배송혜택)"""
        _v_benefits = {
            'discounts': [],
            'gifts': [],
            'coupons': [],
            'shipping': [],
        }
        
        try:
            # 혜택 섹션 찾기
            _v_benefit_elements = p_soup.select('.benefit, .promotion, [class*="benefit"], [class*="coupon"]')
            
            for _v_elem in _v_benefit_elements:
                _v_text = _v_elem.get_text(strip=True)
                
                # 할인 혜택
                if any(keyword in _v_text for keyword in ['할인', '특가', '세일', '%']):
                    _v_benefits['discounts'].append(_v_text)
                
                # 사은품
                if any(keyword in _v_text for keyword in ['사은품', '증정', '무료제공']):
                    _v_benefits['gifts'].append(_v_text)
                
                # 쿠폰
                if any(keyword in _v_text for keyword in ['쿠폰', '할인쿠폰']):
                    _v_benefits['coupons'].append(_v_text)
                
                # 배송혜택
                if any(keyword in _v_text for keyword in ['무료배송', '배송', '당일배송', '새벽배송']):
                    _v_benefits['shipping'].append(_v_text)
            
            _v_logger.info(f"추출된 혜택: 할인 {len(_v_benefits['discounts'])}개, "
                          f"사은품 {len(_v_benefits['gifts'])}개, "
                          f"쿠폰 {len(_v_benefits['coupons'])}개, "
                          f"배송 {len(_v_benefits['shipping'])}개")
            
        except Exception as p_error:
            _v_logger.warning(f"혜택 정보 추출 실패: {p_error}")
        
        return _v_benefits
    
    def _extract_channel_info(self, p_soup):
        """채널(브랜드) 정보 추출"""
        try:
            _v_channel_elem = p_soup.select_one('.channel-name, .brand-name, [class*="channel"]')
            if _v_channel_elem:
                return _v_channel_elem.get_text(strip=True)
            return "네이버 쇼핑라이브"
        except Exception:
            return "네이버 쇼핑라이브"
    
    def create_event_data(self, p_broadcast_data):
        """
        데이터베이스 저장용 이벤트 데이터 생성
        
        Args:
            p_broadcast_data (dict): 파싱된 방송 정보
            
        Returns:
            dict: 데이터베이스 저장용 이벤트 데이터
        """
        # 상품 정보 요약
        _v_products = p_broadcast_data.get('products', [])
        _v_product_names = [p['name'] for p in _v_products if 'name' in p]
        _v_product_summary = ', '.join(_v_product_names[:5])
        
        # 혜택 정보 요약
        _v_benefits = p_broadcast_data.get('benefits', {})
        _v_benefit_texts = []
        
        if _v_benefits.get('discounts'):
            _v_benefit_texts.extend(_v_benefits['discounts'][:3])
        if _v_benefits.get('coupons'):
            _v_benefit_texts.extend(_v_benefits['coupons'][:2])
        if _v_benefits.get('gifts'):
            _v_benefit_texts.extend(_v_benefits['gifts'][:2])
        if _v_benefits.get('shipping'):
            _v_benefit_texts.append(_v_benefits['shipping'][0])
        
        _v_benefit_summary = ' / '.join(_v_benefit_texts[:5]) if _v_benefit_texts else '다양한 혜택 제공'
        
        # 상세 혜택 정보
        _v_benefit_detail = []
        if _v_benefits.get('discounts'):
            _v_benefit_detail.append(f"📌 할인 혜택:\n" + '\n'.join(f"- {d}" for d in _v_benefits['discounts']))
        if _v_benefits.get('coupons'):
            _v_benefit_detail.append(f"🎟️ 쿠폰:\n" + '\n'.join(f"- {c}" for c in _v_benefits['coupons']))
        if _v_benefits.get('gifts'):
            _v_benefit_detail.append(f"🎁 사은품:\n" + '\n'.join(f"- {g}" for g in _v_benefits['gifts']))
        if _v_benefits.get('shipping'):
            _v_benefit_detail.append(f"🚚 배송 혜택:\n" + '\n'.join(f"- {s}" for s in _v_benefits['shipping']))
        
        _v_benefit_detail_text = '\n\n'.join(_v_benefit_detail) if _v_benefit_detail else '상세 혜택은 방송을 참고해주세요'
        
        # 상품 목록 생성
        _v_product_list = []
        for _v_prod in _v_products[:10]:
            _v_prod_text = _v_prod.get('name', '')
            if _v_prod.get('price'):
                _v_prod_text += f" - {int(_v_prod['price']):,}원"
            if _v_prod.get('discount_rate'):
                _v_prod_text += f" ({_v_prod['discount_rate']}% 할인)"
            if _v_prod.get('stock_info'):
                _v_prod_text += f" [{_v_prod['stock_info']}]"
            _v_product_list.append(_v_prod_text)
        
        _v_target_products = '\n'.join(f"{i+1}. {p}" for i, p in enumerate(_v_product_list))
        
        # URL에서 broadcast_id 추출
        _v_broadcast_id = re.search(r'/replays/(\d+)', p_broadcast_data['url'])
        _v_external_id = f"naver_live_{_v_broadcast_id.group(1)}" if _v_broadcast_id else f"naver_live_{int(time.time())}"
        
        return {
            'external_id': _v_external_id,
            'title': p_broadcast_data['title'],
            'subtitle': f"{p_broadcast_data.get('channel_info', '네이버 쇼핑라이브')} 라이브 방송",
            'description': f"네이버 쇼핑라이브에서 진행된 라이브 방송입니다. {len(_v_products)}개 상품이 소개되었습니다.",
            'start_date': p_broadcast_data['broadcast_date'],
            'end_date': p_broadcast_data['broadcast_date'],
            'benefit_summary': _v_benefit_summary[:500],
            'benefit_detail': _v_benefit_detail_text[:2000],
            'target_products': _v_target_products[:1000] if _v_target_products else _v_product_summary,
            'event_url': p_broadcast_data['url'],
            'conditions': '네이버 쇼핑라이브 방송 상품입니다. 재고 및 혜택은 실시간으로 변동될 수 있습니다.',
            'tags': ['네이버쇼핑라이브', '라이브방송', '라이브커머스', p_broadcast_data.get('channel_info', '')],
            'priority': 7,
        }


def parse_naver_shopping_live(p_url):
    """
    네이버 쇼핑라이브 페이지 파싱 (편의 함수)
    
    Args:
        p_url (str): 네이버 쇼핑라이브 URL
        
    Returns:
        dict: 데이터베이스 저장용 이벤트 데이터
    """
    _v_parser = NaverShoppingLiveParser()
    _v_broadcast_data = _v_parser.parse_live_broadcast(p_url)
    
    if _v_broadcast_data:
        return _v_parser.create_event_data(_v_broadcast_data)
    
    return None


