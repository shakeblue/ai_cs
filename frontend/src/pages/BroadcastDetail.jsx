/**
 * BroadcastDetail Page
 * Individual broadcast detail view with tabs for products, coupons, benefits, chat, and info
 */
import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Stack,
  Chip,
  Tabs,
  Tab,
  Grid,
  CircularProgress,
  Alert,
  Divider,
  Link,
  Paper,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  ShoppingCart as ShoppingCartIcon,
  LocalOffer as LocalOfferIcon,
  CardGiftcard as CardGiftcardIcon,
  Chat as ChatIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useBroadcastDetail } from '../hooks/useBroadcastDetail';
import ProductCard from '../components/broadcasts/ProductCard';
import CouponCard from '../components/broadcasts/CouponCard';
import BenefitCard from '../components/broadcasts/BenefitCard';
import ChatList from '../components/broadcasts/ChatList';

// Dark theme colors
const DARK_COLORS = {
  background: '#0F1419',
  cardBg: '#1A1F2E',
  primary: '#6366F1',
  secondary: '#EC4899',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
  },
  border: '#2D3748',
};

const BroadcastDetail = () => {
  const { broadcastId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);

  const { broadcast, loading, error } = useBroadcastDetail(broadcastId);

  const formatDate = (dateString) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  if (loading) {
    return (
      <Box
        sx={{
          bgcolor: DARK_COLORS.background,
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ bgcolor: DARK_COLORS.background, minHeight: '100vh', py: 4 }}>
        <Container maxWidth="xl">
          <Alert severity="error">Error loading broadcast: {error.message}</Alert>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/broadcasts')}
            sx={{ mt: 2 }}
          >
            Back to List
          </Button>
        </Container>
      </Box>
    );
  }

  if (!broadcast) {
    return (
      <Box sx={{ bgcolor: DARK_COLORS.background, minHeight: '100vh', py: 4 }}>
        <Container maxWidth="xl">
          <Alert severity="info">Broadcast not found</Alert>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/broadcasts')}
            sx={{ mt: 2 }}
          >
            Back to List
          </Button>
        </Container>
      </Box>
    );
  }

  return (
    <Box sx={{ bgcolor: DARK_COLORS.background, minHeight: '100vh', py: 4 }}>
      <Container maxWidth="xl">
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => navigate('/broadcasts')}
            sx={{ color: DARK_COLORS.text.primary, mb: 2 }}
          >
            Back to List
          </Button>
        </Box>

        {/* Broadcast Info Card */}
        <Card sx={{ mb: 3, bgcolor: DARK_COLORS.cardBg }}>
          <CardContent sx={{ p: 4 }}>
            <Typography
              variant="h4"
              sx={{
                color: DARK_COLORS.text.primary,
                fontWeight: 700,
                mb: 2,
              }}
            >
              {broadcast.title}
            </Typography>

            <Stack direction="row" spacing={2} sx={{ mb: 2, flexWrap: 'wrap' }}>
              <Chip
                label={broadcast.brand_name}
                sx={{
                  bgcolor: DARK_COLORS.primary,
                  color: 'white',
                  fontWeight: 600,
                }}
              />
              <Chip
                label={broadcast.status}
                sx={{
                  bgcolor: DARK_COLORS.secondary,
                  color: 'white',
                }}
              />
            </Stack>

            {broadcast.description && (
              <Typography
                variant="body1"
                sx={{
                  color: DARK_COLORS.text.secondary,
                  mb: 2,
                }}
              >
                {broadcast.description}
              </Typography>
            )}

            <Stack spacing={1}>
              <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                <strong>Broadcast Date:</strong> {formatDate(broadcast.broadcast_date)}
                {broadcast.broadcast_end_date && ` ~ ${formatDate(broadcast.broadcast_end_date)}`}
              </Typography>
              {broadcast.expected_start_date && (
                <Typography variant="body2" color={DARK_COLORS.text.secondary}>
                  <strong>Expected Start:</strong> {formatDate(broadcast.expected_start_date)}
                </Typography>
              )}
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
                  color: DARK_COLORS.primary,
                },
              },
              '& .MuiTabs-indicator': {
                bgcolor: DARK_COLORS.primary,
              },
            }}
          >
            <Tab
              icon={<ShoppingCartIcon />}
              label={`Products (${broadcast.products?.length || 0})`}
              iconPosition="start"
            />
            <Tab
              icon={<LocalOfferIcon />}
              label={`Coupons (${broadcast.coupons?.length || 0})`}
              iconPosition="start"
            />
            <Tab
              icon={<CardGiftcardIcon />}
              label={`Benefits (${broadcast.live_benefits?.length || 0})`}
              iconPosition="start"
            />
            <Tab
              icon={<ChatIcon />}
              label={`Chat (${broadcast.live_chat?.length || 0})`}
              iconPosition="start"
            />
            <Tab icon={<InfoIcon />} label="Info" iconPosition="start" />
          </Tabs>
        </Paper>

        {/* Tab Panels */}
        <Box>
          {/* Products Tab */}
          {activeTab === 0 && (
            <Box>
              {broadcast.products && broadcast.products.length > 0 ? (
                <Grid container spacing={2}>
                  {broadcast.products.map((product, index) => (
                    <Grid item xs={12} sm={6} md={4} lg={3} key={product.id || index}>
                      <ProductCard product={product} />
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Paper sx={{ bgcolor: DARK_COLORS.cardBg, p: 4, textAlign: 'center' }}>
                  <Typography color={DARK_COLORS.text.secondary}>
                    No products available
                  </Typography>
                </Paper>
              )}
            </Box>
          )}

          {/* Coupons Tab */}
          {activeTab === 1 && (
            <Box>
              {broadcast.coupons && broadcast.coupons.length > 0 ? (
                <Stack spacing={2}>
                  {broadcast.coupons.map((coupon, index) => (
                    <CouponCard key={coupon.id || index} coupon={coupon} />
                  ))}
                </Stack>
              ) : (
                <Paper sx={{ bgcolor: DARK_COLORS.cardBg, p: 4, textAlign: 'center' }}>
                  <Typography color={DARK_COLORS.text.secondary}>
                    No coupons available
                  </Typography>
                </Paper>
              )}
            </Box>
          )}

          {/* Benefits Tab */}
          {activeTab === 2 && (
            <Box>
              {broadcast.live_benefits && broadcast.live_benefits.length > 0 ? (
                <Stack spacing={2}>
                  {broadcast.live_benefits.map((benefit, index) => (
                    <BenefitCard key={benefit.id || index} benefit={benefit} />
                  ))}
                </Stack>
              ) : (
                <Paper sx={{ bgcolor: DARK_COLORS.cardBg, p: 4, textAlign: 'center' }}>
                  <Typography color={DARK_COLORS.text.secondary}>
                    No benefits available
                  </Typography>
                </Paper>
              )}
            </Box>
          )}

          {/* Chat Tab */}
          {activeTab === 3 && (
            <ChatList messages={broadcast.live_chat || []} broadcastId={broadcast.id} />
          )}

          {/* Info Tab */}
          {activeTab === 4 && (
            <Card sx={{ bgcolor: DARK_COLORS.cardBg }}>
              <CardContent sx={{ p: 4 }}>
                <Typography variant="h6" color={DARK_COLORS.text.primary} sx={{ mb: 3 }}>
                  Broadcast Information
                </Typography>
                <Divider sx={{ mb: 3, borderColor: DARK_COLORS.border }} />

                <Grid container spacing={3}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color={DARK_COLORS.text.secondary} sx={{ mb: 0.5 }}>
                      Broadcast ID
                    </Typography>
                    <Typography variant="body1" color={DARK_COLORS.text.primary}>
                      {broadcast.id}
                    </Typography>
                  </Grid>

                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color={DARK_COLORS.text.secondary} sx={{ mb: 0.5 }}>
                      Status
                    </Typography>
                    <Typography variant="body1" color={DARK_COLORS.text.primary}>
                      {broadcast.status}
                    </Typography>
                  </Grid>

                  <Grid item xs={12}>
                    <Typography variant="body2" color={DARK_COLORS.text.secondary} sx={{ mb: 0.5 }}>
                      Replay URL
                    </Typography>
                    <Link
                      href={broadcast.replay_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{ color: DARK_COLORS.primary }}
                    >
                      {broadcast.replay_url}
                    </Link>
                  </Grid>

                  <Grid item xs={12}>
                    <Typography variant="body2" color={DARK_COLORS.text.secondary} sx={{ mb: 0.5 }}>
                      Broadcast URL
                    </Typography>
                    <Link
                      href={broadcast.broadcast_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{ color: DARK_COLORS.primary }}
                    >
                      {broadcast.broadcast_url}
                    </Link>
                  </Grid>

                  <Grid item xs={12}>
                    <Typography variant="body2" color={DARK_COLORS.text.secondary} sx={{ mb: 0.5 }}>
                      Livebridge URL
                    </Typography>
                    <Link
                      href={broadcast.livebridge_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      sx={{ color: DARK_COLORS.primary }}
                    >
                      {broadcast.livebridge_url}
                    </Link>
                  </Grid>

                  {broadcast.created_at && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color={DARK_COLORS.text.secondary} sx={{ mb: 0.5 }}>
                        Created At
                      </Typography>
                      <Typography variant="body1" color={DARK_COLORS.text.primary}>
                        {formatDate(broadcast.created_at)}
                      </Typography>
                    </Grid>
                  )}

                  {broadcast.updated_at && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color={DARK_COLORS.text.secondary} sx={{ mb: 0.5 }}>
                        Updated At
                      </Typography>
                      <Typography variant="body1" color={DARK_COLORS.text.primary}>
                        {formatDate(broadcast.updated_at)}
                      </Typography>
                    </Grid>
                  )}
                </Grid>
              </CardContent>
            </Card>
          )}
        </Box>
      </Container>
    </Box>
  );
};

export default BroadcastDetail;
