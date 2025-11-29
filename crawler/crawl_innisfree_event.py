"""
이니스프리 이벤트 크롤러 실행 스크립트
특정 이벤트 페이지를 크롤링하여 데이터베이스에 저장합니다.
"""

import sys
import time
import logging
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# 로컬 모듈 임포트
sys.path.append('.')
from config import CRAWLER_CONFIG
from database import (
    initialize_pool, 
    close_pool, 
    get_channel_by_code, 
    check_event_exists,
    insert_event,
    update_event,
    log_crawl_result
)
from parsers.innisfree_parser import parse_innisfree_event

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_v_logger = logging.getLogger(__name__)


def crawl_innisfree_event(p_event_url):
    """
    이니스프리 이벤트 페이지 크롤링
    
    Args:
        p_event_url (str): 크롤링할 이벤트 페이지 URL
        
    Returns:
        dict: 크롤링 통계
    """
    _v_start_time = datetime.now()
    _v_stats = {
        'started_at': _v_start_time,
        'items_found': 0,
        'items_new': 0,
        'items_updated': 0,
        'items_failed': 0,
    }
    
    try:
        _v_logger.info(f"=== 이니스프리 이벤트 크롤링 시작 ===")
        _v_logger.info(f"URL: {p_event_url}")
        
        # 1. 채널 정보 조회
        _v_channel = get_channel_by_code('INNISFREE_MALL')
        if not _v_channel:
            raise Exception("INNISFREE_MALL 채널을 찾을 수 없습니다.")
        
        _v_logger.info(f"채널: {_v_channel['channel_name']} (ID: {_v_channel['channel_id']})")
        
        # 2. HTML 다운로드
        _v_logger.info("HTML 다운로드 중...")
        _v_headers = {
            'User-Agent': CRAWLER_CONFIG['user_agent'],
            'Accept': 'text/html,application/xhtml+xml',
            'Accept-Language': 'ko-KR,ko;q=0.9',
        }
        
        _v_response = requests.get(
            p_event_url,
            headers=_v_headers,
            timeout=CRAWLER_CONFIG['timeout']
        )
        _v_response.raise_for_status()
        _v_html = _v_response.text
        
        _v_logger.info(f"HTML 다운로드 완료 ({len(_v_html)} bytes)")
        
        # 3. HTML 파싱
        _v_logger.info("이벤트 정보 파싱 중...")
        _v_event_data = parse_innisfree_event(_v_html, p_event_url)
        
        if not _v_event_data:
            raise Exception("이벤트 데이터 파싱 실패")
        
        _v_stats['items_found'] = 1
        
        _v_logger.info(f"파싱 완료:")
        _v_logger.info(f"  - 제목: {_v_event_data['title']}")
        _v_logger.info(f"  - 기간: {_v_event_data['start_date']} ~ {_v_event_data['end_date']}")
        _v_logger.info(f"  - 혜택: {_v_event_data['benefit_summary'][:100]}...")
        
        # 4. 데이터베이스 저장
        _v_event_data['channel_id'] = _v_channel['channel_id']
        
        # 중복 체크
        _v_existing = check_event_exists(
            _v_channel['channel_id'],
            _v_event_data['external_id']
        )
        
        if _v_existing:
            _v_logger.info(f"기존 이벤트 업데이트: {_v_existing['event_id']}")
            update_event(_v_existing['event_id'], _v_event_data)
            _v_stats['items_updated'] = 1
        else:
            _v_logger.info("새 이벤트 삽입")
            _v_event_id = insert_event(_v_event_data)
            _v_logger.info(f"이벤트 생성 완료: {_v_event_id}")
            _v_stats['items_new'] = 1
        
        # 5. 통계 업데이트
        _v_end_time = datetime.now()
        _v_duration = (_v_end_time - _v_start_time).total_seconds() * 1000
        
        _v_stats['completed_at'] = _v_end_time
        _v_stats['duration_ms'] = int(_v_duration)
        
        # 6. 크롤링 로그 기록
        log_crawl_result(
            _v_channel['channel_id'],
            'SUCCESS',
            _v_stats
        )
        
        _v_logger.info(f"=== 크롤링 완료 ===")
        _v_logger.info(f"신규: {_v_stats['items_new']}개")
        _v_logger.info(f"업데이트: {_v_stats['items_updated']}개")
        _v_logger.info(f"소요 시간: {_v_duration:.0f}ms")
        
        return _v_stats
        
    except Exception as p_error:
        _v_logger.error(f"크롤링 실패: {p_error}", exc_info=True)
        
        _v_stats['items_failed'] = 1
        _v_stats['completed_at'] = datetime.now()
        
        # 실패 로그 기록
        if _v_channel:
            log_crawl_result(
                _v_channel['channel_id'],
                'FAILED',
                _v_stats,
                str(p_error)
            )
        
        raise


def main():
    """메인 실행 함수"""
    # 크롤링할 이벤트 URL
    _v_event_url = "https://www.innisfree.com/kr/ko/ca/event/102214"
    
    try:
        # 데이터베이스 연결
        _v_logger.info("데이터베이스 연결 중...")
        initialize_pool()
        
        # 크롤링 실행
        _v_stats = crawl_innisfree_event(_v_event_url)
        
        print("\n" + "="*60)
        print("✅ 이니스프리 이벤트 크롤링 성공!")
        print("="*60)
        print(f"발견: {_v_stats['items_found']}개")
        print(f"신규: {_v_stats['items_new']}개")
        print(f"업데이트: {_v_stats['items_updated']}개")
        print(f"실패: {_v_stats['items_failed']}개")
        print("="*60)
        print("\n상담 시스템에서 이벤트를 조회할 수 있습니다!")
        print("프론트엔드: http://localhost:3001/search")
        print("검색어: 이니스프리, 레티놀, 비타민C 등")
        print("="*60)
        
    except Exception as p_error:
        print("\n" + "="*60)
        print("❌ 크롤링 실패")
        print("="*60)
        print(f"에러: {p_error}")
        print("="*60)
        sys.exit(1)
        
    finally:
        # 데이터베이스 연결 종료
        close_pool()


if __name__ == '__main__':
    main()


