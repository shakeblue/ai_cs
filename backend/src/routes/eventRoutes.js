/**
 * 이벤트 라우터
 * 이벤트/프로모션 관련 API 엔드포인트
 */

const express = require('express');
const router = express.Router();

const eventService = require('../services/eventService');
const { authenticate, optionalAuth } = require('../middleware/auth');
const {
  validateEventSearch,
  validateEventId,
  validateChannelCompare,
  validateDateRange,
} = require('../middleware/validator');
const { searchLimiter } = require('../middleware/rateLimit');
const logger = require('../config/logger');

/**
 * GET /api/events/search
 * 이벤트 검색
 * 쿼리 파라미터: channel, status, keyword, start_date, end_date, page, page_size, sort_by, sort_order
 */
router.get(
  '/search',
  optionalAuth,
  searchLimiter,
  validateEventSearch,
  validateDateRange,
  async (p_req, p_res) => {
    try {
      const _v_filters = {
        channel: p_req.query.channel,
        status: p_req.query.status || 'ACTIVE',
        keyword: p_req.query.keyword,
        start_date: p_req.query.start_date,
        end_date: p_req.query.end_date,
        page: p_req.query.page,
        page_size: p_req.query.page_size,
        sort_by: p_req.query.sort_by,
        sort_order: p_req.query.sort_order,
      };
      
      const _v_result = await eventService.searchEvents(_v_filters);
      
      p_res.json(_v_result);
    } catch (p_error) {
      logger.error('이벤트 검색 API 에러:', p_error);
      p_res.status(500).json({
        success: false,
        message: p_error.message || '이벤트 검색 중 오류가 발생했습니다.',
      });
    }
  }
);

/**
 * GET /api/events/:event_id
 * 이벤트 상세 조회
 */
router.get(
  '/:event_id',
  optionalAuth,
  validateEventId,
  async (p_req, p_res) => {
    try {
      const _v_event_id = p_req.params.event_id;
      const _v_user_id = p_req.user?.user_id;
      
      const _v_event = await eventService.getEventById(_v_event_id, _v_user_id);
      
      if (!_v_event) {
        return p_res.status(404).json({
          success: false,
          message: '이벤트를 찾을 수 없습니다.',
        });
      }
      
      p_res.json({
        success: true,
        data: _v_event,
      });
    } catch (p_error) {
      logger.error('이벤트 상세 조회 API 에러:', p_error);
      p_res.status(500).json({
        success: false,
        message: p_error.message || '이벤트 조회 중 오류가 발생했습니다.',
      });
    }
  }
);

/**
 * GET /api/events/:event_id/consultation-text
 * 상담용 문구 생성
 */
router.get(
  '/:event_id/consultation-text',
  authenticate,
  validateEventId,
  async (p_req, p_res) => {
    try {
      const _v_event_id = p_req.params.event_id;
      
      const _v_result = await eventService.generateConsultationText(_v_event_id);
      
      p_res.json(_v_result);
    } catch (p_error) {
      logger.error('상담 문구 생성 API 에러:', p_error);
      p_res.status(500).json({
        success: false,
        message: p_error.message || '상담 문구 생성 중 오류가 발생했습니다.',
      });
    }
  }
);

/**
 * GET /api/events/compare/channels
 * 채널 비교
 * 쿼리 파라미터: keyword
 */
router.get(
  '/compare/channels',
  authenticate,
  validateChannelCompare,
  async (p_req, p_res) => {
    try {
      const _v_keyword = p_req.query.keyword;
      
      const _v_result = await eventService.compareChannels(_v_keyword);
      
      p_res.json(_v_result);
    } catch (p_error) {
      logger.error('채널 비교 API 에러:', p_error);
      p_res.status(500).json({
        success: false,
        message: p_error.message || '채널 비교 중 오류가 발생했습니다.',
      });
    }
  }
);

module.exports = router;


