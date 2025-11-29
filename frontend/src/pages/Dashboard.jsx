/**
 * 대시보드 페이지
 * 플랫폼별, 브랜드별 라이브 방송 현황 표시 (Dark Modern Theme)
 */

import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Avatar,
  Stack,
  Divider,
  alpha,
} from '@mui/material';
import {
  LiveTv as LiveTvIcon,
  Schedule as ScheduleIcon,
  CheckCircle as CheckCircleIcon,
  TrendingUp as TrendingUpIcon,
  Storefront as StorefrontIcon,
  BusinessCenter as BusinessCenterIcon,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getRealCollectedEvents } from '../mockData/realCollectedData';

// 다크 테마 색상 팔레트
const DARK_COLORS = {
  background: '#0F1419',
  cardBg: '#1A1F2E',
  cardHoverBg: '#252B3B',
  primary: '#6366F1',
  secondary: '#EC4899',
  success: '#10B981',
  warning: '#F59E0B',
  info: '#3B82F6',
  text: {
    primary: '#F9FAFB',
    secondary: '#9CA3AF',
    disabled: '#6B7280',
  },
  border: '#2D3748',
  chart: ['#6366F1', '#EC4899', '#10B981', '#F59E0B', '#3B82F6', '#8B5CF6', '#14B8A6', '#F97316', '#06B6D4', '#A855F7']
};

const Dashboard = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  
  // 데이터 로드 및 분석
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  const loadDashboardData = () => {
    try {
      const allEvents = getRealCollectedEvents();
      
      const activeEvents = allEvents.filter(e => e.status === 'ACTIVE');
      const pendingEvents = allEvents.filter(e => e.status === 'PENDING' || e.status === 'SCHEDULED');
      const endedEvents = allEvents.filter(e => e.status === 'ENDED' || e.status === 'COMPLETED');
      
      const platformStats = {};
      allEvents.forEach(event => {
        const platform = event.channel_name || '기타';
        if (!platformStats[platform]) {
          platformStats[platform] = { platform, active: 0, pending: 0, ended: 0, total: 0 };
        }
        platformStats[platform].total++;
        if (event.status === 'ACTIVE') platformStats[platform].active++;
        else if (event.status === 'PENDING' || event.status === 'SCHEDULED') platformStats[platform].pending++;
        else if (event.status === 'ENDED' || event.status === 'COMPLETED') platformStats[platform].ended++;
      });
      
      const brandStats = {};
      allEvents.forEach(event => {
        const brands = ['설화수', '라네즈', '아이오페', '헤라', '에스트라', '이니스프리', '해피바스', '바이탈뷰티', '프리메라', '오설록'];
        const foundBrand = brands.find(brand => 
          event.title?.includes(brand) || 
          event.subtitle?.includes(brand) || 
          (event.tags && event.tags.includes(brand))
        );
        
        if (foundBrand) {
          if (!brandStats[foundBrand]) {
            brandStats[foundBrand] = { brand: foundBrand, active: 0, pending: 0, ended: 0, total: 0 };
          }
          brandStats[foundBrand].total++;
          if (event.status === 'ACTIVE') brandStats[foundBrand].active++;
          else if (event.status === 'PENDING' || event.status === 'SCHEDULED') brandStats[foundBrand].pending++;
          else if (event.status === 'ENDED' || event.status === 'COMPLETED') brandStats[foundBrand].ended++;
        }
      });
      
      const platformChartData = Object.values(platformStats);
      const brandChartData = Object.values(brandStats);
      const recentActiveEvents = activeEvents.slice(0, 5);
      const recentPendingEvents = pendingEvents.slice(0, 5);
      
      setDashboardData({
        summary: {
          totalEvents: allEvents.length,
          activeEvents: activeEvents.length,
          pendingEvents: pendingEvents.length,
          endedEvents: endedEvents.length,
          totalPlatforms: Object.keys(platformStats).length,
          totalBrands: Object.keys(brandStats).length
        },
        platformStats: platformChartData,
        brandStats: brandChartData,
        recentActiveEvents,
        recentPendingEvents
      });
      
    } catch (err) {
      console.error('대시보드 데이터 로드 오류:', err);
    }
  };
  
  if (!dashboardData) {
    return (
      <Box 
        sx={{ 
          minHeight: '100vh', 
          bgcolor: DARK_COLORS.background, 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center' 
        }}
      >
        <Typography sx={{ color: DARK_COLORS.text.primary }}>데이터를 로드하는 중...</Typography>
      </Box>
    );
  }
  
  const { summary, platformStats, brandStats, recentActiveEvents, recentPendingEvents } = dashboardData;
  
  // 커스텀 툴팁
  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      return (
        <Paper
          sx={{
            p: 2,
            bgcolor: alpha(DARK_COLORS.cardBg, 0.95),
            border: `1px solid ${DARK_COLORS.border}`,
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.6)',
          }}
        >
          {payload.map((entry, index) => (
            <Typography 
              key={index} 
              variant="body2" 
              sx={{ color: entry.color, fontWeight: 600 }}
            >
              {entry.name}: {entry.value}
            </Typography>
          ))}
        </Paper>
      );
    }
    return null;
  };
  
  return (
    <Box sx={{ minHeight: '100vh', bgcolor: DARK_COLORS.background, pb: 6 }}>
      <Container maxWidth="xl" sx={{ pt: 4 }}>
        {/* 페이지 헤더 */}
        <Box mb={5}>
          <Typography 
            variant="h3" 
            component="h1" 
            gutterBottom 
            sx={{ 
              fontWeight: 800,
              color: DARK_COLORS.text.primary,
              letterSpacing: '-0.02em',
              background: `linear-gradient(135deg, ${DARK_COLORS.primary} 0%, ${DARK_COLORS.secondary} 100%)`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              mb: 1,
            }}
          >
            Live Dashboard
          </Typography>
          <Typography 
            variant="h6" 
            sx={{ 
              color: DARK_COLORS.text.secondary,
              fontWeight: 400,
              letterSpacing: '0.02em',
            }}
          >
            플랫폼별, 브랜드별 실시간 라이브 방송 현황
          </Typography>
        </Box>
        
        {/* 통계 카드 */}
        <Grid container spacing={3} mb={5}>
          <Grid item xs={12} sm={6} md={2}>
            <Card 
              sx={{ 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: `0 12px 48px ${alpha(DARK_COLORS.primary, 0.3)}`,
                  border: `1px solid ${alpha(DARK_COLORS.primary, 0.5)}`,
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" flexDirection="column" alignItems="center">
                  <Box 
                    sx={{ 
                      width: 56, 
                      height: 56, 
                      borderRadius: '16px',
                      background: `linear-gradient(135deg, ${alpha(DARK_COLORS.primary, 0.2)} 0%, ${alpha(DARK_COLORS.primary, 0.05)} 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                    }}
                  >
                    <TrendingUpIcon sx={{ fontSize: 28, color: DARK_COLORS.primary }} />
                  </Box>
                  <Typography 
                    variant="h3" 
                    sx={{ 
                      color: DARK_COLORS.text.primary, 
                      fontWeight: 800, 
                      mb: 0.5,
                      fontSize: { xs: '2rem', md: '2.5rem' }
                    }}
                  >
                    {summary.totalEvents}
                  </Typography>
                  <Typography variant="body2" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 500 }}>
                    전체 방송
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <Card 
              sx={{ 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: `0 12px 48px ${alpha(DARK_COLORS.secondary, 0.3)}`,
                  border: `1px solid ${alpha(DARK_COLORS.secondary, 0.5)}`,
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" flexDirection="column" alignItems="center">
                  <Box 
                    sx={{ 
                      width: 56, 
                      height: 56, 
                      borderRadius: '16px',
                      background: `linear-gradient(135deg, ${alpha(DARK_COLORS.secondary, 0.2)} 0%, ${alpha(DARK_COLORS.secondary, 0.05)} 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                    }}
                  >
                    <LiveTvIcon sx={{ fontSize: 28, color: DARK_COLORS.secondary }} />
                  </Box>
                  <Typography variant="h3" sx={{ color: DARK_COLORS.text.primary, fontWeight: 800, mb: 0.5 }}>
                    {summary.activeEvents}
                  </Typography>
                  <Typography variant="body2" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 500 }}>
                    진행중
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <Card 
              sx={{ 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: `0 12px 48px ${alpha(DARK_COLORS.info, 0.3)}`,
                  border: `1px solid ${alpha(DARK_COLORS.info, 0.5)}`,
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" flexDirection="column" alignItems="center">
                  <Box 
                    sx={{ 
                      width: 56, 
                      height: 56, 
                      borderRadius: '16px',
                      background: `linear-gradient(135deg, ${alpha(DARK_COLORS.info, 0.2)} 0%, ${alpha(DARK_COLORS.info, 0.05)} 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                    }}
                  >
                    <ScheduleIcon sx={{ fontSize: 28, color: DARK_COLORS.info }} />
                  </Box>
                  <Typography variant="h3" sx={{ color: DARK_COLORS.text.primary, fontWeight: 800, mb: 0.5 }}>
                    {summary.pendingEvents}
                  </Typography>
                  <Typography variant="body2" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 500 }}>
                    예정
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <Card 
              sx={{ 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: `0 12px 48px ${alpha(DARK_COLORS.success, 0.3)}`,
                  border: `1px solid ${alpha(DARK_COLORS.success, 0.5)}`,
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" flexDirection="column" alignItems="center">
                  <Box 
                    sx={{ 
                      width: 56, 
                      height: 56, 
                      borderRadius: '16px',
                      background: `linear-gradient(135deg, ${alpha(DARK_COLORS.success, 0.2)} 0%, ${alpha(DARK_COLORS.success, 0.05)} 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                    }}
                  >
                    <CheckCircleIcon sx={{ fontSize: 28, color: DARK_COLORS.success }} />
                  </Box>
                  <Typography variant="h3" sx={{ color: DARK_COLORS.text.primary, fontWeight: 800, mb: 0.5 }}>
                    {summary.endedEvents}
                  </Typography>
                  <Typography variant="body2" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 500 }}>
                    종료
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <Card 
              sx={{ 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: `0 12px 48px ${alpha(DARK_COLORS.warning, 0.3)}`,
                  border: `1px solid ${alpha(DARK_COLORS.warning, 0.5)}`,
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" flexDirection="column" alignItems="center">
                  <Box 
                    sx={{ 
                      width: 56, 
                      height: 56, 
                      borderRadius: '16px',
                      background: `linear-gradient(135deg, ${alpha(DARK_COLORS.warning, 0.2)} 0%, ${alpha(DARK_COLORS.warning, 0.05)} 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                    }}
                  >
                    <StorefrontIcon sx={{ fontSize: 28, color: DARK_COLORS.warning }} />
                  </Box>
                  <Typography variant="h3" sx={{ color: DARK_COLORS.text.primary, fontWeight: 800, mb: 0.5 }}>
                    {summary.totalPlatforms}
                  </Typography>
                  <Typography variant="body2" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 500 }}>
                    플랫폼
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} sm={6} md={2}>
            <Card 
              sx={{ 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': { 
                  transform: 'translateY(-8px)',
                  boxShadow: `0 12px 48px ${alpha('#8B5CF6', 0.3)}`,
                  border: `1px solid ${alpha('#8B5CF6', 0.5)}`,
                }
              }}
            >
              <CardContent sx={{ p: 3 }}>
                <Box display="flex" flexDirection="column" alignItems="center">
                  <Box 
                    sx={{ 
                      width: 56, 
                      height: 56, 
                      borderRadius: '16px',
                      background: `linear-gradient(135deg, ${alpha('#8B5CF6', 0.2)} 0%, ${alpha('#8B5CF6', 0.05)} 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                    }}
                  >
                    <BusinessCenterIcon sx={{ fontSize: 28, color: '#8B5CF6' }} />
                  </Box>
                  <Typography variant="h3" sx={{ color: DARK_COLORS.text.primary, fontWeight: 800, mb: 0.5 }}>
                    {summary.totalBrands}
                  </Typography>
                  <Typography variant="body2" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 500 }}>
                    브랜드
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
        
        {/* 차트 섹션 */}
        <Grid container spacing={3} mb={5}>
          {/* 플랫폼별 차트 */}
          <Grid item xs={12} md={6}>
            <Paper 
              sx={{ 
                p: 4, 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
              }}
            >
              <Typography 
                variant="h5" 
                gutterBottom 
                sx={{ 
                  fontWeight: 700, 
                  color: DARK_COLORS.text.primary, 
                  mb: 3,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                }}
              >
                <Box 
                  sx={{ 
                    width: 4, 
                    height: 28, 
                    bgcolor: DARK_COLORS.primary, 
                    borderRadius: 2 
                  }} 
                />
                플랫폼별 라이브 방송
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={platformStats} margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
                  <defs>
                    <linearGradient id="colorActive" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={DARK_COLORS.secondary} stopOpacity={0.9}/>
                      <stop offset="100%" stopColor={DARK_COLORS.secondary} stopOpacity={0.6}/>
                    </linearGradient>
                    <linearGradient id="colorPending" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={DARK_COLORS.info} stopOpacity={0.9}/>
                      <stop offset="100%" stopColor={DARK_COLORS.info} stopOpacity={0.6}/>
                    </linearGradient>
                    <linearGradient id="colorEnded" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={DARK_COLORS.text.disabled} stopOpacity={0.5}/>
                      <stop offset="100%" stopColor={DARK_COLORS.text.disabled} stopOpacity={0.2}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(DARK_COLORS.border, 0.3)} vertical={false} />
                  <XAxis 
                    dataKey="platform" 
                    tick={{ fill: DARK_COLORS.text.secondary, fontSize: 12 }}
                    axisLine={{ stroke: DARK_COLORS.border }}
                    tickLine={{ stroke: DARK_COLORS.border }}
                  />
                  <YAxis 
                    tick={{ fill: DARK_COLORS.text.secondary, fontSize: 12 }}
                    axisLine={{ stroke: DARK_COLORS.border }}
                    tickLine={{ stroke: DARK_COLORS.border }}
                  />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: alpha(DARK_COLORS.primary, 0.1) }} />
                  <Legend 
                    wrapperStyle={{ color: DARK_COLORS.text.secondary }}
                    iconType="circle"
                  />
                  <Bar dataKey="active" fill="url(#colorActive)" name="진행중" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="pending" fill="url(#colorPending)" name="예정" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="ended" fill="url(#colorEnded)" name="종료" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
          
          {/* 브랜드별 차트 */}
          <Grid item xs={12} md={6}>
            <Paper 
              sx={{ 
                p: 4, 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
              }}
            >
              <Typography 
                variant="h5" 
                gutterBottom 
                sx={{ 
                  fontWeight: 700, 
                  color: DARK_COLORS.text.primary, 
                  mb: 3,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                }}
              >
                <Box 
                  sx={{ 
                    width: 4, 
                    height: 28, 
                    bgcolor: DARK_COLORS.secondary, 
                    borderRadius: 2 
                  }} 
                />
                브랜드별 라이브 방송
              </Typography>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={brandStats} margin={{ top: 20, right: 20, left: 0, bottom: 60 }}>
                  <defs>
                    <linearGradient id="colorActive2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={DARK_COLORS.secondary} stopOpacity={0.9}/>
                      <stop offset="100%" stopColor={DARK_COLORS.secondary} stopOpacity={0.6}/>
                    </linearGradient>
                    <linearGradient id="colorPending2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={DARK_COLORS.info} stopOpacity={0.9}/>
                      <stop offset="100%" stopColor={DARK_COLORS.info} stopOpacity={0.6}/>
                    </linearGradient>
                    <linearGradient id="colorEnded2" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor={DARK_COLORS.text.disabled} stopOpacity={0.5}/>
                      <stop offset="100%" stopColor={DARK_COLORS.text.disabled} stopOpacity={0.2}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke={alpha(DARK_COLORS.border, 0.3)} vertical={false} />
                  <XAxis 
                    dataKey="brand" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    tick={{ fill: DARK_COLORS.text.secondary, fontSize: 11 }}
                    axisLine={{ stroke: DARK_COLORS.border }}
                    tickLine={{ stroke: DARK_COLORS.border }}
                  />
                  <YAxis 
                    tick={{ fill: DARK_COLORS.text.secondary, fontSize: 12 }}
                    axisLine={{ stroke: DARK_COLORS.border }}
                    tickLine={{ stroke: DARK_COLORS.border }}
                  />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: alpha(DARK_COLORS.secondary, 0.1) }} />
                  <Legend 
                    wrapperStyle={{ color: DARK_COLORS.text.secondary }}
                    iconType="circle"
                  />
                  <Bar dataKey="active" fill="url(#colorActive2)" name="진행중" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="pending" fill="url(#colorPending2)" name="예정" radius={[8, 8, 0, 0]} />
                  <Bar dataKey="ended" fill="url(#colorEnded2)" name="종료" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
        
        {/* 테이블 섹션 */}
        <Grid container spacing={3} mb={5}>
          {/* 플랫폼 테이블 */}
          <Grid item xs={12} md={6}>
            <Paper 
              sx={{ 
                p: 3, 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
              }}
            >
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  fontWeight: 700, 
                  color: DARK_COLORS.text.primary, 
                  mb: 3,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                }}
              >
                <StorefrontIcon sx={{ color: DARK_COLORS.primary }} />
                플랫폼 상세 현황
              </Typography>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        플랫폼
                      </TableCell>
                      <TableCell align="center" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        진행중
                      </TableCell>
                      <TableCell align="center" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        예정
                      </TableCell>
                      <TableCell align="center" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        종료
                      </TableCell>
                      <TableCell align="center" sx={{ color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        전체
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {platformStats.map((platform, index) => (
                      <TableRow 
                        key={index}
                        sx={{ 
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          '&:hover': { 
                            bgcolor: alpha(DARK_COLORS.primary, 0.08),
                          }
                        }}
                        onClick={() => navigate(`/search?channel=${platform.platform}`)}
                      >
                        <TableCell sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Box display="flex" alignItems="center" gap={1.5}>
                            <Avatar 
                              sx={{ 
                                width: 32, 
                                height: 32, 
                                bgcolor: alpha(DARK_COLORS.chart[index % DARK_COLORS.chart.length], 0.2),
                                color: DARK_COLORS.chart[index % DARK_COLORS.chart.length],
                                fontSize: '0.875rem',
                                fontWeight: 700,
                              }}
                            >
                              {platform.platform.charAt(0)}
                            </Avatar>
                            <Typography variant="body2" sx={{ color: DARK_COLORS.text.primary, fontWeight: 600 }}>
                              {platform.platform}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="center" sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Chip 
                            label={platform.active} 
                            size="small" 
                            sx={{ 
                              bgcolor: alpha(DARK_COLORS.secondary, 0.15), 
                              color: DARK_COLORS.secondary, 
                              fontWeight: 700,
                              border: `1px solid ${alpha(DARK_COLORS.secondary, 0.3)}`,
                            }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Chip 
                            label={platform.pending} 
                            size="small" 
                            sx={{ 
                              bgcolor: alpha(DARK_COLORS.info, 0.15), 
                              color: DARK_COLORS.info, 
                              fontWeight: 700,
                              border: `1px solid ${alpha(DARK_COLORS.info, 0.3)}`,
                            }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Chip 
                            label={platform.ended} 
                            size="small" 
                            sx={{ 
                              bgcolor: alpha(DARK_COLORS.text.disabled, 0.15), 
                              color: DARK_COLORS.text.disabled, 
                              fontWeight: 700,
                              border: `1px solid ${alpha(DARK_COLORS.text.disabled, 0.3)}`,
                            }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Typography variant="body2" sx={{ color: DARK_COLORS.text.primary, fontWeight: 700 }}>
                            {platform.total}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
          
          {/* 브랜드 테이블 */}
          <Grid item xs={12} md={6}>
            <Paper 
              sx={{ 
                p: 3, 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
              }}
            >
              <Typography 
                variant="h6" 
                gutterBottom 
                sx={{ 
                  fontWeight: 700, 
                  color: DARK_COLORS.text.primary, 
                  mb: 3,
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1.5,
                }}
              >
                <BusinessCenterIcon sx={{ color: DARK_COLORS.secondary }} />
                브랜드 상세 현황
              </Typography>
              <TableContainer sx={{ maxHeight: 400 }}>
                <Table stickyHeader>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ bgcolor: DARK_COLORS.cardBg, color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        브랜드
                      </TableCell>
                      <TableCell align="center" sx={{ bgcolor: DARK_COLORS.cardBg, color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        진행중
                      </TableCell>
                      <TableCell align="center" sx={{ bgcolor: DARK_COLORS.cardBg, color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        예정
                      </TableCell>
                      <TableCell align="center" sx={{ bgcolor: DARK_COLORS.cardBg, color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        종료
                      </TableCell>
                      <TableCell align="center" sx={{ bgcolor: DARK_COLORS.cardBg, color: DARK_COLORS.text.secondary, fontWeight: 600, borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                        전체
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {brandStats.map((brand, index) => (
                      <TableRow 
                        key={index}
                        sx={{ 
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          '&:hover': { 
                            bgcolor: alpha(DARK_COLORS.secondary, 0.08),
                          }
                        }}
                        onClick={() => navigate(`/search?brand=${brand.brand}`)}
                      >
                        <TableCell sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Box display="flex" alignItems="center" gap={1.5}>
                            <Avatar 
                              sx={{ 
                                width: 32, 
                                height: 32, 
                                bgcolor: alpha(DARK_COLORS.chart[index % DARK_COLORS.chart.length], 0.2),
                                color: DARK_COLORS.chart[index % DARK_COLORS.chart.length],
                                fontSize: '0.875rem',
                                fontWeight: 700,
                              }}
                            >
                              {brand.brand.charAt(0)}
                            </Avatar>
                            <Typography variant="body2" sx={{ color: DARK_COLORS.text.primary, fontWeight: 600 }}>
                              {brand.brand}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="center" sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Chip 
                            label={brand.active} 
                            size="small" 
                            sx={{ 
                              bgcolor: alpha(DARK_COLORS.secondary, 0.15), 
                              color: DARK_COLORS.secondary, 
                              fontWeight: 700,
                              border: `1px solid ${alpha(DARK_COLORS.secondary, 0.3)}`,
                            }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Chip 
                            label={brand.pending} 
                            size="small" 
                            sx={{ 
                              bgcolor: alpha(DARK_COLORS.info, 0.15), 
                              color: DARK_COLORS.info, 
                              fontWeight: 700,
                              border: `1px solid ${alpha(DARK_COLORS.info, 0.3)}`,
                            }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Chip 
                            label={brand.ended} 
                            size="small" 
                            sx={{ 
                              bgcolor: alpha(DARK_COLORS.text.disabled, 0.15), 
                              color: DARK_COLORS.text.disabled, 
                              fontWeight: 700,
                              border: `1px solid ${alpha(DARK_COLORS.text.disabled, 0.3)}`,
                            }}
                          />
                        </TableCell>
                        <TableCell align="center" sx={{ borderBottom: `1px solid ${DARK_COLORS.border}` }}>
                          <Typography variant="body2" sx={{ color: DARK_COLORS.text.primary, fontWeight: 700 }}>
                            {brand.total}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
        
        {/* 최근 방송 현황 */}
        <Grid container spacing={3}>
          {/* 진행중인 방송 */}
          <Grid item xs={12} md={6}>
            <Paper 
              sx={{ 
                p: 3, 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
              }}
            >
              <Box display="flex" alignItems="center" mb={2.5}>
                <Box 
                  sx={{ 
                    width: 40, 
                    height: 40, 
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(DARK_COLORS.secondary, 0.2)} 0%, ${alpha(DARK_COLORS.secondary, 0.05)} 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 1.5,
                  }}
                >
                  <LiveTvIcon sx={{ color: DARK_COLORS.secondary }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: DARK_COLORS.text.primary }}>
                  진행중인 라이브 방송
                </Typography>
              </Box>
              <Divider sx={{ borderColor: DARK_COLORS.border, mb: 2.5 }} />
              {recentActiveEvents.length > 0 ? (
                <Stack spacing={2}>
                  {recentActiveEvents.map((event, index) => (
                    <Card 
                      key={index} 
                      sx={{ 
                        p: 2.5, 
                        cursor: 'pointer',
                        bgcolor: alpha(DARK_COLORS.secondary, 0.05),
                        border: `1px solid ${alpha(DARK_COLORS.secondary, 0.2)}`,
                        borderRadius: 2,
                        transition: 'all 0.3s',
                        '&:hover': { 
                          boxShadow: `0 8px 24px ${alpha(DARK_COLORS.secondary, 0.3)}`,
                          transform: 'translateY(-4px)',
                          border: `1px solid ${alpha(DARK_COLORS.secondary, 0.5)}`,
                        }
                      }}
                      onClick={() => navigate(`/live/${event.event_id}`)}
                    >
                      <Typography variant="body1" sx={{ color: DARK_COLORS.text.primary, fontWeight: 600, mb: 0.5 }}>
                        {event.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: DARK_COLORS.text.secondary }}>
                        {event.channel_name} | {event.subtitle}
                      </Typography>
                      <Box mt={1.5} display="flex" gap={1} flexWrap="wrap">
                        <Chip 
                          label="🔴 LIVE" 
                          size="small" 
                          sx={{ 
                            bgcolor: alpha(DARK_COLORS.secondary, 0.2), 
                            color: DARK_COLORS.secondary,
                            fontWeight: 700,
                            border: `1px solid ${alpha(DARK_COLORS.secondary, 0.4)}`,
                          }} 
                        />
                        {event.tags && event.tags.slice(0, 2).map((tag, idx) => (
                          <Chip 
                            key={idx} 
                            label={tag} 
                            size="small" 
                            sx={{ 
                              bgcolor: alpha(DARK_COLORS.primary, 0.1),
                              color: DARK_COLORS.text.secondary,
                              border: `1px solid ${DARK_COLORS.border}`,
                            }}
                          />
                        ))}
                      </Box>
                    </Card>
                  ))}
                </Stack>
              ) : (
                <Typography variant="body2" sx={{ color: DARK_COLORS.text.secondary, textAlign: 'center', py: 4 }}>
                  진행중인 방송이 없습니다.
                </Typography>
              )}
            </Paper>
          </Grid>
          
          {/* 예정된 방송 */}
          <Grid item xs={12} md={6}>
            <Paper 
              sx={{ 
                p: 3, 
                bgcolor: DARK_COLORS.cardBg,
                border: `1px solid ${DARK_COLORS.border}`,
                borderRadius: 3,
                boxShadow: '0 4px 24px rgba(0, 0, 0, 0.3)',
              }}
            >
              <Box display="flex" alignItems="center" mb={2.5}>
                <Box 
                  sx={{ 
                    width: 40, 
                    height: 40, 
                    borderRadius: 2,
                    background: `linear-gradient(135deg, ${alpha(DARK_COLORS.info, 0.2)} 0%, ${alpha(DARK_COLORS.info, 0.05)} 100%)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mr: 1.5,
                  }}
                >
                  <ScheduleIcon sx={{ color: DARK_COLORS.info }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 700, color: DARK_COLORS.text.primary }}>
                  예정된 라이브 방송
                </Typography>
              </Box>
              <Divider sx={{ borderColor: DARK_COLORS.border, mb: 2.5 }} />
              {recentPendingEvents.length > 0 ? (
                <Stack spacing={2}>
                  {recentPendingEvents.map((event, index) => (
                    <Card 
                      key={index} 
                      sx={{ 
                        p: 2.5, 
                        cursor: 'pointer',
                        bgcolor: alpha(DARK_COLORS.info, 0.05),
                        border: `1px solid ${alpha(DARK_COLORS.info, 0.2)}`,
                        borderRadius: 2,
                        transition: 'all 0.3s',
                        '&:hover': { 
                          boxShadow: `0 8px 24px ${alpha(DARK_COLORS.info, 0.3)}`,
                          transform: 'translateY(-4px)',
                          border: `1px solid ${alpha(DARK_COLORS.info, 0.5)}`,
                        }
                      }}
                      onClick={() => navigate(`/live/${event.event_id}`)}
                    >
                      <Typography variant="body1" sx={{ color: DARK_COLORS.text.primary, fontWeight: 600, mb: 0.5 }}>
                        {event.title}
                      </Typography>
                      <Typography variant="caption" sx={{ color: DARK_COLORS.text.secondary }}>
                        {event.channel_name} | {event.start_date}
                      </Typography>
                      <Box mt={1.5} display="flex" gap={1} flexWrap="wrap">
                        <Chip 
                          label="📅 예정" 
                          size="small" 
                          sx={{ 
                            bgcolor: alpha(DARK_COLORS.info, 0.2), 
                            color: DARK_COLORS.info,
                            fontWeight: 700,
                            border: `1px solid ${alpha(DARK_COLORS.info, 0.4)}`,
                          }} 
                        />
                        {event.tags && event.tags.slice(0, 2).map((tag, idx) => (
                          <Chip 
                            key={idx} 
                            label={tag} 
                            size="small" 
                            sx={{ 
                              bgcolor: alpha(DARK_COLORS.primary, 0.1),
                              color: DARK_COLORS.text.secondary,
                              border: `1px solid ${DARK_COLORS.border}`,
                            }}
                          />
                        ))}
                      </Box>
                    </Card>
                  ))}
                </Stack>
              ) : (
                <Typography variant="body2" sx={{ color: DARK_COLORS.text.secondary, textAlign: 'center', py: 4 }}>
                  예정된 방송이 없습니다.
                </Typography>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
};

export default Dashboard;
