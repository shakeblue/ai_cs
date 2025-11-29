"""
네이버 쇼핑라이브 멀티 브랜드 크롤러
여러 브랜드의 라이브 방송을 한 번에 수집합니다.
"""

import sys
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import urllib.parse

# 로컬 모듈 임포트
sys.path.append('.')
from parsers.naver_live_detail_parser import NaverLiveDetailParser

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_v_logger = logging.getLogger(__name__)


class NaverShoppingLiveMultiBrandCrawler:
    """네이버 쇼핑라이브 멀티 브랜드 크롤러"""
    
    # 수집할 브랜드 목록
    BRANDS = [
        '라네즈',
        '설화수',
        '아이오페',
        '헤라',
        '에스트라',
        '이니스프리',
        '해피바스',
        '바이탈뷰티',
        '프리메라',
        '오설록',
    ]
    
    def __init__(self):
        """크롤러 초기화"""
        self._v_driver = None
        self._v_parser = NaverLiveDetailParser()
    
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
    
    def search_brand_lives(self, p_brand_name):
        """
        특정 브랜드의 라이브 방송 목록 검색
        
        Args:
            p_brand_name (str): 브랜드명
            
        Returns:
            list: 라이브 방송 URL 목록
        """
        try:
            # URL 인코딩
            _v_encoded_brand = urllib.parse.quote(p_brand_name)
            _v_search_url = f"https://shoppinglive.naver.com/search/lives?query={_v_encoded_brand}"
            
            _v_logger.info(f"🔍 {p_brand_name} 브랜드 검색 중...")
            _v_logger.info(f"   URL: {_v_search_url}")
            
            # 페이지 로드
            self._v_driver.get(_v_search_url)
            time.sleep(3)
            
            # 스크롤하여 더 많은 결과 로드
            for i in range(3):
                self._v_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1.5)
            
            # HTML 파싱
            _v_html = self._v_driver.page_source
            _v_soup = BeautifulSoup(_v_html, 'lxml')
            
            # 라이브 방송 링크 추출
            _v_live_urls = []
            
            # 여러 선택자 시도
            _v_selectors = [
                'a[href*="/replays/"]',
                'a[href*="/lives/"]',
                '.live-item a',
                '[class*="live"] a[href]',
            ]
            
            for _v_selector in _v_selectors:
                _v_links = _v_soup.select(_v_selector)
                for _v_link in _v_links:
                    _v_href = _v_link.get('href')
                    if _v_href and ('/replays/' in _v_href or '/lives/' in _v_href):
                        # 상대 URL을 절대 URL로 변환
                        if _v_href.startswith('/'):
                            _v_href = f"https://view.shoppinglive.naver.com{_v_href}"
                        elif _v_href.startswith('http'):
                            pass
                        else:
                            continue
                        
                        if _v_href not in _v_live_urls:
                            _v_live_urls.append(_v_href)
            
            _v_logger.info(f"   ✅ {p_brand_name}: {len(_v_live_urls)}개 라이브 방송 발견")
            
            return _v_live_urls[:5]  # 최대 5개
            
        except Exception as p_error:
            _v_logger.error(f"   ❌ {p_brand_name} 검색 실패: {p_error}")
            return []
    
    def crawl_all_brands(self, p_max_per_brand=5):
        """
        모든 브랜드의 라이브 방송 수집
        
        Args:
            p_max_per_brand (int): 브랜드당 최대 수집 개수
            
        Returns:
            list: 수집된 라이브 방송 데이터 목록
        """
        _v_all_lives = []
        _v_stats = {
            'total_brands': len(self.BRANDS),
            'successful_brands': 0,
            'total_lives': 0,
            'by_brand': {}
        }
        
        try:
            # 드라이버 초기화
            self._init_driver()
            
            _v_logger.info(f"🎬 네이버 쇼핑라이브 멀티 브랜드 크롤링 시작")
            _v_logger.info(f"   대상 브랜드: {len(self.BRANDS)}개")
            _v_logger.info(f"   브랜드당 최대: {p_max_per_brand}개")
            
            # 각 브랜드별로 크롤링
            for idx, _v_brand in enumerate(self.BRANDS, 1):
                _v_logger.info(f"\n{'='*70}")
                _v_logger.info(f"[{idx}/{len(self.BRANDS)}] {_v_brand} 브랜드 처리 중...")
                _v_logger.info(f"{'='*70}")
                
                try:
                    # 1단계: 브랜드 검색하여 라이브 URL 목록 가져오기
                    _v_live_urls = self.search_brand_lives(_v_brand)
                    
                    if not _v_live_urls:
                        _v_logger.warning(f"   ⚠️ {_v_brand}: 라이브 방송을 찾을 수 없습니다")
                        _v_stats['by_brand'][_v_brand] = 0
                        continue
                    
                    # 2단계: 각 라이브 방송 상세 정보 수집
                    _v_brand_lives = []
                    for _v_url in _v_live_urls[:p_max_per_brand]:
                        try:
                            _v_logger.info(f"   📦 상세 정보 수집 중: {_v_url}")
                            
                            # 상세 파서로 모든 정보 수집
                            _v_live_data = self._v_parser.parse_live_broadcast_detail(_v_url)
                            
                            # 브랜드명 업데이트
                            _v_live_data['brand_name'] = _v_brand
                            
                            _v_brand_lives.append(_v_live_data)
                            _v_logger.info(f"   ✅ 수집 완료: {_v_live_data['live_title_customer']}")
                            
                            # 서버 부하 방지를 위한 대기
                            time.sleep(2)
                            
                        except Exception as p_error:
                            _v_logger.error(f"   ❌ 상세 수집 실패: {p_error}")
                            continue
                    
                    # 브랜드별 통계
                    _v_stats['by_brand'][_v_brand] = len(_v_brand_lives)
                    _v_stats['successful_brands'] += 1
                    _v_stats['total_lives'] += len(_v_brand_lives)
                    
                    # 전체 목록에 추가
                    _v_all_lives.extend(_v_brand_lives)
                    
                    _v_logger.info(f"   ✅ {_v_brand}: {len(_v_brand_lives)}개 수집 완료")
                    
                except Exception as p_error:
                    _v_logger.error(f"   ❌ {_v_brand} 처리 실패: {p_error}")
                    _v_stats['by_brand'][_v_brand] = 0
            
            # 최종 통계
            _v_logger.info(f"\n{'='*70}")
            _v_logger.info(f"🎉 크롤링 완료!")
            _v_logger.info(f"{'='*70}")
            _v_logger.info(f"전체 브랜드: {_v_stats['total_brands']}개")
            _v_logger.info(f"성공한 브랜드: {_v_stats['successful_brands']}개")
            _v_logger.info(f"총 수집 라이브: {_v_stats['total_lives']}개")
            _v_logger.info(f"\n브랜드별 수집 현황:")
            for _v_brand, _v_count in _v_stats['by_brand'].items():
                _v_logger.info(f"  - {_v_brand}: {_v_count}개")
            
            return _v_all_lives
            
        except Exception as p_error:
            _v_logger.error(f"❌ 멀티 브랜드 크롤링 실패: {p_error}", exc_info=True)
            raise
        finally:
            self._close_driver()
    
    def generate_mock_data(self, p_lives_data):
        """
        프론트엔드용 Mock 데이터 생성
        
        Args:
            p_lives_data (list): 수집된 라이브 방송 데이터
            
        Returns:
            str: JavaScript Mock 데이터 코드
        """
        import json
        
        _v_js_code = """/**
 * 네이버 쇼핑라이브 멀티 브랜드 Mock 데이터
 * 자동 생성됨 - 수동 편집 금지
 */

export const allBrandsLiveData = """
        
        # JSON으로 변환 (한글 유지)
        _v_js_code += json.dumps(p_lives_data, ensure_ascii=False, indent=2)
        
        _v_js_code += """;

/**
 * 브랜드별 라이브 방송 조회
 */
export const getLivesByBrand = (p_brand_name) => {
  return allBrandsLiveData.filter(_v_live => _v_live.brand_name === p_brand_name);
};

/**
 * 전체 브랜드 목록 조회
 */
export const getAllBrands = () => {
  const _v_brands = new Set();
  allBrandsLiveData.forEach(_v_live => _v_brands.add(_v_live.brand_name));
  return Array.from(_v_brands).sort();
};

/**
 * 키워드로 검색
 */
export const searchAllBrandsLives = (p_keyword = '') => {
  if (!p_keyword) {
    return allBrandsLiveData;
  }
  
  const _v_lower_keyword = p_keyword.toLowerCase();
  
  return allBrandsLiveData.filter(_v_live => {
    const _v_searchable = `
      ${_v_live.live_title_customer}
      ${_v_live.brand_name}
      ${_v_live.products.map(p => p.product_name).join(' ')}
    `.toLowerCase();
    
    return _v_searchable.includes(_v_lower_keyword);
  });
};
"""
        
        return _v_js_code


def main():
    """메인 실행 함수"""
    print("\n" + "="*70)
    print("🎬 네이버 쇼핑라이브 멀티 브랜드 크롤러")
    print("="*70)
    print("대상 브랜드:", ', '.join(NaverShoppingLiveMultiBrandCrawler.BRANDS))
    print("="*70 + "\n")
    
    _v_crawler = NaverShoppingLiveMultiBrandCrawler()
    
    try:
        # 모든 브랜드 크롤링 (브랜드당 최대 3개)
        _v_all_lives = _v_crawler.crawl_all_brands(p_max_per_brand=3)
        
        if _v_all_lives:
            # Mock 데이터 생성
            _v_mock_code = _v_crawler.generate_mock_data(_v_all_lives)
            
            # 파일 저장
            _v_output_path = '../frontend/src/mockData/allBrandsLiveData.js'
            with open(_v_output_path, 'w', encoding='utf-8') as f:
                f.write(_v_mock_code)
            
            print("\n" + "="*70)
            print("✅ Mock 데이터 생성 완료!")
            print("="*70)
            print(f"파일: {_v_output_path}")
            print(f"총 {len(_v_all_lives)}개 라이브 방송 데이터")
            print("="*70 + "\n")
        else:
            print("\n❌ 수집된 데이터가 없습니다.")
        
    except Exception as p_error:
        print("\n" + "="*70)
        print("❌ 크롤링 실패")
        print("="*70)
        print(f"에러: {p_error}")
        print("\n💡 해결 방법:")
        print("   1. ChromeDriver가 설치되어 있는지 확인")
        print("   2. 네트워크 연결 확인")
        print("   3. 네이버 쇼핑라이브 사이트 접근 가능 여부 확인")
        print("="*70 + "\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

