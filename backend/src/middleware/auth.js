/**
 * 인증 미들웨어
 * JWT 토큰 검증 및 사용자 인증 처리
 */

const jwt = require('jsonwebtoken');
const logger = require('../config/logger');

// JWT 시크릿 키 (환경변수에서 로드)
const _v_jwt_secret = process.env.JWT_SECRET || 'your_jwt_secret_key_change_in_production';

/**
 * JWT 토큰 생성
 * @param {Object} p_payload - 토큰에 포함할 데이터
 * @param {string} p_expires_in - 만료 시간 (예: '24h', '7d')
 * @returns {string} - JWT 토큰
 */
const generateToken = (p_payload, p_expires_in = '24h') => {
  try {
    const _v_token = jwt.sign(p_payload, _v_jwt_secret, {
      expiresIn: p_expires_in,
      issuer: 'cosmetic-consultation-system',
    });
    
    logger.debug('JWT 토큰 생성:', { userId: p_payload.user_id });
    return _v_token;
  } catch (p_error) {
    logger.error('JWT 토큰 생성 실패:', p_error);
    throw new Error('토큰 생성에 실패했습니다.');
  }
};

/**
 * JWT 토큰 검증
 * @param {string} p_token - 검증할 토큰
 * @returns {Object} - 디코딩된 페이로드
 */
const verifyToken = (p_token) => {
  try {
    const _v_decoded = jwt.verify(p_token, _v_jwt_secret);
    return _v_decoded;
  } catch (p_error) {
    if (p_error.name === 'TokenExpiredError') {
      throw new Error('토큰이 만료되었습니다.');
    } else if (p_error.name === 'JsonWebTokenError') {
      throw new Error('유효하지 않은 토큰입니다.');
    }
    throw new Error('토큰 검증에 실패했습니다.');
  }
};

/**
 * 인증 미들웨어
 * 요청 헤더에서 JWT 토큰을 추출하고 검증
 */
const authenticate = (p_req, p_res, p_next) => {
  try {
    // Authorization 헤더 확인
    const _v_auth_header = p_req.headers.authorization;
    
    if (!_v_auth_header) {
      return p_res.status(401).json({
        success: false,
        message: '인증 토큰이 제공되지 않았습니다.',
      });
    }
    
    // Bearer 토큰 추출
    const _v_parts = _v_auth_header.split(' ');
    
    if (_v_parts.length !== 2 || _v_parts[0] !== 'Bearer') {
      return p_res.status(401).json({
        success: false,
        message: '잘못된 토큰 형식입니다. (Bearer 토큰 사용 필요)',
      });
    }
    
    const _v_token = _v_parts[1];
    
    // 토큰 검증
    const _v_decoded = verifyToken(_v_token);
    
    // 요청 객체에 사용자 정보 추가
    p_req.user = {
      user_id: _v_decoded.user_id,
      username: _v_decoded.username,
      role: _v_decoded.role,
    };
    
    logger.debug('사용자 인증 성공:', {
      userId: _v_decoded.user_id,
      username: _v_decoded.username,
    });
    
    p_next();
  } catch (p_error) {
    logger.warn('인증 실패:', p_error.message);
    return p_res.status(401).json({
      success: false,
      message: p_error.message,
    });
  }
};

/**
 * 권한 검증 미들웨어
 * @param {Array<string>} p_allowed_roles - 허용된 역할 목록
 * @returns {Function} - Express 미들웨어 함수
 */
const authorize = (p_allowed_roles = []) => {
  return (p_req, p_res, p_next) => {
    // 인증 정보 확인
    if (!p_req.user) {
      return p_res.status(401).json({
        success: false,
        message: '인증이 필요합니다.',
      });
    }
    
    // 역할 확인
    if (p_allowed_roles.length > 0 && !p_allowed_roles.includes(p_req.user.role)) {
      logger.warn('권한 부족:', {
        userId: p_req.user.user_id,
        requiredRoles: p_allowed_roles,
        userRole: p_req.user.role,
      });
      
      return p_res.status(403).json({
        success: false,
        message: '접근 권한이 없습니다.',
      });
    }
    
    p_next();
  };
};

/**
 * 선택적 인증 미들웨어
 * 토큰이 있으면 검증하지만, 없어도 요청 진행
 */
const optionalAuth = (p_req, p_res, p_next) => {
  try {
    const _v_auth_header = p_req.headers.authorization;
    
    if (_v_auth_header) {
      const _v_parts = _v_auth_header.split(' ');
      
      if (_v_parts.length === 2 && _v_parts[0] === 'Bearer') {
        const _v_token = _v_parts[1];
        const _v_decoded = verifyToken(_v_token);
        
        p_req.user = {
          user_id: _v_decoded.user_id,
          username: _v_decoded.username,
          role: _v_decoded.role,
        };
      }
    }
    
    p_next();
  } catch (p_error) {
    // 토큰이 유효하지 않아도 계속 진행
    logger.debug('선택적 인증 실패 (계속 진행):', p_error.message);
    p_next();
  }
};

module.exports = {
  generateToken,
  verifyToken,
  authenticate,
  authorize,
  optionalAuth,
};


