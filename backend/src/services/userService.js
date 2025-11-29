/**
 * 사용자 서비스
 * 사용자 인증 및 관리 관련 비즈니스 로직
 */

const bcrypt = require('bcrypt');
const db = require('../config/database');
const logger = require('../config/logger');
const { generateToken } = require('../middleware/auth');

// 비밀번호 해시 라운드
const _v_salt_rounds = 10;

/**
 * 사용자 로그인
 * @param {string} p_username - 사용자명
 * @param {string} p_password - 비밀번호
 * @returns {Promise<Object>} - 로그인 결과 및 토큰
 */
const login = async (p_username, p_password) => {
  try {
    // 사용자 조회
    const _v_query = `
      SELECT 
        user_id,
        username,
        password_hash,
        full_name,
        email,
        role,
        department,
        team,
        is_active
      FROM users
      WHERE username = $1
    `;
    
    const _v_result = await db.query(_v_query, [p_username]);
    
    if (_v_result.rows.length === 0) {
      logger.warn('로그인 실패 - 사용자 없음:', p_username);
      throw new Error('사용자명 또는 비밀번호가 올바르지 않습니다.');
    }
    
    const _v_user = _v_result.rows[0];
    
    // 계정 활성화 확인
    if (!_v_user.is_active) {
      logger.warn('로그인 실패 - 비활성 계정:', p_username);
      throw new Error('비활성화된 계정입니다. 관리자에게 문의하세요.');
    }
    
    // 비밀번호 검증
    const _v_password_match = await bcrypt.compare(p_password, _v_user.password_hash);
    
    if (!_v_password_match) {
      logger.warn('로그인 실패 - 비밀번호 불일치:', p_username);
      throw new Error('사용자명 또는 비밀번호가 올바르지 않습니다.');
    }
    
    // JWT 토큰 생성
    const _v_token = generateToken({
      user_id: _v_user.user_id,
      username: _v_user.username,
      role: _v_user.role,
    });
    
    // 로그인 정보 업데이트 (비동기)
    db.query(
      'UPDATE users SET last_login_at = NOW(), login_count = login_count + 1 WHERE user_id = $1',
      [_v_user.user_id]
    ).catch((_v_err) => logger.warn('로그인 정보 업데이트 실패:', _v_err));
    
    logger.info('로그인 성공:', {
      userId: _v_user.user_id,
      username: p_username,
    });
    
    // 민감 정보 제외하고 반환
    delete _v_user.password_hash;
    
    return {
      success: true,
      data: {
        user: _v_user,
        token: _v_token,
      },
    };
  } catch (p_error) {
    logger.error('로그인 처리 실패:', p_error);
    throw p_error;
  }
};

/**
 * 사용자 생성
 * @param {Object} p_user_data - 사용자 정보
 * @returns {Promise<Object>} - 생성된 사용자 정보
 */
const createUser = async (p_user_data) => {
  try {
    // 중복 확인
    const _v_check_query = `
      SELECT user_id 
      FROM users 
      WHERE username = $1 OR email = $2
    `;
    
    const _v_check_result = await db.query(_v_check_query, [
      p_user_data.username,
      p_user_data.email,
    ]);
    
    if (_v_check_result.rows.length > 0) {
      throw new Error('이미 존재하는 사용자명 또는 이메일입니다.');
    }
    
    // 비밀번호 해시화
    const _v_password_hash = await bcrypt.hash(p_user_data.password, _v_salt_rounds);
    
    // 사용자 생성
    const _v_insert_query = `
      INSERT INTO users (
        username,
        password_hash,
        full_name,
        email,
        phone,
        role,
        department,
        team
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      RETURNING user_id, username, full_name, email, role, department, team, created_at
    `;
    
    const _v_insert_result = await db.query(_v_insert_query, [
      p_user_data.username,
      _v_password_hash,
      p_user_data.full_name,
      p_user_data.email,
      p_user_data.phone || null,
      p_user_data.role || 'AGENT',
      p_user_data.department || null,
      p_user_data.team || null,
    ]);
    
    const _v_new_user = _v_insert_result.rows[0];
    
    logger.info('사용자 생성 완료:', {
      userId: _v_new_user.user_id,
      username: _v_new_user.username,
    });
    
    return {
      success: true,
      data: _v_new_user,
    };
  } catch (p_error) {
    logger.error('사용자 생성 실패:', p_error);
    throw p_error;
  }
};

/**
 * 사용자 정보 조회
 * @param {number} p_user_id - 사용자 ID
 * @returns {Promise<Object>} - 사용자 정보
 */
const getUserById = async (p_user_id) => {
  try {
    const _v_query = `
      SELECT 
        user_id,
        username,
        full_name,
        email,
        phone,
        role,
        department,
        team,
        is_active,
        last_login_at,
        login_count,
        created_at
      FROM users
      WHERE user_id = $1
    `;
    
    const _v_result = await db.query(_v_query, [p_user_id]);
    
    if (_v_result.rows.length === 0) {
      return null;
    }
    
    return _v_result.rows[0];
  } catch (p_error) {
    logger.error('사용자 조회 실패:', p_error);
    throw new Error('사용자 조회 중 오류가 발생했습니다.');
  }
};

/**
 * 사용자 목록 조회
 * @param {Object} p_filters - 필터 조건
 * @returns {Promise<Object>} - 사용자 목록
 */
const getUsers = async (p_filters = {}) => {
  try {
    const _v_page = parseInt(p_filters.page || 0);
    const _v_page_size = parseInt(p_filters.page_size || 20);
    const _v_offset = _v_page * _v_page_size;
    
    // WHERE 절 구성
    const _v_where_conditions = [];
    const _v_params = [];
    let _v_param_index = 1;
    
    if (p_filters.role) {
      _v_where_conditions.push(`role = $${_v_param_index}`);
      _v_params.push(p_filters.role);
      _v_param_index++;
    }
    
    if (p_filters.is_active !== undefined) {
      _v_where_conditions.push(`is_active = $${_v_param_index}`);
      _v_params.push(p_filters.is_active);
      _v_param_index++;
    }
    
    if (p_filters.keyword) {
      _v_where_conditions.push(`(
        username ILIKE $${_v_param_index} OR 
        full_name ILIKE $${_v_param_index} OR 
        email ILIKE $${_v_param_index}
      )`);
      _v_params.push(`%${p_filters.keyword}%`);
      _v_param_index++;
    }
    
    const _v_where_clause = _v_where_conditions.length > 0
      ? `WHERE ${_v_where_conditions.join(' AND ')}`
      : '';
    
    // 전체 개수 조회
    const _v_count_query = `SELECT COUNT(*) as total FROM users ${_v_where_clause}`;
    const _v_count_result = await db.query(_v_count_query, _v_params);
    const _v_total = parseInt(_v_count_result.rows[0].total);
    
    // 데이터 조회
    const _v_data_query = `
      SELECT 
        user_id,
        username,
        full_name,
        email,
        phone,
        role,
        department,
        team,
        is_active,
        last_login_at,
        login_count,
        created_at
      FROM users
      ${_v_where_clause}
      ORDER BY created_at DESC
      LIMIT $${_v_param_index} OFFSET $${_v_param_index + 1}
    `;
    
    _v_params.push(_v_page_size, _v_offset);
    
    const _v_data_result = await db.query(_v_data_query, _v_params);
    
    return {
      success: true,
      data: _v_data_result.rows,
      pagination: {
        total: _v_total,
        page: _v_page,
        page_size: _v_page_size,
        total_pages: Math.ceil(_v_total / _v_page_size),
      },
    };
  } catch (p_error) {
    logger.error('사용자 목록 조회 실패:', p_error);
    throw new Error('사용자 목록 조회 중 오류가 발생했습니다.');
  }
};

module.exports = {
  login,
  createUser,
  getUserById,
  getUsers,
};


