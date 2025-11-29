"""
데이터베이스 연결 및 쿼리 헬퍼
PostgreSQL 연결 관리 및 CRUD 작업
"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
from config import DB_CONFIG

# 로거 설정
_v_logger = logging.getLogger(__name__)

# 연결 풀 초기화
_v_connection_pool = None


def initialize_pool(p_min_conn=2, p_max_conn=10):
    """
    데이터베이스 연결 풀 초기화
    
    Args:
        p_min_conn (int): 최소 연결 수
        p_max_conn (int): 최대 연결 수
    """
    global _v_connection_pool
    
    try:
        _v_connection_pool = psycopg2.pool.ThreadedConnectionPool(
            p_min_conn,
            p_max_conn,
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        _v_logger.info("데이터베이스 연결 풀이 생성되었습니다.")
    except Exception as p_error:
        _v_logger.error(f"데이터베이스 연결 풀 생성 실패: {p_error}")
        raise


def get_connection():
    """
    연결 풀에서 데이터베이스 연결 획득
    
    Returns:
        psycopg2.connection: 데이터베이스 연결 객체
    """
    if _v_connection_pool is None:
        initialize_pool()
    
    return _v_connection_pool.getconn()


def release_connection(p_conn):
    """
    연결 풀에 데이터베이스 연결 반환
    
    Args:
        p_conn: 반환할 연결 객체
    """
    if _v_connection_pool:
        _v_connection_pool.putconn(p_conn)


def close_pool():
    """연결 풀 종료"""
    global _v_connection_pool
    
    if _v_connection_pool:
        _v_connection_pool.closeall()
        _v_logger.info("데이터베이스 연결 풀이 종료되었습니다.")


def execute_query(p_query, p_params=None, p_fetch=True):
    """
    SQL 쿼리 실행 헬퍼 함수
    
    Args:
        p_query (str): SQL 쿼리 문자열
        p_params (tuple): 쿼리 파라미터
        p_fetch (bool): 결과 조회 여부
        
    Returns:
        list: 조회 결과 (fetch=True인 경우) 또는 영향받은 행 수
    """
    _v_conn = None
    _v_cursor = None
    
    try:
        # 연결 획득
        _v_conn = get_connection()
        _v_cursor = _v_conn.cursor(cursor_factory=RealDictCursor)
        
        # 쿼리 실행
        _v_cursor.execute(p_query, p_params)
        
        if p_fetch:
            # SELECT 쿼리 결과 조회
            _v_result = _v_cursor.fetchall()
            return [dict(_v_row) for _v_row in _v_result]
        else:
            # INSERT/UPDATE/DELETE 커밋
            _v_conn.commit()
            return _v_cursor.rowcount
            
    except Exception as p_error:
        if _v_conn:
            _v_conn.rollback()
        _v_logger.error(f"쿼리 실행 실패: {p_error}")
        _v_logger.error(f"Query: {p_query}")
        _v_logger.error(f"Params: {p_params}")
        raise
        
    finally:
        if _v_cursor:
            _v_cursor.close()
        if _v_conn:
            release_connection(_v_conn)


def get_channel_by_code(p_channel_code):
    """
    채널 코드로 채널 정보 조회
    
    Args:
        p_channel_code (str): 채널 코드
        
    Returns:
        dict: 채널 정보 또는 None
    """
    _v_query = """
        SELECT channel_id, channel_code, channel_name, channel_type
        FROM channels
        WHERE channel_code = %s AND is_active = TRUE
    """
    
    _v_result = execute_query(_v_query, (p_channel_code,))
    return _v_result[0] if _v_result else None


def check_event_exists(p_channel_id, p_external_id):
    """
    이벤트 존재 여부 확인
    
    Args:
        p_channel_id (int): 채널 ID
        p_external_id (str): 외부 시스템 이벤트 ID
        
    Returns:
        dict: 이벤트 정보 또는 None
    """
    _v_query = """
        SELECT event_id, title, start_date, end_date, discount_rate, benefit_summary
        FROM events
        WHERE channel_id = %s AND external_id = %s
    """
    
    _v_result = execute_query(_v_query, (p_channel_id, p_external_id))
    return _v_result[0] if _v_result else None


def insert_event(p_event_data):
    """
    새 이벤트 삽입
    
    Args:
        p_event_data (dict): 이벤트 데이터
        
    Returns:
        str: 생성된 이벤트 ID (UUID)
    """
    _v_query = """
        INSERT INTO events (
            channel_id, external_id, title, subtitle, description,
            start_date, end_date, discount_rate, discount_amount,
            benefit_summary, benefit_detail, target_products,
            target_brands, conditions, cautions, event_url,
            image_url, thumbnail_url, priority, tags
        ) VALUES (
            %(channel_id)s, %(external_id)s, %(title)s, %(subtitle)s, %(description)s,
            %(start_date)s, %(end_date)s, %(discount_rate)s, %(discount_amount)s,
            %(benefit_summary)s, %(benefit_detail)s, %(target_products)s,
            %(target_brands)s, %(conditions)s, %(cautions)s, %(event_url)s,
            %(image_url)s, %(thumbnail_url)s, %(priority)s, %(tags)s
        )
        RETURNING event_id
    """
    
    _v_conn = None
    _v_cursor = None
    
    try:
        _v_conn = get_connection()
        _v_cursor = _v_conn.cursor()
        
        _v_cursor.execute(_v_query, p_event_data)
        _v_event_id = _v_cursor.fetchone()[0]
        
        _v_conn.commit()
        _v_logger.info(f"이벤트 삽입 완료: {p_event_data.get('title')} (ID: {_v_event_id})")
        
        return _v_event_id
        
    except Exception as p_error:
        if _v_conn:
            _v_conn.rollback()
        _v_logger.error(f"이벤트 삽입 실패: {p_error}")
        raise
        
    finally:
        if _v_cursor:
            _v_cursor.close()
        if _v_conn:
            release_connection(_v_conn)


def update_event(p_event_id, p_event_data):
    """
    기존 이벤트 업데이트
    
    Args:
        p_event_id (str): 이벤트 ID (UUID)
        p_event_data (dict): 업데이트할 이벤트 데이터
        
    Returns:
        bool: 업데이트 성공 여부
    """
    _v_query = """
        UPDATE events SET
            title = %(title)s,
            subtitle = %(subtitle)s,
            description = %(description)s,
            start_date = %(start_date)s,
            end_date = %(end_date)s,
            discount_rate = %(discount_rate)s,
            discount_amount = %(discount_amount)s,
            benefit_summary = %(benefit_summary)s,
            benefit_detail = %(benefit_detail)s,
            target_products = %(target_products)s,
            target_brands = %(target_brands)s,
            conditions = %(conditions)s,
            cautions = %(cautions)s,
            event_url = %(event_url)s,
            image_url = %(image_url)s,
            thumbnail_url = %(thumbnail_url)s,
            priority = %(priority)s,
            tags = %(tags)s,
            updated_at = CURRENT_TIMESTAMP
        WHERE event_id = %(event_id)s
    """
    
    p_event_data['event_id'] = p_event_id
    
    _v_row_count = execute_query(_v_query, p_event_data, p_fetch=False)
    
    if _v_row_count > 0:
        _v_logger.info(f"이벤트 업데이트 완료: {p_event_data.get('title')} (ID: {p_event_id})")
        return True
    else:
        _v_logger.warning(f"이벤트 업데이트 실패 - 존재하지 않는 ID: {p_event_id}")
        return False


def log_crawl_result(p_channel_id, p_status, p_stats, p_error_message=None):
    """
    크롤링 결과 로그 기록
    
    Args:
        p_channel_id (int): 채널 ID
        p_status (str): 상태 (SUCCESS, FAILED, PARTIAL)
        p_stats (dict): 통계 데이터 (items_found, items_new, items_updated, duration_ms)
        p_error_message (str): 에러 메시지 (선택)
    """
    _v_query = """
        INSERT INTO crawl_logs (
            channel_id, status, started_at, completed_at, duration_ms,
            items_found, items_new, items_updated, items_failed,
            error_message, crawler_version
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """
    
    _v_params = (
        p_channel_id,
        p_status,
        p_stats.get('started_at', datetime.now()),
        p_stats.get('completed_at', datetime.now()),
        p_stats.get('duration_ms', 0),
        p_stats.get('items_found', 0),
        p_stats.get('items_new', 0),
        p_stats.get('items_updated', 0),
        p_stats.get('items_failed', 0),
        p_error_message,
        '1.0.0',  # 크롤러 버전
    )
    
    try:
        execute_query(_v_query, _v_params, p_fetch=False)
        _v_logger.info(f"크롤링 로그 기록 완료: 채널 ID {p_channel_id}, 상태 {p_status}")
    except Exception as p_error:
        _v_logger.error(f"크롤링 로그 기록 실패: {p_error}")


def get_recent_crawl_logs(p_channel_id=None, p_limit=10):
    """
    최근 크롤링 로그 조회
    
    Args:
        p_channel_id (int): 채널 ID (선택)
        p_limit (int): 조회 개수
        
    Returns:
        list: 크롤링 로그 목록
    """
    if p_channel_id:
        _v_query = """
            SELECT * FROM crawl_logs
            WHERE channel_id = %s
            ORDER BY started_at DESC
            LIMIT %s
        """
        _v_params = (p_channel_id, p_limit)
    else:
        _v_query = """
            SELECT * FROM crawl_logs
            ORDER BY started_at DESC
            LIMIT %s
        """
        _v_params = (p_limit,)
    
    return execute_query(_v_query, _v_params)


