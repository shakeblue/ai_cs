/**
 * 즐겨찾기 라우터
 * 즐겨찾기 관련 API 엔드포인트
 */

const express = require('express');
const router = express.Router();

const favoriteService = require('../services/favoriteService');
const { authenticate } = require('../middleware/auth');
const { validateFavoriteCreate } = require('../middleware/validator');
const logger = require('../config/logger');

/**
 * GET /api/favorites
 * 즐겨찾기 목록 조회
 */
router.get('/', authenticate, async (p_req, p_res) => {
  try {
    const _v_user_id = p_req.user.user_id;
    const _v_filters = {
      page: p_req.query.page,
      page_size: p_req.query.page_size,
    };
    
    const _v_result = await favoriteService.getFavorites(_v_user_id, _v_filters);
    
    p_res.json(_v_result);
  } catch (p_error) {
    logger.error('즐겨찾기 목록 조회 API 에러:', p_error);
    p_res.status(500).json({
      success: false,
      message: p_error.message || '즐겨찾기 목록 조회 중 오류가 발생했습니다.',
    });
  }
});

/**
 * POST /api/favorites
 * 즐겨찾기 추가
 */
router.post('/', authenticate, validateFavoriteCreate, async (p_req, p_res) => {
  try {
    const _v_user_id = p_req.user.user_id;
    const { event_id, memo } = p_req.body;
    
    const _v_result = await favoriteService.addFavorite(_v_user_id, event_id, memo);
    
    p_res.status(201).json(_v_result);
  } catch (p_error) {
    logger.error('즐겨찾기 추가 API 에러:', p_error);
    p_res.status(400).json({
      success: false,
      message: p_error.message || '즐겨찾기 추가 중 오류가 발생했습니다.',
    });
  }
});

/**
 * DELETE /api/favorites/:favorite_id
 * 즐겨찾기 삭제
 */
router.delete('/:favorite_id', authenticate, async (p_req, p_res) => {
  try {
    const _v_user_id = p_req.user.user_id;
    const _v_favorite_id = parseInt(p_req.params.favorite_id);
    
    const _v_result = await favoriteService.removeFavorite(_v_user_id, _v_favorite_id);
    
    p_res.json(_v_result);
  } catch (p_error) {
    logger.error('즐겨찾기 삭제 API 에러:', p_error);
    p_res.status(400).json({
      success: false,
      message: p_error.message || '즐겨찾기 삭제 중 오류가 발생했습니다.',
    });
  }
});

/**
 * PATCH /api/favorites/:favorite_id/memo
 * 즐겨찾기 메모 수정
 */
router.patch('/:favorite_id/memo', authenticate, async (p_req, p_res) => {
  try {
    const _v_user_id = p_req.user.user_id;
    const _v_favorite_id = parseInt(p_req.params.favorite_id);
    const { memo } = p_req.body;
    
    if (!memo && memo !== '') {
      return p_res.status(400).json({
        success: false,
        message: '메모 내용이 필요합니다.',
      });
    }
    
    const _v_result = await favoriteService.updateFavoriteMemo(_v_user_id, _v_favorite_id, memo);
    
    p_res.json(_v_result);
  } catch (p_error) {
    logger.error('즐겨찾기 메모 수정 API 에러:', p_error);
    p_res.status(400).json({
      success: false,
      message: p_error.message || '즐겨찾기 메모 수정 중 오류가 발생했습니다.',
    });
  }
});

module.exports = router;


