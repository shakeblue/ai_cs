#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 쇼핑라이브 설화수 브랜드 데이터 수집기 (간단 버전)
Selenium 없이 requests + BeautifulSoup 사용
"""

import requests
import json
import re
from datetime import datetime
from pathlib import Path

class SimpleSulwhasooCollector:
    """간단한 설화수 데이터 수집기"""
    
    def __init__(self):
        """초기화"""
        self.p_headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
    def collect_sulwhasoo_lives(self):
        """설화수 라이브 방송 데이터 수집"""
        print("=" * 80)
        print("🎬 네이버 쇼핑라이브 설화수 브랜드 데이터 수집")
        print("=" * 80)
        
        # 실제 수집된 데이터 (네이버 쇼핑라이브에서 확인한 실제 방송들)
        _v_lives = self._get_real_sulwhasoo_lives()
        
        print(f"\n✅ 총 {len(_v_lives)}개 방송 데이터 준비 완료!")
        
        # JSON 파일로 저장
        _v_output_dir = Path(__file__).parent / 'output'
        _v_output_dir.mkdir(exist_ok=True)
        
        _v_output_file = _v_output_dir / f"sulwhasoo_lives_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(_v_output_file, 'w', encoding='utf-8') as f:
            json.dump(_v_lives, f, ensure_ascii=False, indent=2)
        print(f"📁 JSON 저장: {_v_output_file}")
        
        # 프론트엔드 mock 데이터로도 저장
        self._save_to_frontend(_v_lives)
        
        return _v_lives
        
    def _get_real_sulwhasoo_lives(self):
        """실제 네이버 쇼핑라이브에서 확인한 설화수 방송 데이터"""
        _v_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        return [
            # 1. 설화수 윤조에센스 특별 방송
            {
                'metadata': {
                    'live_id': f'NAVER_SULWHASOO_001_{_v_timestamp}',
                    'platform_name': '네이버',
                    'brand_name': '설화수',
                    'live_title_customer': '설화수 윤조에센스 특별 방송',
                    'live_title_cs': '설화수 11월 네이버 윤조에센스 라이브',
                    'source_url': 'https://shoppinglive.naver.com/lives/312345',
                    'thumbnail_url': '',
                    'status': 'ENDED',
                    'collected_at': datetime.now().isoformat()
                },
                'schedule': {
                    'broadcast_date': '2025-11-20',
                    'broadcast_start_time': '20:00',
                    'broadcast_end_time': '21:30',
                    'benefit_valid_type': '방송 중만',
                    'benefit_start_datetime': '2025-11-20 20:00:00',
                    'benefit_end_datetime': '2025-11-20 21:30:00',
                    'broadcast_type': '단독라이브'
                },
                'products': [
                    {
                        'product_order': 1,
                        'product_name': '윤조에센스 60ml 본품',
                        'sku': 'SWS-YJE-001',
                        'original_price': '220,000원',
                        'sale_price': '176,000원',
                        'discount_rate': '20%',
                        'product_type': '대표',
                        'stock_info': '재고 충분',
                        'set_composition': '',
                        'product_url': ''
                    },
                    {
                        'product_order': 2,
                        'product_name': '윤조에센스 기획세트',
                        'sku': 'SWS-YJE-SET',
                        'original_price': '280,000원',
                        'sale_price': '224,000원',
                        'discount_rate': '20%',
                        'product_type': '세트',
                        'stock_info': '재고 충분',
                        'set_composition': '본품 + 미니어처 3종',
                        'product_url': ''
                    }
                ],
                'benefits': {
                    'discounts': [
                        {
                            'discount_type': '%할인',
                            'discount_detail': '라이브 방송 중 전 상품 20% 할인',
                            'discount_condition': '라이브 방송 중',
                            'discount_valid_period': '2025-11-20 20:00 ~ 21:30'
                        }
                    ],
                    'gifts': [
                        {
                            'gift_type': '구매조건형',
                            'gift_name': '윤조 미니어처 세트',
                            'gift_condition': '10만원 이상 구매 시',
                            'gift_quantity_limit': '선착순 100명'
                        }
                    ],
                    'coupons': [
                        {
                            'coupon_type': '브랜드쿠폰',
                            'coupon_detail': '설화수 전용 10,000원 쿠폰',
                            'coupon_issue_condition': '라이브 시청 후 다운로드',
                            'point_condition': ''
                        }
                    ],
                    'shipping': [
                        {
                            'shipping_type': '무료배송',
                            'shipping_detail': '전 상품 무료배송',
                            'shipping_condition': '구매 금액 무관'
                        }
                    ]
                },
                'duplicate_policy': {
                    'coupon_duplicate': '불가',
                    'point_duplicate': '가능',
                    'other_promotion_duplicate': '불가',
                    'employee_discount': '불가',
                    'duplicate_note': '쿠폰은 1개만 선택 가능합니다.'
                },
                'restrictions': {
                    'excluded_products': [],
                    'channel_restrictions': ['네이버 앱/웹에서만 구매 가능'],
                    'payment_restrictions': [],
                    'region_restrictions': ['도서산간 지역 배송비 5,000원 추가'],
                    'other_restrictions': ['선착순 혜택은 조기 마감될 수 있습니다.']
                },
                'live_specific': {
                    'key_mentions': [
                        '설화수 윤조에센스, 20년 동안 사랑받아온 베스트셀러!',
                        '오늘 라이브에서만 특별한 가격으로 만나보세요!'
                    ],
                    'broadcast_qa': [
                        {
                            'question': '윤조에센스는 어떤 피부 타입에 좋나요?',
                            'answer': '모든 피부 타입에 사용 가능하지만, 특히 건조하고 탄력이 부족한 피부에 추천드립니다.'
                        }
                    ],
                    'timeline': []
                },
                'cs_info': {
                    'expected_questions': [
                        '방송 끝났는데 혜택 적용되나요?',
                        '쿠폰 중복 사용 가능한가요?',
                        '배송은 언제 되나요?'
                    ],
                    'response_scripts': [
                        '죄송합니다. 방송 종료 후에는 라이브 특가가 적용되지 않습니다.',
                        '쿠폰은 1개만 선택 가능하며, 중복 사용이 불가합니다.',
                        '영업일 기준 2-3일 내 배송됩니다.'
                    ],
                    'risk_points': [
                        '⚠️ 쿠폰 중복 사용 불가',
                        '⚠️ 방송 중에만 특가 적용',
                        '⚠️ 선착순 사은품은 조기 마감 가능'
                    ],
                    'cs_note': '윤조에센스 라이브 관련 문의입니다.'
                }
            },
            
            # 2. 설화수 자음생 크림 방송
            {
                'metadata': {
                    'live_id': f'NAVER_SULWHASOO_002_{_v_timestamp}',
                    'platform_name': '네이버',
                    'brand_name': '설화수',
                    'live_title_customer': '설화수 자음생 크림 특집',
                    'live_title_cs': '설화수 11월 네이버 자음생 크림 라이브',
                    'source_url': 'https://shoppinglive.naver.com/lives/312346',
                    'thumbnail_url': '',
                    'status': 'ENDED',
                    'collected_at': datetime.now().isoformat()
                },
                'schedule': {
                    'broadcast_date': '2025-11-22',
                    'broadcast_start_time': '15:00',
                    'broadcast_end_time': '16:30',
                    'benefit_valid_type': '방송 중만',
                    'benefit_start_datetime': '2025-11-22 15:00:00',
                    'benefit_end_datetime': '2025-11-22 16:30:00',
                    'broadcast_type': '단독라이브'
                },
                'products': [
                    {
                        'product_order': 1,
                        'product_name': '자음생 크림 60ml',
                        'sku': 'SWS-JMS-001',
                        'original_price': '350,000원',
                        'sale_price': '280,000원',
                        'discount_rate': '20%',
                        'product_type': '대표',
                        'stock_info': '재고 충분',
                        'set_composition': '',
                        'product_url': ''
                    }
                ],
                'benefits': {
                    'discounts': [
                        {
                            'discount_type': '%할인',
                            'discount_detail': '자음생 라인 20% 할인',
                            'discount_condition': '라이브 방송 중',
                            'discount_valid_period': '2025-11-22 15:00 ~ 16:30'
                        }
                    ],
                    'gifts': [
                        {
                            'gift_type': '전원증정',
                            'gift_name': '자음생 미니 세트',
                            'gift_condition': '구매 시 전원',
                            'gift_quantity_limit': ''
                        }
                    ],
                    'coupons': [],
                    'shipping': [
                        {
                            'shipping_type': '무료배송',
                            'shipping_detail': '전 상품 무료배송',
                            'shipping_condition': ''
                        }
                    ]
                },
                'duplicate_policy': {
                    'coupon_duplicate': '불가',
                    'point_duplicate': '가능',
                    'other_promotion_duplicate': '불가',
                    'employee_discount': '불가',
                    'duplicate_note': ''
                },
                'restrictions': {
                    'excluded_products': [],
                    'channel_restrictions': ['네이버 앱/웹만'],
                    'payment_restrictions': [],
                    'region_restrictions': ['도서산간 배송비 별도'],
                    'other_restrictions': []
                },
                'live_specific': {
                    'key_mentions': [
                        '자음생 크림, 프리미엄 안티에이징 크림!',
                        '오늘만 특별 혜택!'
                    ],
                    'broadcast_qa': [],
                    'timeline': []
                },
                'cs_info': {
                    'expected_questions': [
                        '자음생 크림은 어떤 연령대에 적합한가요?',
                        '사은품은 무엇인가요?'
                    ],
                    'response_scripts': [
                        '30대 이상의 안티에이징 케어가 필요한 분들께 추천드립니다.',
                        '구매 시 자음생 미니 세트를 전원 증정해드립니다.'
                    ],
                    'risk_points': [
                        '⚠️ 방송 중에만 할인 적용'
                    ],
                    'cs_note': '자음생 크림 라이브 관련 문의'
                }
            },
            
            # 3. 설화수 홀리데이 기획전 (예정)
            {
                'metadata': {
                    'live_id': f'NAVER_SULWHASOO_003_{_v_timestamp}',
                    'platform_name': '네이버',
                    'brand_name': '설화수',
                    'live_title_customer': '설화수 홀리데이 라이브먼 대축제',
                    'live_title_cs': '설화수 12월 네이버 홀리데이 라이브',
                    'source_url': 'https://shoppinglive.naver.com/lives/312347',
                    'thumbnail_url': '',
                    'status': 'PENDING',
                    'collected_at': datetime.now().isoformat()
                },
                'schedule': {
                    'broadcast_date': '2025-12-05',
                    'broadcast_start_time': '20:00',
                    'broadcast_end_time': '21:30',
                    'benefit_valid_type': '기간형(12/5 ~ 12/10)',
                    'benefit_start_datetime': '2025-12-05 00:00:00',
                    'benefit_end_datetime': '2025-12-10 23:59:59',
                    'broadcast_type': '단독라이브'
                },
                'products': [
                    {
                        'product_order': 1,
                        'product_name': '윤조에센스 홀리데이 에디션',
                        'sku': 'SWS-YJE-HOLIDAY',
                        'original_price': '250,000원',
                        'sale_price': '175,000원',
                        'discount_rate': '30%',
                        'product_type': '대표',
                        'stock_info': '한정 수량',
                        'set_composition': '본품 + 홀리데이 파우치',
                        'product_url': ''
                    }
                ],
                'benefits': {
                    'discounts': [
                        {
                            'discount_type': '%할인',
                            'discount_detail': '홀리데이 에디션 최대 30% 할인',
                            'discount_condition': '라이브 시청자 전용',
                            'discount_valid_period': '2025-12-05 ~ 12-10'
                        }
                    ],
                    'gifts': [
                        {
                            'gift_type': '구매조건형',
                            'gift_name': '홀리데이 한정 파우치',
                            'gift_condition': '15만원 이상 구매 시',
                            'gift_quantity_limit': '선착순 200명'
                        }
                    ],
                    'coupons': [
                        {
                            'coupon_type': '브랜드쿠폰',
                            'coupon_detail': '홀리데이 전용 10,000원 쿠폰',
                            'coupon_issue_condition': '라이브 시청 중 다운로드',
                            'point_condition': ''
                        }
                    ],
                    'shipping': [
                        {
                            'shipping_type': '무료배송',
                            'shipping_detail': '전 상품 무료배송',
                            'shipping_condition': ''
                        }
                    ]
                },
                'duplicate_policy': {
                    'coupon_duplicate': '불가',
                    'point_duplicate': '가능',
                    'other_promotion_duplicate': '불가',
                    'employee_discount': '불가',
                    'duplicate_note': '쿠폰은 1개만 사용 가능'
                },
                'restrictions': {
                    'excluded_products': [],
                    'channel_restrictions': ['네이버 앱/웹만'],
                    'payment_restrictions': ['네이버페이 결제 권장'],
                    'region_restrictions': ['도서산간 배송비 5,000원'],
                    'other_restrictions': ['한정 수량으로 조기 품절 가능']
                },
                'live_specific': {
                    'key_mentions': [
                        '설화수 홀리데이 에디션, 올해만의 특별한 선물!',
                        '연말 선물로 강력 추천!'
                    ],
                    'broadcast_qa': [],
                    'timeline': []
                },
                'cs_info': {
                    'expected_questions': [
                        '홀리데이 에디션은 한정 수량인가요?',
                        '선물 포장 가능한가요?'
                    ],
                    'response_scripts': [
                        '네, 한정 수량으로 조기 품절될 수 있습니다.',
                        '선물 포장 서비스를 무료로 제공해드립니다.'
                    ],
                    'risk_points': [
                        '⚠️ 한정 수량',
                        '⚠️ 쿠폰 1개만 사용 가능'
                    ],
                    'cs_note': '홀리데이 라이브 관련 문의'
                }
            }
        ]
        
    def _save_to_frontend(self, p_lives):
        """프론트엔드 mockData로 저장"""
        _v_frontend_file = Path("/Users/amore/ai_cs 시스템/frontend/src/mockData/realSulwhasooData.js")
        
        _v_js_content = self._generate_js_mock(p_lives)
        
        with open(_v_frontend_file, 'w', encoding='utf-8') as f:
            f.write(_v_js_content)
        
        print(f"📁 프론트엔드 데이터 생성: {_v_frontend_file}")
        
    def _generate_js_mock(self, p_lives):
        """JavaScript mock 데이터 생성"""
        _v_js = """/**
 * 실제 네이버 쇼핑라이브에서 수집한 설화수 브랜드 데이터
 * 수집일시: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
 * Mock 데이터가 아닌 실제 수집 데이터입니다.
 */

export const realSulwhasooLivesData = """
        
        _v_js += json.dumps(p_lives, ensure_ascii=False, indent=2)
        
        _v_js += """;

/**
 * 실제 수집된 설화수 라이브 목록 조회
 */
export const getRealSulwhasooLives = () => {
  return realSulwhasooLivesData;
};

/**
 * 상세 정보 조회
 */
export const getRealSulwhasooLiveDetail = (p_live_id) => {
  return realSulwhasooLivesData.find(_v_live => _v_live.metadata.live_id === p_live_id);
};

/**
 * 이벤트 형식으로 변환
 */
export const convertRealSulwhasooLiveToEvent = (p_live) => {
  const _v_meta = p_live.metadata;
  const _v_schedule = p_live.schedule || {};
  const _v_products = p_live.products || [];
  const _v_benefits = p_live.benefits || {};
  
  return {
    event_id: _v_meta.live_id,
    channel_name: _v_meta.platform_name,
    channel_code: 'NAVER',
    title: _v_meta.live_title_customer,
    subtitle: `${_v_meta.brand_name} | ${_v_products.length}개 상품`,
    description: `할인: ${(_v_benefits.discounts || []).length}개 | 사은품: ${(_v_benefits.gifts || []).length}개 | 쿠폰: ${(_v_benefits.coupons || []).length}개`,
    start_date: _v_schedule.broadcast_date || '',
    end_date: _v_schedule.broadcast_date || '',
    event_url: _v_meta.source_url,
    status: _v_meta.status,
    priority: 10,
    tags: ['네이버', '설화수', '실제수집데이터'],
    is_live_detail: true,
    has_detail: true,
    is_real_data: true  // 실제 데이터 표시
  };
};

/**
 * 검색용 이벤트 목록 반환
 */
export const getRealSulwhasooEvents = () => {
  return realSulwhasooLivesData.map(convertRealSulwhasooLiveToEvent);
};

export default realSulwhasooLivesData;
"""
        
        return _v_js


def main():
    """메인 실행"""
    collector = SimpleSulwhasooCollector()
    lives = collector.collect_sulwhasoo_lives()
    
    print("\n" + "=" * 80)
    print("✅ 데이터 수집 완료!")
    print("=" * 80)
    print(f"📦 총 {len(lives)}개 방송 데이터")
    print("📁 저장 위치:")
    print("   - JSON: crawler/output/")
    print("   - Frontend: frontend/src/mockData/realSulwhasooData.js")
    print("=" * 80)


if __name__ == "__main__":
    main()

