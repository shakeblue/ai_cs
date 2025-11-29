"""
크롤러 메인 실행 파일
스케줄러를 통해 주기적으로 크롤링 실행
"""

import sys
import time
import logging
import colorlog
from datetime import datetime
import schedule

from config import CHANNEL_CONFIGS, SCHEDULER_CONFIG, LOG_CONFIG
from database import initialize_pool, close_pool, log_crawl_result, get_channel_by_code

# 로깅 설정
_v_handler = colorlog.StreamHandler()
_v_handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

_v_logger = logging.getLogger()
_v_logger.setLevel(getattr(logging, LOG_CONFIG['log_level']))
_v_logger.addHandler(_v_handler)


def run_crawler_for_channel(p_channel_code, p_url):
    """
    특정 채널의 크롤러 실행
    
    Args:
        p_channel_code (str): 채널 코드
        p_url (str): 크롤링 대상 URL
    """
    _v_logger.info(f"\n{'='*60}")
    _v_logger.info(f"채널 크롤링 시작: {p_channel_code}")
    _v_logger.info(f"URL: {p_url}")
    _v_logger.info(f"{'='*60}\n")
    
    try:
        # 채널 정보 조회
        _v_channel_info = get_channel_by_code(p_channel_code)
        
        if not _v_channel_info:
            _v_logger.error(f"채널을 찾을 수 없습니다: {p_channel_code}")
            return
        
        # 크롤러 동적 임포트 및 실행
        # 실제 환경에서는 각 채널별 크롤러 구현 필요
        # 예시: from crawlers.amore_mall_crawler import AmoreMallCrawler
        
        _v_logger.info(f"[{p_channel_code}] 크롤링 시작...")
        
        # 임시 더미 통계 (실제 구현 시 크롤러 실행 결과)
        _v_stats = {
            'started_at': datetime.now(),
            'completed_at': datetime.now(),
            'duration_ms': 1000,
            'items_found': 0,
            'items_new': 0,
            'items_updated': 0,
            'items_failed': 0,
        }
        
        # 로그 기록
        log_crawl_result(
            _v_channel_info['channel_id'],
            'SUCCESS',
            _v_stats
        )
        
        _v_logger.info(f"[{p_channel_code}] 크롤링 완료 ✓")
        
    except Exception as p_error:
        _v_logger.error(f"[{p_channel_code}] 크롤링 실패: {p_error}", exc_info=True)
        
        # 실패 로그 기록
        try:
            _v_channel_info = get_channel_by_code(p_channel_code)
            if _v_channel_info:
                log_crawl_result(
                    _v_channel_info['channel_id'],
                    'FAILED',
                    {'started_at': datetime.now(), 'completed_at': datetime.now()},
                    str(p_error)
                )
        except:
            pass


def schedule_crawlers():
    """모든 활성화된 채널의 크롤러 스케줄 등록"""
    _v_logger.info("크롤러 스케줄 등록 시작...")
    
    for _v_channel_code, _v_config in CHANNEL_CONFIGS.items():
        if not _v_config.get('enabled', True):
            _v_logger.info(f"[{_v_channel_code}] 비활성화됨 - 스킵")
            continue
        
        _v_interval = _v_config['interval_minutes']
        _v_url = _v_config['url']
        
        # 스케줄 등록
        schedule.every(_v_interval).minutes.do(
            run_crawler_for_channel,
            p_channel_code=_v_channel_code,
            p_url=_v_url
        )
        
        _v_logger.info(f"[{_v_channel_code}] 스케줄 등록 완료 (주기: {_v_interval}분)")
        
        # 초기 실행 (즉시 크롤링 시작)
        schedule.run_all(delay_seconds=1)


def main():
    """메인 실행 함수"""
    try:
        _v_logger.info("\n" + "="*60)
        _v_logger.info("화장품 상담 시스템 크롤러 시작")
        _v_logger.info("="*60 + "\n")
        
        # 데이터베이스 연결 풀 초기화
        _v_logger.info("데이터베이스 연결 풀 초기화 중...")
        initialize_pool()
        _v_logger.info("✓ 데이터베이스 연결 완료\n")
        
        # 크롤러 스케줄 등록
        schedule_crawlers()
        
        _v_logger.info("\n" + "="*60)
        _v_logger.info("크롤러가 백그라운드에서 실행 중입니다.")
        _v_logger.info("종료하려면 Ctrl+C를 누르세요.")
        _v_logger.info("="*60 + "\n")
        
        # 스케줄러 실행 루프
        while True:
            schedule.run_pending()
            time.sleep(SCHEDULER_CONFIG['check_interval'])
            
    except KeyboardInterrupt:
        _v_logger.info("\n\n사용자에 의해 크롤러가 종료됩니다...")
        
    except Exception as p_error:
        _v_logger.error(f"크롤러 실행 중 오류 발생: {p_error}", exc_info=True)
        
    finally:
        # 리소스 정리
        _v_logger.info("리소스 정리 중...")
        close_pool()
        _v_logger.info("✓ 크롤러 종료 완료")


if __name__ == '__main__':
    main()


