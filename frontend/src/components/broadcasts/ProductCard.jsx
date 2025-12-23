/**
 * ProductCard Component
 * Displays product information with image, price, and discount
 */
import React from 'react';
import { Card, CardContent, CardMedia, Typography, Chip, Stack, Box } from '@mui/material';
import { OpenInNew as OpenInNewIcon } from '@mui/icons-material';

// Dark theme colors
const DARK_COLORS = {
  cardBg: '#1A1F2E',
  cardHover: '#252B3B',
  success: '#10B981',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
  },
};

const ProductCard = ({ product }) => {
  const formatPrice = (price) => {
    if (!price) return '-';
    return `₩${parseInt(price).toLocaleString()}`;
  };

  const handleClick = () => {
    if (product.link_url || product.link) {
      window.open(product.link_url || product.link, '_blank');
    }
  };

  return (
    <Card
      sx={{
        bgcolor: DARK_COLORS.cardBg,
        cursor: product.link_url || product.link ? 'pointer' : 'default',
        transition: 'all 0.2s ease',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        '&:hover': {
          bgcolor: DARK_COLORS.cardHover,
          transform: product.link_url || product.link ? 'translateY(-2px)' : 'none',
        },
      }}
      onClick={handleClick}
    >
      <CardMedia
        component="img"
        height="180"
        image={product.image_url || product.image || '/placeholder.png'}
        alt={product.name}
        sx={{ objectFit: 'cover' }}
        loading="lazy"
        onError={(e) => {
          e.target.src = '/placeholder.png';
        }}
      />
      <CardContent sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        <Typography
          variant="body2"
          sx={{
            color: DARK_COLORS.text.primary,
            mb: 1,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            minHeight: '2.8em',
          }}
        >
          {product.name}
        </Typography>

        {product.brand_name && (
          <Typography variant="caption" color={DARK_COLORS.text.secondary} sx={{ mb: 1 }}>
            {product.brand_name}
          </Typography>
        )}

        {product.discount_rate > 0 && (
          <Chip
            label={`${product.discount_rate}% OFF`}
            size="small"
            sx={{
              bgcolor: DARK_COLORS.success,
              color: 'white',
              alignSelf: 'flex-start',
              mb: 1,
            }}
          />
        )}

        <Stack spacing={0.5} sx={{ mt: 'auto' }}>
          {product.original_price && product.original_price !== product.discounted_price && (
            <Typography
              variant="caption"
              sx={{
                color: DARK_COLORS.text.secondary,
                textDecoration: 'line-through',
              }}
            >
              {formatPrice(product.original_price)}
            </Typography>
          )}
          <Typography
            variant="h6"
            sx={{
              color: DARK_COLORS.text.primary,
              fontWeight: 700,
            }}
          >
            {formatPrice(product.discounted_price)}
          </Typography>
        </Stack>

        {product.stock !== undefined && product.stock !== null && (
          <Typography variant="caption" color={DARK_COLORS.text.secondary} sx={{ mt: 1 }}>
            Stock: {product.stock}
          </Typography>
        )}

        {(product.link_url || product.link) && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <OpenInNewIcon fontSize="small" sx={{ color: DARK_COLORS.text.secondary }} />
            <Typography variant="caption" color={DARK_COLORS.text.secondary}>
              View product
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ProductCard;
