/**
 * 인증 라우터
 * 로그인, 회원가입 등 인증 관련 API 엔드포인트
 */

const express = require('express');
const router = express.Router();

const userService = require('../services/userService');
const { authenticate, authorize } = require('../middleware/auth');
const { validateLogin, validateUserCreate } = require('../middleware/validator');
const { loginLimiter } = require('../middleware/rateLimit');
const logger = require('../config/logger');

/**
 * POST /api/auth/login
 * 로그인
 */
router.post('/login', loginLimiter, validateLogin, async (p_req, p_res) => {
  try {
    const { username, password } = p_req.body;
    
    const _v_result = await userService.login(username, password);
    
    p_res.json(_v_result);
  } catch (p_error) {
    logger.error('로그인 API 에러:', p_error);
    p_res.status(401).json({
      success: false,
      message: p_error.message || '로그인에 실패했습니다.',
    });
  }
});

/**
 * POST /api/auth/register
 * 사용자 등록 (관리자만 가능)
 */
router.post(
  '/register',
  authenticate,
  authorize(['ADMIN']),
  validateUserCreate,
  async (p_req, p_res) => {
    try {
      const _v_user_data = {
        username: p_req.body.username,
        password: p_req.body.password,
        full_name: p_req.body.full_name,
        email: p_req.body.email,
        phone: p_req.body.phone,
        role: p_req.body.role,
        department: p_req.body.department,
        team: p_req.body.team,
      };
      
      const _v_result = await userService.createUser(_v_user_data);
      
      p_res.status(201).json(_v_result);
    } catch (p_error) {
      logger.error('사용자 등록 API 에러:', p_error);
      p_res.status(400).json({
        success: false,
        message: p_error.message || '사용자 등록에 실패했습니다.',
      });
    }
  }
);

/**
 * GET /api/auth/me
 * 현재 로그인한 사용자 정보 조회
 */
router.get('/me', authenticate, async (p_req, p_res) => {
  try {
    const _v_user = await userService.getUserById(p_req.user.user_id);
    
    if (!_v_user) {
      return p_res.status(404).json({
        success: false,
        message: '사용자 정보를 찾을 수 없습니다.',
      });
    }
    
    p_res.json({
      success: true,
      data: _v_user,
    });
  } catch (p_error) {
    logger.error('사용자 정보 조회 API 에러:', p_error);
    p_res.status(500).json({
      success: false,
      message: '사용자 정보 조회 중 오류가 발생했습니다.',
    });
  }
});

/**
 * GET /api/auth/verify
 * 토큰 유효성 검증
 */
router.get('/verify', authenticate, (p_req, p_res) => {
  p_res.json({
    success: true,
    message: '유효한 토큰입니다.',
    data: {
      user_id: p_req.user.user_id,
      username: p_req.user.username,
      role: p_req.user.role,
    },
  });
});

module.exports = router;


