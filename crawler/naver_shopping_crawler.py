#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
네이버 쇼핑 전시 페이지 크롤러
네이버 스마트스토어 쇼핑스토리 전시 페이지에서 행사 정보를 수집합니다.

수집 항목:
1. 플랫폼명: 네이버스마트스토어
2. 브랜드명
3. 행사 타이틀
4. 행사 일자
5. 혜택 정보 (금액대별 혜택, 쿠폰)
6. 상품 정보
"""

import os
import sys
import time
import re
import json
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client

# 로깅 설정
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('naver_shopping_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 환경 변수 로드
load_dotenv()


class NaverShoppingCrawler:
    """네이버 쇼핑 전시 페이지 크롤러"""
    
    def __init__(self):
        """크롤러 초기화"""
        self.driver = None
        self.supabase: Optional[Client] = None
        self._init_supabase()
    
    def _init_supabase(self):
        """Supabase 클라이언트 초기화"""
        try:
            _v_url = os.getenv('SUPABASE_URL')
            _v_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not _v_url or not _v_key:
                logger.warning("⚠️ Supabase 환경 변수가 설정되지 않았습니다.")
                return
            
            self.supabase = create_client(_v_url, _v_key)
            logger.info("✅ Supabase 연결 성공")
        except Exception as e:
            logger.error(f"❌ Supabase 연결 실패: {e}")
    
    def _init_driver(self):
        """Selenium WebDriver 초기화"""
        try:
            _v_chrome_options = Options()
            _v_chrome_options.add_argument('--headless')
            _v_chrome_options.add_argument('--no-sandbox')
            _v_chrome_options.add_argument('--disable-dev-shm-usage')
            _v_chrome_options.add_argument('--disable-gpu')
            _v_chrome_options.add_argument('--window-size=1920,1080')
            _v_chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=_v_chrome_options
            )
            logger.info("✅ WebDriver 초기화 성공")
        except Exception as e:
            logger.error(f"❌ WebDriver 초기화 실패: {e}")
            raise
    
    def crawl(self, p_url: str, p_brand: str = "아이오페") -> Dict:
        """
        네이버 쇼핑 전시 페이지 크롤링
        
        Args:
            p_url: 크롤링할 URL
            p_brand: 브랜드명
        
        Returns:
            수집된 데이터 딕셔너리
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"🔍 네이버 쇼핑 전시 페이지 크롤링 시작")
        logger.info(f"{'='*80}")
        logger.info(f"📍 URL: {p_url}")
        logger.info(f"🏷️  브랜드: {p_brand}")
        
        try:
            # WebDriver 초기화
            if not self.driver:
                self._init_driver()
            
            # 페이지 로드
            logger.info("\n📄 페이지 로딩 중...")
            self.driver.get(p_url)
            time.sleep(5)  # 동적 콘텐츠 로딩 대기
            
            # 페이지 스크롤 (lazy loading 콘텐츠 로드)
            logger.info("📜 페이지 스크롤 중...")
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(2)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            # 데이터 수집
            _v_data = {
                'platform': '네이버스마트스토어',
                'brand': p_brand,
                'url': p_url,
                'event_id': self._extract_event_id(p_url),
                'title': self._collect_title(),
                'date_info': self._collect_date(),
                'benefits': self._collect_benefits(),
                'coupons': self._collect_coupons(),
                'products': self._collect_products(),
                'collected_at': datetime.now().isoformat()
            }
            
            logger.info(f"\n✅ 데이터 수집 완료!")
            logger.info(f"   타이틀: {_v_data['title']}")
            logger.info(f"   행사 일자: {_v_data['date_info']}")
            logger.info(f"   혜택: {len(_v_data['benefits'])}개")
            logger.info(f"   쿠폰: {len(_v_data['coupons'])}개")
            logger.info(f"   상품: {len(_v_data['products'])}개")
            
            return _v_data
            
        except Exception as e:
            logger.error(f"❌ 크롤링 실패: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _extract_event_id(self, p_url: str) -> str:
        """URL에서 이벤트 ID 추출"""
        try:
            _v_parsed = urlparse(p_url)
            _v_params = parse_qs(_v_parsed.query)
            _v_event_id = _v_params.get('id', [''])[0]
            return f"NAVER_SHOPPING_{_v_event_id}" if _v_event_id else f"NAVER_SHOPPING_{int(time.time())}"
        except:
            return f"NAVER_SHOPPING_{int(time.time())}"
    
    def _collect_title(self) -> str:
        """행사 타이틀 수집"""
        logger.info("\n📌 [1] 행사 타이틀 수집 중...")
        
        try:
            # 페이지 소스에서 타이틀 찾기
            _v_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 방법 1: 페이지 타이틀
            _v_page_title = self.driver.title
            if _v_page_title and '쇼핑스토리' not in _v_page_title:
                logger.info(f"   ✅ 타이틀 발견: {_v_page_title}")
                return _v_page_title.strip()
            
            # 방법 2: 텍스트에서 패턴 매칭
            _v_all_text = _v_soup.get_text()
            
            # "아이오페 XMD스템3" 같은 패턴 찾기
            _v_title_patterns = [
                r'아이오페\s+[A-Z]+[가-힣\s]+',
                r'[가-힣]+\s+기획전',
                r'[가-힣]+\s+프로모션',
                r'[가-힣]+\s+이벤트'
            ]
            
            for pattern in _v_title_patterns:
                _v_match = re.search(pattern, _v_all_text)
                if _v_match:
                    _v_title = _v_match.group(0).strip()
                    logger.info(f"   ✅ 타이틀 발견: {_v_title}")
                    return _v_title
            
            # 방법 3: h1, h2 태그
            for tag in ['h1', 'h2', 'h3']:
                _v_heading = _v_soup.find(tag)
                if _v_heading:
                    _v_text = _v_heading.get_text(strip=True)
                    if _v_text and len(_v_text) > 5:
                        logger.info(f"   ✅ 타이틀 발견: {_v_text}")
                        return _v_text
            
            logger.warning("   ⚠️ 타이틀을 찾을 수 없습니다.")
            return "제목 없음"
            
        except Exception as e:
            logger.error(f"   ❌ 타이틀 수집 실패: {e}")
            return "제목 없음"
    
    def _collect_date(self) -> str:
        """행사 일자 수집"""
        logger.info("\n📅 [2] 행사 일자 수집 중...")
        
        try:
            _v_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            _v_all_text = _v_soup.get_text()
            
            # 날짜 패턴 찾기
            _v_date_patterns = [
                r'\d{2,4}[./-]\d{1,2}[./-]\d{1,2}\s*~\s*\d{2,4}[./-]\d{1,2}[./-]\d{1,2}',  # 기간
                r'\d{2,4}[./-]\d{1,2}[./-]\d{1,2}',  # 단일 날짜
            ]
            
            for pattern in _v_date_patterns:
                _v_matches = re.findall(pattern, _v_all_text)
                if _v_matches:
                    _v_date = _v_matches[0]
                    logger.info(f"   ✅ 행사 일자 발견: {_v_date}")
                    return _v_date
            
            logger.warning("   ⚠️ 행사 일자를 찾을 수 없습니다.")
            return "날짜 정보 없음"
            
        except Exception as e:
            logger.error(f"   ❌ 행사 일자 수집 실패: {e}")
            return "날짜 정보 없음"
    
    def _collect_benefits(self) -> List[Dict]:
        """혜택 정보 수집 (금액대별 혜택)"""
        logger.info("\n🎁 [3] 혜택 정보 수집 중...")
        
        _v_benefits = []
        
        try:
            _v_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            _v_all_text = _v_soup.get_text()
            
            # 금액대별 혜택 패턴
            _v_price_patterns = [
                r'(\d+만?\s*원)\s*이상\s*구매\s*시?\s*([^.]+)',
                r'전\s*구매\s*고객\s*([^.]+)',
            ]
            
            for pattern in _v_price_patterns:
                _v_matches = re.findall(pattern, _v_all_text)
                for match in _v_matches:
                    if isinstance(match, tuple):
                        if len(match) == 2:
                            _v_benefits.append({
                                'type': '금액대별 혜택',
                                'condition': match[0].strip(),
                                'benefit': match[1].strip()[:200]
                            })
                        else:
                            _v_benefits.append({
                                'type': '금액대별 혜택',
                                'condition': '전 구매 고객',
                                'benefit': match[0].strip()[:200]
                            })
            
            logger.info(f"   ✅ 혜택 {len(_v_benefits)}개 수집")
            for idx, benefit in enumerate(_v_benefits, 1):
                logger.info(f"      [{idx}] {benefit['condition']}: {benefit['benefit'][:50]}")
            
            return _v_benefits
            
        except Exception as e:
            logger.error(f"   ❌ 혜택 정보 수집 실패: {e}")
            return []
    
    def _collect_coupons(self) -> List[Dict]:
        """쿠폰 정보 수집"""
        logger.info("\n🎫 [4] 쿠폰 정보 수집 중...")
        
        _v_coupons = []
        
        try:
            _v_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            _v_all_text = _v_soup.get_text()
            
            # 쿠폰 관련 텍스트 찾기
            _v_coupon_keywords = ['쿠폰', 'COUPON']
            _v_lines = _v_all_text.split('\n')
            
            for line in _v_lines:
                for keyword in _v_coupon_keywords:
                    if keyword in line:
                        _v_clean_line = line.strip()
                        if _v_clean_line and len(_v_clean_line) > 3 and len(_v_clean_line) < 200:
                            _v_coupons.append({
                                'type': '쿠폰',
                                'name': _v_clean_line
                            })
            
            # 중복 제거
            _v_unique_coupons = []
            _v_seen = set()
            for coupon in _v_coupons:
                if coupon['name'] not in _v_seen:
                    _v_seen.add(coupon['name'])
                    _v_unique_coupons.append(coupon)
            
            logger.info(f"   ✅ 쿠폰 {len(_v_unique_coupons)}개 수집")
            for idx, coupon in enumerate(_v_unique_coupons, 1):
                logger.info(f"      [{idx}] {coupon['name'][:80]}")
            
            return _v_unique_coupons
            
        except Exception as e:
            logger.error(f"   ❌ 쿠폰 정보 수집 실패: {e}")
            return []
    
    def _collect_products(self) -> List[Dict]:
        """상품 정보 수집"""
        logger.info("\n🛍️  [5] 상품 정보 수집 중...")
        
        _v_products = []
        
        try:
            # Selenium으로 상품 요소 찾기
            try:
                # 상품 링크 찾기 (a 태그 중 상품 URL 패턴)
                _v_product_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/products/"]')
                
                logger.info(f"   📦 상품 링크 {len(_v_product_links)}개 발견")
                
                # 중복 제거를 위한 set
                _v_seen_urls = set()
                
                for idx, link in enumerate(_v_product_links[:20], 1):  # 최대 20개
                    try:
                        _v_url = link.get_attribute('href')
                        if not _v_url or _v_url in _v_seen_urls:
                            continue
                        
                        _v_seen_urls.add(_v_url)
                        
                        # 상품명 찾기
                        _v_name = link.text.strip()
                        if not _v_name or len(_v_name) < 3:
                            # 부모 요소에서 텍스트 찾기
                            _v_parent = link.find_element(By.XPATH, '..')
                            _v_name = _v_parent.text.strip()
                        
                        if _v_name and len(_v_name) > 3:
                            _v_products.append({
                                'product_order': len(_v_products) + 1,
                                'product_name': _v_name[:200],
                                'product_url': _v_url,
                                'original_price': None,
                                'sale_price': None,
                                'discount_rate': None
                            })
                            
                            logger.info(f"      [{len(_v_products)}] {_v_name[:80]}")
                    
                    except Exception as e:
                        logger.debug(f"      상품 {idx} 파싱 실패: {e}")
                        continue
                
            except Exception as e:
                logger.warning(f"   ⚠️ Selenium으로 상품 찾기 실패: {e}")
            
            logger.info(f"   ✅ 상품 {len(_v_products)}개 수집")
            return _v_products
            
        except Exception as e:
            logger.error(f"   ❌ 상품 정보 수집 실패: {e}")
            return []
    
    def save_to_supabase(self, p_data: Dict) -> bool:
        """
        수집한 데이터를 Supabase에 저장
        
        Args:
            p_data: 수집된 데이터
        
        Returns:
            저장 성공 여부
        """
        if not self.supabase:
            logger.warning("⚠️ Supabase 클라이언트가 초기화되지 않았습니다.")
            return False
        
        try:
            logger.info(f"\n{'='*80}")
            logger.info("💾 Supabase에 데이터 저장 중...")
            logger.info(f"{'='*80}")
            
            # 1. live_broadcasts 테이블에 저장
            _v_live_data = {
                'live_id': p_data['event_id'],
                'channel_code': 'NAVER_SHOPPING',
                'platform_name': p_data['platform'],
                'brand_name': p_data['brand'],
                'live_title_customer': p_data['title'],
                'live_title_cs': p_data['title'],
                'source_url': p_data['url'],
                'broadcast_date': datetime.now().date().isoformat(),
                'status': 'ACTIVE',  # 기본값
                'collected_at': datetime.now().isoformat()
            }
            
            # 기존 데이터 확인
            _v_existing = self.supabase.table('live_broadcasts').select('*').eq('live_id', p_data['event_id']).execute()
            
            if _v_existing.data:
                # 업데이트
                self.supabase.table('live_broadcasts').update(_v_live_data).eq('live_id', p_data['event_id']).execute()
                logger.info(f"   ✅ live_broadcasts 업데이트: {p_data['event_id']}")
            else:
                # 삽입
                self.supabase.table('live_broadcasts').insert(_v_live_data).execute()
                logger.info(f"   ✅ live_broadcasts 저장: {p_data['event_id']}")
            
            # 2. 상품 정보 저장
            if p_data['products']:
                for product in p_data['products']:
                    _v_product_data = {
                        'live_id': p_data['event_id'],
                        'product_order': product.get('product_order', 0),
                        'product_name': product.get('product_name'),
                        'original_price': product.get('original_price'),
                        'sale_price': product.get('sale_price'),
                        'discount_rate': product.get('discount_rate'),
                        'product_url': product.get('product_url')
                    }
                    try:
                        self.supabase.table('live_products').insert(_v_product_data).execute()
                    except Exception as e:
                        logger.debug(f"   상품 저장 실패: {e}")
                
                logger.info(f"   ✅ 상품 {len(p_data['products'])}개 저장")
            
            # 3. 혜택/쿠폰 정보는 JSON으로 저장 (메타데이터)
            _v_metadata = {
                'benefits': p_data['benefits'],
                'coupons': p_data['coupons']
            }
            
            # live_broadcasts 테이블에 메타데이터 업데이트 (live_title_cs에 저장)
            _v_metadata_str = f"{p_data['title']} | 혜택: {len(p_data['benefits'])}개 | 쿠폰: {len(p_data['coupons'])}개"
            self.supabase.table('live_broadcasts').update({
                'live_title_cs': _v_metadata_str[:500]
            }).eq('live_id', p_data['event_id']).execute()
            
            logger.info(f"   ✅ 혜택/쿠폰 정보 저장")
            logger.info(f"\n{'='*80}")
            logger.info("✅ Supabase 저장 완료!")
            logger.info(f"{'='*80}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Supabase 저장 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def close(self):
        """리소스 정리"""
        if self.driver:
            self.driver.quit()
            logger.info("🔚 WebDriver 종료")


def main():
    """메인 실행 함수"""
    # 샘플 URL
    _v_url = "https://brand.naver.com/iope/shoppingstory/detail?id=5002337684"
    _v_brand = "아이오페"
    
    _v_crawler = NaverShoppingCrawler()
    
    try:
        # 크롤링 실행
        _v_data = _v_crawler.crawl(_v_url, _v_brand)
        
        if _v_data:
            # Supabase에 저장
            _v_crawler.save_to_supabase(_v_data)
            
            # JSON 파일로도 저장
            _v_filename = f"naver_shopping_{_v_data['event_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(_v_filename, 'w', encoding='utf-8') as f:
                json.dump(_v_data, f, ensure_ascii=False, indent=2)
            logger.info(f"\n📁 JSON 파일 저장: {_v_filename}")
    
    finally:
        _v_crawler.close()


if __name__ == "__main__":
    main()
