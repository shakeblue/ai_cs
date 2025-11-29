/**
 * 인증 상태 관리 스토어 (Zustand)
 * 사용자 인증 정보 및 로그인/로그아웃 처리
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { login as apiLogin, getCurrentUser, verifyToken } from '../api/services';

// 인증 스토어 생성
const useAuthStore = create(
  persist(
    (set, get) => ({
      // 상태
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      // 로그인
      login: async (username, password) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await apiLogin(username, password);
          
          if (response.success) {
            const { user, token } = response.data;
            
            // 토큰 저장
            localStorage.setItem('auth_token', token);
            localStorage.setItem('user_info', JSON.stringify(user));
            
            // 상태 업데이트
            set({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              error: null,
            });
            
            return { success: true };
          } else {
            set({ isLoading: false, error: response.message });
            return { success: false, message: response.message };
          }
        } catch (error) {
          const errorMessage = error.customMessage || '로그인에 실패했습니다.';
          set({ isLoading: false, error: errorMessage });
          return { success: false, message: errorMessage };
        }
      },
      
      // 로그아웃
      logout: () => {
        // 토큰 제거
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_info');
        
        // 상태 초기화
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null,
        });
      },
      
      // 사용자 정보 새로고침
      refreshUser: async () => {
        try {
          const response = await getCurrentUser();
          
          if (response.success) {
            set({ user: response.data });
          }
        } catch (error) {
          console.error('사용자 정보 새로고침 실패:', error);
        }
      },
      
      // 토큰 검증
      validateToken: async () => {
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          get().logout();
          return false;
        }
        
        try {
          const response = await verifyToken();
          
          if (response.success) {
            // 토큰 유효
            return true;
          } else {
            // 토큰 무효
            get().logout();
            return false;
          }
        } catch (error) {
          // 검증 실패
          get().logout();
          return false;
        }
      },
      
      // 초기화 (새로고침 시 토큰 검증)
      initialize: async () => {
        const token = localStorage.getItem('auth_token');
        const userInfo = localStorage.getItem('user_info');
        
        if (token && userInfo) {
          try {
            // 토큰 검증
            const isValid = await get().validateToken();
            
            if (isValid) {
              set({
                user: JSON.parse(userInfo),
                token,
                isAuthenticated: true,
              });
            }
          } catch (error) {
            console.error('초기화 실패:', error);
            get().logout();
          }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export default useAuthStore;


