/**
 * 로그인 페이지
 * 사용자 인증 처리
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
} from '@mui/material';
import { Login as LoginIcon } from '@mui/icons-material';
import useAuthStore from '../store/authStore';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuthStore();
  
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // 입력 검증
    if (!username || !password) {
      setError('사용자명과 비밀번호를 입력해주세요.');
      return;
    }
    
    // 로그인 시도
    const result = await login(username, password);
    
    if (result.success) {
      navigate('/');
    } else {
      setError(result.message || '로그인에 실패했습니다.');
    }
  };
  
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="sm">
        <Paper elevation={3} sx={{ p: 4 }}>
          <Box textAlign="center" mb={4}>
            <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
              화장품 상담 시스템
            </Typography>
            <Typography variant="body2" color="text.secondary">
              로그인하여 시스템을 사용하세요
            </Typography>
          </Box>
          
          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="사용자명"
              margin="normal"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading}
              autoFocus
            />
            
            <TextField
              fullWidth
              label="비밀번호"
              type="password"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />
            
            <Button
              fullWidth
              variant="contained"
              size="large"
              type="submit"
              startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <LoginIcon />}
              disabled={isLoading}
              sx={{ mt: 3 }}
            >
              {isLoading ? '로그인 중...' : '로그인'}
            </Button>
          </form>
          
          <Box mt={3}>
            <Typography variant="caption" color="text.secondary" align="center" display="block">
              테스트 계정: agent001 / agent123
            </Typography>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default LoginPage;


