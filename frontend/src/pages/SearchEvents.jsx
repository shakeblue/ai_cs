/**
 * 프로모션 조회 페이지
 * 프로모션/이벤트 검색, 필터링, 상세 보기 기능
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Typography,
  Card,
  CardContent,
  CardActions,
  Chip,
  Pagination,
  CircularProgress,
  Alert,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Snackbar,
  Tooltip,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  ContentCopy as ContentCopyIcon,
  OpenInNew as OpenInNewIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import moment from 'moment';
import { searchEvents, getEventById, generateConsultationText, addFavorite } from '../api/services';
// Mock 데이터는 사용하지 않음 - 실제 수집 데이터만 사용
import { getRealCollectedEvents, getRealCollectedDetail } from '../mockData/realCollectedData';

const SearchEvents = () => {
  const navigate = useNavigate();
  
  // 저장된 상태 복원 (sessionStorage)
  const getSavedState = () => {
    try {
      const saved = sessionStorage.getItem('searchState');
      return saved ? JSON.parse(saved) : null;
    } catch (e) {
      return null;
    }
  };
  
  const savedState = getSavedState();
  
  // 상태 관리
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [events, setEvents] = useState(savedState?.events || []);
  const [totalPages, setTotalPages] = useState(savedState?.totalPages || 0);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  
  // 필터 상태 (저장된 상태가 있으면 복원)
  const [filters, setFilters] = useState(savedState?.filters || {
    channel: '',
    brand: '',  // 브랜드 필터 추가
    status: '',  // 기본값: 전체
    keyword: '',
    start_date: '',
    end_date: '',
    page: 0,
    page_size: 12,
    sort_by: 'start_date',
    sort_order: 'DESC',
  });
  
  // 검색 상태를 sessionStorage에 저장
  const saveSearchState = (filters, events, totalPages) => {
    try {
      sessionStorage.setItem('searchState', JSON.stringify({
        filters,
        events,
        totalPages,
        timestamp: Date.now()
      }));
    } catch (e) {
      console.error('검색 상태 저장 실패:', e);
    }
  };
  
  // 페이지 변경 시에도 검색 실행
  useEffect(() => {
    // 페이지가 변경되면 기존 검색 조건으로 재검색
    if (events.length > 0) {
      handleSearch();
    }
  }, [filters.page]);
  
  // 검색 실행 (Mock 데이터만 사용)
  const handleSearch = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // ✅ 실제 수집된 데이터만 사용 (Mock 데이터 제외)
      console.log('🔍 SearchEvents - 실제 수집 데이터 조회');
      console.log('   - 키워드:', filters.keyword || '(없음)');
      console.log('   - 플랫폼:', filters.channel || '(전체)');
      console.log('   - 브랜드:', filters.brand || '(전체)');
      console.log('   - 상태:', filters.status || '(전체)');
      
      // 실제 크롤링으로 수집된 모든 브랜드 라이브 방송 데이터
      let realCollectedEvents = getRealCollectedEvents();
      
      console.log('📦 전체 수집 데이터:', realCollectedEvents.length, '개');
      
      // 키워드 필터링 (키워드가 있을 때만)
      if (filters.keyword && filters.keyword.trim() !== '') {
        const keyword = filters.keyword.toLowerCase();
        realCollectedEvents = realCollectedEvents.filter(event => {
          const searchText = `${event.title} ${event.subtitle} ${event.description} ${event.channel_name}`.toLowerCase();
          return searchText.includes(keyword);
        });
        console.log('🔍 키워드 필터링 후:', realCollectedEvents.length, '개');
      }
      
      // 플랫폼 필터링
      if (filters.channel && filters.channel !== '') {
        realCollectedEvents = realCollectedEvents.filter(event => {
          return event.channel_code === filters.channel || event.channel_name.includes(filters.channel);
        });
        console.log('🏢 플랫폼 필터링 후:', realCollectedEvents.length, '개');
      }
      
      // 브랜드 필터링
      if (filters.brand && filters.brand !== '') {
        realCollectedEvents = realCollectedEvents.filter(event => {
          // 이벤트의 title이나 subtitle, tags에서 브랜드 검색
          const brandText = `${event.title} ${event.subtitle} ${(event.tags || []).join(' ')}`.toLowerCase();
          return brandText.includes(filters.brand.toLowerCase());
        });
        console.log('🏷️  브랜드 필터링 후:', realCollectedEvents.length, '개');
      }
      
      console.log('✅ 실제 수집 데이터 검색 결과:', realCollectedEvents.length, '개');
      
      let mockEvents = realCollectedEvents;
      
      // 상태 필터링 (전체/진행중/예정/종료)
      if (filters.status && filters.status !== '') {
        mockEvents = mockEvents.filter(event => {
          const eventStatus = event.status || '';
          
          if (filters.status === 'ACTIVE') {
            // 진행중
            return eventStatus === 'ACTIVE';
          } else if (filters.status === 'PENDING') {
            // 예정
            return eventStatus === 'PENDING' || eventStatus === 'SCHEDULED';
          } else if (filters.status === 'ENDED') {
            // 종료
            return eventStatus === 'ENDED' || eventStatus === 'COMPLETED';
          }
          
          return true;
        });
      }
      
      console.log(`🔍 상태 필터 적용: ${filters.status || '전체'} → ${mockEvents.length}개 결과`);
      
      setEvents(mockEvents);
      const newTotalPages = mockEvents.length > 0 ? 1 : 0;
      setTotalPages(newTotalPages);
      setError(null);  // 에러 메시지 제거
      
      // 검색 상태 저장 (상세보기 후 돌아올 때 복원용)
      saveSearchState(filters, mockEvents, newTotalPages);
      
    } catch (err) {
      setError(err.customMessage || '검색 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };
  
  // 필터 변경 핸들러
  const handleFilterChange = (field, value) => {
    setFilters(prev => ({
      ...prev,
      [field]: value,
      page: 0, // 필터 변경 시 첫 페이지로
    }));
  };
  
  // 페이지 변경
  const handlePageChange = (event, value) => {
    setFilters(prev => ({ ...prev, page: value - 1 }));
  };
  
  // 이벤트 상세보기
  const handleEventDetail = async (eventId) => {
    try {
      console.log('🔍 handleEventDetail - eventId:', eventId);
      
      // 현재 이벤트 정보 확인
      const currentEvent = events.find(e => e.event_id === eventId);
      console.log('📦 handleEventDetail - currentEvent:', currentEvent);
      
      if (!currentEvent) {
        showSnackbar('이벤트 정보를 찾을 수 없습니다.');
        return;
      }
      
      // 라이브 상세 정보가 있는 경우 상세 페이지로 이동
      if (currentEvent.is_live_detail) {
        console.log('✅ 라이브 상세 페이지로 이동:', `/live/${eventId}`);
        navigate(`/live/${eventId}`);
        return;
      }
      
      // 기존 이벤트는 다이얼로그로 표시 (이미 로드된 데이터 사용)
      setSelectedEvent(currentEvent);
      setDialogOpen(true);
      console.log('✅ 다이얼로그 표시:', currentEvent.title);
      
    } catch (err) {
      console.error('❌ handleEventDetail 오류:', err);
      showSnackbar('이벤트 정보를 불러올 수 없습니다.');
    }
  };
  
  // 상담 문구 생성 및 복사
  const handleGenerateText = async (eventId) => {
    try {
      // 현재 이벤트 정보로 상담 문구 생성 (Mock)
      const currentEvent = events.find(e => e.event_id === eventId);
      
      if (!currentEvent) {
        showSnackbar('이벤트 정보를 찾을 수 없습니다.');
        return;
      }
      
      // 간단한 상담 문구 생성
      const consultationText = `
[${currentEvent.channel_name}] ${currentEvent.title}

${currentEvent.benefit_summary || currentEvent.description}

기간: ${moment(currentEvent.start_date).format('YYYY-MM-DD')} ~ ${moment(currentEvent.end_date).format('YYYY-MM-DD')}

자세한 내용은 이벤트 페이지를 참고해주세요.
${currentEvent.event_url}
      `.trim();
      
      // 클립보드에 복사
      await navigator.clipboard.writeText(consultationText);
      showSnackbar('상담 문구가 클립보드에 복사되었습니다!');
      
    } catch (err) {
      console.error('❌ 상담 문구 복사 오류:', err);
      showSnackbar('상담 문구 복사에 실패했습니다.');
    }
  };
  
  // 즐겨찾기 추가 (Mock)
  const handleAddFavorite = async (eventId, eventTitle) => {
    try {
      // Mock: 로컬 스토리지에 저장
      const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
      
      // 이미 즐겨찾기에 있는지 확인
      if (favorites.includes(eventId)) {
        showSnackbar('이미 즐겨찾기에 추가된 이벤트입니다.');
        return;
      }
      
      // 즐겨찾기 추가
      favorites.push(eventId);
      localStorage.setItem('favorites', JSON.stringify(favorites));
      
      showSnackbar(`"${eventTitle}"이(가) 즐겨찾기에 추가되었습니다!`);
      console.log('✅ 즐겨찾기 추가:', eventId);
      
    } catch (err) {
      console.error('❌ 즐겨찾기 추가 오류:', err);
      showSnackbar('즐겨찾기 추가에 실패했습니다.');
    }
  };
  
  // 스낵바 표시
  const showSnackbar = (message) => {
    setSnackbarMessage(message);
    setSnackbarOpen(true);
  };
  
  // 상태 색상 매핑
  const getStatusColor = (status) => {
    switch (status) {
      case 'ACTIVE': return 'success';
      case 'PENDING': return 'info';
      case 'ENDED': return 'default';
      default: return 'default';
    }
  };
  
  // 상태 라벨 매핑
  const getStatusLabel = (status) => {
    switch (status) {
      case 'ACTIVE': return '진행중';
      case 'PENDING': return '예정';
      case 'ENDED': return '종료';
      default: return status;
    }
  };
  
  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* 페이지 헤더 */}
      <Box mb={4}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight="bold">
          프로모션 조회
        </Typography>
        <Typography variant="body2" color="text.secondary">
          진행 중인 프로모션/이벤트를 검색하고 상담 문구를 생성하세요
        </Typography>
      </Box>
      
      {/* 검색 필터 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          {/* 플랫폼 선택 (첫 번째) */}
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>플랫폼</InputLabel>
              <Select
                value={filters.channel}
                label="플랫폼"
                onChange={(e) => handleFilterChange('channel', e.target.value)}
              >
                <MenuItem value="">전체</MenuItem>
                <MenuItem value="NAVER">네이버</MenuItem>
                <MenuItem value="KAKAO">카카오</MenuItem>
                <MenuItem value="COUPANG">쿠팡</MenuItem>
                <MenuItem value="GRIP">그립</MenuItem>
                <MenuItem value="OLIVEYOUNG">올영</MenuItem>
                <MenuItem value="100LIVE">100라이브</MenuItem>
                <MenuItem value="MUSINSA">무신사</MenuItem>
                <MenuItem value="11ST">11번가</MenuItem>
                <MenuItem value="GMARKET">G마켓</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* 브랜드 선택 (두 번째) */}
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>브랜드</InputLabel>
              <Select
                value={filters.brand}
                label="브랜드"
                onChange={(e) => handleFilterChange('brand', e.target.value)}
              >
                <MenuItem value="">전체</MenuItem>
                <MenuItem value="설화수">설화수</MenuItem>
                <MenuItem value="라네즈">라네즈</MenuItem>
                <MenuItem value="아이오페">아이오페</MenuItem>
                <MenuItem value="헤라">헤라</MenuItem>
                <MenuItem value="에스트라">에스트라</MenuItem>
                <MenuItem value="이니스프리">이니스프리</MenuItem>
                <MenuItem value="해피바스">해피바스</MenuItem>
                <MenuItem value="바이탈뷰티">바이탈뷰티</MenuItem>
                <MenuItem value="프리메라">프리메라</MenuItem>
                <MenuItem value="오설록">오설록</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* 키워드 검색 (세 번째) */}
          <Grid item xs={12} sm={6} md={2}>
            <TextField
              fullWidth
              label="키워드 검색"
              placeholder="이벤트명, 제품명 등"
              value={filters.keyword}
              onChange={(e) => handleFilterChange('keyword', e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            />
          </Grid>
          
          {/* 상태 선택 (세 번째) */}
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>상태</InputLabel>
              <Select
                value={filters.status}
                label="상태"
                onChange={(e) => handleFilterChange('status', e.target.value)}
              >
                <MenuItem value="">전체</MenuItem>
                <MenuItem value="ACTIVE">진행중</MenuItem>
                <MenuItem value="PENDING">예정</MenuItem>
                <MenuItem value="ENDED">종료</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* 정렬 선택 (네 번째) */}
          <Grid item xs={12} sm={6} md={2}>
            <FormControl fullWidth>
              <InputLabel>정렬</InputLabel>
              <Select
                value={filters.sort_by}
                label="정렬"
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
              >
                <MenuItem value="start_date">시작일</MenuItem>
                <MenuItem value="end_date">종료일</MenuItem>
                <MenuItem value="created_at">등록일</MenuItem>
                <MenuItem value="discount_rate">할인율</MenuItem>
                <MenuItem value="favorite_count">인기도</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          {/* 검색 버튼 (다섯 번째) */}
          <Grid item xs={12} sm={12} md={2}>
            <Box display="flex" gap={1}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<SearchIcon />}
                onClick={handleSearch}
                disabled={loading}
              >
                검색
              </Button>
              <IconButton onClick={handleSearch} disabled={loading}>
                <RefreshIcon />
              </IconButton>
            </Box>
          </Grid>
        </Grid>
      </Paper>
      
      {/* 에러 메시지 */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      {/* 로딩 상태 */}
      {loading && (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      )}
      
      {/* 이벤트 목록 */}
      {!loading && events.length > 0 && (
        <>
          <Grid container spacing={3}>
            {events.map((event) => (
              <Grid item xs={12} sm={6} md={4} key={event.event_id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  {event.thumbnail_url && (
                    <Box
                      component="img"
                      src={event.thumbnail_url}
                      alt={event.title}
                      sx={{
                        height: 180,
                        objectFit: 'cover',
                        backgroundColor: '#f5f5f5',
                      }}
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                  )}
                  
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box display="flex" alignItems="center" gap={1} mb={1}>
                      <Chip
                        label={event.channel_name}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Chip
                        label={getStatusLabel(event.status)}
                        size="small"
                        color={getStatusColor(event.status)}
                      />
                      {event.discount_rate && (
                        <Chip
                          label={`${event.discount_rate}% 할인`}
                          size="small"
                          color="error"
                        />
                      )}
                    </Box>
                    
                    <Typography variant="h6" gutterBottom noWrap>
                      {event.title}
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {event.benefit_summary}
                    </Typography>
                    
                    <Box mt={2}>
                      <Typography variant="caption" color="text.secondary">
                        기간: {moment(event.start_date).format('YYYY-MM-DD')} ~ {moment(event.end_date).format('YYYY-MM-DD')}
                      </Typography>
                    </Box>
                  </CardContent>
                  
                  <CardActions>
                    <Button
                      size="small"
                      onClick={() => handleEventDetail(event.event_id)}
                    >
                      상세보기
                    </Button>
                    <Tooltip title="상담 문구 복사">
                      <IconButton
                        size="small"
                        onClick={() => handleGenerateText(event.event_id)}
                      >
                        <ContentCopyIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="즐겨찾기 추가">
                      <IconButton
                        size="small"
                        onClick={() => handleAddFavorite(event.event_id, event.title)}
                      >
                        <FavoriteBorderIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="이벤트 페이지 열기">
                      <IconButton
                        size="small"
                        component="a"
                        href={event.event_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        <OpenInNewIcon fontSize="small" />
                      </IconButton>
                    </Tooltip>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          {/* 페이지네이션 */}
          <Box display="flex" justifyContent="center" mt={4}>
            <Pagination
              count={totalPages}
              page={filters.page + 1}
              onChange={handlePageChange}
              color="primary"
              size="large"
            />
          </Box>
        </>
      )}
      
      {/* 결과 없음 */}
      {!loading && events.length === 0 && (
        <Box textAlign="center" py={8}>
          <Typography variant="h6" color="text.secondary">
            검색 결과가 없습니다.
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={1}>
            다른 검색 조건을 시도해보세요.
          </Typography>
        </Box>
      )}
      
      {/* 이벤트 상세 다이얼로그 */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        {selectedEvent && (
          <>
            <DialogTitle>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography variant="h6">{selectedEvent.title}</Typography>
                <Chip label={selectedEvent.channel_name} color="primary" />
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              {selectedEvent.image_url && (
                <Box
                  component="img"
                  src={selectedEvent.image_url}
                  alt={selectedEvent.title}
                  sx={{
                    width: '100%',
                    maxHeight: 300,
                    objectFit: 'contain',
                    mb: 2,
                  }}
                />
              )}
              
              <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                혜택 내용
              </Typography>
              <Typography variant="body1" paragraph>
                {selectedEvent.benefit_detail || selectedEvent.benefit_summary}
              </Typography>
              
              {selectedEvent.target_products && (
                <>
                  <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                    대상 제품
                  </Typography>
                  <Typography variant="body2" paragraph>
                    {selectedEvent.target_products}
                  </Typography>
                </>
              )}
              
              {selectedEvent.conditions && (
                <>
                  <Typography variant="subtitle1" gutterBottom fontWeight="bold">
                    유의사항
                  </Typography>
                  <Typography variant="body2" paragraph>
                    {selectedEvent.conditions}
                  </Typography>
                </>
              )}
              
              <Box mt={2}>
                <Typography variant="caption" color="text.secondary">
                  기간: {moment(selectedEvent.start_date).format('YYYY-MM-DD HH:mm')} ~ {moment(selectedEvent.end_date).format('YYYY-MM-DD HH:mm')}
                </Typography>
              </Box>
            </DialogContent>
            <DialogActions>
              <Button
                startIcon={<ContentCopyIcon />}
                onClick={() => handleGenerateText(selectedEvent.event_id)}
              >
                상담 문구 복사
              </Button>
              <Button
                startIcon={<FavoriteIcon />}
                onClick={() => handleAddFavorite(selectedEvent.event_id, selectedEvent.title)}
              >
                즐겨찾기
              </Button>
              <Button
                variant="contained"
                startIcon={<OpenInNewIcon />}
                component="a"
                href={selectedEvent.event_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                이벤트 페이지 보기
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
      
      {/* 스낵바 알림 */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Container>
  );
};

export default SearchEvents;


