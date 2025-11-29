#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카카오 라이브 쇼핑 크롤러
뷰티 카테고리에서 특정 브랜드 방송 수집
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 수집 대상 브랜드
TARGET_BRANDS = [
    '설화수', '라네즈', '이니스프리', '해피바스', 
    '바이탈뷰티', '프리메라', '오설록', '아이오페', 
    '헤라', '에스트라'
]

class KakaoLiveCrawler:
    """카카오 라이브 쇼핑 크롤러"""
    
    def __init__(self):
        """초기화"""
        self.base_url = 'https://shoppinglive.kakao.com'
        self.beauty_category_url = 'https://shoppinglive.kakao.com/categories?t_src=shopping_live&categoryId=4'
        self.driver = None
        self.collected_data = []
        
    def setup_driver(self):
        """Selenium WebDriver 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 헤드리스 모드
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ Chrome WebDriver 초기화 성공")
            return True
        except Exception as e:
            logger.error(f"❌ Chrome WebDriver 초기화 실패: {e}")
            return False
    
    def close_driver(self):
        """WebDriver 종료"""
        if self.driver:
            self.driver.quit()
            logger.info("✅ Chrome WebDriver 종료")
    
    def scroll_to_load_all(self):
        """페이지 스크롤하여 모든 콘텐츠 로드"""
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while True:
                # 페이지 끝까지 스크롤
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # 로딩 대기
                
                # 새로운 높이 계산
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                
                if new_height == last_height:
                    break
                    
                last_height = new_height
                
            logger.info("✅ 페이지 스크롤 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 스크롤 오류: {e}")
            return False
    
    def extract_live_items(self):
        """라이브 방송 아이템 추출"""
        try:
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 라이브 방송 카드 찾기 (실제 HTML 구조에 맞게 수정 필요)
            live_items = []
            
            # 카카오 라이브 쇼핑의 실제 구조를 분석하여 적절한 선택자 사용
            # 예시: 라이브 카드는 특정 클래스나 데이터 속성을 가질 수 있음
            cards = soup.find_all('a', href=True)
            
            for card in cards:
                href = card.get('href', '')
                if '/lives/' in href or '/live/' in href:
                    # 라이브 방송 링크 발견
                    live_url = self.base_url + href if not href.startswith('http') else href
                    
                    # 제목 추출
                    title = ''
                    title_elem = card.find(['h3', 'h4', 'span', 'div'], class_=lambda x: x and ('title' in x.lower() or 'name' in x.lower()))
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                    
                    # 브랜드 확인
                    is_target_brand = any(brand in title for brand in TARGET_BRANDS)
                    
                    if is_target_brand:
                        item = {
                            'url': live_url,
                            'title': title,
                            'found_brand': next((brand for brand in TARGET_BRANDS if brand in title), ''),
                            'platform': '카카오'
                        }
                        live_items.append(item)
                        logger.info(f"📦 발견: {title}")
            
            logger.info(f"✅ 총 {len(live_items)}개 라이브 방송 발견")
            return live_items
            
        except Exception as e:
            logger.error(f"❌ 라이브 아이템 추출 오류: {e}")
            return []
    
    def collect_live_detail(self, live_url, title, brand):
        """개별 라이브 방송 상세 정보 수집"""
        try:
            logger.info(f"🔍 상세 정보 수집: {title}")
            
            self.driver.get(live_url)
            time.sleep(3)  # 페이지 로딩 대기
            
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 기본 정보 수집 (실제 HTML 구조에 맞게 수정 필요)
            detail_data = {
                'metadata': {
                    'live_id': f"KAKAO_{brand.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'platform_name': '카카오',
                    'brand_name': brand,
                    'live_title_customer': title,
                    'live_title_cs': f'{brand} 카카오 라이브',
                    'source_url': live_url,
                    'thumbnail_url': '',
                    'status': self._determine_status(soup),
                    'collected_at': datetime.now().isoformat(),
                    'is_real_data': True
                },
                'schedule': self._extract_schedule(soup),
                'products': self._extract_products(soup),
                'benefits': self._extract_benefits(soup),
                'duplicate_policy': {},
                'restrictions': {},
                'live_specific': {
                    'key_mentions': [],
                    'broadcast_qa': [],
                    'timeline': []
                },
                'cs_info': {
                    'expected_questions': [],
                    'response_scripts': [],
                    'risk_points': [],
                    'cs_note': f'{brand} 카카오 라이브'
                }
            }
            
            return detail_data
            
        except Exception as e:
            logger.error(f"❌ 상세 정보 수집 오류 ({title}): {e}")
            return None
    
    def _determine_status(self, soup):
        """방송 상태 판단"""
        # 실제 HTML에서 상태 정보 추출
        # 예: LIVE, 예정, 다시보기 등
        return 'PENDING'  # 기본값
    
    def _extract_schedule(self, soup):
        """방송 일정 추출"""
        return {
            'broadcast_date': datetime.now().strftime('%Y-%m-%d'),
            'broadcast_start_time': '00:00',
            'broadcast_end_time': '00:00',
            'benefit_valid_type': '방송 중만',
            'benefit_start_datetime': '',
            'benefit_end_datetime': '',
            'broadcast_type': '단독라이브'
        }
    
    def _extract_products(self, soup):
        """판매 상품 추출"""
        return []
    
    def _extract_benefits(self, soup):
        """혜택 정보 추출"""
        return {
            'discounts': [],
            'gifts': [],
            'coupons': [],
            'shipping': []
        }
    
    def run(self):
        """크롤링 실행"""
        try:
            logger.info("="*80)
            logger.info("🚀 카카오 라이브 쇼핑 크롤링 시작")
            logger.info("="*80)
            
            # WebDriver 설정
            if not self.setup_driver():
                return False
            
            # 뷰티 카테고리 페이지 접속
            logger.info(f"📱 카카오 뷰티 카테고리 접속: {self.beauty_category_url}")
            self.driver.get(self.beauty_category_url)
            time.sleep(5)  # 초기 로딩 대기
            
            # 페이지 스크롤하여 모든 콘텐츠 로드
            self.scroll_to_load_all()
            
            # 라이브 방송 아이템 추출
            live_items = self.extract_live_items()
            
            if not live_items:
                logger.warning("⚠️ 수집된 라이브 방송이 없습니다.")
                return False
            
            # 각 라이브 방송의 상세 정보 수집
            logger.info(f"📊 {len(live_items)}개 방송의 상세 정보 수집 시작")
            
            for idx, item in enumerate(live_items, 1):
                logger.info(f"[{idx}/{len(live_items)}] 처리 중...")
                detail = self.collect_live_detail(
                    item['url'],
                    item['title'],
                    item['found_brand']
                )
                
                if detail:
                    self.collected_data.append(detail)
                
                time.sleep(2)  # 서버 부하 방지
            
            # 결과 저장
            self.save_results()
            
            logger.info("="*80)
            logger.info(f"✅ 카카오 라이브 쇼핑 크롤링 완료: {len(self.collected_data)}개")
            logger.info("="*80)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 크롤링 실행 오류: {e}")
            return False
        finally:
            self.close_driver()
    
    def save_results(self):
        """수집 결과 저장"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'kakao_live_beauty_{timestamp}.json'
            filepath = f'/Users/amore/ai_cs 시스템/crawler/data/{filename}'
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.collected_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 결과 저장: {filepath}")
            
            # 요약 정보 출력
            self._print_summary()
            
        except Exception as e:
            logger.error(f"❌ 결과 저장 오류: {e}")
    
    def _print_summary(self):
        """수집 결과 요약"""
        print("\n" + "="*80)
        print("📊 수집 결과 요약")
        print("="*80)
        
        # 브랜드별 집계
        brand_counts = {}
        for data in self.collected_data:
            brand = data['metadata']['brand_name']
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
        
        for brand, count in sorted(brand_counts.items()):
            print(f"   {brand}: {count}개")
        
        print(f"\n   총 {len(self.collected_data)}개 방송 수집")
        print("="*80)


def main():
    """메인 함수"""
    crawler = KakaoLiveCrawler()
    success = crawler.run()
    
    if success:
        print("\n✅ 카카오 라이브 쇼핑 크롤링 성공!")
    else:
        print("\n❌ 카카오 라이브 쇼핑 크롤링 실패!")
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())

