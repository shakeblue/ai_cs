/**
 * 네이버 쇼핑라이브 멀티 브랜드 Mock 데이터
 * 10개 브랜드의 라이브 방송 샘플
 */

export const allBrandsLiveData = [
  // 라네즈 (이미 있는 데이터)
  {
    live_id: 'NAVER_LANEIGE_001',
    platform_name: '네이버',
    brand_name: '라네즈',
    live_title_customer: '라네즈 겨울 수분 특집 라이브',
    live_title_cs: '라네즈 12월 네이버 라이브 수분 케어',
    broadcast_date: '2025-11-28',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000001',
    products: [
      { product_name: '워터뱅크 크림', sale_price: 29900, discount_rate: 35 },
      { product_name: '워터뱅크 에센스', sale_price: 35000, discount_rate: 30 },
    ],
    benefits: {
      discounts: [{ discount_type: '%할인', discount_value: '35%', discount_detail: '최대 35% 할인' }],
      gifts: [{ gift_type: '구매조건형', gift_name: '미니어처 3종 세트', gift_condition: '3만원 이상' }],
      coupons: [{ coupon_type: '플랫폼쿠폰', coupon_name: '5,000원 할인', coupon_value: '5000원' }],
      shipping: [{ shipping_benefit: '무료배송', shipping_detail: '전 상품 무료배송' }],
    },
  },
  
  // 설화수 (상세 정보 있음 - 상세 페이지로 이동)
  {
    live_id: 'NAVER_SULWHASOO_001',
    platform_name: '네이버',
    brand_name: '설화수',
    live_title_customer: '설화수 윤조 에센스 특별 방송',
    live_title_cs: '설화수 12월 네이버 라이브 윤조 에센스',
    broadcast_date: '2025-11-29',
    broadcast_start_time: '15:00',
    broadcast_end_time: '16:30',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000002',
    products: [
      { product_name: '윤조에센스', sale_price: 189000, discount_rate: 20 },
      { product_name: '자음생크림', sale_price: 142000, discount_rate: 25 },
      { product_name: '윤조 3종 세트', sale_price: 320000, discount_rate: 29 },
    ],
    benefits: {
      discounts: [
        { discount_type: '%할인', discount_value: '20%', discount_detail: '윤조에센스 20% 할인' },
        { discount_type: '%할인', discount_value: '29%', discount_detail: '윤조 3종 세트 29% 할인' },
      ],
      gifts: [
        { gift_type: '구매조건형', gift_name: '윤조 미니어처 3종 세트', gift_condition: '20만원 이상' },
        { gift_type: '선착순형', gift_name: '설화수 고급 쇼핑백', gift_condition: '선착순 100명' },
      ],
      coupons: [
        { coupon_type: '브랜드쿠폰', coupon_name: '10,000원 할인', coupon_value: '10000원' },
        { coupon_type: '플랫폼쿠폰', coupon_name: '15,000원 할인', coupon_value: '15000원' },
      ],
      shipping: [
        { shipping_benefit: '무료배송', shipping_detail: '전 상품 무료배송' },
        { shipping_benefit: '특급배송', shipping_detail: '서울/경기 익일 배송' },
      ],
    },
    has_detail: true,  // 상세 정보 있음 플래그
  },
  
  // 아이오페
  {
    live_id: 'NAVER_IOPE_001',
    platform_name: '네이버',
    brand_name: '아이오페',
    live_title_customer: '아이오페 바이오에센스 라이브 특가',
    live_title_cs: '아이오페 12월 네이버 라이브 바이오에센스',
    broadcast_date: '2025-11-30',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000003',
    products: [
      { product_name: '바이오에센스 인텐시브 컨디셔닝', sale_price: 49000, discount_rate: 30 },
      { product_name: '레티놀 크림', sale_price: 38000, discount_rate: 35 },
    ],
    benefits: {
      discounts: [{ discount_type: '%할인', discount_value: '35%', discount_detail: '라이브 특별 할인' }],
      gifts: [{ gift_type: '선착순형', gift_name: '바이오에센스 미니', gift_condition: '선착순 200명', quantity_limit: 200 }],
      coupons: [{ coupon_type: '플랫폼쿠폰', coupon_name: '7,000원 할인', coupon_value: '7000원' }],
      shipping: [{ shipping_benefit: '무료배송', shipping_detail: '전 상품 무료배송' }],
    },
  },
  
  // 헤라
  {
    live_id: 'NAVER_HERA_001',
    platform_name: '네이버',
    brand_name: '헤라',
    live_title_customer: '헤라 루즈홀릭 립스틱 1+1 특가',
    live_title_cs: '헤라 12월 네이버 라이브 립스틱 1+1',
    broadcast_date: '2025-12-01',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000004',
    products: [
      { product_name: '루즈홀릭 립스틱', sale_price: 19900, discount_rate: 40 },
      { product_name: '센슈얼 파우더 매트', sale_price: 24900, discount_rate: 35 },
    ],
    benefits: {
      discounts: [{ discount_type: '1+1', discount_value: '50%', discount_detail: '루즈홀릭 1+1 이벤트' }],
      gifts: [{ gift_type: '구매조건형', gift_name: '립스틱 파우치', gift_condition: '2만원 이상' }],
      coupons: [{ coupon_type: '장바구니쿠폰', coupon_name: '5,000원 할인', coupon_value: '5000원' }],
      shipping: [{ shipping_benefit: '무료배송', shipping_detail: '전 상품 무료배송' }],
    },
  },
  
  // 에스트라
  {
    live_id: 'NAVER_AESTURA_001',
    platform_name: '네이버',
    brand_name: '에스트라',
    live_title_customer: '에스트라 아토배리어 365 크림 특가',
    live_title_cs: '에스트라 12월 네이버 라이브 아토배리어',
    broadcast_date: '2025-12-02',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000005',
    products: [
      { product_name: '아토배리어 365 크림', sale_price: 22000, discount_rate: 40 },
      { product_name: '아토배리어 365 로션', sale_price: 18000, discount_rate: 35 },
    ],
    benefits: {
      discounts: [{ discount_type: '%할인', discount_value: '40%', discount_detail: '민감성 피부 특가' }],
      gifts: [{ gift_type: '증정형', gift_name: '아토배리어 미니 세트', gift_condition: '전 상품 구매 시' }],
      coupons: [{ coupon_type: '브랜드쿠폰', coupon_name: '3,000원 할인', coupon_value: '3000원' }],
      shipping: [{ shipping_benefit: '무료배송', shipping_detail: '전 상품 무료배송' }],
    },
  },
  
  // 이니스프리 (기존 데이터 유지)
  {
    live_id: 'NAVER_INNISFREE_001',
    platform_name: '네이버',
    brand_name: '이니스프리',
    live_title_customer: '이니스프리 그린티 라인 특별 방송',
    live_title_cs: '이니스프리 12월 네이버 라이브 그린티',
    broadcast_date: '2025-12-03',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000006',
    products: [
      { product_name: '그린티 씨드 세럼', sale_price: 24000, discount_rate: 30 },
      { product_name: '그린티 밸런싱 크림', sale_price: 18000, discount_rate: 35 },
    ],
    benefits: {
      discounts: [{ discount_type: '%할인', discount_value: '35%', discount_detail: '그린티 라인 특가' }],
      gifts: [{ gift_type: '구매조건형', gift_name: '그린티 미니 세트', gift_condition: '2만원 이상' }],
      coupons: [{ coupon_type: '플랫폼쿠폰', coupon_name: '4,000원 할인', coupon_value: '4000원' }],
      shipping: [{ shipping_benefit: '무료배송', shipping_detail: '전 상품 무료배송' }],
    },
  },
  
  // 해피바스
  {
    live_id: 'NAVER_HAPPYBATH_001',
    platform_name: '네이버',
    brand_name: '해피바스',
    live_title_customer: '해피바스 바디워시 대용량 특가',
    live_title_cs: '해피바스 12월 네이버 라이브 바디워시',
    broadcast_date: '2025-12-04',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000007',
    products: [
      { product_name: '모이스처 바디워시 900ml', sale_price: 9900, discount_rate: 50 },
      { product_name: '퍼퓸 바디워시 세트', sale_price: 19900, discount_rate: 45 },
    ],
    benefits: {
      discounts: [{ discount_type: '%할인', discount_value: '50%', discount_detail: '대용량 반값 특가' }],
      gifts: [{ gift_type: '구매조건형', gift_name: '샤워볼 증정', gift_condition: '1만원 이상' }],
      coupons: [{ coupon_type: '장바구니쿠폰', coupon_name: '2,000원 할인', coupon_value: '2000원' }],
      shipping: [{ shipping_benefit: '무료배송', shipping_detail: '2만원 이상 무료배송' }],
    },
  },
  
  // 바이탈뷰티
  {
    live_id: 'NAVER_VITALBEAUTIE_001',
    platform_name: '네이버',
    brand_name: '바이탈뷰티',
    live_title_customer: '바이탈뷰티 메타그린 다이어트 특집',
    live_title_cs: '바이탈뷰티 12월 네이버 라이브 메타그린',
    broadcast_date: '2025-12-05',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000008',
    products: [
      { product_name: '메타그린 다이어트', sale_price: 49000, discount_rate: 30 },
      { product_name: '슈퍼콜라겐', sale_price: 39000, discount_rate: 25 },
    ],
    benefits: {
      discounts: [{ discount_type: '%할인', discount_value: '30%', discount_detail: '건강기능식품 특가' }],
      gifts: [{ gift_type: '선착순형', gift_name: '메타그린 7일분', gift_condition: '선착순 300명', quantity_limit: 300 }],
      coupons: [{ coupon_type: '브랜드쿠폰', coupon_name: '10,000원 할인', coupon_value: '10000원' }],
      shipping: [{ shipping_benefit: '무료배송', shipping_detail: '전 상품 무료배송' }],
    },
  },
  
  // 프리메라
  {
    live_id: 'NAVER_PRIMERA_001',
    platform_name: '네이버',
    brand_name: '프리메라',
    live_title_customer: '프리메라 오가니언스 라이브 특가',
    live_title_cs: '프리메라 12월 네이버 라이브 오가니언스',
    broadcast_date: '2025-12-06',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000009',
    products: [
      { product_name: '오가니언스 워터', sale_price: 28000, discount_rate: 30 },
      { product_name: '오가니언스 에멀전', sale_price: 32000, discount_rate: 30 },
    ],
    benefits: {
      discounts: [{ discount_type: '%할인', discount_value: '30%', discount_detail: '오가닉 스킨케어 특가' }],
      gifts: [{ gift_type: '구매조건형', gift_name: '오가니언스 토너 미니', gift_condition: '3만원 이상' }],
      coupons: [{ coupon_type: '플랫폼쿠폰', coupon_name: '5,000원 할인', coupon_value: '5000원' }],
      shipping: [{ shipping_benefit: '무료배송', shipping_detail: '전 상품 무료배송' }],
    },
  },
  
  // 오설록
  {
    live_id: 'NAVER_OSULLOC_001',
    platform_name: '네이버',
    brand_name: '오설록',
    live_title_customer: '오설록 프리미엄 티 세트 특별 방송',
    live_title_cs: '오설록 12월 네이버 라이브 프리미엄 티',
    broadcast_date: '2025-12-07',
    source_url: 'https://view.shoppinglive.naver.com/replays/1000010',
    products: [
      { product_name: '프리미엄 녹차 세트', sale_price: 39000, discount_rate: 25 },
      { product_name: '제주 한라봉 티', sale_price: 15000, discount_rate: 30 },
    ],
    benefits: {
      discounts: [{ discount_type: '%할인', discount_value: '30%', discount_detail: '겨울 티 특가' }],
      gifts: [{ gift_type: '증정형', gift_name: '티백 샘플 세트', gift_condition: '전 상품 구매 시' }],
      coupons: [{ coupon_type: '브랜드쿠폰', coupon_name: '5,000원 할인', coupon_value: '5000원' }],
      shipping: [{ shipping_benefit: '무료배송', shipping_detail: '3만원 이상 무료배송' }],
    },
  },
];

/**
 * 브랜드별 라이브 방송 조회
 */
export const getLivesByBrand = (p_brand_name) => {
  return allBrandsLiveData.filter(_v_live => _v_live.brand_name === p_brand_name);
};

/**
 * 전체 브랜드 목록 조회
 */
export const getAllBrands = () => {
  const _v_brands = new Set();
  allBrandsLiveData.forEach(_v_live => _v_brands.add(_v_live.brand_name));
  return Array.from(_v_brands).sort();
};

/**
 * 키워드로 검색
 */
export const searchAllBrandsLives = (p_keyword = '') => {
  if (!p_keyword) {
    return [];
  }
  
  const _v_lower_keyword = p_keyword.toLowerCase();
  
  return allBrandsLiveData.filter(_v_live => {
    const _v_searchable = `
      ${_v_live.live_title_customer}
      ${_v_live.brand_name}
      ${_v_live.products.map(p => p.product_name).join(' ')}
    `.toLowerCase();
    
    return _v_searchable.includes(_v_lower_keyword);
  });
};

/**
 * 라이브 방송을 이벤트 형식으로 변환
 */
export const convertLiveToEvent = (p_live) => {
  return {
    event_id: p_live.live_id,
    channel_name: p_live.platform_name,
    channel_code: 'NAVER_LIVE',
    title: p_live.live_title_customer,
    subtitle: `${p_live.brand_name} 라이브 방송`,
    description: p_live.broadcast_start_time 
      ? `방송시간: ${p_live.broadcast_start_time} ~ ${p_live.broadcast_end_time} | ${p_live.products.length}개 상품 | ${p_live.benefits.discounts.length}개 할인`
      : `${p_live.products.length}개 상품 | ${p_live.benefits.discounts.length}개 할인 | ${p_live.benefits.gifts.length}개 사은품`,
    start_date: p_live.broadcast_date,
    end_date: p_live.broadcast_date,
    benefit_summary: p_live.benefits.discounts[0]?.discount_detail || '특별 혜택',
    event_url: p_live.source_url,
    status: 'ACTIVE',
    priority: p_live.has_detail ? 10 : 8,  // 상세 정보가 있으면 우선순위 높임
    tags: ['네이버라이브', '라이브방송', p_live.brand_name],
    is_live_detail: p_live.has_detail || false,  // 상세 정보 플래그
  };
};

