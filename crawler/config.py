"""
크롤러 설정 파일
환경변수 및 전역 설정 관리
"""

import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

# ============================================================================
# 데이터베이스 설정
# ============================================================================
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'cosmetic_consultation_system'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),
}

# SQLAlchemy 연결 문자열
DB_CONNECTION_STRING = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# ============================================================================
# 크롤링 설정
# ============================================================================
CRAWLER_CONFIG = {
    # User Agent
    'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    
    # 타임아웃 설정 (초)
    'timeout': 30,
    
    # 재시도 설정
    'max_retries': 3,
    'retry_delay': 5,  # 초
    
    # 딜레이 설정 (초) - 서버 부하 방지
    'request_delay': 2,
    
    # Selenium 설정
    'selenium_headless': True,
    'selenium_implicit_wait': 10,
    
    # 페이지 로드 대기 시간 (초)
    'page_load_timeout': 30,
}

# ============================================================================
# 채널별 크롤링 설정
# ============================================================================
CHANNEL_CONFIGS = {
    'AMORE_MALL': {
        'url': 'https://www.amoremall.com/kr/ko/display/event',
        'interval_minutes': 360,  # 6시간
        'parser': 'amore_mall',
        'enabled': True,
    },
    'INNISFREE_MALL': {
        'url': 'https://www.innisfree.com/kr/ko/event',
        'interval_minutes': 360,
        'parser': 'innisfree_mall',
        'enabled': True,
    },
    'OSULLOC_MALL': {
        'url': 'https://www.osulloc.com/kr/ko/event',
        'interval_minutes': 360,
        'parser': 'osulloc_mall',
        'enabled': True,
    },
    'COUPANG': {
        'url': 'https://shop.coupang.com/amorepacific/480332',
        'interval_minutes': 720,  # 12시간
        'parser': 'coupang',
        'enabled': True,
    },
    'NAVER_LIVE': {
        'url': 'https://shopping.naver.com/live',
        'interval_minutes': 60,  # 1시간
        'parser': 'naver_live',
        'enabled': True,
        'use_selenium': True,  # 동적 페이지
    },
}

# ============================================================================
# 로깅 설정
# ============================================================================
LOG_CONFIG = {
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'log_file': os.getenv('LOG_FILE', './logs/crawler.log'),
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'max_bytes': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}

# ============================================================================
# 알림 설정
# ============================================================================
ALERT_CONFIG = {
    'slack_webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
    'slack_enabled': os.getenv('SLACK_ENABLED', 'false').lower() == 'true',
}

# ============================================================================
# 스케줄러 설정
# ============================================================================
SCHEDULER_CONFIG = {
    'timezone': 'Asia/Seoul',
    'check_interval': 60,  # 스케줄 체크 주기 (초)
}

# ============================================================================
# 데이터 정규화 설정
# ============================================================================
NORMALIZATION_CONFIG = {
    # 할인율 추출 정규식 패턴
    'discount_pattern': r'(\d+)%',
    
    # 날짜 포맷
    'date_formats': [
        '%Y-%m-%d',
        '%Y.%m.%d',
        '%Y/%m/%d',
        '%Y년 %m월 %d일',
    ],
    
    # 제거할 HTML 태그
    'strip_tags': ['script', 'style', 'meta', 'link'],
}


