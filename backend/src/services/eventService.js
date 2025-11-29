/**
 * 이벤트 서비스
 * 이벤트/프로모션 관련 비즈니스 로직 처리
 */

const db = require('../config/database');
const cache = require('../config/redis');
const logger = require('../config/logger');

/**
 * 이벤트 목록 조회
 * @param {Object} p_filters - 필터 조건
 * @returns {Promise<Object>} - 이벤트 목록 및 페이지네이션 정보
 */
const searchEvents = async (p_filters = {}) => {
  try {
    // 기본값 설정
    const _v_page = parseInt(p_filters.page || 0);
    const _v_page_size = parseInt(p_filters.page_size || 20);
    const _v_offset = _v_page * _v_page_size;
    const _v_sort_by = p_filters.sort_by || 'start_date';
    const _v_sort_order = p_filters.sort_order || 'DESC';
    
    // 캐시 키 생성
    const _v_cache_key = `events:search:${JSON.stringify(p_filters)}`;
    
    // 캐시 확인
    const _v_cached = await cache.getCache(_v_cache_key);
    if (_v_cached) {
      logger.debug('이벤트 검색 결과 캐시 히트');
      return _v_cached;
    }
    
    // WHERE 절 구성
    const _v_where_conditions = ['c.is_active = TRUE'];
    const _v_params = [];
    let _v_param_index = 1;
    
    // 채널 필터
    if (p_filters.channel) {
      _v_where_conditions.push(`c.channel_code = $${_v_param_index}`);
      _v_params.push(p_filters.channel);
      _v_param_index++;
    }
    
    // 상태 필터
    if (p_filters.status) {
      _v_where_conditions.push(`e.status = $${_v_param_index}`);
      _v_params.push(p_filters.status);
      _v_param_index++;
    }
    
    // 키워드 검색
    if (p_filters.keyword) {
      _v_where_conditions.push(`(
        e.title ILIKE $${_v_param_index} OR 
        e.benefit_summary ILIKE $${_v_param_index} OR 
        e.target_products ILIKE $${_v_param_index}
      )`);
      _v_params.push(`%${p_filters.keyword}%`);
      _v_param_index++;
    }
    
    // 시작일 필터
    if (p_filters.start_date) {
      _v_where_conditions.push(`e.start_date >= $${_v_param_index}`);
      _v_params.push(p_filters.start_date);
      _v_param_index++;
    }
    
    // 종료일 필터
    if (p_filters.end_date) {
      _v_where_conditions.push(`e.end_date <= $${_v_param_index}`);
      _v_params.push(p_filters.end_date);
      _v_param_index++;
    }
    
    const _v_where_clause = _v_where_conditions.length > 0
      ? `WHERE ${_v_where_conditions.join(' AND ')}`
      : '';
    
    // 전체 개수 조회
    const _v_count_query = `
      SELECT COUNT(*) as total
      FROM events e
      INNER JOIN channels c ON e.channel_id = c.channel_id
      ${_v_where_clause}
    `;
    
    const _v_count_result = await db.query(_v_count_query, _v_params);
    const _v_total = parseInt(_v_count_result.rows[0].total);
    
    // 데이터 조회
    const _v_data_query = `
      SELECT 
        e.event_id,
        e.title,
        e.subtitle,
        c.channel_id,
        c.channel_name,
        c.channel_code,
        c.channel_type,
        e.start_date,
        e.end_date,
        e.discount_rate,
        e.discount_amount,
        e.benefit_summary,
        e.benefit_detail,
        e.target_products,
        e.event_url,
        e.thumbnail_url,
        e.status,
        e.priority,
        e.favorite_count,
        e.view_count,
        e.tags,
        e.created_at,
        e.updated_at
      FROM events e
      INNER JOIN channels c ON e.channel_id = c.channel_id
      ${_v_where_clause}
      ORDER BY e.${_v_sort_by} ${_v_sort_order}
      LIMIT $${_v_param_index} OFFSET $${_v_param_index + 1}
    `;
    
    _v_params.push(_v_page_size, _v_offset);
    
    const _v_data_result = await db.query(_v_data_query, _v_params);
    
    // 결과 구성
    const _v_result = {
      success: true,
      data: _v_data_result.rows,
      pagination: {
        total: _v_total,
        page: _v_page,
        page_size: _v_page_size,
        total_pages: Math.ceil(_v_total / _v_page_size),
      },
    };
    
    // 캐시 저장 (5분)
    await cache.setCache(_v_cache_key, _v_result, 300);
    
    logger.info('이벤트 검색 완료:', {
      filters: p_filters,
      resultCount: _v_data_result.rows.length,
      total: _v_total,
    });
    
    return _v_result;
  } catch (p_error) {
    logger.error('이벤트 검색 실패:', p_error);
    throw new Error('이벤트 검색 중 오류가 발생했습니다.');
  }
};

/**
 * 이벤트 상세 조회
 * @param {string} p_event_id - 이벤트 ID
 * @param {number} p_user_id - 조회하는 사용자 ID (선택)
 * @returns {Promise<Object>} - 이벤트 상세 정보
 */
const getEventById = async (p_event_id, p_user_id = null) => {
  try {
    // 캐시 확인
    const _v_cache_key = `event:${p_event_id}`;
    const _v_cached = await cache.getCache(_v_cache_key);
    
    if (_v_cached) {
      logger.debug('이벤트 상세 캐시 히트:', p_event_id);
    } else {
      // 데이터베이스 조회
      const _v_query = `
        SELECT 
          e.*,
          c.channel_name,
          c.channel_code,
          c.channel_type,
          c.icon_url as channel_icon
        FROM events e
        INNER JOIN channels c ON e.channel_id = c.channel_id
        WHERE e.event_id = $1
      `;
      
      const _v_result = await db.query(_v_query, [p_event_id]);
      
      if (_v_result.rows.length === 0) {
        return null;
      }
      
      // 캐시 저장 (5분)
      await cache.setCache(_v_cache_key, _v_result.rows[0], 300);
      _v_cached = _v_result.rows[0];
    }
    
    // 조회수 증가 (비동기, 에러 무시)
    db.query('UPDATE events SET view_count = view_count + 1 WHERE event_id = $1', [p_event_id])
      .catch((_v_err) => logger.warn('조회수 증가 실패:', _v_err));
    
    // 조회 로그 기록 (비동기, 에러 무시)
    if (p_user_id) {
      db.query(
        'INSERT INTO view_logs (user_id, event_id, view_type) VALUES ($1, $2, $3)',
        [p_user_id, p_event_id, 'DETAIL']
      ).catch((_v_err) => logger.warn('조회 로그 기록 실패:', _v_err));
    }
    
    logger.info('이벤트 상세 조회 완료:', p_event_id);
    return _v_cached;
  } catch (p_error) {
    logger.error('이벤트 상세 조회 실패:', p_error);
    throw new Error('이벤트 조회 중 오류가 발생했습니다.');
  }
};

/**
 * 대시보드 데이터 조회
 * @returns {Promise<Object>} - 대시보드 통계 데이터
 */
const getDashboardData = async () => {
  try {
    // 캐시 확인
    const _v_cache_key = 'dashboard:stats';
    const _v_cached = await cache.getCache(_v_cache_key);
    
    if (_v_cached) {
      logger.debug('대시보드 데이터 캐시 히트');
      return _v_cached;
    }
    
    // 1. 전체 통계
    const _v_stats_query = `
      SELECT
        COUNT(*) FILTER (WHERE status = 'ACTIVE') as active_events,
        COUNT(*) FILTER (WHERE status = 'PENDING') as pending_events,
        COUNT(*) FILTER (WHERE status = 'ENDED') as ended_events,
        COUNT(DISTINCT channel_id) as total_channels,
        AVG(discount_rate) FILTER (WHERE status = 'ACTIVE' AND discount_rate IS NOT NULL) as avg_discount
      FROM events
    `;
    
    const _v_stats_result = await db.query(_v_stats_query);
    const _v_statistics = _v_stats_result.rows[0];
    
    // 2. 채널별 통계
    const _v_channel_query = `
      SELECT 
        c.channel_id,
        c.channel_name,
        c.channel_type,
        COUNT(e.event_id) as total_events,
        COUNT(e.event_id) FILTER (WHERE e.status = 'ACTIVE') as active_events
      FROM channels c
      LEFT JOIN events e ON c.channel_id = e.channel_id
      WHERE c.is_active = TRUE
      GROUP BY c.channel_id, c.channel_name, c.channel_type
      ORDER BY active_events DESC
    `;
    
    const _v_channel_result = await db.query(_v_channel_query);
    
    // 3. 최근 7일 트렌드
    const _v_trend_query = `
      SELECT 
        DATE(created_at) as date,
        COUNT(*) as count
      FROM events
      WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
      GROUP BY DATE(created_at)
      ORDER BY date
    `;
    
    const _v_trend_result = await db.query(_v_trend_query);
    
    // 4. 곧 종료되는 이벤트 (긴급)
    const _v_urgent_query = `
      SELECT 
        e.event_id,
        e.title,
        c.channel_name,
        e.end_date,
        e.benefit_summary,
        EXTRACT(EPOCH FROM (e.end_date - NOW())) / 3600 as hours_remaining
      FROM events e
      INNER JOIN channels c ON e.channel_id = c.channel_id
      WHERE e.status = 'ACTIVE'
        AND e.end_date BETWEEN NOW() AND NOW() + INTERVAL '2 days'
      ORDER BY e.end_date
      LIMIT 10
    `;
    
    const _v_urgent_result = await db.query(_v_urgent_query);
    
    // 5. 인기 이벤트 (즐겨찾기 + 조회수 기반)
    const _v_popular_query = `
      SELECT 
        e.event_id,
        e.title,
        c.channel_name,
        e.start_date,
        e.end_date,
        e.benefit_summary,
        e.favorite_count,
        e.view_count,
        (e.favorite_count * 3 + e.view_count) as popularity_score
      FROM events e
      INNER JOIN channels c ON e.channel_id = c.channel_id
      WHERE e.status = 'ACTIVE'
      ORDER BY popularity_score DESC
      LIMIT 10
    `;
    
    const _v_popular_result = await db.query(_v_popular_query);
    
    // 결과 구성
    const _v_result = {
      success: true,
      data: {
        statistics: {
          active_events: parseInt(_v_statistics.active_events),
          pending_events: parseInt(_v_statistics.pending_events),
          ended_events: parseInt(_v_statistics.ended_events),
          total_channels: parseInt(_v_statistics.total_channels),
          avg_discount: parseFloat(_v_statistics.avg_discount || 0).toFixed(2),
        },
        by_channel: _v_channel_result.rows,
        trend: _v_trend_result.rows,
        urgent_events: _v_urgent_result.rows,
        popular_events: _v_popular_result.rows,
      },
    };
    
    // 캐시 저장 (5분)
    await cache.setCache(_v_cache_key, _v_result, 300);
    
    logger.info('대시보드 데이터 조회 완료');
    return _v_result;
  } catch (p_error) {
    logger.error('대시보드 데이터 조회 실패:', p_error);
    throw new Error('대시보드 데이터 조회 중 오류가 발생했습니다.');
  }
};

/**
 * 상담용 문구 생성
 * @param {string} p_event_id - 이벤트 ID
 * @returns {Promise<Object>} - 생성된 상담 문구
 */
const generateConsultationText = async (p_event_id) => {
  try {
    // 이벤트 정보 조회
    const _v_event = await getEventById(p_event_id);
    
    if (!_v_event) {
      throw new Error('이벤트를 찾을 수 없습니다.');
    }
    
    // 날짜 포맷팅
    const _v_start_date = new Date(_v_event.start_date).toLocaleDateString('ko-KR');
    const _v_end_date = new Date(_v_event.end_date).toLocaleDateString('ko-KR');
    
    // 상담 문구 템플릿 생성
    let _v_text = '안녕하세요, 고객님.\n\n';
    _v_text += `문의하신 [${_v_event.title}] 이벤트는\n`;
    _v_text += `${_v_event.channel_name}에서 진행 중입니다.\n\n`;
    _v_text += '■ 이벤트 기간\n';
    _v_text += `${_v_start_date} ~ ${_v_end_date}\n\n`;
    _v_text += '■ 혜택 내용\n';
    _v_text += `${_v_event.benefit_summary || _v_event.benefit_detail || '상세 혜택은 이벤트 페이지를 참고해주세요.'}\n\n`;
    
    if (_v_event.conditions) {
      _v_text += '■ 유의사항\n';
      _v_text += `${_v_event.conditions}\n\n`;
    }
    
    _v_text += '자세한 내용은 아래 링크에서 확인하실 수 있습니다.\n';
    _v_text += `${_v_event.event_url}\n\n`;
    _v_text += '감사합니다.';
    
    // 조회 로그 기록 (비동기)
    db.query(
      'INSERT INTO view_logs (event_id, view_type) VALUES ($1, $2)',
      [p_event_id, 'CONSULTATION']
    ).catch((_v_err) => logger.warn('조회 로그 기록 실패:', _v_err));
    
    logger.info('상담 문구 생성 완료:', p_event_id);
    
    return {
      success: true,
      data: {
        event_id: p_event_id,
        event_title: _v_event.title,
        text: _v_text,
      },
    };
  } catch (p_error) {
    logger.error('상담 문구 생성 실패:', p_error);
    throw new Error(p_error.message || '상담 문구 생성 중 오류가 발생했습니다.');
  }
};

/**
 * 채널 비교
 * @param {string} p_keyword - 제품 키워드
 * @returns {Promise<Object>} - 채널별 비교 결과
 */
const compareChannels = async (p_keyword) => {
  try {
    // 캐시 확인
    const _v_cache_key = `channel:compare:${p_keyword}`;
    const _v_cached = await cache.getCache(_v_cache_key);
    
    if (_v_cached) {
      logger.debug('채널 비교 캐시 히트:', p_keyword);
      return _v_cached;
    }
    
    // 제품 관련 이벤트 조회
    const _v_query = `
      SELECT 
        c.channel_id,
        c.channel_name,
        c.channel_type,
        e.event_id,
        e.title,
        e.benefit_summary,
        e.discount_rate,
        e.event_url,
        e.start_date,
        e.end_date
      FROM events e
      INNER JOIN channels c ON e.channel_id = c.channel_id
      WHERE e.status = 'ACTIVE'
        AND (
          e.title ILIKE $1 OR 
          e.target_products ILIKE $1 OR
          e.benefit_summary ILIKE $1
        )
      ORDER BY c.channel_id, e.discount_rate DESC NULLS LAST
    `;
    
    const _v_result = await db.query(_v_query, [`%${p_keyword}%`]);
    
    if (_v_result.rows.length === 0) {
      return {
        success: true,
        data: {
          keyword: p_keyword,
          comparison: [],
          recommended_channel: null,
          message: '검색 결과가 없습니다.',
        },
      };
    }
    
    // 채널별 그룹화
    const _v_grouped = _v_result.rows.reduce((_v_acc, _v_row) => {
      if (!_v_acc[_v_row.channel_id]) {
        _v_acc[_v_row.channel_id] = {
          channel_id: _v_row.channel_id,
          channel_name: _v_row.channel_name,
          channel_type: _v_row.channel_type,
          events: [],
          best_discount: 0,
        };
      }
      
      _v_acc[_v_row.channel_id].events.push({
        event_id: _v_row.event_id,
        title: _v_row.title,
        benefit_summary: _v_row.benefit_summary,
        discount_rate: _v_row.discount_rate,
        event_url: _v_row.event_url,
      });
      
      // 최고 할인율 업데이트
      if (_v_row.discount_rate && _v_row.discount_rate > _v_acc[_v_row.channel_id].best_discount) {
        _v_acc[_v_row.channel_id].best_discount = _v_row.discount_rate;
      }
      
      return _v_acc;
    }, {});
    
    const _v_comparison = Object.values(_v_grouped);
    
    // 추천 채널 결정 (최고 할인율 기준)
    const _v_recommended = _v_comparison.reduce((_v_best, _v_current) => {
      return _v_current.best_discount > _v_best.best_discount ? _v_current : _v_best;
    });
    
    const _v_response = {
      success: true,
      data: {
        keyword: p_keyword,
        comparison: _v_comparison,
        recommended_channel: _v_recommended.channel_name,
        reason: _v_recommended.best_discount > 0 
          ? `최대 ${_v_recommended.best_discount}% 할인`
          : '관련 이벤트 진행 중',
      },
    };
    
    // 캐시 저장 (10분)
    await cache.setCache(_v_cache_key, _v_response, 600);
    
    logger.info('채널 비교 완료:', {
      keyword: p_keyword,
      channelCount: _v_comparison.length,
    });
    
    return _v_response;
  } catch (p_error) {
    logger.error('채널 비교 실패:', p_error);
    throw new Error('채널 비교 중 오류가 발생했습니다.');
  }
};

module.exports = {
  searchEvents,
  getEventById,
  getDashboardData,
  generateConsultationText,
  compareChannels,
};


