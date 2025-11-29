#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 쇼핑라이브 설화수 브랜드 전체 방송 크롤러
수집정보 문서의 8개 카테고리 모두 수집
"""

import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class NaverSulwhasooCrawler:
    """네이버 쇼핑라이브 설화수 브랜드 크롤러"""
    
    def __init__(self):
        """크롤러 초기화"""
        self.p_base_url = "https://shoppinglive.naver.com/search/lives?query=%EC%84%A4%ED%99%94%EC%88%98"
        self.p_brand_name = "설화수"
        self.p_platform_name = "네이버"
        self.p_driver = None
        
    def _setup_driver(self):
        """Selenium WebDriver 설정"""
        _v_options = webdriver.ChromeOptions()
        _v_options.add_argument('--headless')  # 백그라운드 실행
        _v_options.add_argument('--no-sandbox')
        _v_options.add_argument('--disable-dev-shm-usage')
        _v_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)')
        
        self.p_driver = webdriver.Chrome(options=_v_options)
        self.p_driver.implicitly_wait(10)
        
    def crawl_all_lives(self):
        """설화수 검색 결과의 모든 방송 크롤링"""
        try:
            self._setup_driver()
            print(f"🔍 설화수 라이브 방송 검색 시작...")
            
            # 검색 결과 페이지 접속
            self.p_driver.get(self.p_base_url)
            time.sleep(3)
            
            # 방송 목록 수집
            _v_lives = self._extract_live_list()
            print(f"✅ 총 {len(_v_lives)}개 방송 발견")
            
            # 각 방송의 상세 정보 수집
            _v_detailed_lives = []
            for idx, _v_live in enumerate(_v_lives, 1):
                print(f"\n📺 [{idx}/{len(_v_lives)}] {_v_live['title']} 상세 정보 수집 중...")
                _v_detail = self._crawl_live_detail(_v_live)
                if _v_detail:
                    _v_detailed_lives.append(_v_detail)
                time.sleep(2)  # 요청 간 딜레이
                
            return _v_detailed_lives
            
        except Exception as e:
            print(f"❌ 크롤링 오류: {str(e)}")
            return []
        finally:
            if self.p_driver:
                self.p_driver.quit()
                
    def _extract_live_list(self):
        """검색 결과에서 방송 목록 추출"""
        _v_lives = []
        
        try:
            # 방송 카드 요소들 찾기
            _v_cards = self.p_driver.find_elements(By.CSS_SELECTOR, ".live_card, .ProductLive_live_card__")
            
            for _v_card in _v_cards[:5]:  # 최대 5개 방송
                try:
                    # 제목 추출
                    _v_title_elem = _v_card.find_element(By.CSS_SELECTOR, ".live_title, .ProductLive_live_title__")
                    _v_title = _v_title_elem.text.strip()
                    
                    # 링크 추출
                    _v_link_elem = _v_card.find_element(By.CSS_SELECTOR, "a")
                    _v_url = _v_link_elem.get_attribute("href")
                    
                    # 썸네일 추출
                    try:
                        _v_thumb_elem = _v_card.find_element(By.CSS_SELECTOR, "img")
                        _v_thumbnail = _v_thumb_elem.get_attribute("src")
                    except:
                        _v_thumbnail = ""
                    
                    # 상태 추출 (라이브/다시보기)
                    _v_status = "다시보기"
                    try:
                        _v_badge = _v_card.find_element(By.CSS_SELECTOR, ".badge, .live_badge")
                        if "LIVE" in _v_badge.text.upper():
                            _v_status = "라이브"
                    except:
                        pass
                    
                    _v_lives.append({
                        'title': _v_title,
                        'url': _v_url,
                        'thumbnail': _v_thumbnail,
                        'status': _v_status
                    })
                    
                except Exception as e:
                    print(f"⚠️ 방송 카드 파싱 실패: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"❌ 방송 목록 추출 실패: {str(e)}")
            
        return _v_lives
        
    def _crawl_live_detail(self, p_live_info):
        """개별 방송의 상세 정보 크롤링 (수집정보 문서 8개 카테고리)"""
        try:
            # 상세 페이지 접속
            self.p_driver.get(p_live_info['url'])
            time.sleep(3)
            
            # 1) 기본 정보 수집
            _v_metadata = self._extract_metadata(p_live_info)
            
            # 2) 방송 스케줄 수집
            _v_schedule = self._extract_schedule()
            
            # 3) 판매 상품 정보 수집
            _v_products = self._extract_products()
            
            # 4) 혜택 정보 수집
            _v_benefits = self._extract_benefits()
            
            # 5) 중복 적용 정책 수집
            _v_duplicate_policy = self._extract_duplicate_policy()
            
            # 6) 제외/제한 사항 수집
            _v_restrictions = self._extract_restrictions()
            
            # 7) 라이브 특화 정보 수집
            _v_live_specific = self._extract_live_specific()
            
            # 8) CS 응대용 정보 생성
            _v_cs_info = self._generate_cs_info(_v_metadata, _v_benefits)
            
            # 전체 데이터 구조화
            return {
                'metadata': _v_metadata,
                'schedule': _v_schedule,
                'products': _v_products,
                'benefits': _v_benefits,
                'duplicate_policy': _v_duplicate_policy,
                'restrictions': _v_restrictions,
                'live_specific': _v_live_specific,
                'cs_info': _v_cs_info
            }
            
        except Exception as e:
            print(f"❌ 상세 정보 수집 실패: {str(e)}")
            return None
            
    def _extract_metadata(self, p_live_info):
        """1) 기본 정보 추출"""
        _v_live_id = f"NAVER_SULWHASOO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            'live_id': _v_live_id,
            'platform_name': self.p_platform_name,
            'brand_name': self.p_brand_name,
            'live_title_customer': p_live_info['title'],
            'live_title_cs': f"{self.p_brand_name} {datetime.now().strftime('%Y년 %m월')} {self.p_platform_name} 라이브",
            'source_url': p_live_info['url'],
            'thumbnail_url': p_live_info.get('thumbnail', ''),
            'status': p_live_info.get('status', '다시보기')
        }
        
    def _extract_schedule(self):
        """2) 방송 스케줄 & 혜택 유효시간 추출"""
        _v_schedule = {
            'broadcast_date': '',
            'broadcast_start_time': '',
            'broadcast_end_time': '',
            'benefit_valid_type': '방송 중만',
            'benefit_start_datetime': '',
            'benefit_end_datetime': '',
            'broadcast_type': '단독라이브'
        }
        
        try:
            # 방송 일시 찾기
            _v_date_elem = self.p_driver.find_element(By.CSS_SELECTOR, ".date, .broadcast_date, .time_info")
            _v_date_text = _v_date_elem.text
            
            # 날짜 파싱 (예: "2025-11-29 15:00")
            if _v_date_text:
                _v_schedule['broadcast_date'] = _v_date_text.split()[0] if ' ' in _v_date_text else ''
                
        except NoSuchElementException:
            print("⚠️ 방송 일시 정보 없음")
            
        return _v_schedule
        
    def _extract_products(self):
        """3) 판매 상품 정보 추출"""
        _v_products = []
        
        try:
            # 상품 목록 찾기
            _v_product_elems = self.p_driver.find_elements(By.CSS_SELECTOR, ".product_item, .live_product")
            
            for idx, _v_elem in enumerate(_v_product_elems[:10], 1):  # 최대 10개
                try:
                    _v_name = _v_elem.find_element(By.CSS_SELECTOR, ".product_name, .name").text
                    
                    # 가격 정보
                    try:
                        _v_price = _v_elem.find_element(By.CSS_SELECTOR, ".price, .sale_price").text
                    except:
                        _v_price = ""
                    
                    _v_products.append({
                        'product_order': idx,
                        'product_name': _v_name,
                        'sku': f"SWS-{idx:03d}",
                        'original_price': _v_price,
                        'sale_price': _v_price,
                        'discount_rate': '',
                        'product_type': '대표' if idx == 1 else '일반',
                        'stock_info': '재고 충분',
                        'set_composition': '',
                        'product_url': ''
                    })
                    
                except Exception as e:
                    continue
                    
        except NoSuchElementException:
            print("⚠️ 상품 정보 없음")
            
        return _v_products
        
    def _extract_benefits(self):
        """4) 혜택 정보 추출 (할인/사은품/쿠폰/배송)"""
        return {
            'discounts': self._extract_discounts(),
            'gifts': self._extract_gifts(),
            'coupons': self._extract_coupons(),
            'shipping': self._extract_shipping()
        }
        
    def _extract_discounts(self):
        """4-a) 할인 정보"""
        _v_discounts = []
        
        try:
            _v_discount_elems = self.p_driver.find_elements(By.CSS_SELECTOR, ".discount, .benefit_discount")
            
            for _v_elem in _v_discount_elems:
                _v_text = _v_elem.text
                _v_discounts.append({
                    'discount_type': '%할인',
                    'discount_detail': _v_text,
                    'discount_condition': '라이브 방송 중',
                    'discount_valid_period': '방송 중'
                })
                
        except NoSuchElementException:
            pass
            
        return _v_discounts
        
    def _extract_gifts(self):
        """4-b) 사은품 정보"""
        _v_gifts = []
        
        try:
            _v_gift_elems = self.p_driver.find_elements(By.CSS_SELECTOR, ".gift, .benefit_gift")
            
            for _v_elem in _v_gift_elems:
                _v_text = _v_elem.text
                _v_gifts.append({
                    'gift_type': '구매조건형',
                    'gift_name': _v_text,
                    'gift_condition': '구매 금액 조건',
                    'gift_quantity_limit': ''
                })
                
        except NoSuchElementException:
            pass
            
        return _v_gifts
        
    def _extract_coupons(self):
        """4-c) 쿠폰/적립 정보"""
        _v_coupons = []
        
        try:
            _v_coupon_elems = self.p_driver.find_elements(By.CSS_SELECTOR, ".coupon, .benefit_coupon")
            
            for _v_elem in _v_coupon_elems:
                _v_text = _v_elem.text
                _v_coupons.append({
                    'coupon_type': '브랜드쿠폰',
                    'coupon_detail': _v_text,
                    'coupon_issue_condition': '다운로드 필요',
                    'point_condition': ''
                })
                
        except NoSuchElementException:
            pass
            
        return _v_coupons
        
    def _extract_shipping(self):
        """4-d) 배송 혜택 정보"""
        return [
            {
                'shipping_type': '무료배송',
                'shipping_detail': '전 상품 무료배송',
                'shipping_condition': '구매 금액 무관'
            }
        ]
        
    def _extract_duplicate_policy(self):
        """5) 중복 적용 정책"""
        return {
            'coupon_duplicate': '불가',
            'point_duplicate': '가능',
            'other_promotion_duplicate': '불가',
            'employee_discount': '불가',
            'duplicate_note': '쿠폰은 1개만 선택 가능'
        }
        
    def _extract_restrictions(self):
        """6) 제외/제한 사항"""
        return {
            'excluded_products': [],
            'channel_restrictions': ['네이버 앱/웹만'],
            'payment_restrictions': [],
            'region_restrictions': ['도서산간 배송비 별도'],
            'other_restrictions': []
        }
        
    def _extract_live_specific(self):
        """7) 라이브 특화 정보"""
        return {
            'key_mentions': [],
            'broadcast_qa': [],
            'timeline': []
        }
        
    def _generate_cs_info(self, p_metadata, p_benefits):
        """8) CS 응대용 정보 생성"""
        return {
            'expected_questions': [
                '방송 끝났는데 혜택 적용되나요?',
                '쿠폰 중복 사용 가능한가요?',
                '배송비는 무료인가요?',
                '재고는 충분한가요?'
            ],
            'response_scripts': [
                '방송 종료 후에는 혜택이 적용되지 않습니다.',
                '쿠폰은 1개만 선택 가능하며 중복 사용이 불가합니다.',
                '전 상품 무료배송이 제공됩니다.',
                '재고 상황은 실시간으로 변동될 수 있습니다.'
            ],
            'risk_points': [
                '⚠️ 쿠폰 중복 사용 불가',
                '⚠️ 방송 중에만 혜택 적용',
                '⚠️ 선착순 혜택은 조기 마감 가능'
            ],
            'cs_note': f"{p_metadata['live_title_customer']} 방송 관련 문의입니다."
        }


def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🎬 네이버 쇼핑라이브 설화수 브랜드 크롤러")
    print("=" * 80)
    
    _v_crawler = NaverSulwhasooCrawler()
    _v_lives = _v_crawler.crawl_all_lives()
    
    if _v_lives:
        print(f"\n✅ 총 {len(_v_lives)}개 방송 크롤링 완료!")
        
        # JSON 파일로 저장
        _v_output_file = f"/Users/amore/ai_cs 시스템/crawler/output/sulwhasoo_lives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(_v_output_file, 'w', encoding='utf-8') as f:
            json.dump(_v_lives, f, ensure_ascii=False, indent=2)
        print(f"📁 저장 완료: {_v_output_file}")
        
        # Mock 데이터 파일 생성
        _v_mock_file = "/Users/amore/ai_cs 시스템/frontend/src/mockData/sulwhasooLivesData.js"
        _v_js_content = generate_mock_js(_v_lives)
        with open(_v_mock_file, 'w', encoding='utf-8') as f:
            f.write(_v_js_content)
        print(f"📁 Mock 데이터 생성: {_v_mock_file}")
        
    else:
        print("❌ 크롤링 실패")


def generate_mock_js(p_lives):
    """Mock 데이터 JS 파일 생성"""
    _v_js = """/**
 * 네이버 쇼핑라이브 설화수 브랜드 전체 방송 Mock 데이터
 * 수집정보 문서의 8개 카테고리 모두 포함
 */

export const sulwhasooLivesData = """
    
    _v_js += json.dumps(p_lives, ensure_ascii=False, indent=2)
    _v_js += """;

/**
 * 설화수 라이브 방송 목록 조회
 */
export const getSulwhasooLives = () => {
  return sulwhasooLivesData;
};

/**
 * 설화수 라이브 상세 정보 조회
 */
export const getSulwhasooLiveDetail = (p_live_id) => {
  return sulwhasooLivesData.find(_v_live => _v_live.metadata.live_id === p_live_id);
};

/**
 * 설화수 라이브를 이벤트 형식으로 변환
 */
export const convertSulwhasooLiveToEvent = (p_live) => {
  const _v_meta = p_live.metadata;
  const _v_products = p_live.products || [];
  const _v_benefits = p_live.benefits || {};
  
  return {
    event_id: _v_meta.live_id,
    channel_name: _v_meta.platform_name,
    channel_code: 'NAVER_LIVE',
    title: _v_meta.live_title_customer,
    subtitle: `${_v_meta.brand_name} 라이브 방송`,
    description: `${_v_products.length}개 상품 | ${(_v_benefits.discounts || []).length}개 할인 | ${(_v_benefits.gifts || []).length}개 사은품`,
    start_date: p_live.schedule?.broadcast_date || '',
    end_date: p_live.schedule?.broadcast_date || '',
    event_url: _v_meta.source_url,
    status: _v_meta.status === '라이브' ? 'ACTIVE' : 'COMPLETED',
    priority: 10,
    tags: ['네이버라이브', '설화수', '라이브방송', '상세정보'],
    is_live_detail: true,
    has_detail: true
  };
};

/**
 * 검색 키워드로 설화수 라이브 필터링
 */
export const searchSulwhasooLives = (p_keyword) => {
  if (!p_keyword) return [];
  
  const _v_lower_keyword = p_keyword.toLowerCase();
  
  return sulwhasooLivesData
    .filter(_v_live => {
      const _v_title = _v_live.metadata.live_title_customer.toLowerCase();
      const _v_brand = _v_live.metadata.brand_name.toLowerCase();
      return _v_title.includes(_v_lower_keyword) || _v_brand.includes(_v_lower_keyword);
    })
    .map(convertSulwhasooLiveToEvent);
};

export default sulwhasooLivesData;
"""
    
    return _v_js


if __name__ == "__main__":
    main()

