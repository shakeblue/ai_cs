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
  const [sortBy, setSortBy] = useState('date_desc');

  // Debounce search input
  const debouncedSearch = useDebounce(searchInput, 500);

  // Fetch broadcasts
  const { broadcasts, loading, error, pagination } = useBroadcasts({
    page,
    limit: 20,
    search: debouncedSearch,
    brand,
    status,
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

  const handleSortChange = (event) => {
    setSortBy(event.target.value);
    setPage(1);
  };

  const handleClearFilters = () => {
    setSearchInput('');
    setBrand('');
    setStatus('');
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
          Naver Shopping Live Broadcasts
        </Typography>
        <Typography
          variant="body1"
          sx={{
            color: DARK_COLORS.text.secondary,
            mb: 4,
          }}
        >
          Browse and search through collected broadcast data
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
              placeholder="Search broadcasts, brands, or products..."
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
                <InputLabel>Brand</InputLabel>
                <Select value={brand} label="Brand" onChange={handleBrandChange}>
                  <MenuItem value="">All Brands</MenuItem>
                  <MenuItem value="아이오페">아이오페</MenuItem>
                  <MenuItem value="설화수">설화수</MenuItem>
                  <MenuItem value="라네즈">라네즈</MenuItem>
                  <MenuItem value="이니스프리">이니스프리</MenuItem>
                  <MenuItem value="헤라">헤라</MenuItem>
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
                <InputLabel>Status</InputLabel>
                <Select value={status} label="Status" onChange={handleStatusChange}>
                  <MenuItem value="">All Status</MenuItem>
                  <MenuItem value="ONAIR">On Air</MenuItem>
                  <MenuItem value="BLOCK">Ended</MenuItem>
                  <MenuItem value="READY">Scheduled</MenuItem>
                  <MenuItem value="OPENED">Available</MenuItem>
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
                <InputLabel>Sort By</InputLabel>
                <Select value={sortBy} label="Sort By" onChange={handleSortChange}>
                  <MenuItem value="date_desc">Newest First</MenuItem>
                  <MenuItem value="date_asc">Oldest First</MenuItem>
                  <MenuItem value="products_desc">Most Products</MenuItem>
                  <MenuItem value="coupons_desc">Most Coupons</MenuItem>
                </Select>
              </FormControl>

              {(searchInput || brand || status || sortBy !== 'date_desc') && (
                <Chip
                  label="Clear Filters"
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
              Showing {broadcasts.length} of {pagination.total} broadcasts
              {debouncedSearch && ` for "${debouncedSearch}"`}
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
            Error loading broadcasts: {error.message}
          </Alert>
        )}

        {/* Empty State */}
        {!loading && !error && broadcasts.length === 0 && (
          <Paper sx={{ bgcolor: DARK_COLORS.cardBg, p: 8, textAlign: 'center' }}>
            <Typography variant="h6" color={DARK_COLORS.text.primary} sx={{ mb: 2 }}>
              No broadcasts found
            </Typography>
            <Typography variant="body2" color={DARK_COLORS.text.secondary}>
              {debouncedSearch || brand || status
                ? 'Try adjusting your filters or search query'
                : 'No broadcast data available yet'}
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
