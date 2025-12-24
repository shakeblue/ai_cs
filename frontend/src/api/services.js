/**
 * API 서비스 함수
 * 백엔드 API 호출을 위한 함수들
 */

import axios from './axios';

// ============================================================================
// 인증 관련 API
// ============================================================================

/**
 * 로그인
 * @param {string} username - 사용자명
 * @param {string} password - 비밀번호
 * @returns {Promise} - 로그인 결과
 */
export const login = async (username, password) => {
  const response = await axios.post('/auth/login', { username, password });
  return response.data;
};

/**
 * 현재 사용자 정보 조회
 * @returns {Promise} - 사용자 정보
 */
export const getCurrentUser = async () => {
  const response = await axios.get('/auth/me');
  return response.data;
};

/**
 * 토큰 검증
 * @returns {Promise} - 검증 결과
 */
export const verifyToken = async () => {
  const response = await axios.get('/auth/verify');
  return response.data;
};

// ============================================================================
// 대시보드 API
// ============================================================================

/**
 * 대시보드 전체 데이터 조회
 * @returns {Promise} - 대시보드 데이터
 */
export const getDashboardData = async () => {
  const response = await axios.get('/dashboard');
  return response.data;
};

/**
 * 통계 요약 정보 조회
 * @returns {Promise} - 통계 데이터
 */
export const getDashboardStats = async () => {
  const response = await axios.get('/dashboard/stats');
  return response.data;
};

/**
 * 긴급 이벤트 목록 조회 (곧 종료되는 이벤트)
 * @returns {Promise} - 긴급 이벤트 목록
 */
export const getUrgentEvents = async () => {
  const response = await axios.get('/dashboard/urgent');
  return response.data;
};

/**
 * 인기 이벤트 목록 조회
 * @returns {Promise} - 인기 이벤트 목록
 */
export const getPopularEvents = async () => {
  const response = await axios.get('/dashboard/popular');
  return response.data;
};

// ============================================================================
// 이벤트 API
// ============================================================================

/**
 * 이벤트 검색
 * @param {Object} filters - 필터 조건
 * @returns {Promise} - 이벤트 목록
 */
export const searchEvents = async (filters = {}) => {
  const response = await axios.get('/events/search', { params: filters });
  return response.data;
};

/**
 * 이벤트 상세 조회
 * @param {string} eventId - 이벤트 ID
 * @returns {Promise} - 이벤트 상세 정보
 */
export const getEventById = async (eventId) => {
  const response = await axios.get(`/events/${eventId}`);
  return response.data;
};

/**
 * 상담용 문구 생성
 * @param {string} eventId - 이벤트 ID
 * @returns {Promise} - 생성된 상담 문구
 */
export const generateConsultationText = async (eventId) => {
  const response = await axios.get(`/events/${eventId}/consultation-text`);
  return response.data;
};

/**
 * 채널 비교
 * @param {string} keyword - 검색 키워드
 * @returns {Promise} - 채널별 비교 결과
 */
export const compareChannels = async (keyword) => {
  const response = await axios.get('/events/compare/channels', {
    params: { keyword },
  });
  return response.data;
};

// ============================================================================
// 즐겨찾기 API
// ============================================================================

/**
 * 즐겨찾기 목록 조회
 * @param {Object} params - 페이지네이션 파라미터
 * @returns {Promise} - 즐겨찾기 목록
 */
export const getFavorites = async (params = {}) => {
  const response = await axios.get('/favorites', { params });
  return response.data;
};

/**
 * 즐겨찾기 추가
 * @param {string} eventId - 이벤트 ID
 * @param {string} memo - 메모 (선택)
 * @returns {Promise} - 추가 결과
 */
export const addFavorite = async (eventId, memo = null) => {
  const response = await axios.post('/favorites', { event_id: eventId, memo });
  return response.data;
};

/**
 * 즐겨찾기 삭제
 * @param {number} favoriteId - 즐겨찾기 ID
 * @returns {Promise} - 삭제 결과
 */
export const removeFavorite = async (favoriteId) => {
  const response = await axios.delete(`/favorites/${favoriteId}`);
  return response.data;
};

/**
 * 즐겨찾기 메모 수정
 * @param {number} favoriteId - 즐겨찾기 ID
 * @param {string} memo - 새 메모
 * @returns {Promise} - 수정 결과
 */
export const updateFavoriteMemo = async (favoriteId, memo) => {
  const response = await axios.patch(`/favorites/${favoriteId}/memo`, { memo });
  return response.data;
};

export default {
  // 인증
  login,
  getCurrentUser,
  verifyToken,
  
  // 대시보드
  getDashboardData,
  getDashboardStats,
  getUrgentEvents,
  getPopularEvents,
  
  // 이벤트
  searchEvents,
  getEventById,
  generateConsultationText,
  compareChannels,
  
  // 즐겨찾기
  getFavorites,
  addFavorite,
  removeFavorite,
  updateFavoriteMemo,
};


