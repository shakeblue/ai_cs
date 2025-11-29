"""
네이버 쇼핑라이브 크롤러 실행 스크립트
라이브 방송 정보를 크롤링하여 데이터베이스에 저장합니다.
"""

import sys
import logging
from datetime import datetime

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
from parsers.naver_shopping_live_parser import parse_naver_shopping_live

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
_v_logger = logging.getLogger(__name__)


def crawl_naver_shopping_live(p_broadcast_url):
    """
    네이버 쇼핑라이브 방송 크롤링
    
    Args:
        p_broadcast_url (str): 크롤링할 방송 URL
        
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
    
    _v_channel = None
    
    try:
        _v_logger.info(f"=== 네이버 쇼핑라이브 크롤링 시작 ===")
        _v_logger.info(f"URL: {p_broadcast_url}")
        
        # 1. 채널 정보 조회
        _v_logger.info("채널 정보 조회 중...")
        _v_channel = get_channel_by_code('NAVER_SHOPPING_LIVE')
        if not _v_channel:
            raise Exception("NAVER_SHOPPING_LIVE 채널을 찾을 수 없습니다.")
        
        _v_logger.info(f"채널: {_v_channel['channel_name']} (ID: {_v_channel['channel_id']})")
        
        # 2. 라이브 방송 파싱
        _v_logger.info("라이브 방송 정보 파싱 중...")
        _v_logger.info("⚠️ Selenium으로 페이지 로드 중... 약 10-15초 소요됩니다.")
        
        _v_event_data = parse_naver_shopping_live(p_broadcast_url)
        
        if not _v_event_data:
            raise Exception("방송 데이터 파싱 실패")
        
        _v_stats['items_found'] = 1
        
        _v_logger.info(f"파싱 완료:")
        _v_logger.info(f"  - 제목: {_v_event_data['title']}")
        _v_logger.info(f"  - 방송일자: {_v_event_data['start_date']}")
        _v_logger.info(f"  - 혜택: {_v_event_data['benefit_summary'][:100]}...")
        
        # 3. 데이터베이스 저장
        _v_event_data['channel_id'] = _v_channel['channel_id']
        
        # 중복 체크
        _v_existing = check_event_exists(
            _v_channel['channel_id'],
            _v_event_data['external_id']
        )
        
        if _v_existing:
            _v_logger.info(f"기존 방송 업데이트: {_v_existing['event_id']}")
            update_event(_v_existing['event_id'], _v_event_data)
            _v_stats['items_updated'] = 1
        else:
            _v_logger.info("새 방송 정보 삽입")
            _v_event_id = insert_event(_v_event_data)
            _v_logger.info(f"방송 정보 저장 완료: {_v_event_id}")
            _v_stats['items_new'] = 1
        
        # 4. 통계 업데이트
        _v_end_time = datetime.now()
        _v_duration = (_v_end_time - _v_start_time).total_seconds() * 1000
        
        _v_stats['completed_at'] = _v_end_time
        _v_stats['duration_ms'] = int(_v_duration)
        
        # 5. 크롤링 로그 기록
        log_crawl_result(
            _v_channel['channel_id'],
            'SUCCESS',
            _v_stats
        )
        
        _v_logger.info(f"=== 크롤링 완료 ===")
        _v_logger.info(f"신규: {_v_stats['items_new']}개")
        _v_logger.info(f"업데이트: {_v_stats['items_updated']}개")
        _v_logger.info(f"소요 시간: {_v_duration/1000:.1f}초")
        
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
    # 크롤링할 방송 URL
    _v_broadcast_url = "https://view.shoppinglive.naver.com/replays/1764981?fm=shoppinglive&sn=home"
    
    print("\n" + "="*70)
    print("🎬 네이버 쇼핑라이브 크롤러")
    print("="*70)
    print(f"방송 URL: {_v_broadcast_url}")
    print("="*70 + "\n")
    
    try:
        # 데이터베이스 연결
        _v_logger.info("데이터베이스 연결 중...")
        initialize_pool()
        
        # 크롤링 실행
        _v_stats = crawl_naver_shopping_live(_v_broadcast_url)
        
        print("\n" + "="*70)
        print("✅ 네이버 쇼핑라이브 크롤링 성공!")
        print("="*70)
        print(f"📊 크롤링 결과:")
        print(f"   - 발견: {_v_stats['items_found']}개")
        print(f"   - 신규: {_v_stats['items_new']}개")
        print(f"   - 업데이트: {_v_stats['items_updated']}개")
        print(f"   - 실패: {_v_stats['items_failed']}개")
        print(f"   - 소요 시간: {_v_stats['duration_ms']/1000:.1f}초")
        print("="*70)
        print("\n✨ 상담 시스템에서 방송 정보를 조회할 수 있습니다!")
        print("   프론트엔드: http://localhost:3001/search")
        print("   검색어: 네이버, 라이브, 쇼핑라이브")
        print("="*70 + "\n")
        
    except Exception as p_error:
        print("\n" + "="*70)
        print("❌ 크롤링 실패")
        print("="*70)
        print(f"에러: {p_error}")
        print("\n💡 해결 방법:")
        print("   1. ChromeDriver가 설치되어 있는지 확인")
        print("   2. 데이터베이스가 실행 중인지 확인")
        print("   3. 네트워크 연결 확인")
        print("="*70 + "\n")
        sys.exit(1)
        
    finally:
        # 데이터베이스 연결 종료
        close_pool()


if __name__ == '__main__':
    main()


