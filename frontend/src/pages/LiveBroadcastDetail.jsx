/**
 * 라이브 방송 상세 조회 페이지
 * 수집정보 문서의 모든 항목 표시
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Chip,
  Divider,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Button,
  Stack,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  ArrowBack as ArrowBackIcon,
  ShoppingCart as ShoppingCartIcon,
  LocalOffer as LocalOfferIcon,
  CardGiftcard as CardGiftcardIcon,
  LocalShipping as LocalShippingIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Schedule as ScheduleIcon,
  Event as EventIcon,
} from '@mui/icons-material';
// Mock 데이터 대신 실제 수집 데이터 사용
import { getRealCollectedDetail } from '../mockData/realCollectedData';

const LiveBroadcastDetail = () => {
  const { liveId } = useParams();
  const navigate = useNavigate();
  const [liveData, setLiveData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // ✅ 실제 수집된 데이터 로드
    console.log('🔍 LiveBroadcastDetail - liveId:', liveId);
    console.log('📦 실제 수집 데이터에서 조회 중...');
    
    // 실제 크롤링으로 수집된 데이터에서 조회
    const data = getRealCollectedDetail(liveId);
    
    console.log('📦 LiveBroadcastDetail - 실제 수집 데이터:', data);
    
    if (data) {
      setLiveData(data);
      console.log('✅ LiveBroadcastDetail - 실제 수집 데이터 로드 성공');
    } else {
      console.error('❌ LiveBroadcastDetail - 데이터를 찾을 수 없음');
    }
    setLoading(false);
  }, [liveId]);

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography>로딩 중...</Typography>
      </Container>
    );
  }

  if (!liveData) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">라이브 방송 정보를 찾을 수 없습니다.</Alert>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/search')} sx={{ mt: 2 }}>
          목록으로 돌아가기
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* 상단 헤더 */}
      <Box sx={{ mb: 3 }}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/search')}
          sx={{ mb: 2 }}
        >
          목록으로
        </Button>
        
        <Typography variant="h4" gutterBottom fontWeight="bold">
          {liveData.metadata?.live_title_customer || liveData.live_title_customer}
        </Typography>
        
        <Stack direction="row" spacing={1} sx={{ mt: 1 }}>
          <Chip label={liveData.metadata?.platform_name || liveData.platform_name} color="primary" size="small" />
          <Chip label={liveData.metadata?.brand_name || liveData.brand_name} color="secondary" size="small" />
          <Chip label={liveData.schedule?.broadcast_type || liveData.broadcast_format || '라이브'} variant="outlined" size="small" />
        </Stack>
      </Box>

      {/* ========== 1) 기본 정보 ========== */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
          <InfoIcon sx={{ mr: 1 }} /> 기본 정보
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">라이브 ID</Typography>
            <Typography variant="body1">{liveData.metadata?.live_id || liveData.live_id}</Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">CS용 방송명</Typography>
            <Typography variant="body1">{liveData.metadata?.live_title_cs || liveData.live_title_cs}</Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body2" color="text.secondary">원천 URL</Typography>
            <Typography variant="body1">
              <a href={liveData.metadata?.source_url || liveData.source_url} target="_blank" rel="noopener noreferrer">
                {liveData.metadata?.source_url || liveData.source_url}
              </a>
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* ========== 2) 방송 스케줄 & 혜택 유효시간 ========== */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
          <EventIcon sx={{ mr: 1 }} /> 방송 스케줄 & 혜택 유효시간
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">방송일자</Typography>
            <Typography variant="body1" fontWeight="bold">{liveData.schedule?.broadcast_date || liveData.broadcast_date}</Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">방송시간</Typography>
            <Typography variant="body1">
              {liveData.schedule?.broadcast_start_time || liveData.broadcast_start_time} ~ {liveData.schedule?.broadcast_end_time || liveData.broadcast_end_time}
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <Typography variant="body2" color="text.secondary">혜택 유효기간 타입</Typography>
            <Chip label={liveData.schedule?.benefit_valid_type || liveData.benefit_valid_type} color="warning" size="small" />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">혜택 시작일시</Typography>
            <Typography variant="body1">{liveData.schedule?.benefit_start_datetime || liveData.benefit_start_datetime}</Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">혜택 종료일시</Typography>
            <Typography variant="body1">{liveData.schedule?.benefit_end_datetime || liveData.benefit_end_datetime}</Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* ========== 3) 판매 상품 정보 ========== */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
          <ShoppingCartIcon sx={{ mr: 1 }} /> 판매 상품 정보 ({liveData.products.length}개)
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>순서</TableCell>
                <TableCell>상품명</TableCell>
                <TableCell>옵션</TableCell>
                <TableCell align="right">정가</TableCell>
                <TableCell align="right">판매가</TableCell>
                <TableCell align="right">할인율</TableCell>
                <TableCell>재고</TableCell>
                <TableCell>구분</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {liveData.products.map((product, index) => (
                <TableRow key={product.product_id || index}>
                  <TableCell>{product.product_order || product.display_order || index + 1}</TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={(product.product_type === '대표' || product.is_main_product) ? 'bold' : 'normal'}>
                      {product.product_name}
                    </Typography>
                    {product.sku && (
                      <Typography variant="caption" color="text.secondary">
                        SKU: {product.sku}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{product.product_option || product.set_composition || '-'}</Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" sx={{ textDecoration: 'line-through', color: 'text.secondary' }}>
                      {typeof product.original_price === 'number' 
                        ? `${product.original_price.toLocaleString()}원`
                        : product.original_price || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Typography variant="body2" fontWeight="bold" color="error">
                      {typeof product.sale_price === 'number'
                        ? `${product.sale_price.toLocaleString()}원`
                        : product.sale_price || '-'}
                    </Typography>
                  </TableCell>
                  <TableCell align="right">
                    <Chip label={product.discount_rate || '0%'} color="error" size="small" />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontSize="0.75rem">
                      {product.stock_info || '재고 충분'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {(product.product_type === '대표' || product.is_main_product) && <Chip label="대표" color="primary" size="small" sx={{ mr: 0.5 }} />}
                    {product.product_type === '세트' && <Chip label="세트" color="secondary" size="small" />}
                    {product.is_set_product && <Chip label="세트" color="secondary" size="small" />}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        {/* 세트 상품 구성 상세 */}
        {liveData.products.filter(p => p.is_set_product && p.set_composition).length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" fontWeight="bold" gutterBottom>세트 상품 구성 상세</Typography>
            {liveData.products
              .filter(p => p.is_set_product && p.set_composition)
              .map(product => (
                <Alert key={product.product_id} severity="info" sx={{ mt: 1 }}>
                  <Typography variant="body2" fontWeight="bold">{product.product_name}</Typography>
                  <Typography variant="body2">{product.set_composition}</Typography>
                </Alert>
              ))}
          </Box>
        )}
      </Paper>

      {/* ========== 4) 혜택(Promotion) 구조 ========== */}
      <Typography variant="h5" gutterBottom fontWeight="bold" sx={{ mt: 4, mb: 2 }}>
        혜택 정보
      </Typography>

      {/* 4-a) 할인 관련 */}
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
          <LocalOfferIcon sx={{ mr: 1, color: 'error.main' }} /> 할인 혜택 ({liveData.benefits.discounts.length}개)
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        {liveData.benefits.discounts.map((discount, index) => (
          <Card key={index} sx={{ mb: 1.5, backgroundColor: '#fff3f3' }}>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <Chip label={discount.discount_type} color="error" size="small" />
                <Typography variant="h6" color="error" fontWeight="bold">
                  {discount.discount_value}
                </Typography>
              </Stack>
              <Typography variant="body2">{discount.discount_detail}</Typography>
              {discount.conditions && (
                <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                  조건: {discount.conditions}
                </Typography>
              )}
            </CardContent>
          </Card>
        ))}
      </Paper>

      {/* 4-b) 사은품(GWP) */}
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
          <CardGiftcardIcon sx={{ mr: 1, color: 'success.main' }} /> 사은품 ({liveData.benefits.gifts.length}개)
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        {liveData.benefits.gifts.map((gift, index) => (
          <Card key={index} sx={{ mb: 1.5, backgroundColor: '#f0f9f4' }}>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <Chip label={gift.gift_type} color="success" size="small" />
                {gift.quantity_limit_text && (
                  <Chip label={gift.quantity_limit_text} color="warning" size="small" />
                )}
              </Stack>
              <Typography variant="body1" fontWeight="bold">{gift.gift_name}</Typography>
              {gift.gift_condition && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  조건: {gift.gift_condition}
                </Typography>
              )}
              {gift.gift_quantity && (
                <Typography variant="caption">수량: {gift.gift_quantity}개</Typography>
              )}
            </CardContent>
          </Card>
        ))}
      </Paper>

      {/* 4-c) 쿠폰/적립 */}
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
          🎟️ 쿠폰/적립 ({liveData.benefits.coupons.length}개)
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        {liveData.benefits.coupons.map((coupon, index) => (
          <Card key={index} sx={{ mb: 1.5, backgroundColor: '#f9f6ff' }}>
            <CardContent>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <Chip label={coupon.coupon_type} color="secondary" size="small" />
                <Typography variant="h6" color="secondary" fontWeight="bold">
                  {coupon.coupon_value}
                </Typography>
              </Stack>
              <Typography variant="body1" fontWeight="bold">{coupon.coupon_name}</Typography>
              <Grid container spacing={1} sx={{ mt: 1 }}>
                {coupon.issue_condition && (
                  <Grid item xs={12}>
                    <Typography variant="caption">발급: {coupon.issue_condition}</Typography>
                  </Grid>
                )}
                {coupon.usage_condition && (
                  <Grid item xs={12}>
                    <Typography variant="caption">사용: {coupon.usage_condition}</Typography>
                  </Grid>
                )}
                {coupon.reward_detail && (
                  <Grid item xs={12}>
                    <Typography variant="caption" color="primary">{coupon.reward_detail}</Typography>
                  </Grid>
                )}
              </Grid>
            </CardContent>
          </Card>
        ))}
      </Paper>

      {/* 4-d) 배송 혜택 */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
          <LocalShippingIcon sx={{ mr: 1, color: 'info.main' }} /> 배송 혜택 ({liveData.benefits.shipping.length}개)
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        {liveData.benefits.shipping.map((shipping, index) => (
          <Alert key={index} severity="info" sx={{ mb: 1 }}>
            <Typography variant="body1" fontWeight="bold">{shipping.shipping_benefit}</Typography>
            <Typography variant="body2">{shipping.shipping_detail}</Typography>
            {shipping.shipping_condition && (
              <Typography variant="caption">조건: {shipping.shipping_condition}</Typography>
            )}
          </Alert>
        ))}
      </Paper>

      {/* ========== 5) 중복 적용 정책 (Risk Point) ========== */}
      <Paper sx={{ p: 3, mb: 3, backgroundColor: '#fff8e1' }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
          <WarningIcon sx={{ mr: 1, color: 'warning.main' }} /> 중복 적용 정책 (Risk Point)
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">쿠폰 중복</Typography>
            <Chip 
              label={liveData.duplicate_policy?.coupon_duplicate || liveData.policy?.coupon_duplicate || '정보 없음'} 
              color={(liveData.duplicate_policy?.coupon_duplicate || liveData.policy?.coupon_duplicate) === '가능' ? 'success' : 'error'} 
              size="small" 
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">적립 중복</Typography>
            <Chip 
              label={liveData.duplicate_policy?.point_duplicate || liveData.policy?.reward_duplicate || '정보 없음'} 
              color={(liveData.duplicate_policy?.point_duplicate || liveData.policy?.reward_duplicate) === '가능' ? 'success' : 'error'} 
              size="small" 
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">타행사 중복</Typography>
            <Typography variant="body2">{liveData.duplicate_policy?.other_promotion_duplicate || liveData.policy?.other_event_combination || '정보 없음'}</Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography variant="body2" color="text.secondary">임직원 할인 적용</Typography>
            <Chip 
              label={liveData.duplicate_policy?.employee_discount || liveData.policy?.employee_discount_applicable || '정보 없음'} 
              color={(liveData.duplicate_policy?.employee_discount || liveData.policy?.employee_discount_applicable) === '가능' ? 'success' : 'error'} 
              size="small" 
            />
          </Grid>
          <Grid item xs={12}>
            <Alert severity="warning">
              <Typography variant="body2">{liveData.duplicate_policy?.duplicate_note || liveData.policy?.policy_detail || '중복 적용 정책을 확인해주세요.'}</Typography>
            </Alert>
          </Grid>
        </Grid>
      </Paper>

      {/* ========== 6) 제외/제한 사항 ========== */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" sx={{ display: 'flex', alignItems: 'center' }}>
          ⚠️ 제외/제한 사항
        </Typography>
        <Divider sx={{ mb: 2 }} />
        
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="body2" fontWeight="bold">제외 상품</Typography>
            <Typography variant="body2" color="text.secondary">
              {Array.isArray(liveData.restrictions?.excluded_products) 
                ? liveData.restrictions.excluded_products.join(', ') || '없음'
                : liveData.restrictions?.excluded_products || '없음'}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body2" fontWeight="bold">채널 제한</Typography>
            <Typography variant="body2" color="text.secondary">
              {Array.isArray(liveData.restrictions?.channel_restrictions) 
                ? liveData.restrictions.channel_restrictions.join(', ') || '없음'
                : liveData.restrictions?.channel_restriction || '없음'}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body2" fontWeight="bold">결제수단 제한</Typography>
            <Typography variant="body2" color="text.secondary">
              {Array.isArray(liveData.restrictions?.payment_restrictions) 
                ? liveData.restrictions.payment_restrictions.join(', ') || '없음'
                : liveData.restrictions?.payment_restriction || '없음'}
            </Typography>
          </Grid>
          <Grid item xs={12}>
            <Typography variant="body2" fontWeight="bold">지역/배송 제한</Typography>
            <Typography variant="body2" color="text.secondary">
              {Array.isArray(liveData.restrictions?.region_restrictions) 
                ? liveData.restrictions.region_restrictions.join(', ') || '없음'
                : liveData.restrictions?.region_restriction || '없음'}
            </Typography>
          </Grid>
          {(Array.isArray(liveData.restrictions?.other_restrictions) 
              ? liveData.restrictions.other_restrictions.length > 0
              : liveData.restrictions?.other_restrictions) && (
            <Grid item xs={12}>
              <Alert severity="warning">
                <Typography variant="body2">
                  {Array.isArray(liveData.restrictions.other_restrictions) 
                    ? liveData.restrictions.other_restrictions.join(', ')
                    : liveData.restrictions.other_restrictions}
                </Typography>
              </Alert>
            </Grid>
          )}
        </Grid>
      </Paper>

      {/* ========== 7) 라이브 특화 정보 (STT 기반) ========== */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" fontWeight="bold">
            <ScheduleIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
            라이브 특화 정보 (STT 기반)
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          {/* 핵심 멘트 */}
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>핵심 세일즈 멘트</Typography>
          {(liveData.live_specific?.key_mentions || liveData.stt_info?.key_message || []).map((message, index) => (
            <Alert key={index} severity="info" sx={{ mb: 1 }}>
              {message}
            </Alert>
          ))}
          {!(liveData.live_specific?.key_mentions || liveData.stt_info?.key_message)?.length && (
            <Typography variant="body2" color="text.secondary">정보 없음</Typography>
          )}
          
          {/* 방송 QA */}
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 3 }}>시청자 QA</Typography>
          {(liveData.live_specific?.broadcast_qa || liveData.stt_info?.broadcast_qa || []).map((qa, index) => (
            <Card key={index} sx={{ mb: 1 }}>
              <CardContent>
                <Typography variant="body2" fontWeight="bold" color="primary">Q. {qa.question}</Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>A. {qa.answer}</Typography>
              </CardContent>
            </Card>
          ))}
          {!(liveData.live_specific?.broadcast_qa || liveData.stt_info?.broadcast_qa)?.length && (
            <Typography variant="body2" color="text.secondary">정보 없음</Typography>
          )}
          
          {/* 타임라인 */}
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 3 }}>방송 타임라인</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell width="100px">시간</TableCell>
                  <TableCell>내용</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(liveData.live_specific?.timeline || liveData.stt_info?.timeline_summary || []).map((timeline, index) => (
                  <TableRow key={index}>
                    <TableCell>{timeline.time}</TableCell>
                    <TableCell>{timeline.content || timeline.description}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          {!(liveData.live_specific?.timeline || liveData.stt_info?.timeline_summary)?.length && (
            <Typography variant="body2" color="text.secondary">정보 없음</Typography>
          )}
        </AccordionDetails>
      </Accordion>

      {/* ========== 8) CS 응대용 정보 ========== */}
      <Accordion sx={{ mb: 4 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" fontWeight="bold">
            💬 CS 응대용 정보
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          {/* 예상 질문 */}
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>예상 고객 질문</Typography>
          <Box sx={{ mb: 3 }}>
            {(liveData.cs_info?.expected_questions || liveData.cs_response?.expected_questions || []).map((question, index) => (
              <Chip key={index} label={question} sx={{ mr: 1, mb: 1 }} />
            ))}
            {!(liveData.cs_info?.expected_questions || liveData.cs_response?.expected_questions)?.length && (
              <Typography variant="body2" color="text.secondary">정보 없음</Typography>
            )}
          </Box>
          
          {/* 응답 스크립트 */}
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>CS 응답 스크립트</Typography>
          {(liveData.cs_info?.response_scripts || liveData.cs_response?.response_scripts || []).map((script, index) => (
            <Card key={index} sx={{ mb: 2, backgroundColor: '#f5f5f5' }}>
              <CardContent>
                {typeof script === 'string' ? (
                  <Typography variant="body2">
                    {index + 1}. {script}
                  </Typography>
                ) : (
                  <>
                    <Typography variant="body2" fontWeight="bold" color="primary">
                      Q. {script.question}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      A. {script.answer}
                    </Typography>
                  </>
                )}
              </CardContent>
            </Card>
          ))}
          {!(liveData.cs_info?.response_scripts || liveData.cs_response?.response_scripts)?.length && (
            <Typography variant="body2" color="text.secondary">정보 없음</Typography>
          )}
          
          {/* 리스크 포인트 */}
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ mt: 3 }}>
            ⚠️ 리스크 포인트
          </Typography>
          {(liveData.cs_info?.risk_points || liveData.cs_response?.risk_points || []).map((risk, index) => (
            <Alert key={index} severity="error" sx={{ mb: 1 }}>
              {risk}
            </Alert>
          ))}
          {!(liveData.cs_info?.risk_points || liveData.cs_response?.risk_points)?.length && (
            <Typography variant="body2" color="text.secondary">정보 없음</Typography>
          )}
          
          {/* CS 노트 */}
          {(liveData.cs_info?.cs_note || liveData.cs_info?.cs_notes || liveData.cs_response?.cs_note) && (
            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2" fontWeight="bold">CS 노트</Typography>
              <Typography variant="body2">{liveData.cs_info?.cs_note || liveData.cs_info?.cs_notes || liveData.cs_response?.cs_note}</Typography>
            </Alert>
          )}
        </AccordionDetails>
      </Accordion>

      {/* 하단 버튼 */}
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Button 
          variant="contained" 
          size="large"
          onClick={() => window.open(liveData.metadata?.source_url || liveData.source_url, '_blank')}
          sx={{ mr: 2 }}
        >
          라이브 방송 보기
        </Button>
        <Button 
          variant="outlined" 
          size="large"
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/search')}
        >
          목록으로 돌아가기
        </Button>
      </Box>
    </Container>
  );
};

export default LiveBroadcastDetail;

