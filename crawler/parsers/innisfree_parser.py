"""
이니스프리 이벤트 페이지 파서
특정 이벤트 페이지의 상품 정보를 추출합니다.
"""

from bs4 import BeautifulSoup
import re
from datetime import datetime
import logging

_v_logger = logging.getLogger(__name__)


class InnisfreeEventParser:
    """이니스프리 이벤트 페이지 파서"""
    
    def __init__(self):
        """파서 초기화"""
        self._v_channel_code = 'INNISFREE_MALL'
    
    def parse_event_page(self, p_html, p_url):
        """
        이벤트 페이지 HTML 파싱
        
        Args:
            p_html (str): HTML 콘텐츠
            p_url (str): 이벤트 페이지 URL
            
        Returns:
            dict: 파싱된 이벤트 정보
        """
        try:
            _v_soup = BeautifulSoup(p_html, 'lxml')
            
            # 이벤트 기본 정보 추출
            _v_event_info = self._extract_event_info(_v_soup, p_url)
            
            # 상품 목록 추출
            _v_products = self._extract_products(_v_soup)
            
            _v_event_info['products'] = _v_products
            
            _v_logger.info(f"이니스프리 이벤트 파싱 완료: {_v_event_info.get('title')} ({len(_v_products)}개 상품)")
            
            return _v_event_info
            
        except Exception as p_error:
            _v_logger.error(f"이니스프리 이벤트 파싱 실패: {p_error}")
            return None
    
    def _extract_event_info(self, p_soup, p_url):
        """
        이벤트 기본 정보 추출
        
        Args:
            p_soup: BeautifulSoup 객체
            p_url (str): 이벤트 URL
            
        Returns:
            dict: 이벤트 기본 정보
        """
        _v_event = {
            'channel_code': self._v_channel_code,
            'event_url': p_url,
        }
        
        # 이벤트 제목 추출
        _v_title_elem = p_soup.select_one('h2, .event-title')
        if _v_title_elem:
            _v_event['title'] = _v_title_elem.get_text(strip=True)
        else:
            _v_event['title'] = '이니스프리 이벤트'
        
        # 이벤트 기간 추출
        _v_date_pattern = r'(\d{2,4})\.(\d{1,2})\.(\d{1,2})'
        _v_date_text = p_soup.get_text()
        _v_dates = re.findall(_v_date_pattern, _v_date_text)
        
        if len(_v_dates) >= 2:
            # 시작일
            _v_start_year = _v_dates[0][0] if len(_v_dates[0][0]) == 4 else f"20{_v_dates[0][0]}"
            _v_event['start_date'] = f"{_v_start_year}-{_v_dates[0][1].zfill(2)}-{_v_dates[0][2].zfill(2)}"
            
            # 종료일
            _v_end_year = _v_dates[1][0] if len(_v_dates[1][0]) == 4 else f"20{_v_dates[1][0]}"
            _v_event['end_date'] = f"{_v_end_year}-{_v_dates[1][1].zfill(2)}-{_v_dates[1][2].zfill(2)}"
        else:
            # 기본값 설정
            _v_today = datetime.now()
            _v_event['start_date'] = _v_today.strftime('%Y-%m-%d')
            _v_event['end_date'] = '2025-12-31'
        
        return _v_event
    
    def _extract_products(self, p_soup):
        """
        이벤트 상품 목록 추출
        
        Args:
            p_soup: BeautifulSoup 객체
            
        Returns:
            list: 상품 정보 리스트
        """
        _v_products = []
        
        # 상품 카드 요소 찾기 (일반적인 선택자)
        _v_product_cards = p_soup.select('.product-item, .item, article')
        
        for _v_card in _v_product_cards:
            try:
                _v_product = {}
                
                # 상품명
                _v_name_elem = _v_card.select_one('.product-name, .title, h3, h4')
                if _v_name_elem:
                    _v_product['name'] = _v_name_elem.get_text(strip=True)
                else:
                    continue  # 상품명이 없으면 스킵
                
                # 가격 정보
                _v_price_elem = _v_card.select_one('.price, .sale-price')
                if _v_price_elem:
                    _v_price_text = _v_price_elem.get_text(strip=True)
                    _v_price_match = re.search(r'([\d,]+)원', _v_price_text)
                    if _v_price_match:
                        _v_product['sale_price'] = _v_price_match.group(1).replace(',', '')
                
                # 원가
                _v_original_price_elem = _v_card.select_one('.original-price, del')
                if _v_original_price_elem:
                    _v_orig_text = _v_original_price_elem.get_text(strip=True)
                    _v_orig_match = re.search(r'([\d,]+)원', _v_orig_text)
                    if _v_orig_match:
                        _v_product['original_price'] = _v_orig_match.group(1).replace(',', '')
                
                # 할인율
                _v_discount_elem = _v_card.select_one('.discount, .percent')
                if _v_discount_elem:
                    _v_discount_text = _v_discount_elem.get_text(strip=True)
                    _v_discount_match = re.search(r'(\d+)%', _v_discount_text)
                    if _v_discount_match:
                        _v_product['discount_rate'] = _v_discount_match.group(1)
                
                # 상품 URL
                _v_link_elem = _v_card.select_one('a[href]')
                if _v_link_elem:
                    _v_href = _v_link_elem.get('href', '')
                    if _v_href.startswith('http'):
                        _v_product['url'] = _v_href
                    elif _v_href.startswith('/'):
                        _v_product['url'] = f"https://www.innisfree.com{_v_href}"
                
                # 이미지 URL
                _v_img_elem = _v_card.select_one('img')
                if _v_img_elem:
                    _v_product['image_url'] = _v_img_elem.get('src', '')
                
                if _v_product:
                    _v_products.append(_v_product)
                    
            except Exception as p_error:
                _v_logger.warning(f"상품 파싱 중 에러: {p_error}")
                continue
        
        return _v_products
    
    def create_event_data(self, p_event_info):
        """
        데이터베이스 저장용 이벤트 데이터 생성
        
        Args:
            p_event_info (dict): 파싱된 이벤트 정보
            
        Returns:
            dict: 데이터베이스 저장용 이벤트 데이터
        """
        # 상품 정보 요약
        _v_products = p_event_info.get('products', [])
        _v_product_summary = []
        
        for _v_prod in _v_products[:5]:  # 최대 5개
            if 'name' in _v_prod:
                _v_summary = _v_prod['name']
                if 'discount_rate' in _v_prod:
                    _v_summary += f" ({_v_prod['discount_rate']}% 할인)"
                _v_product_summary.append(_v_summary)
        
        _v_benefit_text = ', '.join(_v_product_summary) if _v_product_summary else '다양한 상품 할인 진행'
        
        return {
            'external_id': f"innisfree_event_{p_event_info.get('event_url', '').split('/')[-1]}",
            'title': p_event_info.get('title', '이니스프리 이벤트'),
            'subtitle': f"총 {len(_v_products)}개 상품",
            'description': f"이니스프리에서 진행하는 특별 이벤트입니다.",
            'start_date': p_event_info.get('start_date'),
            'end_date': p_event_info.get('end_date'),
            'benefit_summary': _v_benefit_text[:500],
            'benefit_detail': f"참여 상품: {len(_v_products)}개\n" + '\n'.join(_v_product_summary),
            'target_products': ', '.join([p['name'] for p in _v_products if 'name' in p])[:1000],
            'event_url': p_event_info.get('event_url'),
            'conditions': 'APP 전용 이벤트일 수 있습니다. 자세한 내용은 이벤트 페이지를 확인하세요.',
            'tags': ['이니스프리', 'APP전용', '할인'],
            'priority': 5,
        }


def parse_innisfree_event(p_html, p_url):
    """
    이니스프리 이벤트 페이지 파싱 (편의 함수)
    
    Args:
        p_html (str): HTML 콘텐츠
        p_url (str): 이벤트 URL
        
    Returns:
        dict: 데이터베이스 저장용 이벤트 데이터
    """
    _v_parser = InnisfreeEventParser()
    _v_event_info = _v_parser.parse_event_page(p_html, p_url)
    
    if _v_event_info:
        return _v_parser.create_event_data(_v_event_info)
    
    return None


