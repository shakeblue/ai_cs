/**
 * CouponCard Component
 * Displays coupon information with discount details and validity
 */
import React from 'react';
import { Card, CardContent, Typography, Stack, Chip, Box, Divider } from '@mui/material';
import {
  LocalOffer as CouponIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';

// Dark theme colors
const DARK_COLORS = {
  cardBg: '#1A1F2E',
  secondary: '#EC4899',
  success: '#10B981',
  warning: '#F59E0B',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
  },
  border: '#2D3748',
};

const CouponCard = ({ coupon }) => {
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatPrice = (price) => {
    if (!price) return '-';
    return `₩${parseInt(price).toLocaleString()}`;
  };

  const getBenefitText = () => {
    if (coupon.benefit_unit === 'PERCENT') {
      return `${coupon.benefit_value}% OFF`;
    } else if (coupon.benefit_unit === 'AMOUNT') {
      return `${formatPrice(coupon.benefit_value)} OFF`;
    }
    return coupon.benefit_value;
  };

  const isValid = () => {
    if (!coupon.valid_end) return true;
    const now = new Date();
    const endDate = new Date(coupon.valid_end);
    return now <= endDate;
  };

  return (
    <Card
      sx={{
        bgcolor: DARK_COLORS.cardBg,
        border: `2px solid ${isValid() ? DARK_COLORS.secondary : DARK_COLORS.border}`,
        transition: 'all 0.2s ease',
        '&:hover': {
          transform: 'translateX(4px)',
        },
      }}
    >
      <CardContent>
        <Stack direction="row" spacing={2} alignItems="flex-start">
          <Box
            sx={{
              bgcolor: DARK_COLORS.secondary,
              borderRadius: 2,
              p: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <CouponIcon sx={{ color: 'white', fontSize: 32 }} />
          </Box>

          <Box sx={{ flexGrow: 1 }}>
            <Typography
              variant="h6"
              sx={{
                color: DARK_COLORS.text.primary,
                mb: 0.5,
              }}
            >
              {coupon.title}
            </Typography>

            {coupon.benefit_type && (
              <Chip
                label={coupon.benefit_type}
                size="small"
                sx={{
                  bgcolor: DARK_COLORS.secondary,
                  color: 'white',
                  mb: 1,
                }}
              />
            )}

            {coupon.benefit_value && (
              <Typography
                variant="h5"
                sx={{
                  color: DARK_COLORS.secondary,
                  fontWeight: 700,
                  my: 1,
                }}
              >
                {getBenefitText()}
              </Typography>
            )}

            <Divider sx={{ my: 1.5, borderColor: DARK_COLORS.border }} />

            <Stack spacing={1}>
              {coupon.min_order_amount > 0 && (
                <Stack direction="row" spacing={1} alignItems="center">
                  <CheckCircleIcon fontSize="small" sx={{ color: DARK_COLORS.text.secondary }} />
                  <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                    Minimum purchase: {formatPrice(coupon.min_order_amount)}
                  </Typography>
                </Stack>
              )}

              {coupon.max_discount_amount > 0 && (
                <Stack direction="row" spacing={1} alignItems="center">
                  <CheckCircleIcon fontSize="small" sx={{ color: DARK_COLORS.text.secondary }} />
                  <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                    Maximum discount: {formatPrice(coupon.max_discount_amount)}
                  </Typography>
                </Stack>
              )}

              {(coupon.valid_start || coupon.valid_end) && (
                <Stack direction="row" spacing={1} alignItems="center">
                  <ScheduleIcon fontSize="small" sx={{ color: DARK_COLORS.text.secondary }} />
                  <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                    {formatDate(coupon.valid_start)} ~ {formatDate(coupon.valid_end)}
                  </Typography>
                </Stack>
              )}
            </Stack>

            {!isValid() && (
              <Chip
                label="Expired"
                size="small"
                sx={{
                  bgcolor: DARK_COLORS.warning,
                  color: 'white',
                  mt: 1,
                }}
              />
            )}
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default CouponCard;
