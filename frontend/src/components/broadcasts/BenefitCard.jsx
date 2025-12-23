/**
 * BenefitCard Component
 * Displays live broadcast benefit/promotion information
 */
import React from 'react';
import { Card, CardContent, Typography, Stack, Chip, Box } from '@mui/material';
import { CardGiftcard as GiftIcon } from '@mui/icons-material';

// Dark theme colors
const DARK_COLORS = {
  cardBg: '#1A1F2E',
  success: '#10B981',
  info: '#3B82F6',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
  },
};

const BenefitCard = ({ benefit }) => {
  const getBenefitColor = () => {
    switch (benefit.benefit_type?.toUpperCase()) {
      case 'ONAIR':
        return DARK_COLORS.info;
      case 'GIFT':
        return DARK_COLORS.success;
      default:
        return DARK_COLORS.info;
    }
  };

  return (
    <Card
      sx={{
        bgcolor: DARK_COLORS.cardBg,
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
              bgcolor: getBenefitColor(),
              borderRadius: 2,
              p: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <GiftIcon sx={{ color: 'white', fontSize: 32 }} />
          </Box>

          <Box sx={{ flexGrow: 1 }}>
            {benefit.benefit_type && (
              <Chip
                label={benefit.benefit_type}
                size="small"
                sx={{
                  bgcolor: getBenefitColor(),
                  color: 'white',
                  mb: 1,
                }}
              />
            )}

            <Typography
              variant="h6"
              sx={{
                color: DARK_COLORS.text.primary,
                mb: 1,
              }}
            >
              {benefit.message}
            </Typography>

            {benefit.detail && (
              <Typography
                variant="body2"
                sx={{
                  color: DARK_COLORS.text.secondary,
                  lineHeight: 1.6,
                }}
              >
                {benefit.detail}
              </Typography>
            )}

            {benefit.benefit_id && (
              <Typography
                variant="caption"
                sx={{
                  color: DARK_COLORS.text.secondary,
                  mt: 1,
                  display: 'block',
                }}
              >
                Benefit ID: {benefit.benefit_id}
              </Typography>
            )}
          </Box>
        </Stack>
      </CardContent>
    </Card>
  );
};

export default BenefitCard;
