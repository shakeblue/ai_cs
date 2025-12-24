/**
 * BroadcastCard Component
 * Single broadcast card for list view
 */
import React from 'react';
import { Card, CardContent, CardMedia, Typography, Chip, Stack, alpha } from '@mui/material';
import { useNavigate } from 'react-router-dom';

// Dark theme colors
const DARK_COLORS = {
  cardBg: '#1A1F2E',
  cardHover: '#252B3B',
  primary: '#6366F1',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
  },
};

const BroadcastCard = ({ broadcast }) => {
  const navigate = useNavigate();

  // Use stand_by_image as thumbnail, fallback to first product image
  const thumbnail = broadcast.stand_by_image || broadcast.products?.[0]?.image_url || broadcast.products?.[0]?.image || '/placeholder.png';

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // Get product and coupon counts
  const productCount = broadcast.products?.length || broadcast.product_count || 0;
  const couponCount = broadcast.coupons?.length || broadcast.coupon_count || 0;

  return (
    <Card
      sx={{
        bgcolor: DARK_COLORS.cardBg,
        cursor: 'pointer',
        transition: 'all 0.3s ease',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        '&:hover': {
          bgcolor: DARK_COLORS.cardHover,
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 16px ${alpha(DARK_COLORS.primary, 0.2)}`,
        },
      }}
      onClick={() => navigate(`/broadcasts/${broadcast.id}`)}
    >
      <CardMedia
        component="img"
        height="200"
        image={thumbnail}
        alt={broadcast.title}
        sx={{ objectFit: 'cover' }}
        loading="lazy"
        onError={(e) => {
          e.target.src = '/placeholder.png';
        }}
      />
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Typography
          variant="h6"
          sx={{
            color: DARK_COLORS.text.primary,
            mb: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            minHeight: '3em',
          }}
        >
          {broadcast.title}
        </Typography>

        <Chip
          label={broadcast.brand_name}
          size="small"
          sx={{
            bgcolor: DARK_COLORS.primary,
            color: 'white',
            mb: 1,
            alignSelf: 'flex-start',
          }}
        />

        <Typography variant="body2" color={DARK_COLORS.text.secondary} sx={{ mb: 1 }}>
          {formatDate(broadcast.broadcast_date)}
        </Typography>

        <Stack direction="row" spacing={1} sx={{ mt: 'auto' }}>
          <Chip
            label={`${productCount} products`}
            size="small"
            variant="outlined"
            sx={{
              borderColor: DARK_COLORS.text.secondary,
              color: DARK_COLORS.text.secondary,
            }}
          />
          <Chip
            label={`${couponCount} coupons`}
            size="small"
            variant="outlined"
            sx={{
              borderColor: DARK_COLORS.text.secondary,
              color: DARK_COLORS.text.secondary,
            }}
          />
        </Stack>
      </CardContent>
    </Card>
  );
};

export default BroadcastCard;
