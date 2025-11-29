/**
 * 즐겨찾기 서비스
 * 상담원의 이벤트 즐겨찾기 관리
 */

const db = require('../config/database');
const logger = require('../config/logger');

/**
 * 즐겨찾기 추가
 * @param {number} p_user_id - 사용자 ID
 * @param {string} p_event_id - 이벤트 ID
 * @param {string} p_memo - 메모 (선택)
 * @returns {Promise<Object>} - 생성된 즐겨찾기 정보
 */
const addFavorite = async (p_user_id, p_event_id, p_memo = null) => {
  try {
    // 이벤트 존재 확인
    const _v_event_check = await db.query(
      'SELECT event_id FROM events WHERE event_id = $1',
      [p_event_id]
    );
    
    if (_v_event_check.rows.length === 0) {
      throw new Error('존재하지 않는 이벤트입니다.');
    }
    
    // 중복 확인
    const _v_duplicate_check = await db.query(
      'SELECT favorite_id FROM favorites WHERE user_id = $1 AND event_id = $2',
      [p_user_id, p_event_id]
    );
    
    if (_v_duplicate_check.rows.length > 0) {
      throw new Error('이미 즐겨찾기에 추가된 이벤트입니다.');
    }
    
    // 즐겨찾기 추가
    const _v_insert_query = `
      INSERT INTO favorites (user_id, event_id, memo)
      VALUES ($1, $2, $3)
      RETURNING favorite_id, user_id, event_id, memo, created_at
    `;
    
    const _v_result = await db.query(_v_insert_query, [p_user_id, p_event_id, p_memo]);
    
    logger.info('즐겨찾기 추가 완료:', {
      userId: p_user_id,
      eventId: p_event_id,
    });
    
    return {
      success: true,
      data: _v_result.rows[0],
    };
  } catch (p_error) {
    logger.error('즐겨찾기 추가 실패:', p_error);
    throw p_error;
  }
};

/**
 * 즐겨찾기 목록 조회
 * @param {number} p_user_id - 사용자 ID
 * @param {Object} p_filters - 필터 조건
 * @returns {Promise<Object>} - 즐겨찾기 목록
 */
const getFavorites = async (p_user_id, p_filters = {}) => {
  try {
    const _v_page = parseInt(p_filters.page || 0);
    const _v_page_size = parseInt(p_filters.page_size || 20);
    const _v_offset = _v_page * _v_page_size;
    
    // 전체 개수 조회
    const _v_count_query = `
      SELECT COUNT(*) as total
      FROM favorites
      WHERE user_id = $1
    `;
    
    const _v_count_result = await db.query(_v_count_query, [p_user_id]);
    const _v_total = parseInt(_v_count_result.rows[0].total);
    
    // 데이터 조회
    const _v_data_query = `
      SELECT 
        f.favorite_id,
        f.event_id,
        f.memo,
        f.created_at,
        e.title as event_title,
        e.subtitle as event_subtitle,
        c.channel_name,
        e.start_date,
        e.end_date,
        e.status,
        e.benefit_summary,
        e.event_url,
        e.thumbnail_url
      FROM favorites f
      INNER JOIN events e ON f.event_id = e.event_id
      INNER JOIN channels c ON e.channel_id = c.channel_id
      WHERE f.user_id = $1
      ORDER BY f.created_at DESC
      LIMIT $2 OFFSET $3
    `;
    
    const _v_data_result = await db.query(_v_data_query, [p_user_id, _v_page_size, _v_offset]);
    
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
    logger.error('즐겨찾기 목록 조회 실패:', p_error);
    throw new Error('즐겨찾기 목록 조회 중 오류가 발생했습니다.');
  }
};

/**
 * 즐겨찾기 삭제
 * @param {number} p_user_id - 사용자 ID
 * @param {number} p_favorite_id - 즐겨찾기 ID
 * @returns {Promise<Object>} - 삭제 결과
 */
const removeFavorite = async (p_user_id, p_favorite_id) => {
  try {
    const _v_delete_query = `
      DELETE FROM favorites
      WHERE favorite_id = $1 AND user_id = $2
      RETURNING favorite_id
    `;
    
    const _v_result = await db.query(_v_delete_query, [p_favorite_id, p_user_id]);
    
    if (_v_result.rows.length === 0) {
      throw new Error('즐겨찾기를 찾을 수 없습니다.');
    }
    
    logger.info('즐겨찾기 삭제 완료:', {
      userId: p_user_id,
      favoriteId: p_favorite_id,
    });
    
    return {
      success: true,
      message: '즐겨찾기가 삭제되었습니다.',
    };
  } catch (p_error) {
    logger.error('즐겨찾기 삭제 실패:', p_error);
    throw p_error;
  }
};

/**
 * 즐겨찾기 메모 수정
 * @param {number} p_user_id - 사용자 ID
 * @param {number} p_favorite_id - 즐겨찾기 ID
 * @param {string} p_memo - 새 메모
 * @returns {Promise<Object>} - 수정 결과
 */
const updateFavoriteMemo = async (p_user_id, p_favorite_id, p_memo) => {
  try {
    const _v_update_query = `
      UPDATE favorites
      SET memo = $1
      WHERE favorite_id = $2 AND user_id = $3
      RETURNING favorite_id, memo
    `;
    
    const _v_result = await db.query(_v_update_query, [p_memo, p_favorite_id, p_user_id]);
    
    if (_v_result.rows.length === 0) {
      throw new Error('즐겨찾기를 찾을 수 없습니다.');
    }
    
    logger.info('즐겨찾기 메모 수정 완료:', {
      userId: p_user_id,
      favoriteId: p_favorite_id,
    });
    
    return {
      success: true,
      data: _v_result.rows[0],
    };
  } catch (p_error) {
    logger.error('즐겨찾기 메모 수정 실패:', p_error);
    throw p_error;
  }
};

module.exports = {
  addFavorite,
  getFavorites,
  removeFavorite,
  updateFavoriteMemo,
};


