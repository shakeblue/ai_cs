/**
 * BroadcastList Page
 * Main broadcast listing page with search, filters, and pagination
 */
import React, { useState } from 'react';
import {
  Container,
  Grid,
  Typography,
  Box,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Stack,
  Pagination,
  CircularProgress,
  Alert,
  Paper,
  Chip,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { useBroadcasts } from '../hooks/useBroadcasts';
import { useBrands } from '../hooks/useBrands';
import { useDebounce } from '../hooks/useDebounce';
import BroadcastCard from '../components/broadcasts/BroadcastCard';

// Dark theme colors
const DARK_COLORS = {
  background: '#0F1419',
  cardBg: '#1A1F2E',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
  },
  border: '#2D3748',
};

const BroadcastList = () => {
  const [page, setPage] = useState(1);
  const [searchInput, setSearchInput] = useState('');
  const [brand, setBrand] = useState('');
  const [status, setStatus] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [sortBy, setSortBy] = useState('date_desc');

  // Debounce search input
  const debouncedSearch = useDebounce(searchInput, 500);

  // Fetch brands
  const { brands, loading: brandsLoading } = useBrands();

  // Fetch broadcasts
  const { broadcasts, loading, error, pagination } = useBroadcasts({
    page,
    limit: 20,
    search: debouncedSearch,
    brand,
    status,
    startDate,
    endDate,
    sortBy,
  });

  const handlePageChange = (event, value) => {
    setPage(value);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleBrandChange = (event) => {
    setBrand(event.target.value);
    setPage(1); // Reset to first page
  };

  const handleStatusChange = (event) => {
    setStatus(event.target.value);
    setPage(1);
  };

  const handleStartDateChange = (event) => {
    setStartDate(event.target.value);
    setPage(1);
  };

  const handleEndDateChange = (event) => {
    setEndDate(event.target.value);
    setPage(1);
  };

  const handleSortChange = (event) => {
    setSortBy(event.target.value);
    setPage(1);
  };

  const handleClearFilters = () => {
    setSearchInput('');
    setBrand('');
    setStatus('');
    setStartDate('');
    setEndDate('');
    setSortBy('date_desc');
    setPage(1);
  };

  return (
    <Box sx={{ bgcolor: DARK_COLORS.background, minHeight: '100vh', py: 4 }}>
      <Container maxWidth="xl">
        {/* Header */}
        <Typography
          variant="h3"
          sx={{
            color: DARK_COLORS.text.primary,
            fontWeight: 700,
            mb: 1,
          }}
        >
          네이버 쇼핑 라이브 방송
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: DARK_COLORS.text.secondary,
            mb: 4,
          }}
        >
          수집된 방송 데이터를 검색하고 탐색하세요
        </Typography>

        {/* Search and Filters */}
        <Paper
          sx={{
            bgcolor: DARK_COLORS.cardBg,
            p: 3,
            mb: 4,
            borderRadius: 2,
          }}
        >
          <Stack spacing={3}>
            {/* Search Bar */}
            <TextField
              fullWidth
              placeholder="방송, 브랜드 또는 상품 검색..."
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon sx={{ color: DARK_COLORS.text.secondary }} />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: DARK_COLORS.background,
                  color: DARK_COLORS.text.primary,
                  '& fieldset': {
                    borderColor: DARK_COLORS.border,
                  },
                  '&:hover fieldset': {
                    borderColor: DARK_COLORS.text.secondary,
                  },
                },
              }}
            />

            {/* Filters Row */}
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <FormControl
                fullWidth
                size="small"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: DARK_COLORS.background,
                    color: DARK_COLORS.text.primary,
                    '& fieldset': {
                      borderColor: DARK_COLORS.border,
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: DARK_COLORS.text.secondary,
                  },
                }}
              >
                <InputLabel>브랜드</InputLabel>
                <Select
                  value={brand}
                  label="브랜드"
                  onChange={handleBrandChange}
                  disabled={brandsLoading}
                >
                  <MenuItem value="">모든 브랜드</MenuItem>
                  {brands.map((brandObj) => (
                    <MenuItem key={brandObj.id} value={brandObj.id}>
                      {brandObj.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl
                fullWidth
                size="small"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: DARK_COLORS.background,
                    color: DARK_COLORS.text.primary,
                    '& fieldset': {
                      borderColor: DARK_COLORS.border,
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: DARK_COLORS.text.secondary,
                  },
                }}
              >
                <InputLabel>상태</InputLabel>
                <Select value={status} label="상태" onChange={handleStatusChange}>
                  <MenuItem value="">모든 상태</MenuItem>
                  <MenuItem value="ONAIR">방송 중</MenuItem>
                  <MenuItem value="BLOCK">종료</MenuItem>
                  <MenuItem value="READY">예정</MenuItem>
                  <MenuItem value="OPENED">이용 가능</MenuItem>
                </Select>
              </FormControl>

              <FormControl
                fullWidth
                size="small"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: DARK_COLORS.background,
                    color: DARK_COLORS.text.primary,
                    '& fieldset': {
                      borderColor: DARK_COLORS.border,
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: DARK_COLORS.text.secondary,
                  },
                }}
              >
                <InputLabel>정렬</InputLabel>
                <Select value={sortBy} label="정렬" onChange={handleSortChange}>
                  <MenuItem value="date_desc">최신순</MenuItem>
                  <MenuItem value="date_asc">오래된순</MenuItem>
                  <MenuItem value="products_desc">상품 많은순</MenuItem>
                  <MenuItem value="coupons_desc">쿠폰 많은순</MenuItem>
                </Select>
              </FormControl>
            </Stack>

            {/* Date Range Filters */}
            <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
              <TextField
                fullWidth
                size="small"
                label="시작일"
                type="date"
                value={startDate}
                onChange={handleStartDateChange}
                InputLabelProps={{ shrink: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: DARK_COLORS.background,
                    color: DARK_COLORS.text.primary,
                    '& fieldset': {
                      borderColor: DARK_COLORS.border,
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: DARK_COLORS.text.secondary,
                  },
                }}
              />

              <TextField
                fullWidth
                size="small"
                label="종료일"
                type="date"
                value={endDate}
                onChange={handleEndDateChange}
                InputLabelProps={{ shrink: true }}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    bgcolor: DARK_COLORS.background,
                    color: DARK_COLORS.text.primary,
                    '& fieldset': {
                      borderColor: DARK_COLORS.border,
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: DARK_COLORS.text.secondary,
                  },
                }}
              />

              {(searchInput || brand || status || startDate || endDate || sortBy !== 'date_desc') && (
                <Chip
                  label="필터 초기화"
                  onClick={handleClearFilters}
                  sx={{
                    color: DARK_COLORS.text.primary,
                    borderColor: DARK_COLORS.text.secondary,
                    '&:hover': {
                      bgcolor: DARK_COLORS.cardBg,
                    },
                  }}
                  variant="outlined"
                />
              )}
            </Stack>
          </Stack>
        </Paper>

        {/* Stats */}
        {pagination && pagination.total > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" color={DARK_COLORS.text.secondary}>
              {pagination.total}개 중 {broadcasts.length}개 방송 표시
              {debouncedSearch && ` (검색어: "${debouncedSearch}")`}
            </Typography>
          </Box>
        )}

        {/* Loading State */}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
            <CircularProgress />
          </Box>
        )}

        {/* Error State */}
        {error && (
          <Alert severity="error" sx={{ mb: 4 }}>
            방송 로딩 오류: {error.message}
          </Alert>
        )}

        {/* Empty State */}
        {!loading && !error && broadcasts.length === 0 && (
          <Paper sx={{ bgcolor: DARK_COLORS.cardBg, p: 8, textAlign: 'center' }}>
            <Typography variant="h6" color={DARK_COLORS.text.primary} sx={{ mb: 2 }}>
              방송을 찾을 수 없습니다
            </Typography>
            <Typography variant="body2" color={DARK_COLORS.text.secondary}>
              {debouncedSearch || brand || status
                ? '필터나 검색어를 조정해 보세요'
                : '아직 방송 데이터가 없습니다'}
            </Typography>
          </Paper>
        )}

        {/* Broadcast Grid */}
        {!loading && broadcasts.length > 0 && (
          <>
            <Grid container spacing={3}>
              {broadcasts.map((broadcast) => (
                <Grid item xs={12} sm={6} md={4} lg={3} key={broadcast.id}>
                  <BroadcastCard broadcast={broadcast} />
                </Grid>
              ))}
            </Grid>

            {/* Pagination */}
            {pagination && pagination.pages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 6 }}>
                <Pagination
                  count={pagination.pages}
                  page={page}
                  onChange={handlePageChange}
                  color="primary"
                  size="large"
                  sx={{
                    '& .MuiPaginationItem-root': {
                      color: DARK_COLORS.text.primary,
                      borderColor: DARK_COLORS.border,
                    },
                    '& .Mui-selected': {
                      bgcolor: `${DARK_COLORS.cardBg} !important`,
                    },
                  }}
                />
              </Box>
            )}
          </>
        )}
      </Container>
    </Box>
  );
};

export default BroadcastList;
