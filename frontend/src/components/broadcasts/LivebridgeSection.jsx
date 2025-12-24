/**
 * LivebridgeSection Component
 * Displays livebridge promotional data including special coupons, products, and benefits
 */
import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Divider,
  Stack,
  Tabs,
  Tab,
  Paper,
  Alert,
} from '@mui/material';
import {
  LocalOffer as CouponIcon,
  ShoppingCart as ProductIcon,
  CardGiftcard as BenefitIcon,
  Star as StarIcon,
} from '@mui/icons-material';

// Dark theme colors
const DARK_COLORS = {
  background: '#0F1419',
  cardBg: '#1A1F2E',
  primary: '#6366F1',
  secondary: '#EC4899',
  accent: '#10B981',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
  },
  border: '#2D3748',
};

const LivebridgeSection = ({ livebridge }) => {
  const [activeTab, setActiveTab] = useState(0);

  if (!livebridge) {
    return null;
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatCurrency = (amount) => {
    if (!amount) return '-';
    return new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
    }).format(amount);
  };

  const hasData =
    (livebridge.special_coupons && livebridge.special_coupons.length > 0) ||
    (livebridge.products && livebridge.products.length > 0) ||
    (livebridge.live_benefits && livebridge.live_benefits.length > 0) ||
    (livebridge.benefits_by_amount && livebridge.benefits_by_amount.length > 0) ||
    (livebridge.simple_coupons && livebridge.simple_coupons.length > 0);

  if (!hasData) {
    return null;
  }

  return (
    <Box sx={{ mt: 4 }}>
      {/* Section Header */}
      <Card sx={{ bgcolor: DARK_COLORS.cardBg, mb: 3 }}>
        <CardContent>
          <Stack direction="row" alignItems="center" spacing={2}>
            <StarIcon sx={{ color: DARK_COLORS.secondary, fontSize: 32 }} />
            <Box>
              <Typography
                variant="h5"
                sx={{
                  color: DARK_COLORS.text.primary,
                  fontWeight: 700,
                }}
              >
                Livebridge 특별 혜택
              </Typography>
              <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                라이브 방송 전용 프로모션 정보
              </Typography>
            </Box>
          </Stack>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Paper sx={{ bgcolor: DARK_COLORS.cardBg, mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              color: DARK_COLORS.text.secondary,
              '&.Mui-selected': {
                color: DARK_COLORS.secondary,
              },
            },
            '& .MuiTabs-indicator': {
              bgcolor: DARK_COLORS.secondary,
            },
          }}
        >
          {livebridge.special_coupons && livebridge.special_coupons.length > 0 && (
            <Tab
              icon={<CouponIcon />}
              label={`특별 쿠폰 (${livebridge.special_coupons.length})`}
              iconPosition="start"
            />
          )}
          {livebridge.products && livebridge.products.length > 0 && (
            <Tab
              icon={<ProductIcon />}
              label={`상품 (${livebridge.products.length})`}
              iconPosition="start"
            />
          )}
          {livebridge.live_benefits && livebridge.live_benefits.length > 0 && (
            <Tab
              icon={<BenefitIcon />}
              label={`라이브 혜택 (${livebridge.live_benefits.length})`}
              iconPosition="start"
            />
          )}
          {livebridge.benefits_by_amount && livebridge.benefits_by_amount.length > 0 && (
            <Tab
              icon={<BenefitIcon />}
              label={`금액별 혜택 (${livebridge.benefits_by_amount.length})`}
              iconPosition="start"
            />
          )}
          {livebridge.simple_coupons && livebridge.simple_coupons.length > 0 && (
            <Tab
              icon={<CouponIcon />}
              label={`간편 쿠폰 (${livebridge.simple_coupons.length})`}
              iconPosition="start"
            />
          )}
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box>
        {/* Special Coupons Tab */}
        {activeTab === 0 && livebridge.special_coupons && livebridge.special_coupons.length > 0 && (
          <Stack spacing={2}>
            {livebridge.special_coupons.map((coupon, index) => (
              <Card key={coupon.id || index} sx={{ bgcolor: DARK_COLORS.cardBg }}>
                <CardContent>
                  <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 2 }}>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" color={DARK_COLORS.text.primary} sx={{ mb: 1 }}>
                        {coupon.coupon_name}
                      </Typography>
                      <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
                        {coupon.coupon_type && (
                          <Chip label={coupon.coupon_type} size="small" sx={{ bgcolor: DARK_COLORS.primary, color: 'white' }} />
                        )}
                        {coupon.coupon_kind && (
                          <Chip label={coupon.coupon_kind} size="small" sx={{ bgcolor: DARK_COLORS.secondary, color: 'white' }} />
                        )}
                        {coupon.availability_status && (
                          <Chip label={coupon.availability_status} size="small" sx={{ bgcolor: DARK_COLORS.accent, color: 'white' }} />
                        )}
                      </Stack>
                    </Box>
                    {coupon.benefit_value && (
                      <Typography
                        variant="h5"
                        sx={{
                          color: DARK_COLORS.secondary,
                          fontWeight: 700,
                          ml: 2,
                        }}
                      >
                        {coupon.benefit_unit === 'WON' ? formatCurrency(coupon.benefit_value) : `${coupon.benefit_value}${coupon.benefit_unit || ''}`}
                      </Typography>
                    )}
                  </Stack>

                  <Divider sx={{ my: 2, borderColor: DARK_COLORS.border }} />

                  <Grid container spacing={2}>
                    {coupon.min_order_amount && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                          최소 주문금액
                        </Typography>
                        <Typography variant="body1" color={DARK_COLORS.text.primary}>
                          {formatCurrency(coupon.min_order_amount)}
                        </Typography>
                      </Grid>
                    )}
                    {coupon.max_discount_amount && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                          최대 할인금액
                        </Typography>
                        <Typography variant="body1" color={DARK_COLORS.text.primary}>
                          {formatCurrency(coupon.max_discount_amount)}
                        </Typography>
                      </Grid>
                    )}
                    {coupon.valid_period_start && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                          유효기간 시작
                        </Typography>
                        <Typography variant="body1" color={DARK_COLORS.text.primary}>
                          {formatDate(coupon.valid_period_start)}
                        </Typography>
                      </Grid>
                    )}
                    {coupon.valid_period_end && (
                      <Grid item xs={12} sm={6}>
                        <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                          유효기간 종료
                        </Typography>
                        <Typography variant="body1" color={DARK_COLORS.text.primary}>
                          {formatDate(coupon.valid_period_end)}
                        </Typography>
                      </Grid>
                    )}
                    {coupon.provider_name && (
                      <Grid item xs={12}>
                        <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                          제공자
                        </Typography>
                        <Typography variant="body1" color={DARK_COLORS.text.primary}>
                          {coupon.provider_name}
                        </Typography>
                      </Grid>
                    )}
                  </Grid>
                </CardContent>
              </Card>
            ))}
          </Stack>
        )}

        {/* Products Tab */}
        {activeTab === 1 && livebridge.products && livebridge.products.length > 0 && (
          <Grid container spacing={2}>
            {livebridge.products.map((product, index) => (
              <Grid item xs={12} sm={6} md={4} lg={3} key={product.id || index}>
                <Card sx={{ bgcolor: DARK_COLORS.cardBg, height: '100%' }}>
                  {product.image && (
                    <Box
                      component="img"
                      src={product.image}
                      alt={product.name}
                      sx={{
                        width: '100%',
                        height: 200,
                        objectFit: 'cover',
                      }}
                    />
                  )}
                  <CardContent>
                    <Typography
                      variant="body1"
                      color={DARK_COLORS.text.primary}
                      sx={{
                        mb: 2,
                        fontWeight: 600,
                        minHeight: 48,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}
                    >
                      {product.name}
                    </Typography>

                    {product.discount_rate && (
                      <Chip
                        label={`${product.discount_rate}% 할인`}
                        size="small"
                        sx={{
                          bgcolor: DARK_COLORS.secondary,
                          color: 'white',
                          fontWeight: 700,
                          mb: 1,
                        }}
                      />
                    )}

                    {product.discount_price && (
                      <Typography
                        variant="h6"
                        sx={{
                          color: DARK_COLORS.primary,
                          fontWeight: 700,
                        }}
                      >
                        {formatCurrency(product.discount_price)}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}

        {/* Live Benefits Tab */}
        {activeTab === 2 && livebridge.live_benefits && livebridge.live_benefits.length > 0 && (
          <Stack spacing={2}>
            {livebridge.live_benefits.map((benefit, index) => (
              <Card key={benefit.id || index} sx={{ bgcolor: DARK_COLORS.cardBg }}>
                <CardContent>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <BenefitIcon sx={{ color: DARK_COLORS.accent, fontSize: 32 }} />
                    <Typography variant="h6" color={DARK_COLORS.text.primary}>
                      {benefit.benefit_text}
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>
        )}

        {/* Benefits by Amount Tab */}
        {activeTab === 3 && livebridge.benefits_by_amount && livebridge.benefits_by_amount.length > 0 && (
          <Stack spacing={2}>
            {livebridge.benefits_by_amount.map((benefit, index) => (
              <Card key={benefit.id || index} sx={{ bgcolor: DARK_COLORS.cardBg }}>
                <CardContent>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <BenefitIcon sx={{ color: DARK_COLORS.primary, fontSize: 32 }} />
                    <Typography variant="body1" color={DARK_COLORS.text.primary}>
                      {benefit.benefit_text}
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>
        )}

        {/* Simple Coupons Tab */}
        {activeTab === 4 && livebridge.simple_coupons && livebridge.simple_coupons.length > 0 && (
          <Stack spacing={2}>
            {livebridge.simple_coupons.map((coupon, index) => (
              <Card key={coupon.id || index} sx={{ bgcolor: DARK_COLORS.cardBg }}>
                <CardContent>
                  <Stack direction="row" spacing={2} alignItems="center">
                    <CouponIcon sx={{ color: DARK_COLORS.secondary, fontSize: 32 }} />
                    <Typography variant="body1" color={DARK_COLORS.text.primary}>
                      {coupon.coupon_text}
                    </Typography>
                  </Stack>
                </CardContent>
              </Card>
            ))}
          </Stack>
        )}
      </Box>
    </Box>
  );
};

export default LivebridgeSection;
