/**
 * 네이버 쇼핑라이브 설화수 브랜드 전체 방송 Mock 데이터
 * 수집정보 문서의 8개 카테고리 모두 포함
 * 
 * @수집정보 기준:
 * 1) 기본 정보 (Metadata)
 * 2) 방송 스케줄 & 혜택 유효시간
 * 3) 판매 상품 정보
 * 4) 혜택(Promotion) 구조
 * 5) 중복 적용 정책
 * 6) 제외/제한 사항
 * 7) 라이브 특화 정보
 * 8) CS 응대용 정보
 */

export const sulwhasooLivesData = [
  // 실제 네이버 쇼핑라이브 설화수 방송 (2025년 12월)
  
  // 1번 방송: 12월 2일 홀리데이 라이브먼 대축제
  {
    metadata: {
      live_id: 'NAVER_SULWHASOO_LIVE_001',
      platform_name: '네이버',
      brand_name: '설화수',
      live_title_customer: '설화수 홀리데이 라이브먼 대축제',
      live_title_cs: '설화수 12월 네이버 라이브 홀리데이 대축제',
      source_url: 'https://shoppinglive.naver.com/lives/302214',
      thumbnail_url: '',
      status: '예정'
    },
    schedule: {
      broadcast_date: '2025-12-02',
      broadcast_start_time: '20:05',
      broadcast_end_time: '21:30',
      benefit_valid_type: '당일23:59',
      benefit_start_datetime: '2025-12-02 20:05:00',
      benefit_end_datetime: '2025-12-02 23:59:59',
      broadcast_type: '단독라이브'
    },
    products: [
      {
        product_order: 1,
        product_name: '윤조에센스 인텐시브 리뉴잉 60ml',
        sku: 'SWS-HOLIDAY-001',
        original_price: '236,000원',
        sale_price: '177,000원',
        discount_rate: '25%',
        product_type: '대표',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: ''
      },
      {
        product_order: 2,
        product_name: '자음생크림 60ml 홀리데이 에디션',
        sku: 'SWS-HOLIDAY-002',
        original_price: '189,000원',
        sale_price: '132,300원',
        discount_rate: '30%',
        product_type: '일반',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: ''
      }
    ],
    benefits: {
      discounts: [
        {
          discount_type: '%할인',
          discount_detail: '홀리데이 특별 할인 최대 30%',
          discount_condition: '라이브 방송 중 결제 시',
          discount_valid_period: '방송 중'
        }
      ],
      gifts: [
        {
          gift_type: '증정형',
          gift_name: '홀리데이 한정 파우치',
          gift_condition: '전원 증정',
          gift_quantity_limit: ''
        }
      ],
      coupons: [
        {
          coupon_type: '브랜드쿠폰',
          coupon_detail: '설화수 20,000원 할인',
          coupon_issue_condition: '다운로드 필요',
          point_condition: '네이버페이 3% 적립'
        }
      ],
      shipping: [
        {
          shipping_type: '무료배송',
          shipping_detail: '전 상품 무료배송',
          shipping_condition: '구매 금액 무관'
        }
      ]
    },
    duplicate_policy: {
      coupon_duplicate: '불가',
      point_duplicate: '가능',
      other_promotion_duplicate: '불가',
      employee_discount: '불가',
      duplicate_note: '쿠폰은 1개만 선택 가능'
    },
    restrictions: {
      excluded_products: [],
      channel_restrictions: ['네이버 앱/웹만'],
      payment_restrictions: [],
      region_restrictions: ['도서산간 배송비 5,000원'],
      other_restrictions: []
    },
    live_specific: {
      key_mentions: ['홀리데이 특별 혜택!', '최대 30% 할인'],
      broadcast_qa: [],
      timeline: []
    },
    cs_info: {
      expected_questions: ['가격이 얼마인가요?', '배송은 언제 되나요?'],
      response_scripts: ['홀리데이 특별 할인가로 제공됩니다.', '주문 후 2-3일 내 배송됩니다.'],
      risk_points: ['⚠️ 쿠폰 중복 사용 불가'],
      cs_note: '홀리데이 특별 방송입니다.'
    }
  },

  // 2번 방송: 12월 15일 홀리데이 특집 최대혜택
  {
    metadata: {
      live_id: 'NAVER_SULWHASOO_LIVE_002',
      platform_name: '네이버',
      brand_name: '설화수',
      live_title_customer: '설화수🎄홀리데이 특집 12월 최대혜택 LIVE',
      live_title_cs: '설화수 12월 네이버 라이브 홀리데이 최대혜택',
      source_url: 'https://shoppinglive.naver.com/lives/302315',
      thumbnail_url: '',
      status: '예정'
    },
    schedule: {
      broadcast_date: '2025-12-15',
      broadcast_start_time: '10:30',
      broadcast_end_time: '12:00',
      benefit_valid_type: '당일23:59',
      benefit_start_datetime: '2025-12-15 10:30:00',
      benefit_end_datetime: '2025-12-15 23:59:59',
      broadcast_type: '단독라이브'
    },
    products: [
      {
        product_order: 1,
        product_name: '윤조 3종 홀리데이 세트',
        sku: 'SWS-HOLIDAY-SET-001',
        original_price: '450,000원',
        sale_price: '292,500원',
        discount_rate: '35%',
        product_type: '세트',
        stock_info: '한정 100세트',
        set_composition: '윤조에센스 60ml + 자음생크림 60ml + 자음생 아이크림 25ml',
        product_url: ''
      }
    ],
    benefits: {
      discounts: [
        {
          discount_type: '%할인',
          discount_detail: '12월 최대 혜택 35% 할인',
          discount_condition: '한정 100세트',
          discount_valid_period: '당일 23:59까지'
        }
      ],
      gifts: [
        {
          gift_type: '선착순형',
          gift_name: '홀리데이 한정 에디션 세트',
          gift_condition: '선착순',
          gift_quantity_limit: '선착순 50명'
        }
      ],
      coupons: [
        {
          coupon_type: '브랜드쿠폰',
          coupon_detail: '설화수 30,000원 할인',
          coupon_issue_condition: '다운로드 필요',
          point_condition: ''
        }
      ],
      shipping: [
        {
          shipping_type: '무료배송',
          shipping_detail: '전 상품 무료배송',
          shipping_condition: '구매 금액 무관'
        }
      ]
    },
    duplicate_policy: {
      coupon_duplicate: '불가',
      point_duplicate: '가능',
      other_promotion_duplicate: '불가',
      employee_discount: '불가',
      duplicate_note: '쿠폰은 1개만 선택 가능'
    },
    restrictions: {
      excluded_products: [],
      channel_restrictions: ['네이버 앱/웹만'],
      payment_restrictions: [],
      region_restrictions: ['도서산간 배송비 5,000원'],
      other_restrictions: ['한정 수량으로 조기 품절 가능']
    },
    live_specific: {
      key_mentions: ['12월 최대 혜택!', '한정 100세트', '35% 할인'],
      broadcast_qa: [],
      timeline: []
    },
    cs_info: {
      expected_questions: ['세트 구성이 어떻게 되나요?', '재고는 충분한가요?'],
      response_scripts: ['윤조에센스, 자음생크림, 아이크림 3종 세트입니다.', '한정 100세트로 조기 품절될 수 있습니다.'],
      risk_points: ['⚠️ 한정 100세트', '⚠️ 조기 품절 가능'],
      cs_note: '12월 최대 혜택 방송입니다.'
    }
  },

  // 3번 방송: 12월 17일 크리스마스&연말 BEST 선물템
  {
    metadata: {
      live_id: 'NAVER_SULWHASOO_LIVE_003',
      platform_name: '네이버',
      brand_name: '설화수',
      live_title_customer: '[설화수] 크리스마스&연말 BEST 선물템🎁',
      live_title_cs: '설화수 12월 네이버 라이브 크리스마스 선물',
      source_url: 'https://shoppinglive.naver.com/lives/302417',
      thumbnail_url: '',
      status: '예정'
    },
    schedule: {
      broadcast_date: '2025-12-17',
      broadcast_start_time: '20:00',
      broadcast_end_time: '21:30',
      benefit_valid_type: '기간형',
      benefit_start_datetime: '2025-12-17 20:00:00',
      benefit_end_datetime: '2025-12-25 23:59:59',
      broadcast_type: '단독라이브'
    },
    products: [
      {
        product_order: 1,
        product_name: '윤조 선물 세트 (크리스마스 에디션)',
        sku: 'SWS-XMAS-GIFT-001',
        original_price: '350,000원',
        sale_price: '245,000원',
        discount_rate: '30%',
        product_type: '세트',
        stock_info: '한정 200세트',
        set_composition: '윤조에센스 60ml + 선물 포장 + 크리스마스 카드',
        product_url: ''
      },
      {
        product_order: 2,
        product_name: '자음생 선물 세트 (연말 에디션)',
        sku: 'SWS-NEWYEAR-GIFT-001',
        original_price: '280,000원',
        sale_price: '196,000원',
        discount_rate: '30%',
        product_type: '세트',
        stock_info: '한정 150세트',
        set_composition: '자음생크림 60ml + 선물 포장',
        product_url: ''
      }
    ],
    benefits: {
      discounts: [
        {
          discount_type: '%할인',
          discount_detail: '크리스마스 선물 세트 30% 할인',
          discount_condition: '한정 수량',
          discount_valid_period: '12월 25일까지'
        }
      ],
      gifts: [
        {
          gift_type: '증정형',
          gift_name: '크리스마스 한정 쇼핑백',
          gift_condition: '전원 증정',
          gift_quantity_limit: ''
        }
      ],
      coupons: [
        {
          coupon_type: '브랜드쿠폰',
          coupon_detail: '설화수 25,000원 할인',
          coupon_issue_condition: '다운로드 필요',
          point_condition: '네이버페이 5% 적립'
        }
      ],
      shipping: [
        {
          shipping_type: '무료배송',
          shipping_detail: '전 상품 무료배송',
          shipping_condition: '구매 금액 무관'
        },
        {
          shipping_type: '선물포장',
          shipping_detail: '프리미엄 선물 포장 서비스',
          shipping_condition: '선물 세트 구매 시 무료'
        }
      ]
    },
    duplicate_policy: {
      coupon_duplicate: '불가',
      point_duplicate: '가능',
      other_promotion_duplicate: '불가',
      employee_discount: '가능 (일부)',
      duplicate_note: '쿠폰은 1개만 선택 가능, 임직원 할인은 브랜드 쿠폰과만 중복 가능'
    },
    restrictions: {
      excluded_products: [],
      channel_restrictions: ['네이버 앱/웹만'],
      payment_restrictions: [],
      region_restrictions: ['도서산간 배송비 5,000원'],
      other_restrictions: ['한정 수량으로 조기 품절 가능', '선물 포장은 선물 세트만 제공']
    },
    live_specific: {
      key_mentions: ['크리스마스 선물 추천!', '프리미엄 포장 무료', '30% 할인'],
      broadcast_qa: [],
      timeline: []
    },
    cs_info: {
      expected_questions: ['선물 포장은 어떻게 되나요?', '배송은 언제 되나요?', '크리스마스 전에 받을 수 있나요?'],
      response_scripts: ['선물 세트 구매 시 프리미엄 포장이 무료로 제공됩니다.', '주문 후 2-3일 내 배송됩니다.', '12월 20일까지 주문하시면 크리스마스 전 배송 가능합니다.'],
      risk_points: ['⚠️ 한정 수량', '⚠️ 12월 20일 이후 주문은 크리스마스 이후 배송 가능'],
      cs_note: '크리스마스 선물 특별 방송입니다.'
    }
  },

  // 4번 방송: 12월 24일 크리스마스 홀리데이 라이브
  {
    metadata: {
      live_id: 'NAVER_SULWHASOO_LIVE_004',
      platform_name: '네이버',
      brand_name: '설화수',
      live_title_customer: '설화수🎄크리스마스😴 홀리데이 라이브 연말최종혜택',
      live_title_cs: '설화수 12월 네이버 라이브 크리스마스 최종 혜택',
      source_url: 'https://shoppinglive.naver.com/lives/302524',
      thumbnail_url: '',
      status: '예정'
    },
    schedule: {
      broadcast_date: '2025-12-24',
      broadcast_start_time: '20:00',
      broadcast_end_time: '22:00',
      benefit_valid_type: '기간형',
      benefit_start_datetime: '2025-12-24 20:00:00',
      benefit_end_datetime: '2025-12-31 23:59:59',
      broadcast_type: '단독라이브'
    },
    products: [
      {
        product_order: 1,
        product_name: '윤조 럭셔리 5종 세트 (연말 한정)',
        sku: 'SWS-NEWYEAR-LUXURY-001',
        original_price: '850,000원',
        sale_price: '510,000원',
        discount_rate: '40%',
        product_type: '세트',
        stock_info: '한정 50세트',
        set_composition: '윤조에센스 60ml + 자음생크림 60ml + 자음생 아이크림 25ml + 순행클렌징폼 200ml + 퍼펙팅쿠션 15g',
        product_url: ''
      },
      {
        product_order: 2,
        product_name: '윤조에센스 단품 (크리스마스 특가)',
        sku: 'SWS-XMAS-ESSENCE-001',
        original_price: '236,000원',
        sale_price: '165,200원',
        discount_rate: '30%',
        product_type: '대표',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: ''
      }
    ],
    benefits: {
      discounts: [
        {
          discount_type: '%할인',
          discount_detail: '연말 최종 혜택 최대 40% 할인',
          discount_condition: '럭셔리 5종 세트',
          discount_valid_period: '12월 31일까지'
        },
        {
          discount_type: '금액할인',
          discount_detail: '50만원 이상 구매 시 추가 50,000원 할인',
          discount_condition: '50만원 이상 구매',
          discount_valid_period: '12월 31일까지'
        }
      ],
      gifts: [
        {
          gift_type: '증정형',
          gift_name: '연말 VIP 럭셔리 키트',
          gift_condition: '세트 구매 시 전원 증정',
          gift_quantity_limit: ''
        },
        {
          gift_type: '선착순형',
          gift_name: '크리스마스 한정 에디션 파우치',
          gift_condition: '선착순',
          gift_quantity_limit: '선착순 100명'
        }
      ],
      coupons: [
        {
          coupon_type: '브랜드쿠폰',
          coupon_detail: '설화수 VIP 50,000원 할인',
          coupon_issue_condition: '다운로드 필요',
          point_condition: ''
        },
        {
          coupon_type: '플랫폼쿠폰',
          coupon_detail: '네이버페이 40,000원 + 5% 적립',
          coupon_issue_condition: '네이버페이 결제 시',
          point_condition: '5% 추가 적립'
        }
      ],
      shipping: [
        {
          shipping_type: '무료배송',
          shipping_detail: '전 상품 무료배송',
          shipping_condition: '구매 금액 무관'
        },
        {
          shipping_type: '특급배송',
          shipping_detail: '전국 특급배송 (당일/익일)',
          shipping_condition: '럭셔리 세트 구매 시'
        }
      ]
    },
    duplicate_policy: {
      coupon_duplicate: '불가',
      point_duplicate: '가능',
      other_promotion_duplicate: '불가',
      employee_discount: '가능 (일부)',
      duplicate_note: '쿠폰은 1개만 선택 가능, 50만원 이상 추가 할인은 자동 적용'
    },
    restrictions: {
      excluded_products: [],
      channel_restrictions: ['네이버 앱/웹만'],
      payment_restrictions: [],
      region_restrictions: ['도서산간 배송비 10,000원'],
      other_restrictions: ['한정 수량으로 조기 품절 가능', '연말 특별 혜택은 12월 31일까지']
    },
    live_specific: {
      key_mentions: ['연말 최종 혜택!', '최대 40% 할인', '럭셔리 5종 세트 한정 50개', '50만원 이상 5만원 추가 할인'],
      broadcast_qa: [],
      timeline: []
    },
    cs_info: {
      expected_questions: ['럭셔리 5종 세트 구성이 어떻게 되나요?', '50만원 이상 추가 할인은 자동으로 적용되나요?', '연말까지 혜택이 계속되나요?'],
      response_scripts: ['윤조에센스, 자음생크림, 아이크림, 순행클렌징폼, 퍼펙팅쿠션 5종 세트입니다.', '네, 50만원 이상 장바구니에 담으시면 결제 시 자동으로 5만원 추가 할인이 적용됩니다.', '네, 혜택은 12월 31일까지 계속됩니다.'],
      risk_points: ['⚠️ 럭셔리 5종 세트 한정 50세트', '⚠️ 선착순 파우치 100개', '⚠️ 쿠폰 중복 사용 불가', '⚠️ 혜택은 12월 31일까지'],
      cs_note: '크리스마스 및 연말 최종 혜택 방송입니다.'
    }
  },

  // 기존 Mock 데이터 (테스트용)
  
  // 5번 방송: 윤조에센스 특별 방송 (이미 구현된 상세 버전)
  {
    metadata: {
      live_id: 'NAVER_SULWHASOO_001',
      platform_name: '네이버',
      brand_name: '설화수',
      live_title_customer: '설화수 윤조 에센스 특별 방송',
      live_title_cs: '설화수 12월 네이버 라이브 윤조 에센스',
      source_url: 'https://view.shoppinglive.naver.com/replays/1764981',
      thumbnail_url: '',
      status: '다시보기'
    },
    schedule: {
      broadcast_date: '2025-11-29',
      broadcast_start_time: '15:00',
      broadcast_end_time: '16:30',
      benefit_valid_type: '당일23:59',
      benefit_start_datetime: '2025-11-29 00:00:00',
      benefit_end_datetime: '2025-11-29 23:59:59',
      broadcast_type: '단독라이브'
    },
    products: [
      {
        product_order: 1,
        product_name: '윤조에센스 인텐시브 리뉴잉',
        sku: 'SWS-YJ-001',
        original_price: '236,000원',
        sale_price: '189,000원',
        discount_rate: '20%',
        product_type: '대표',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: 'https://www.sulwhasoo.com/kr/ko/products/concentrated_ginseng_renewing_essence.html'
      },
      {
        product_order: 2,
        product_name: '자음생크림',
        sku: 'SWS-JU-002',
        original_price: '189,000원',
        sale_price: '142,000원',
        discount_rate: '25%',
        product_type: '일반',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: ''
      }
    ],
    benefits: {
      discounts: [
        {
          discount_type: '%할인',
          discount_detail: '윤조에센스 20% 할인',
          discount_condition: '라이브 방송 중 결제 시',
          discount_valid_period: '방송 중'
        }
      ],
      gifts: [
        {
          gift_type: '구매조건형',
          gift_name: '윤조 미니어처 3종 세트',
          gift_condition: '20만원 이상 구매',
          gift_quantity_limit: ''
        }
      ],
      coupons: [
        {
          coupon_type: '브랜드쿠폰',
          coupon_detail: '설화수 10,000원 할인',
          coupon_issue_condition: '다운로드 필요',
          point_condition: '네이버페이 3% 적립'
        }
      ],
      shipping: [
        {
          shipping_type: '무료배송',
          shipping_detail: '전 상품 무료배송',
          shipping_condition: '구매 금액 무관'
        }
      ]
    },
    duplicate_policy: {
      coupon_duplicate: '불가',
      point_duplicate: '가능',
      other_promotion_duplicate: '불가',
      employee_discount: '불가',
      duplicate_note: '쿠폰은 1개만 선택 가능, 적립은 별도 적용'
    },
    restrictions: {
      excluded_products: ['윤조 리미티드 에디션'],
      channel_restrictions: ['네이버 앱/웹만'],
      payment_restrictions: [],
      region_restrictions: ['도서산간 배송비 5,000원'],
      other_restrictions: ['품절 시 조기 종료']
    },
    live_specific: {
      key_mentions: [
        '설화수의 대표 제품 윤조에센스! 오늘만 20% 특가입니다',
        '한방 성분의 힘으로 피부 탄력과 윤기를 동시에'
      ],
      broadcast_qa: [
        { question: '윤조에센스는 어떤 피부에 좋나요?', answer: '모든 피부 타입, 특히 탄력과 윤기가 필요한 피부에 좋습니다' }
      ],
      timeline: [
        { time: '00:00', description: '방송 시작' },
        { time: '00:05', description: '혜택 안내' }
      ]
    },
    cs_info: {
      expected_questions: [
        '윤조에센스 가격이 얼마인가요?',
        '쿠폰 중복 사용 가능한가요?',
        '배송비는 무료인가요?'
      ],
      response_scripts: [
        '윤조에센스는 정가 236,000원에서 20% 할인된 189,000원입니다.',
        '쿠폰은 1개만 선택 가능하며, 네이버페이 적립은 별도로 받으실 수 있습니다.',
        '전 상품 무료배송이 제공됩니다.'
      ],
      risk_points: [
        '⚠️ 쿠폰 중복 사용 불가',
        '⚠️ 리미티드 에디션 제외',
        '⚠️ 방송 중에만 특가 적용'
      ],
      cs_note: '설화수 윤조 에센스 라이브 방송 관련 문의입니다.'
    }
  },

  // 2번 방송: 자음생크림 겨울 특집
  {
    metadata: {
      live_id: 'NAVER_SULWHASOO_002',
      platform_name: '네이버',
      brand_name: '설화수',
      live_title_customer: '설화수 자음생크림 겨울 보습 특집',
      live_title_cs: '설화수 12월 네이버 라이브 자음생크림',
      source_url: 'https://view.shoppinglive.naver.com/replays/1764982',
      thumbnail_url: '',
      status: '다시보기'
    },
    schedule: {
      broadcast_date: '2025-11-28',
      broadcast_start_time: '14:00',
      broadcast_end_time: '15:00',
      benefit_valid_type: '당일23:59',
      benefit_start_datetime: '2025-11-28 00:00:00',
      benefit_end_datetime: '2025-11-28 23:59:59',
      broadcast_type: '단독라이브'
    },
    products: [
      {
        product_order: 1,
        product_name: '자음생크림 60ml',
        sku: 'SWS-JU-001',
        original_price: '189,000원',
        sale_price: '132,300원',
        discount_rate: '30%',
        product_type: '대표',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: 'https://www.sulwhasoo.com/kr/ko/products/concentrated_ginseng_renewing_cream.html'
      },
      {
        product_order: 2,
        product_name: '자음생 아이크림 25ml',
        sku: 'SWS-EYE-001',
        original_price: '115,000원',
        sale_price: '86,250원',
        discount_rate: '25%',
        product_type: '일반',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: ''
      },
      {
        product_order: 3,
        product_name: '자음생 2종 겨울 세트',
        sku: 'SWS-WINTER-SET-001',
        original_price: '304,000원',
        sale_price: '199,000원',
        discount_rate: '35%',
        product_type: '세트',
        stock_info: '한정 100세트',
        set_composition: '자음생크림 60ml + 자음생 아이크림 25ml',
        product_url: ''
      }
    ],
    benefits: {
      discounts: [
        {
          discount_type: '%할인',
          discount_detail: '자음생크림 30% 할인',
          discount_condition: '라이브 방송 중 결제 시',
          discount_valid_period: '방송 중'
        },
        {
          discount_type: '%할인',
          discount_detail: '자음생 2종 세트 35% 할인',
          discount_condition: '한정 100세트',
          discount_valid_period: '당일 23:59까지'
        }
      ],
      gifts: [
        {
          gift_type: '구매조건형',
          gift_name: '자음생 에멀젼 미니 30ml',
          gift_condition: '15만원 이상 구매',
          gift_quantity_limit: ''
        },
        {
          gift_type: '선착순형',
          gift_name: '겨울 한정 파우치',
          gift_condition: '선착순',
          gift_quantity_limit: '선착순 200명'
        },
        {
          gift_type: '증정형',
          gift_name: '자음생 샘플 5종',
          gift_condition: '전원 증정',
          gift_quantity_limit: ''
        }
      ],
      coupons: [
        {
          coupon_type: '브랜드쿠폰',
          coupon_detail: '설화수 15,000원 할인',
          coupon_issue_condition: '다운로드 필요',
          point_condition: ''
        },
        {
          coupon_type: '플랫폼쿠폰',
          coupon_detail: '네이버페이 20,000원 + 5% 적립',
          coupon_issue_condition: '네이버페이 결제 시',
          point_condition: '5% 추가 적립'
        }
      ],
      shipping: [
        {
          shipping_type: '무료배송',
          shipping_detail: '전 상품 무료배송',
          shipping_condition: '구매 금액 무관'
        },
        {
          shipping_type: '특급배송',
          shipping_detail: '서울/경기 당일/익일 배송',
          shipping_condition: '오후 2시 이전 주문 시'
        }
      ]
    },
    duplicate_policy: {
      coupon_duplicate: '불가',
      point_duplicate: '가능',
      other_promotion_duplicate: '타행사 할인 불가',
      employee_discount: '불가',
      duplicate_note: '브랜드 쿠폰과 플랫폼 쿠폰 중 1개만 선택, 적립은 중복 가능'
    },
    restrictions: {
      excluded_products: ['기획세트', '대용량 제품'],
      channel_restrictions: ['네이버 앱/웹만 구매 가능'],
      payment_restrictions: ['네이버페이 사용 시 추가 혜택'],
      region_restrictions: ['도서산간 배송비 5,000원', '제주도 배송비 3,000원'],
      other_restrictions: ['세트 상품은 한정 수량으로 조기 품절 가능']
    },
    live_specific: {
      key_mentions: [
        '겨울철 건조한 피부를 위한 자음생크림! 오늘 30% 할인',
        '자음생 2종 세트는 35% 할인, 한정 100세트만 준비했습니다',
        '15만원 이상 구매하시면 자음생 에멀젼 미니 증정',
        '선착순 200명께는 겨울 한정 파우치도 드립니다',
        '네이버페이로 결제하시면 20,000원 쿠폰 + 5% 적립까지'
      ],
      broadcast_qa: [
        { 
          question: '자음생크림은 어떤 피부 타입에 좋나요?', 
          answer: '건성, 민감성 피부에 특히 좋고, 겨울철 보습에 최적입니다' 
        },
        { 
          question: '세트 상품 재고는 충분한가요?', 
          answer: '한정 100세트만 준비되어 있어 조기 품절될 수 있습니다' 
        },
        { 
          question: '쿠폰은 어떻게 사용하나요?', 
          answer: '브랜드 쿠폰과 네이버페이 쿠폰 중 하나를 선택하실 수 있습니다' 
        },
        { 
          question: '배송은 언제 되나요?', 
          answer: '오후 2시 이전 주문 시 서울/경기는 당일 또는 익일 배송됩니다' 
        }
      ],
      timeline: [
        { time: '00:00', description: '방송 시작 및 인사' },
        { time: '00:03', description: '오늘의 혜택 안내 (30% 할인, 세트 35% 할인)' },
        { time: '00:10', description: '자음생크림 제품 소개 및 사용법' },
        { time: '00:20', description: '겨울 보습 스킨케어 팁' },
        { time: '00:30', description: '자음생 아이크림 소개' },
        { time: '00:40', description: '자음생 2종 세트 상세 안내 (한정 100세트)' },
        { time: '00:45', description: '사은품 안내 (에멀젼 미니, 파우치, 샘플)' },
        { time: '00:50', description: '쿠폰 사용법 및 결제 안내' },
        { time: '00:55', description: '시청자 Q&A' },
        { time: '01:00', description: '방송 종료 및 마무리' }
      ]
    },
    cs_info: {
      expected_questions: [
        '자음생크림 가격이 얼마인가요?',
        '세트 상품은 어떤 구성인가요?',
        '쿠폰 중복 사용 가능한가요?',
        '사은품은 어떻게 받나요?',
        '배송은 언제 되나요?',
        '임직원 할인도 받을 수 있나요?',
        '세트 재고는 충분한가요?',
        '겨울 한정 파우치는 누구나 받을 수 있나요?'
      ],
      response_scripts: [
        '자음생크림 60ml은 정가 189,000원에서 30% 할인된 132,300원입니다.',
        '자음생 2종 세트는 자음생크림 60ml + 아이크림 25ml 구성으로 304,000원에서 35% 할인된 199,000원입니다. 한정 100세트만 준비되어 있습니다.',
        '쿠폰은 브랜드 쿠폰 15,000원 또는 네이버페이 쿠폰 20,000원 중 1개만 선택 가능하며, 네이버페이 5% 적립은 별도로 받으실 수 있습니다.',
        '15만원 이상 구매 시 자음생 에멀젼 미니 30ml가 자동 증정되며, 선착순 200명께는 겨울 한정 파우치가 추가로 제공됩니다. 전원에게는 자음생 샘플 5종이 증정됩니다.',
        '서울/경기 지역은 오후 2시 이전 주문 시 당일 또는 익일 배송됩니다. 기타 지역은 2-3일 소요됩니다.',
        '임직원 할인과는 중복 적용이 불가능합니다.',
        '자음생 2종 세트는 한정 100세트로 준비되어 있어 조기 품절될 수 있습니다. 실시간 재고 확인 후 구매해주세요.',
        '겨울 한정 파우치는 선착순 200명께만 제공되므로, 품절 전에 서둘러 주문해주세요.'
      ],
      risk_points: [
        '⚠️ 쿠폰 중복 사용 불가 (브랜드 쿠폰 vs 네이버페이 쿠폰 중 1개 선택)',
        '⚠️ 자음생 2종 세트 한정 100세트 (조기 품절 가능)',
        '⚠️ 선착순 겨울 한정 파우치 200개 (품절 시 미제공)',
        '⚠️ 기획세트 및 대용량 제품은 행사 제외',
        '⚠️ 임직원 할인 중복 불가',
        '⚠️ 혜택은 당일 23:59까지만 유효',
        '⚠️ 도서산간/제주 배송비 별도',
        '⚠️ 네이버 앱/웹에서만 구매 가능'
      ],
      cs_note: '설화수 자음생크림 겨울 보습 특집 라이브 방송입니다. 한정 수량 상품(세트 100개, 파우치 200개)과 쿠폰 선택 정책에 주의하여 안내해주세요.'
    }
  },

  // 3번 방송: 순행클렌징 단독 혜택
  {
    metadata: {
      live_id: 'NAVER_SULWHASOO_003',
      platform_name: '네이버',
      brand_name: '설화수',
      live_title_customer: '설화수 순행클렌징 라인 단독 혜택',
      live_title_cs: '설화수 12월 네이버 라이브 순행클렌징',
      source_url: 'https://view.shoppinglive.naver.com/replays/1764983',
      thumbnail_url: '',
      status: '라이브'
    },
    schedule: {
      broadcast_date: '2025-11-30',
      broadcast_start_time: '16:00',
      broadcast_end_time: '17:00',
      benefit_valid_type: '방송 중만',
      benefit_start_datetime: '2025-11-30 16:00:00',
      benefit_end_datetime: '2025-11-30 17:00:00',
      broadcast_type: '단독라이브'
    },
    products: [
      {
        product_order: 1,
        product_name: '순행클렌징폼 EX 200ml',
        sku: 'SWS-CLN-001',
        original_price: '42,000원',
        sale_price: '29,400원',
        discount_rate: '30%',
        product_type: '대표',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: 'https://www.sulwhasoo.com/kr/ko/products/gentle_cleansing_foam.html'
      },
      {
        product_order: 2,
        product_name: '순행클렌징오일 200ml',
        sku: 'SWS-OIL-001',
        original_price: '48,000원',
        sale_price: '33,600원',
        discount_rate: '30%',
        product_type: '일반',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: ''
      },
      {
        product_order: 3,
        product_name: '순행클렌징 2종 세트 (1+1)',
        sku: 'SWS-CLN-SET-001',
        original_price: '90,000원',
        sale_price: '49,900원',
        discount_rate: '45%',
        product_type: '세트',
        stock_info: '한정 200세트',
        set_composition: '순행클렌징폼 200ml + 순행클렌징오일 200ml',
        product_url: ''
      },
      {
        product_order: 4,
        product_name: '순행클렌징워터 200ml',
        sku: 'SWS-WATER-001',
        original_price: '38,000원',
        sale_price: '26,600원',
        discount_rate: '30%',
        product_type: '일반',
        stock_info: '재고 충분',
        set_composition: '',
        product_url: ''
      }
    ],
    benefits: {
      discounts: [
        {
          discount_type: '%할인',
          discount_detail: '순행클렌징 라인 전체 30% 할인',
          discount_condition: '라이브 방송 중 결제 시만',
          discount_valid_period: '방송 중 (16:00~17:00)'
        },
        {
          discount_type: '%할인',
          discount_detail: '순행클렌징 2종 세트 45% 할인',
          discount_condition: '한정 200세트',
          discount_valid_period: '방송 중 (16:00~17:00)'
        },
        {
          discount_type: '금액할인',
          discount_detail: '2개 이상 구매 시 추가 5,000원 할인',
          discount_condition: '2개 이상 구매 시',
          discount_valid_period: '방송 중'
        }
      ],
      gifts: [
        {
          gift_type: '구매조건형',
          gift_name: '순행클렌징 미니 키트 3종',
          gift_condition: '5만원 이상 구매',
          gift_quantity_limit: ''
        },
        {
          gift_type: '증정형',
          gift_name: '클렌징 샘플 파우치',
          gift_condition: '전원 증정',
          gift_quantity_limit: ''
        }
      ],
      coupons: [
        {
          coupon_type: '라이브쿠폰',
          coupon_detail: '라이브 한정 10% 쿠폰',
          coupon_issue_condition: '방송 중 다운로드',
          point_condition: ''
        },
        {
          coupon_type: '플랫폼쿠폰',
          coupon_detail: '네이버페이 10,000원 + 2% 적립',
          coupon_issue_condition: '네이버페이 결제 시',
          point_condition: '2% 적립'
        }
      ],
      shipping: [
        {
          shipping_type: '무료배송',
          shipping_detail: '전 상품 무료배송',
          shipping_condition: '구매 금액 무관'
        }
      ]
    },
    duplicate_policy: {
      coupon_duplicate: '불가',
      point_duplicate: '가능',
      other_promotion_duplicate: '타행사 할인 불가',
      employee_discount: '불가',
      duplicate_note: '라이브 쿠폰과 네이버페이 쿠폰 중 1개만 선택, 2개 이상 구매 시 추가 할인은 자동 적용'
    },
    restrictions: {
      excluded_products: [],
      channel_restrictions: ['네이버 앱/웹만 구매 가능', '방송 중에만 구매 가능'],
      payment_restrictions: [],
      region_restrictions: ['도서산간 배송비 5,000원'],
      other_restrictions: ['방송 종료 후에는 혜택 적용 불가', '세트 상품 한정 수량']
    },
    live_specific: {
      key_mentions: [
        '설화수의 베스트셀러 순행클렌징! 오늘 방송 중에만 30% 할인',
        '2종 세트는 무려 45% 할인, 한정 200세트 준비했습니다',
        '2개 이상 구매하시면 5,000원 추가 할인까지!',
        '5만원 이상 구매 시 순행클렌징 미니 키트 증정',
        '방송 중에만 다운로드 가능한 10% 라이브 쿠폰도 놓치지 마세요'
      ],
      broadcast_qa: [
        { 
          question: '순행클렌징폼과 오일 중 어떤 걸 선택해야 하나요?', 
          answer: '폼은 아침용, 오일은 저녁 메이크업 제거용으로 추천드립니다. 2종 세트로 함께 사용하시면 완벽한 클렌징이 가능합니다' 
        },
        { 
          question: '방송 끝나고도 살 수 있나요?', 
          answer: '방송 중에만 특별 할인이 적용됩니다. 방송 종료 후에는 혜택이 종료됩니다' 
        },
        { 
          question: '2개 이상 구매 할인은 어떻게 받나요?', 
          answer: '2개 이상 장바구니에 담으시면 결제 시 자동으로 5,000원 추가 할인이 적용됩니다' 
        }
      ],
      timeline: [
        { time: '16:00', description: '방송 시작' },
        { time: '16:03', description: '오늘의 혜택 안내 (30% 할인, 세트 45% 할인, 2개 이상 5,000원 추가 할인)' },
        { time: '16:10', description: '순행클렌징폼 제품 소개 및 사용 시연' },
        { time: '16:25', description: '순행클렌징오일 제품 소개 및 메이크업 제거 시연' },
        { time: '16:35', description: '순행클렌징워터 소개' },
        { time: '16:40', description: '2종 세트 상세 안내 (한정 200세트)' },
        { time: '16:45', description: '사은품 및 쿠폰 안내' },
        { time: '16:50', description: '올바른 클렌징 루틴 팁' },
        { time: '16:55', description: '시청자 Q&A' },
        { time: '17:00', description: '방송 종료' }
      ]
    },
    cs_info: {
      expected_questions: [
        '순행클렌징 가격이 얼마인가요?',
        '방송 끝나고도 혜택 받을 수 있나요?',
        '2개 이상 구매 할인은 자동으로 적용되나요?',
        '세트 재고는 충분한가요?',
        '쿠폰은 어떻게 사용하나요?',
        '배송은 언제 되나요?',
        '반품/교환은 가능한가요?',
        '민감성 피부도 사용 가능한가요?'
      ],
      response_scripts: [
        '순행클렌징폼은 정가 42,000원에서 30% 할인된 29,400원, 순행클렌징오일은 48,000원에서 30% 할인된 33,600원입니다. 2종 세트는 45% 할인된 49,900원입니다.',
        '방송 중(16:00~17:00)에만 특별 할인이 적용됩니다. 방송 종료 후에는 혜택이 종료되오니 방송 중에 구매해주세요.',
        '네, 2개 이상 장바구니에 담으시면 결제 시 자동으로 5,000원 추가 할인이 적용됩니다.',
        '순행클렌징 2종 세트는 한정 200세트로 준비되어 있어 조기 품절될 수 있습니다.',
        '라이브 한정 10% 쿠폰은 방송 중에 다운로드하실 수 있으며, 네이버페이 10,000원 쿠폰 중 1개를 선택하여 사용하실 수 있습니다.',
        '주문 후 2-3일 이내 배송됩니다. 전 상품 무료배송입니다.',
        '미개봉 제품에 한해 수령 후 7일 이내 반품/교환이 가능합니다.',
        '순행클렌징 라인은 저자극 포뮬러로 민감성 피부도 안심하고 사용하실 수 있습니다.'
      ],
      risk_points: [
        '⚠️ 방송 중(16:00~17:00)에만 혜택 적용',
        '⚠️ 방송 종료 후에는 할인 불가',
        '⚠️ 순행클렌징 2종 세트 한정 200세트',
        '⚠️ 쿠폰 중복 사용 불가 (라이브 쿠폰 vs 네이버페이 쿠폰 중 1개 선택)',
        '⚠️ 2개 이상 구매 시 추가 5,000원 할인은 자동 적용',
        '⚠️ 임직원 할인 중복 불가',
        '⚠️ 도서산간 배송비 5,000원 별도',
        '⚠️ 네이버 앱/웹에서만 구매 가능'
      ],
      cs_note: '설화수 순행클렌징 라인 단독 혜택 라이브 방송입니다. 방송 중에만 혜택이 적용되며, 종료 후에는 할인 불가하니 주의하여 안내해주세요.'
    }
  },

  // 4번 방송: 퍼펙팅쿠션 1+1
  {
    metadata: {
      live_id: 'NAVER_SULWHASOO_004',
      platform_name: '네이버',
      brand_name: '설화수',
      live_title_customer: '설화수 퍼펙팅쿠션 1+1 특별 기획',
      live_title_cs: '설화수 12월 네이버 라이브 퍼펙팅쿠션',
      source_url: 'https://view.shoppinglive.naver.com/replays/1764984',
      thumbnail_url: '',
      status: '예정'
    },
    schedule: {
      broadcast_date: '2025-12-01',
      broadcast_start_time: '19:00',
      broadcast_end_time: '20:00',
      benefit_valid_type: '당일23:59',
      benefit_start_datetime: '2025-12-01 19:00:00',
      benefit_end_datetime: '2025-12-01 23:59:59',
      broadcast_type: '단독라이브'
    },
    products: [
      {
        product_order: 1,
        product_name: '퍼펙팅쿠션 익스트라 리필 포함 (15g+15g)',
        sku: 'SWS-CUSH-001',
        original_price: '68,000원',
        sale_price: '54,400원',
        discount_rate: '20%',
        product_type: '대표',
        stock_info: '재고 충분',
        set_composition: '본품 15g + 리필 15g',
        product_url: 'https://www.sulwhasoo.com/kr/ko/products/perfecting_cushion.html'
      },
      {
        product_order: 2,
        product_name: '퍼펙팅쿠션 브라이트닝 리필 포함 (15g+15g)',
        sku: 'SWS-CUSH-002',
        original_price: '68,000원',
        sale_price: '54,400원',
        discount_rate: '20%',
        product_type: '일반',
        stock_info: '재고 충분',
        set_composition: '본품 15g + 리필 15g',
        product_url: ''
      },
      {
        product_order: 3,
        product_name: '퍼펙팅쿠션 2개 세트 (1+1+리필)',
        sku: 'SWS-CUSH-SET-001',
        original_price: '136,000원',
        sale_price: '89,900원',
        discount_rate: '34%',
        product_type: '세트',
        stock_info: '한정 150세트',
        set_composition: '본품 2개 (각 15g) + 리필 2개 (각 15g)',
        product_url: ''
      }
    ],
    benefits: {
      discounts: [
        {
          discount_type: '%할인',
          discount_detail: '퍼펙팅쿠션 본품+리필 20% 할인',
          discount_condition: '라이브 방송 중 또는 당일 23:59까지',
          discount_valid_period: '당일 23:59까지'
        },
        {
          discount_type: '%할인',
          discount_detail: '퍼펙팅쿠션 2개 세트 34% 할인',
          discount_condition: '한정 150세트',
          discount_valid_period: '당일 23:59까지'
        }
      ],
      gifts: [
        {
          gift_type: '증정형',
          gift_name: '퍼펙팅 파운데이션 미니 10ml',
          gift_condition: '쿠션 구매 시 전원 증정',
          gift_quantity_limit: ''
        },
        {
          gift_type: '선착순형',
          gift_name: '메이크업 퍼프 5개입',
          gift_condition: '선착순',
          gift_quantity_limit: '선착순 300명'
        },
        {
          gift_type: '구매조건형',
          gift_name: '메이크업 키트 (파운데이션+컨실러+퍼프)',
          gift_condition: '2개 이상 구매',
          gift_quantity_limit: ''
        }
      ],
      coupons: [
        {
          coupon_type: '브랜드쿠폰',
          coupon_detail: '설화수 메이크업 12,000원 할인',
          coupon_issue_condition: '다운로드 필요',
          point_condition: ''
        },
        {
          coupon_type: '플랫폼쿠폰',
          coupon_detail: '네이버페이 15,000원 + 3% 적립',
          coupon_issue_condition: '네이버페이 결제 시',
          point_condition: '3% 추가 적립'
        }
      ],
      shipping: [
        {
          shipping_type: '무료배송',
          shipping_detail: '전 상품 무료배송',
          shipping_condition: '구매 금액 무관'
        },
        {
          shipping_type: '특급배송',
          shipping_detail: '서울/경기 당일 배송',
          shipping_condition: '오전 주문 시'
        }
      ]
    },
    duplicate_policy: {
      coupon_duplicate: '불가',
      point_duplicate: '가능',
      other_promotion_duplicate: '불가',
      employee_discount: '불가',
      duplicate_note: '쿠폰은 1개만 선택 가능, 적립은 별도 적용'
    },
    restrictions: {
      excluded_products: ['퍼펙팅 파운데이션 단품'],
      channel_restrictions: ['네이버 앱/웹만'],
      payment_restrictions: [],
      region_restrictions: ['도서산간 배송비 5,000원'],
      other_restrictions: ['세트 상품은 한정 수량으로 조기 품절 가능', '색상 선택 불가 시 구매 불가']
    },
    live_specific: {
      key_mentions: [
        '설화수 퍼펙팅쿠션 본품+리필 20% 할인!',
        '2개 세트는 34% 할인, 한정 150세트만 준비',
        '쿠션 구매하시면 파운데이션 미니 전원 증정',
        '선착순 300명께는 메이크업 퍼프 5개입도 드립니다',
        '2개 이상 구매 시 메이크업 키트까지!'
      ],
      broadcast_qa: [
        { 
          question: '퍼펙팅쿠션 색상은 어떻게 선택하나요?', 
          answer: '방송 중 색상 선택 옵션을 통해 고객님 피부톤에 맞는 색상을 선택하실 수 있습니다' 
        },
        { 
          question: '리필은 어떻게 교체하나요?', 
          answer: '쿠션 케이스를 열고 기존 리필을 빼낸 후 새 리필을 끼우시면 됩니다. 방송 중 시연해드리겠습니다' 
        },
        { 
          question: '2개 세트는 같은 색상만 가능한가요?', 
          answer: '아니요, 서로 다른 색상으로도 구매 가능합니다' 
        }
      ],
      timeline: [
        { time: '19:00', description: '방송 시작' },
        { time: '19:03', description: '오늘의 혜택 안내' },
        { time: '19:10', description: '퍼펙팅쿠션 제품 소개' },
        { time: '19:20', description: '메이크업 시연 (커버력, 지속력)' },
        { time: '19:35', description: '2개 세트 상세 안내' },
        { time: '19:45', description: '사은품 및 쿠폰 안내' },
        { time: '19:55', description: '시청자 Q&A' },
        { time: '20:00', description: '방송 종료' }
      ]
    },
    cs_info: {
      expected_questions: [
        '퍼펙팅쿠션 가격이 얼마인가요?',
        '색상은 어떻게 선택하나요?',
        '리필 교체는 어떻게 하나요?',
        '2개 세트는 같은 색상만 가능한가요?',
        '쿠폰은 어떻게 사용하나요?',
        '배송은 언제 되나요?',
        '사은품은 어떻게 받나요?',
        '세트 재고는 충분한가요?'
      ],
      response_scripts: [
        '퍼펙팅쿠션 본품+리필은 정가 68,000원에서 20% 할인된 54,400원입니다. 2개 세트는 34% 할인된 89,900원입니다.',
        '주문 시 색상 선택 옵션에서 고객님 피부톤에 맞는 색상을 선택하실 수 있습니다.',
        '쿠션 케이스를 열고 기존 리필을 빼낸 후 새 리필을 끼우시면 됩니다.',
        '네, 2개 세트는 서로 다른 색상으로도 구매 가능합니다.',
        '브랜드 쿠폰 12,000원 또는 네이버페이 쿠폰 15,000원 중 1개를 선택하여 사용하실 수 있습니다.',
        '서울/경기는 오전 주문 시 당일 배송, 기타 지역은 2-3일 소요됩니다.',
        '쿠션 구매 시 파운데이션 미니가 자동 증정되며, 선착순 300명께는 메이크업 퍼프 5개입이 추가로 제공됩니다.',
        '2개 세트는 한정 150세트로 준비되어 있어 조기 품절될 수 있습니다.'
      ],
      risk_points: [
        '⚠️ 2개 세트 한정 150세트',
        '⚠️ 선착순 메이크업 퍼프 300개',
        '⚠️ 쿠폰 중복 사용 불가',
        '⚠️ 색상 선택 필수',
        '⚠️ 퍼펙팅 파운데이션 단품은 행사 제외',
        '⚠️ 임직원 할인 중복 불가',
        '⚠️ 도서산간 배송비 5,000원',
        '⚠️ 혜택은 당일 23:59까지'
      ],
      cs_note: '설화수 퍼펙팅쿠션 1+1 특별 기획 방송입니다. 색상 선택 및 한정 수량에 주의하여 안내해주세요.'
    }
  },

  // 5번 방송: 겨울 한정 세트 기획전
  {
    metadata: {
      live_id: 'NAVER_SULWHASOO_005',
      platform_name: '네이버',
      brand_name: '설화수',
      live_title_customer: '설화수 겨울 한정 럭셔리 스킨케어 세트',
      live_title_cs: '설화수 12월 네이버 라이브 겨울 한정 세트',
      source_url: 'https://view.shoppinglive.naver.com/replays/1764985',
      thumbnail_url: '',
      status: '예정'
    },
    schedule: {
      broadcast_date: '2025-12-05',
      broadcast_start_time: '20:00',
      broadcast_end_time: '21:30',
      benefit_valid_type: '기간형',
      benefit_start_datetime: '2025-12-05 20:00:00',
      benefit_end_datetime: '2025-12-10 23:59:59',
      broadcast_type: '단독라이브'
    },
    products: [
      {
        product_order: 1,
        product_name: '윤조 럭셔리 5종 세트',
        sku: 'SWS-LUXURY-001',
        original_price: '850,000원',
        sale_price: '595,000원',
        discount_rate: '30%',
        product_type: '세트',
        stock_info: '한정 50세트',
        set_composition: '윤조에센스 60ml + 자음생크림 60ml + 자음생 아이크림 25ml + 순행클렌징폼 200ml + 퍼펙팅쿠션 15g',
        product_url: ''
      },
      {
        product_order: 2,
        product_name: '자음생 럭셔리 3종 세트',
        sku: 'SWS-LUXURY-002',
        original_price: '492,000원',
        sale_price: '344,400원',
        discount_rate: '30%',
        product_type: '세트',
        stock_info: '한정 80세트',
        set_composition: '자음생크림 60ml + 자음생 아이크림 25ml + 자음생 에멀젼 125ml',
        product_url: ''
      },
      {
        product_order: 3,
        product_name: '윤조 스페셜 기프트 세트',
        sku: 'SWS-GIFT-001',
        original_price: '320,000원',
        sale_price: '224,000원',
        discount_rate: '30%',
        product_type: '세트',
        stock_info: '한정 100세트',
        set_composition: '윤조에센스 60ml + 순행클렌징폼 200ml + 한정 파우치',
        product_url: ''
      }
    ],
    benefits: {
      discounts: [
        {
          discount_type: '%할인',
          discount_detail: '겨울 한정 세트 전체 30% 할인',
          discount_condition: '라이브 방송 시작 ~ 12/10 23:59',
          discount_valid_period: '2025-12-05 20:00 ~ 2025-12-10 23:59'
        },
        {
          discount_type: '금액할인',
          discount_detail: '50만원 이상 구매 시 추가 30,000원 할인',
          discount_condition: '50만원 이상 구매',
          discount_valid_period: '2025-12-05 20:00 ~ 2025-12-10 23:59'
        }
      ],
      gifts: [
        {
          gift_type: '증정형',
          gift_name: '설화수 VIP 럭셔리 키트 10종',
          gift_condition: '세트 구매 시 전원 증정',
          gift_quantity_limit: ''
        },
        {
          gift_type: '선착순형',
          gift_name: '겨울 한정 에디션 파우치',
          gift_condition: '선착순',
          gift_quantity_limit: '선착순 100명'
        },
        {
          gift_type: '구매조건형',
          gift_name: '설화수 프리미엄 쇼핑백',
          gift_condition: '50만원 이상 구매',
          gift_quantity_limit: ''
        }
      ],
      coupons: [
        {
          coupon_type: '브랜드쿠폰',
          coupon_detail: '설화수 VIP 30,000원 할인',
          coupon_issue_condition: '다운로드 필요',
          point_condition: ''
        },
        {
          coupon_type: '플랫폼쿠폰',
          coupon_detail: '네이버페이 40,000원 + 5% 적립',
          coupon_issue_condition: '네이버페이 결제 시',
          point_condition: '5% 추가 적립'
        },
        {
          coupon_type: '장바구니쿠폰',
          coupon_detail: '추가 10% 쿠폰',
          coupon_issue_condition: '100만원 이상 장바구니',
          point_condition: ''
        }
      ],
      shipping: [
        {
          shipping_type: '무료배송',
          shipping_detail: '전 상품 무료배송',
          shipping_condition: '구매 금액 무관'
        },
        {
          shipping_type: '특급배송',
          shipping_detail: '전국 특급배송 (당일/익일)',
          shipping_condition: '럭셔리 세트 구매 시'
        },
        {
          shipping_type: '선물포장',
          shipping_detail: '프리미엄 선물 포장 서비스',
          shipping_condition: '세트 구매 시 무료'
        }
      ]
    },
    duplicate_policy: {
      coupon_duplicate: '불가',
      point_duplicate: '가능',
      other_promotion_duplicate: '타행사 할인 불가',
      employee_discount: '가능 (일부)',
      duplicate_note: '쿠폰은 1개만 선택 가능, 50만원 이상 추가 할인은 자동 적용, 임직원 할인은 브랜드 쿠폰과만 중복 가능'
    },
    restrictions: {
      excluded_products: [],
      channel_restrictions: ['네이버 앱/웹만'],
      payment_restrictions: ['네이버페이 사용 시 추가 혜택'],
      region_restrictions: ['도서산간 배송비 10,000원'],
      other_restrictions: ['한정 수량으로 조기 품절 가능', '선물 포장 서비스는 세트 구매 시만 제공', '반품 시 사은품 함께 반납 필요']
    },
    live_specific: {
      key_mentions: [
        '설화수 겨울 한정 럭셔리 세트 전체 30% 할인!',
        '윤조 럭셔리 5종 세트는 85만원에서 59만5천원, 무려 25만5천원 할인',
        '50만원 이상 구매하시면 3만원 추가 할인까지',
        '세트 구매하시면 설화수 VIP 럭셔리 키트 10종 전원 증정',
        '선착순 100명께는 겨울 한정 에디션 파우치도 드립니다',
        '프리미엄 선물 포장 서비스 무료 제공, 연말 선물로 최고!',
        '혜택은 12월 10일까지 계속됩니다'
      ],
      broadcast_qa: [
        { 
          question: '윤조 럭셔리 5종 세트 구성이 어떻게 되나요?', 
          answer: '윤조에센스 60ml, 자음생크림 60ml, 자음생 아이크림 25ml, 순행클렌징폼 200ml, 퍼펙팅쿠션 15g로 구성되어 있습니다' 
        },
        { 
          question: '선물 포장은 어떻게 받나요?', 
          answer: '세트 구매 시 자동으로 프리미엄 선물 포장이 제공됩니다. 별도 신청 필요 없습니다' 
        },
        { 
          question: '50만원 이상 추가 할인은 자동으로 적용되나요?', 
          answer: '네, 50만원 이상 장바구니에 담으시면 결제 시 자동으로 3만원 추가 할인이 적용됩니다' 
        },
        { 
          question: '임직원 할인도 받을 수 있나요?', 
          answer: '임직원 할인은 브랜드 쿠폰과만 중복 가능하며, 플랫폼 쿠폰과는 중복 불가합니다' 
        },
        { 
          question: '혜택 기간이 언제까지인가요?', 
          answer: '방송 시작부터 12월 10일 23시 59분까지입니다' 
        }
      ],
      timeline: [
        { time: '20:00', description: '방송 시작' },
        { time: '20:05', description: '겨울 한정 세트 소개 및 혜택 안내' },
        { time: '20:15', description: '윤조 럭셔리 5종 세트 상세 설명' },
        { time: '20:30', description: '윤조에센스 사용법 시연' },
        { time: '20:45', description: '자음생 럭셔리 3종 세트 소개' },
        { time: '21:00', description: '윤조 스페셜 기프트 세트 소개' },
        { time: '21:10', description: '선물 포장 서비스 안내' },
        { time: '21:15', description: '쿠폰 및 추가 할인 안내' },
        { time: '21:20', description: '시청자 Q&A' },
        { time: '21:30', description: '방송 종료 및 혜택 기간 안내' }
      ]
    },
    cs_info: {
      expected_questions: [
        '윤조 럭셔리 5종 세트 가격이 얼마인가요?',
        '세트 구성은 어떻게 되나요?',
        '선물 포장은 어떻게 받나요?',
        '50만원 이상 추가 할인은 자동 적용되나요?',
        '쿠폰은 어떻게 사용하나요?',
        '임직원 할인도 받을 수 있나요?',
        '혜택 기간이 언제까지인가요?',
        '배송은 언제 되나요?',
        '반품/교환은 가능한가요?',
        '한정 수량은 몇 개인가요?'
      ],
      response_scripts: [
        '윤조 럭셔리 5종 세트는 정가 850,000원에서 30% 할인된 595,000원입니다. 50만원 이상 구매 시 3만원 추가 할인이 적용되어 최종 565,000원입니다.',
        '윤조 럭셔리 5종 세트는 윤조에센스 60ml, 자음생크림 60ml, 자음생 아이크림 25ml, 순행클렌징폼 200ml, 퍼펙팅쿠션 15g로 구성되어 있습니다.',
        '세트 구매 시 자동으로 프리미엄 선물 포장이 제공됩니다. 별도 신청 필요 없습니다.',
        '네, 50만원 이상 장바구니에 담으시면 결제 시 자동으로 3만원 추가 할인이 적용됩니다.',
        '브랜드 쿠폰 30,000원, 네이버페이 쿠폰 40,000원, 장바구니 쿠폰 10% 중 1개를 선택하여 사용하실 수 있습니다. 네이버페이 5% 적립은 별도로 받으실 수 있습니다.',
        '임직원 할인은 브랜드 쿠폰과만 중복 가능하며, 플랫폼 쿠폰과는 중복 불가합니다.',
        '방송 시작(12월 5일 20시)부터 12월 10일 23시 59분까지입니다.',
        '럭셔리 세트는 전국 특급배송으로 당일 또는 익일 배송됩니다.',
        '미개봉 제품에 한해 수령 후 7일 이내 반품/교환이 가능합니다. 반품 시 사은품도 함께 반납해주셔야 합니다.',
        '윤조 럭셔리 5종 세트는 한정 50세트, 자음생 럭셔리 3종 세트는 한정 80세트, 윤조 스페셜 기프트 세트는 한정 100세트입니다.'
      ],
      risk_points: [
        '⚠️ 윤조 럭셔리 5종 세트 한정 50세트',
        '⚠️ 자음생 럭셔리 3종 세트 한정 80세트',
        '⚠️ 선착순 한정 에디션 파우치 100개',
        '⚠️ 쿠폰 중복 사용 불가 (1개만 선택)',
        '⚠️ 50만원 이상 추가 할인은 자동 적용',
        '⚠️ 임직원 할인은 브랜드 쿠폰과만 중복 가능',
        '⚠️ 반품 시 사은품 함께 반납 필요',
        '⚠️ 선물 포장 서비스는 세트 구매 시만 제공',
        '⚠️ 도서산간 배송비 10,000원 별도',
        '⚠️ 혜택은 12월 10일 23:59까지'
      ],
      cs_note: '설화수 겨울 한정 럭셔리 스킨케어 세트 방송입니다. 한정 수량 및 쿠폰 선택 정책, 임직원 할인 중복 조건에 주의하여 안내해주세요. 혜택 기간이 12월 10일까지로 방송 후에도 계속됩니다.'
    }
  }
];

/**
 * 설화수 라이브 방송 목록 조회
 */
export const getSulwhasooLives = () => {
  return sulwhasooLivesData;
};

/**
 * 설화수 라이브 상세 정보 조회
 */
export const getSulwhasooLiveDetail = (p_live_id) => {
  const result = sulwhasooLivesData.find(_v_live => _v_live.metadata.live_id === p_live_id);
  
  if (result) {
    console.log('✅ 설화수 라이브 데이터 찾음:', result.metadata.live_id);
  } else {
    console.error('❌ 설화수 라이브 데이터 없음. 사용 가능한 live_id:', 
      sulwhasooLivesData.map(d => d.metadata.live_id));
  }
  
  return result;
};

/**
 * 설화수 라이브를 이벤트 형식으로 변환
 */
export const convertSulwhasooLiveToEvent = (p_live) => {
  const _v_meta = p_live.metadata;
  const _v_schedule = p_live.schedule || {};
  const _v_products = p_live.products || [];
  const _v_benefits = p_live.benefits || {};
  
  return {
    event_id: _v_meta.live_id,
    channel_name: _v_meta.platform_name,
    channel_code: 'NAVER_LIVE',
    title: _v_meta.live_title_customer,
    subtitle: `${_v_meta.brand_name} 라이브 방송`,
    description: _v_schedule.broadcast_start_time 
      ? `방송시간: ${_v_schedule.broadcast_start_time} ~ ${_v_schedule.broadcast_end_time} | ${_v_products.length}개 상품 | ${(_v_benefits.discounts || []).length}개 할인`
      : `${_v_products.length}개 상품 | ${(_v_benefits.discounts || []).length}개 할인 | ${(_v_benefits.gifts || []).length}개 사은품`,
    start_date: _v_schedule.broadcast_date || '',
    end_date: _v_schedule.broadcast_date || '',
    event_url: _v_meta.source_url,
    status: _v_meta.status === '라이브' ? 'ACTIVE' : _v_meta.status === '예정' ? 'SCHEDULED' : 'COMPLETED',
    priority: 10,
    tags: ['네이버라이브', '설화수', '라이브방송', '상세정보'],
    is_live_detail: true,
    has_detail: true
  };
};

/**
 * 검색 키워드로 설화수 라이브 필터링
 */
export const searchSulwhasooLives = (p_keyword) => {
  if (!p_keyword) return [];
  
  const _v_lower_keyword = p_keyword.toLowerCase();
  
  return sulwhasooLivesData
    .filter(_v_live => {
      const _v_title = _v_live.metadata.live_title_customer.toLowerCase();
      const _v_brand = _v_live.metadata.brand_name.toLowerCase();
      const _v_products = _v_live.products.map(p => p.product_name.toLowerCase()).join(' ');
      return _v_title.includes(_v_lower_keyword) || 
             _v_brand.includes(_v_lower_keyword) ||
             _v_products.includes(_v_lower_keyword);
    })
    .map(convertSulwhasooLiveToEvent);
};

export default sulwhasooLivesData;

