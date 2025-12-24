/**
 * 데이터베이스 연결 설정
 * PostgreSQL 연결 풀 관리 및 쿼리 헬퍼 함수 제공
 */

const { Pool } = require('pg');
const logger = require('./logger');

// 환경변수에서 데이터베이스 설정 로드
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'cosmetic_consultation_system',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || '',
  min: parseInt(process.env.DB_POOL_MIN || '2'),
  max: parseInt(process.env.DB_POOL_MAX || '10'),
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
};

// PostgreSQL 연결 풀 생성
const pool = new Pool(dbConfig);

// 연결 풀 이벤트 핸들러
pool.on('connect', () => {
  logger.info('PostgreSQL 데이터베이스에 연결되었습니다.');
});

pool.on('error', (p_error) => {
  logger.error('PostgreSQL 연결 풀 에러:', p_error);
  process.exit(-1);
});

/**
 * 쿼리 실행 헬퍼 함수
 * @param {string} p_text - SQL 쿼리 문자열
 * @param {Array} p_params - 쿼리 파라미터 배열
 * @returns {Promise<Object>} - 쿼리 결과
 */
const query = async (p_text, p_params = []) => {
  const _v_start = Date.now();
  
  try {
    // 쿼리 실행
    const _v_result = await pool.query(p_text, p_params);
    
    // 쿼리 실행 시간 계산
    const _v_duration = Date.now() - _v_start;
    
    // 성능 로깅 (느린 쿼리 감지)
    if (_v_duration > 1000) {
      logger.warn(`느린 쿼리 감지 (${_v_duration}ms):`, {
        query: p_text,
        duration: _v_duration,
      });
    } else {
      logger.debug(`쿼리 실행 완료 (${_v_duration}ms):`, {
        query: p_text.substring(0, 100),
        rowCount: _v_result.rowCount,
      });
    }
    
    return _v_result;
  } catch (p_error) {
    // 에러 로깅
    logger.error('데이터베이스 쿼리 에러:', {
      error: p_error.message,
      query: p_text,
      params: p_params,
    });
    throw p_error;
  }
};

/**
 * 트랜잭션 시작
 * @param {Function} p_callback - 트랜잭션 내에서 실행할 함수
 * @returns {Promise<any>} - 콜백 함수의 반환값
 */
const transaction = async (p_callback) => {
  // 풀에서 클라이언트 획득
  const _v_client = await pool.connect();
  
  try {
    // 트랜잭션 시작
    await _v_client.query('BEGIN');
    logger.debug('트랜잭션 시작');
    
    // 콜백 함수 실행
    const _v_result = await p_callback(_v_client);
    
    // 트랜잭션 커밋
    await _v_client.query('COMMIT');
    logger.debug('트랜잭션 커밋');
    
    return _v_result;
  } catch (p_error) {
    // 에러 발생 시 롤백
    await _v_client.query('ROLLBACK');
    logger.error('트랜잭션 롤백:', p_error);
    throw p_error;
  } finally {
    // 클라이언트 반환
    _v_client.release();
  }
};

/**
 * 데이터베이스 연결 테스트
 * @returns {Promise<boolean>} - 연결 성공 여부
 */
const testConnection = async () => {
  try {
    const _v_result = await query('SELECT NOW() as current_time');
    logger.info('데이터베이스 연결 테스트 성공:', _v_result.rows[0]);
    return true;
  } catch (p_error) {
    logger.error('데이터베이스 연결 테스트 실패:', p_error);
    return false;
  }
};

/**
 * 연결 풀 종료
 */
const closePool = async () => {
  await pool.end();
  logger.info('데이터베이스 연결 풀이 종료되었습니다.');
};

module.exports = {
  pool,
  query,
  transaction,
  testConnection,
  closePool,
};


