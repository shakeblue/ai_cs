#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 쇼핑라이브 데이터 수집 스케줄러
1시간마다 자동으로 데이터를 수집합니다.
"""

import schedule
import time
import logging
import json
import subprocess
from datetime import datetime
from pathlib import Path

# 로깅 설정
log_dir = Path(__file__).parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'scheduler_{datetime.now().strftime("%Y%m%d")}.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class DataCollectionScheduler:
    """데이터 수집 스케줄러"""
    
    def __init__(self):
        """스케줄러 초기화"""
        self.p_crawler_dir = Path(__file__).parent
        self.p_output_dir = self.p_crawler_dir / 'output'
        self.p_output_dir.mkdir(exist_ok=True)
        
        # 수집 통계
        self.p_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'last_run': None,
            'last_success': None,
            'last_error': None
        }
        
    def collect_sulwhasoo_data(self):
        """설화수 브랜드 데이터 수집"""
        logger.info("=" * 80)
        logger.info("🔄 설화수 데이터 수집 시작")
        logger.info("=" * 80)
        
        try:
            self.p_stats['total_runs'] += 1
            self.p_stats['last_run'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 설화수 크롤러 실행
            _v_script = self.p_crawler_dir / 'parsers' / 'naver_sulwhasoo_crawler.py'
            
            if not _v_script.exists():
                logger.warning(f"⚠️ 크롤러 스크립트가 없습니다: {_v_script}")
                logger.info("💡 대신 멀티 브랜드 크롤러를 실행합니다.")
                _v_script = self.p_crawler_dir / 'crawl_multi_brands.py'
            
            if _v_script.exists():
                logger.info(f"📝 실행: {_v_script}")
                _v_result = subprocess.run(
                    ['python3', str(_v_script)],
                    cwd=str(self.p_crawler_dir),
                    capture_output=True,
                    text=True,
                    timeout=600  # 10분 타임아웃
                )
                
                if _v_result.returncode == 0:
                    logger.info("✅ 설화수 데이터 수집 성공!")
                    logger.info(f"출력:\n{_v_result.stdout}")
                    self.p_stats['successful_runs'] += 1
                    self.p_stats['last_success'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    logger.error(f"❌ 크롤러 실행 실패 (코드: {_v_result.returncode})")
                    logger.error(f"에러:\n{_v_result.stderr}")
                    self.p_stats['failed_runs'] += 1
                    self.p_stats['last_error'] = _v_result.stderr[:500]
            else:
                logger.error(f"❌ 크롤러 스크립트를 찾을 수 없습니다: {_v_script}")
                self.p_stats['failed_runs'] += 1
                
        except subprocess.TimeoutExpired:
            logger.error("❌ 크롤링 타임아웃 (10분 초과)")
            self.p_stats['failed_runs'] += 1
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {str(e)}")
            self.p_stats['failed_runs'] += 1
            self.p_stats['last_error'] = str(e)
        finally:
            self._save_stats()
            logger.info("=" * 80)
            logger.info(f"📊 수집 완료 | 성공: {self.p_stats['successful_runs']}, 실패: {self.p_stats['failed_runs']}")
            logger.info("=" * 80)
            
    def collect_all_brands_data(self):
        """모든 브랜드 데이터 수집"""
        logger.info("=" * 80)
        logger.info("🔄 전체 브랜드 데이터 수집 시작")
        logger.info("=" * 80)
        
        try:
            # 멀티 브랜드 크롤러 실행
            _v_script = self.p_crawler_dir / 'crawl_multi_brands.py'
            
            if _v_script.exists():
                logger.info(f"📝 실행: {_v_script}")
                _v_result = subprocess.run(
                    ['python3', str(_v_script)],
                    cwd=str(self.p_crawler_dir),
                    capture_output=True,
                    text=True,
                    timeout=1800  # 30분 타임아웃
                )
                
                if _v_result.returncode == 0:
                    logger.info("✅ 전체 브랜드 데이터 수집 성공!")
                    logger.info(f"출력:\n{_v_result.stdout}")
                else:
                    logger.error(f"❌ 크롤러 실행 실패 (코드: {_v_result.returncode})")
                    logger.error(f"에러:\n{_v_result.stderr}")
            else:
                logger.error(f"❌ 멀티 브랜드 크롤러를 찾을 수 없습니다: {_v_script}")
                
        except Exception as e:
            logger.error(f"❌ 예상치 못한 오류: {str(e)}")
        finally:
            logger.info("=" * 80)
            
    def _save_stats(self):
        """수집 통계 저장"""
        try:
            _v_stats_file = self.p_output_dir / 'scheduler_stats.json'
            with open(_v_stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.p_stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"통계 저장 실패: {str(e)}")
            
    def get_stats(self):
        """수집 통계 출력"""
        logger.info("=" * 80)
        logger.info("📊 데이터 수집 통계")
        logger.info("=" * 80)
        logger.info(f"총 실행 횟수: {self.p_stats['total_runs']}")
        logger.info(f"성공: {self.p_stats['successful_runs']}")
        logger.info(f"실패: {self.p_stats['failed_runs']}")
        logger.info(f"마지막 실행: {self.p_stats['last_run']}")
        logger.info(f"마지막 성공: {self.p_stats['last_success']}")
        if self.p_stats['last_error']:
            logger.info(f"마지막 에러: {self.p_stats['last_error'][:200]}")
        logger.info("=" * 80)


def main():
    """메인 함수"""
    logger.info("=" * 80)
    logger.info("🚀 네이버 쇼핑라이브 데이터 수집 스케줄러 시작")
    logger.info("=" * 80)
    logger.info("⏰ 수집 주기: 1시간마다")
    logger.info("📦 수집 대상: 설화수 브랜드")
    logger.info("=" * 80)
    
    scheduler = DataCollectionScheduler()
    
    # 시작 시 즉시 1회 실행
    logger.info("🔄 초기 데이터 수집 실행...")
    scheduler.collect_sulwhasoo_data()
    
    # 매 시간 정각에 실행 (예: 10:00, 11:00, 12:00...)
    schedule.every().hour.at(":00").do(scheduler.collect_sulwhasoo_data)
    
    # 또는 1시간마다 실행 (시작 시점부터 1시간 간격)
    # schedule.every(1).hours.do(scheduler.collect_sulwhasoo_data)
    
    # 매일 자정에 통계 출력
    schedule.every().day.at("00:00").do(scheduler.get_stats)
    
    logger.info("✅ 스케줄러 준비 완료")
    logger.info("💡 Ctrl+C를 눌러 종료할 수 있습니다.")
    logger.info("=" * 80)
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 체크
    except KeyboardInterrupt:
        logger.info("\n⏹️  스케줄러 종료")
        scheduler.get_stats()


if __name__ == "__main__":
    main()

