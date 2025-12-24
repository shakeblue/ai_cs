import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Chip,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  Stack,
  IconButton,
  Breadcrumbs,
  Link,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  alpha,
} from '@mui/material';
import {
  LocalOffer,
  CardGiftcard,
  Home,
  NavigateNext,
  Refresh,
  OpenInNew,
  Close,
} from '@mui/icons-material';
import axios from 'axios';

// API 기본 URL
const getApiBaseUrl = () => {
  const baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:3001';
  return baseUrl.replace(/\/api\/?$/, '');
};
const API_BASE_URL = getApiBaseUrl();

// Dark theme colors (matching existing pages)
const DARK_COLORS = {
  background: '#0F1419',
  cardBg: '#1A1F2E',
  cardHoverBg: '#252B3B',
  primary: '#6366F1',
  secondary: '#EC4899',
  success: '#10B981',
  warning: '#F59E0B',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
    disabled: '#6B7280',
  },
  border: '#2D3748',
};

const NaverSmartStoreEvents = () => {
  // State management
  const [events, setEvents] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedBrand, setSelectedBrand] = useState('');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Fetch brands on mount
  useEffect(() => {
    fetchBrands();
    fetchEvents();
  }, []);

  /**
   * Fetch unique brands
   */
  const fetchBrands = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/naver-smartstore-events/brands/list`);
      if (response.data.success) {
        setBrands(response.data.data);
      }
    } catch (err) {
      console.error('Error fetching brands:', err);
    }
  };

  /**
   * Fetch events with optional brand filter
   */
  const fetchEvents = async (brand = '') => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      if (brand) {
        params.append('brand_name', brand);
      }
      params.append('limit', '50');
      params.append('sort_by', 'created_at');
      params.append('sort_order', 'desc');

      const response = await axios.get(
        `${API_BASE_URL}/api/naver-smartstore-events?${params.toString()}`
      );

      if (response.data.success) {
        setEvents(response.data.data);
      } else {
        setError('이벤트를 불러올 수 없습니다.');
      }
    } catch (err) {
      console.error('Error fetching events:', err);
      setError('이벤트 조회 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle brand filter change
   */
  const handleBrandChange = (event) => {
    const brand = event.target.value;
    setSelectedBrand(brand);
    fetchEvents(brand);
  };

  /**
   * Handle refresh
   */
  const handleRefresh = () => {
    fetchEvents(selectedBrand);
  };

  /**
   * Open event detail dialog
   */
  const handleEventClick = (event) => {
    setSelectedEvent(event);
    setDialogOpen(true);
  };

  /**
   * Close dialog
   */
  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedEvent(null);
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: DARK_COLORS.background, pb: 6 }}>
      <Container maxWidth="xl" sx={{ pt: 4 }}>
        {/* Header */}
        <Box mb={4}>
          <Breadcrumbs
            separator={<NavigateNext fontSize="small" />}
            sx={{ mb: 2 }}
          >
            <Link
              color="inherit"
              href="/"
              sx={{
                display: 'flex',
                alignItems: 'center',
                textDecoration: 'none',
                color: DARK_COLORS.text.secondary,
              }}
            >
              <Home sx={{ mr: 0.5 }} fontSize="small" />
              홈
            </Link>
            <Typography color={DARK_COLORS.text.primary}>
              네이버 스마트스토어 이벤트
            </Typography>
          </Breadcrumbs>

          <Typography
            variant="h3"
            component="h1"
            gutterBottom
            sx={{
              fontWeight: 800,
              background: `linear-gradient(135deg, ${DARK_COLORS.primary} 0%, ${DARK_COLORS.secondary} 100%)`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 1,
            }}
          >
            네이버 스마트스토어 이벤트
          </Typography>
          <Typography
            variant="h6"
            sx={{
              color: DARK_COLORS.text.secondary,
              fontWeight: 400,
            }}
          >
            OCR 기술로 추출한 최신 이벤트 정보
          </Typography>
        </Box>

        {/* Filter Bar */}
        <Paper
          sx={{
            p: 3,
            mb: 4,
            bgcolor: DARK_COLORS.cardBg,
            border: `1px solid ${DARK_COLORS.border}`,
            borderRadius: 2,
          }}
        >
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6} md={4}>
              <FormControl fullWidth>
                <InputLabel sx={{ color: DARK_COLORS.text.secondary }}>
                  브랜드
                </InputLabel>
                <Select
                  value={selectedBrand}
                  label="브랜드"
                  onChange={handleBrandChange}
                  sx={{
                    color: DARK_COLORS.text.primary,
                    '& .MuiOutlinedInput-notchedOutline': {
                      borderColor: DARK_COLORS.border,
                    },
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: DARK_COLORS.primary,
                    },
                    '& .MuiSvgIcon-root': {
                      color: DARK_COLORS.text.secondary,
                    },
                  }}
                >
                  <MenuItem value="">전체</MenuItem>
                  {brands.map((brand) => (
                    <MenuItem key={brand} value={brand}>
                      {brand}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6} md={2}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<Refresh />}
                onClick={handleRefresh}
                disabled={loading}
                sx={{
                  bgcolor: DARK_COLORS.primary,
                  '&:hover': {
                    bgcolor: alpha(DARK_COLORS.primary, 0.8),
                  },
                }}
              >
                새로고침
              </Button>
            </Grid>
          </Grid>
        </Paper>

        {/* Error */}
        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Loading */}
        {loading && (
          <Box display="flex" justifyContent="center" my={6}>
            <CircularProgress sx={{ color: DARK_COLORS.primary }} />
          </Box>
        )}

        {/* Events Grid */}
        {!loading && events.length > 0 && (
          <Grid container spacing={3}>
            {events.map((event) => (
              <Grid item xs={12} sm={6} md={4} key={event.id}>
                <Card
                  sx={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    bgcolor: DARK_COLORS.cardBg,
                    border: `1px solid ${DARK_COLORS.border}`,
                    borderRadius: 2,
                    transition: 'all 0.3s',
                    cursor: 'pointer',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: `0 12px 48px ${alpha(DARK_COLORS.primary, 0.3)}`,
                      border: `1px solid ${alpha(DARK_COLORS.primary, 0.5)}`,
                    },
                  }}
                  onClick={() => handleEventClick(event)}
                >
                  {/* Thumbnail */}
                  {event.image_urls && event.image_urls.length > 0 && (
                    <CardMedia
                      component="img"
                      height="200"
                      image={event.image_urls[0]}
                      alt={event.event_title}
                      sx={{ objectFit: 'cover', bgcolor: DARK_COLORS.cardHoverBg }}
                    />
                  )}

                  <CardContent sx={{ flexGrow: 1, p: 3 }}>
                    {/* Brand & Platform */}
                    <Box display="flex" gap={1} mb={2}>
                      <Chip
                        label={event.brand_name || 'Unknown'}
                        size="small"
                        sx={{
                          bgcolor: alpha(DARK_COLORS.primary, 0.15),
                          color: DARK_COLORS.primary,
                          fontWeight: 600,
                        }}
                      />
                      <Chip
                        label={event.platform_name}
                        size="small"
                        sx={{
                          bgcolor: alpha(DARK_COLORS.secondary, 0.15),
                          color: DARK_COLORS.secondary,
                          fontWeight: 600,
                        }}
                      />
                    </Box>

                    {/* Event Title */}
                    <Typography
                      variant="h6"
                      gutterBottom
                      sx={{
                        color: DARK_COLORS.text.primary,
                        fontWeight: 700,
                        mb: 1.5,
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                      }}
                    >
                      {event.event_title || '제목 없음'}
                    </Typography>

                    {/* Event Date */}
                    {event.event_date && (
                      <Typography
                        variant="body2"
                        sx={{
                          color: DARK_COLORS.text.secondary,
                          mb: 2,
                        }}
                      >
                        기간: {event.event_date}
                      </Typography>
                    )}

                    {/* Benefits Count */}
                    <Box display="flex" gap={2}>
                      {event.benefits_by_purchase_amount &&
                        event.benefits_by_purchase_amount.length > 0 && (
                          <Chip
                            icon={<LocalOffer />}
                            label={`혜택 ${event.benefits_by_purchase_amount.length}개`}
                            size="small"
                            sx={{
                              bgcolor: alpha(DARK_COLORS.success, 0.15),
                              color: DARK_COLORS.success,
                            }}
                          />
                        )}
                      {event.coupon_benefits &&
                        event.coupon_benefits.length > 0 && (
                          <Chip
                            icon={<CardGiftcard />}
                            label={`쿠폰 ${event.coupon_benefits.length}개`}
                            size="small"
                            sx={{
                              bgcolor: alpha(DARK_COLORS.warning, 0.15),
                              color: DARK_COLORS.warning,
                            }}
                          />
                        )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* No Results */}
        {!loading && events.length === 0 && (
          <Box textAlign="center" py={10}>
            <Typography variant="h6" sx={{ color: DARK_COLORS.text.secondary }}>
              이벤트가 없습니다.
            </Typography>
          </Box>
        )}
      </Container>

      {/* Event Detail Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            bgcolor: DARK_COLORS.cardBg,
            border: `1px solid ${DARK_COLORS.border}`,
            borderRadius: 2,
          },
        }}
      >
        {selectedEvent && (
          <>
            <DialogTitle
              sx={{
                borderBottom: `1px solid ${DARK_COLORS.border}`,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <Typography variant="h6" sx={{ color: DARK_COLORS.text.primary }}>
                {selectedEvent.event_title}
              </Typography>
              <IconButton onClick={handleCloseDialog} size="small">
                <Close sx={{ color: DARK_COLORS.text.secondary }} />
              </IconButton>
            </DialogTitle>

            <DialogContent dividers sx={{ borderColor: DARK_COLORS.border }}>
              {/* Images */}
              {selectedEvent.image_urls && selectedEvent.image_urls.length > 0 && (
                <Box mb={3}>
                  <Grid container spacing={2}>
                    {selectedEvent.image_urls.map((url, index) => (
                      <Grid item xs={12} sm={6} key={index}>
                        <img
                          src={url}
                          alt={`Event ${index + 1}`}
                          style={{
                            width: '100%',
                            borderRadius: '8px',
                          }}
                        />
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {/* Event Info */}
              <Stack spacing={2}>
                <Box>
                  <Typography
                    variant="subtitle2"
                    sx={{ color: DARK_COLORS.text.secondary, mb: 1 }}
                  >
                    브랜드
                  </Typography>
                  <Typography sx={{ color: DARK_COLORS.text.primary }}>
                    {selectedEvent.brand_name}
                  </Typography>
                </Box>

                {selectedEvent.event_date && (
                  <Box>
                    <Typography
                      variant="subtitle2"
                      sx={{ color: DARK_COLORS.text.secondary, mb: 1 }}
                    >
                      이벤트 기간
                    </Typography>
                    <Typography sx={{ color: DARK_COLORS.text.primary }}>
                      {selectedEvent.event_date}
                    </Typography>
                  </Box>
                )}

                {selectedEvent.benefits_by_purchase_amount &&
                  selectedEvent.benefits_by_purchase_amount.length > 0 && (
                    <Box>
                      <Typography
                        variant="subtitle2"
                        sx={{ color: DARK_COLORS.text.secondary, mb: 1 }}
                      >
                        금액대별 혜택
                      </Typography>
                      <Stack spacing={1}>
                        {selectedEvent.benefits_by_purchase_amount.map(
                          (benefit, index) => (
                            <Paper
                              key={index}
                              sx={{
                                p: 1.5,
                                bgcolor: alpha(DARK_COLORS.success, 0.1),
                                border: `1px solid ${alpha(DARK_COLORS.success, 0.3)}`,
                              }}
                            >
                              <Typography
                                variant="body2"
                                sx={{ color: DARK_COLORS.text.primary }}
                              >
                                {benefit}
                              </Typography>
                            </Paper>
                          )
                        )}
                      </Stack>
                    </Box>
                  )}

                {selectedEvent.coupon_benefits &&
                  selectedEvent.coupon_benefits.length > 0 && (
                    <Box>
                      <Typography
                        variant="subtitle2"
                        sx={{ color: DARK_COLORS.text.secondary, mb: 1 }}
                      >
                        쿠폰 혜택
                      </Typography>
                      <Stack spacing={1}>
                        {selectedEvent.coupon_benefits.map((coupon, index) => (
                          <Paper
                            key={index}
                            sx={{
                              p: 1.5,
                              bgcolor: alpha(DARK_COLORS.warning, 0.1),
                              border: `1px solid ${alpha(DARK_COLORS.warning, 0.3)}`,
                            }}
                          >
                            <Typography
                              variant="body2"
                              sx={{ color: DARK_COLORS.text.primary }}
                            >
                              {coupon}
                            </Typography>
                          </Paper>
                        ))}
                      </Stack>
                    </Box>
                  )}
              </Stack>
            </DialogContent>

            <DialogActions sx={{ borderTop: `1px solid ${DARK_COLORS.border}` }}>
              <Button
                variant="contained"
                startIcon={<OpenInNew />}
                component="a"
                href={selectedEvent.url}
                target="_blank"
                rel="noopener noreferrer"
                sx={{
                  bgcolor: DARK_COLORS.primary,
                  '&:hover': {
                    bgcolor: alpha(DARK_COLORS.primary, 0.8),
                  },
                }}
              >
                이벤트 페이지 보기
              </Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default NaverSmartStoreEvents;
