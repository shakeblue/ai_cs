"""
기본 크롤러 클래스
모든 채널별 크롤러의 부모 클래스
"""

import time
import logging
import re
from datetime import datetime
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from config import CRAWLER_CONFIG
from database import get_channel_by_code, check_event_exists, insert_event, update_event

# 로거 설정
_v_logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """
    기본 크롤러 추상 클래스
    
    모든 채널별 크롤러는 이 클래스를 상속받아 구현
    """
    
    def __init__(self, p_channel_code):
        """
        크롤러 초기화
        
        Args:
            p_channel_code (str): 채널 코드
        """
        self._v_channel_code = p_channel_code
        self._v_channel_info = None
        self._v_session = None
        self._v_driver = None
        self._v_stats = {
            'items_found': 0,
            'items_new': 0,
            'items_updated': 0,
            'items_failed': 0,
        }
        
        # 채널 정보 로드
        self._load_channel_info()
        
    def _load_channel_info(self):
        """데이터베이스에서 채널 정보 로드"""
        self._v_channel_info = get_channel_by_code(self._v_channel_code)
        
        if not self._v_channel_info:
            raise ValueError(f"채널을 찾을 수 없습니다: {self._v_channel_code}")
        
        _v_logger.info(f"채널 정보 로드 완료: {self._v_channel_info['channel_name']}")
    
    def _init_session(self):
        """HTTP 세션 초기화"""
        if self._v_session is None:
            self._v_session = requests.Session()
            self._v_session.headers.update({
                'User-Agent': CRAWLER_CONFIG['user_agent'],
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            })
            _v_logger.debug("HTTP 세션 초기화 완료")
    
    def _init_selenium(self):
        """Selenium WebDriver 초기화"""
        if self._v_driver is None:
            _v_chrome_options = Options()
            
            if CRAWLER_CONFIG['selenium_headless']:
                _v_chrome_options.add_argument('--headless')
            
            _v_chrome_options.add_argument('--no-sandbox')
            _v_chrome_options.add_argument('--disable-dev-shm-usage')
            _v_chrome_options.add_argument('--disable-gpu')
            _v_chrome_options.add_argument(f"user-agent={CRAWLER_CONFIG['user_agent']}")
            
            try:
                _v_service = Service(ChromeDriverManager().install())
                self._v_driver = webdriver.Chrome(service=_v_service, options=_v_chrome_options)
                self._v_driver.implicitly_wait(CRAWLER_CONFIG['selenium_implicit_wait'])
                _v_logger.debug("Selenium WebDriver 초기화 완료")
            except Exception as p_error:
                _v_logger.error(f"Selenium 초기화 실패: {p_error}")
                raise
    
    def fetch_html(self, p_url, p_use_selenium=False):
        """
        URL에서 HTML 콘텐츠 가져오기
        
        Args:
            p_url (str): 크롤링할 URL
            p_use_selenium (bool): Selenium 사용 여부
            
        Returns:
            str: HTML 콘텐츠
        """
        try:
            if p_use_selenium:
                # Selenium으로 동적 페이지 크롤링
                self._init_selenium()
                self._v_driver.get(p_url)
                time.sleep(CRAWLER_CONFIG['request_delay'])
                _v_html = self._v_driver.page_source
                _v_logger.debug(f"Selenium으로 페이지 로드 완료: {p_url}")
            else:
                # Requests로 정적 페이지 크롤링
                self._init_session()
                _v_response = self._v_session.get(
                    p_url,
                    timeout=CRAWLER_CONFIG['timeout']
                )
                _v_response.raise_for_status()
                _v_html = _v_response.text
                _v_logger.debug(f"Requests로 페이지 로드 완료: {p_url}")
                
                # 요청 간 딜레이
                time.sleep(CRAWLER_CONFIG['request_delay'])
            
            return _v_html
            
        except Exception as p_error:
            _v_logger.error(f"HTML 가져오기 실패: {p_url} - {p_error}")
            raise
    
    def parse_html(self, p_html):
        """
        HTML 파싱
        
        Args:
            p_html (str): HTML 콘텐츠
            
        Returns:
            BeautifulSoup: 파싱된 HTML 객체
        """
        return BeautifulSoup(p_html, 'lxml')
    
    def extract_discount_rate(self, p_text):
        """
        텍스트에서 할인율 추출
        
        Args:
            p_text (str): 텍스트
            
        Returns:
            float: 할인율 (%) 또는 None
        """
        if not p_text:
            return None
        
        _v_match = re.search(r'(\d+)%', p_text)
        if _v_match:
            return float(_v_match.group(1))
        
        return None
    
    def normalize_text(self, p_text):
        """
        텍스트 정규화 (공백 제거, 줄바꿈 처리)
        
        Args:
            p_text (str): 원본 텍스트
            
        Returns:
            str: 정규화된 텍스트
        """
        if not p_text:
            return None
        
        # 연속된 공백 제거
        _v_text = re.sub(r'\s+', ' ', p_text)
        
        # 앞뒤 공백 제거
        _v_text = _v_text.strip()
        
        return _v_text if _v_text else None
    
    def save_event(self, p_event_data):
        """
        이벤트 데이터 저장 (신규 또는 업데이트)
        
        Args:
            p_event_data (dict): 이벤트 데이터
            
        Returns:
            str: 'new', 'updated', 'failed' 중 하나
        """
        try:
            # 필수 필드 검증
            if not all(k in p_event_data for k in ['title', 'start_date', 'end_date', 'event_url']):
                _v_logger.warning(f"필수 필드 누락: {p_event_data.get('title', 'Unknown')}")
                return 'failed'
            
            # 채널 ID 추가
            p_event_data['channel_id'] = self._v_channel_info['channel_id']
            
            # 기본값 설정
            p_event_data.setdefault('subtitle', None)
            p_event_data.setdefault('description', None)
            p_event_data.setdefault('discount_rate', None)
            p_event_data.setdefault('discount_amount', None)
            p_event_data.setdefault('benefit_summary', None)
            p_event_data.setdefault('benefit_detail', None)
            p_event_data.setdefault('target_products', None)
            p_event_data.setdefault('target_brands', None)
            p_event_data.setdefault('conditions', None)
            p_event_data.setdefault('cautions', None)
            p_event_data.setdefault('image_url', None)
            p_event_data.setdefault('thumbnail_url', None)
            p_event_data.setdefault('priority', 0)
            p_event_data.setdefault('tags', None)
            
            # 중복 확인
            _v_external_id = p_event_data.get('external_id')
            if _v_external_id:
                _v_existing = check_event_exists(
                    self._v_channel_info['channel_id'],
                    _v_external_id
                )
                
                if _v_existing:
                    # 업데이트
                    update_event(_v_existing['event_id'], p_event_data)
                    return 'updated'
            
            # 신규 삽입
            insert_event(p_event_data)
            return 'new'
            
        except Exception as p_error:
            _v_logger.error(f"이벤트 저장 실패: {p_error}")
            return 'failed'
    
    @abstractmethod
    def extract_events(self, p_html):
        """
        HTML에서 이벤트 데이터 추출 (하위 클래스에서 구현)
        
        Args:
            p_html (str): HTML 콘텐츠
            
        Returns:
            list: 이벤트 데이터 딕셔너리 리스트
        """
        pass
    
    def run(self, p_url):
        """
        크롤링 실행
        
        Args:
            p_url (str): 크롤링할 URL
            
        Returns:
            dict: 크롤링 통계
        """
        _v_start_time = datetime.now()
        _v_logger.info(f"=== 크롤링 시작: {self._v_channel_info['channel_name']} ===")
        
        try:
            # HTML 가져오기
            _v_html = self.fetch_html(p_url)
            
            # 이벤트 추출
            _v_events = self.extract_events(_v_html)
            
            self._v_stats['items_found'] = len(_v_events)
            _v_logger.info(f"발견된 이벤트: {len(_v_events)}개")
            
            # 이벤트 저장
            for _v_event in _v_events:
                _v_result = self.save_event(_v_event)
                
                if _v_result == 'new':
                    self._v_stats['items_new'] += 1
                elif _v_result == 'updated':
                    self._v_stats['items_updated'] += 1
                elif _v_result == 'failed':
                    self._v_stats['items_failed'] += 1
            
            _v_end_time = datetime.now()
            _v_duration = (_v_end_time - _v_start_time).total_seconds() * 1000
            
            self._v_stats['duration_ms'] = int(_v_duration)
            self._v_stats['started_at'] = _v_start_time
            self._v_stats['completed_at'] = _v_end_time
            
            _v_logger.info(f"=== 크롤링 완료 ===")
            _v_logger.info(f"신규: {self._v_stats['items_new']}개")
            _v_logger.info(f"업데이트: {self._v_stats['items_updated']}개")
            _v_logger.info(f"실패: {self._v_stats['items_failed']}개")
            _v_logger.info(f"소요 시간: {_v_duration:.0f}ms")
            
            return self._v_stats
            
        except Exception as p_error:
            _v_logger.error(f"크롤링 실패: {p_error}")
            raise
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """리소스 정리"""
        if self._v_session:
            self._v_session.close()
            self._v_session = None
        
        if self._v_driver:
            self._v_driver.quit()
            self._v_driver = None
        
        _v_logger.debug("리소스 정리 완료")


