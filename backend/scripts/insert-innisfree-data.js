/**
 * 이니스프리 이벤트 데이터 삽입 스크립트
 * 
 * 실행 방법:
 * node scripts/insert-innisfree-data.js
 */

require('dotenv').config();
const { Pool } = require('pg');

// 데이터베이스 연결 풀 생성
const _v_pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'cosmetic_consultation',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
});

/**
 * 이니스프리 이벤트 데이터
 */
const _v_innisfree_events = [
  {
    external_id: 'innisfree_event_102214',
    title: '오직 APP에서만 더 챙겨드립니다🎁',
    subtitle: '이니스프리 앱 전용 특별 할인',
    description: '이니스프리 앱에서만 제공하는 특별 할인 이벤트입니다. 레티놀, 비타민C 등 인기 제품을 최대 30% 할인된 가격으로 만나보세요.',
    start_date: '2025-11-25',
    end_date: '2025-11-30',
    discount_rate: 30.00,
    benefit_summary: '레티놀 시카 앰플 28% 할인, 비타민C 캡슐 세럼 28% 할인, 레티놀 시카 흔적 장벽크림 30% 할인, 비타민C 캡슐 크림 대용량 30% 할인',
    benefit_detail: `참여 상품 4개
- 레티놀 시카 앰플 기획세트 (30mL+10mL): 28,800원 (28% 할인, 정상가 40,000원)
- 레티놀 시카 흔적 장벽크림 세트 (50mL+30mL): 24,500원 (30% 할인, 정상가 35,000원)  
- 비타민C 캡슐 세럼 기획세트 (30mL+10mL): 27,360원 (28% 할인, 정상가 38,000원)
- 비타민C 캡슐 크림 대용량 80mL: 31,500원 (30% 할인, 정상가 45,000원)

모든 상품 APP 전용 혜택 적용`,
    target_products: '레티놀 시카 앰플, 레티놀 시카 흔적 장벽크림, 비타민C 캡슐 세럼, 비타민C 캡슐 크림',
    conditions: 'APP 전용 이벤트입니다. 이니스프리 공식 앱에서만 구매 가능합니다. 재고 소진 시 조기 종료될 수 있습니다.',
    event_url: 'https://www.innisfree.com/kr/ko/ca/event/102214',
    status: 'ACTIVE',
    priority: 8,
    tags: ['이니스프리', 'APP전용', '레티놀', '비타민C', '할인', '기획세트']
  },
  {
    external_id: 'innisfree_holiday_2025',
    title: '2025 홀리데이 에디션 출시! ~50% 특가!',
    subtitle: '홀리데이 한정 패키지',
    description: '연말을 맞이하여 특별 제작된 홀리데이 에디션 제품들을 최대 50% 할인된 가격으로 만나보세요.',
    start_date: '2025-11-20',
    end_date: '2025-11-30',
    discount_rate: 50.00,
    benefit_summary: '그린티 씨드 히알루론산 크림 100mL 세트 50% 할인, 레티놀 그린티 앰플 30% 할인',
    benefit_detail: `홀리데이 한정 패키지
- 그린티 씨드 히알루론산 크림 100mL세트: 45,000원 (50% 할인)
- 레티놀 그린티 피디알엔 스킨부스터 앰플 40mL 세트: 39,900원 (30% 할인)
- 레티놀 시카 흔적 앰플 50mL 세트: 39,900원 (30% 할인)
- 마이 퍼퓸드 핸드크림 2종 세트: 16,800원 (30% 할인)`,
    target_products: '그린티 씨드 히알루론산 크림, 레티놀 그린티 앰플, 레티놀 시카 흔적 앰플, 마이 퍼퓸드 핸드크림',
    conditions: '홀리데이 한정 제품으로 재고 소진 시 판매 종료됩니다.',
    event_url: 'https://www.innisfree.com/kr/ko/event',
    status: 'ACTIVE',
    priority: 7,
    tags: ['이니스프리', '홀리데이', '한정판', '대용량', '할인']
  }
];

/**
 * 채널 ID 조회
 */
async function getChannelId(p_channel_code) {
  const _v_query = 'SELECT channel_id FROM channels WHERE channel_code = $1';
  const _v_result = await _v_pool.query(_v_query, [p_channel_code]);
  
  if (_v_result.rows.length === 0) {
    throw new Error(`채널을 찾을 수 없습니다: ${p_channel_code}`);
  }
  
  return _v_result.rows[0].channel_id;
}

/**
 * 이벤트 존재 여부 확인
 */
async function checkEventExists(p_channel_id, p_external_id) {
  const _v_query = `
    SELECT event_id 
    FROM events 
    WHERE channel_id = $1 AND external_id = $2
  `;
  const _v_result = await _v_pool.query(_v_query, [p_channel_id, p_external_id]);
  
  return _v_result.rows.length > 0 ? _v_result.rows[0].event_id : null;
}

/**
 * 이벤트 삽입
 */
async function insertEvent(p_channel_id, p_event) {
  const _v_query = `
    INSERT INTO events (
      channel_id, external_id, title, subtitle, description,
      start_date, end_date, discount_rate, benefit_summary, benefit_detail,
      target_products, conditions, event_url, status, priority, tags
    ) VALUES (
      $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16
    )
    RETURNING event_id
  `;
  
  const _v_values = [
    p_channel_id,
    p_event.external_id,
    p_event.title,
    p_event.subtitle,
    p_event.description,
    p_event.start_date,
    p_event.end_date,
    p_event.discount_rate,
    p_event.benefit_summary,
    p_event.benefit_detail,
    p_event.target_products,
    p_event.conditions,
    p_event.event_url,
    p_event.status,
    p_event.priority,
    p_event.tags
  ];
  
  const _v_result = await _v_pool.query(_v_query, _v_values);
  return _v_result.rows[0].event_id;
}

/**
 * 이벤트 업데이트
 */
async function updateEvent(p_event_id, p_event) {
  const _v_query = `
    UPDATE events SET
      title = $2,
      subtitle = $3,
      description = $4,
      start_date = $5,
      end_date = $6,
      discount_rate = $7,
      benefit_summary = $8,
      benefit_detail = $9,
      target_products = $10,
      conditions = $11,
      event_url = $12,
      status = $13,
      priority = $14,
      tags = $15,
      updated_at = CURRENT_TIMESTAMP
    WHERE event_id = $1
  `;
  
  const _v_values = [
    p_event_id,
    p_event.title,
    p_event.subtitle,
    p_event.description,
    p_event.start_date,
    p_event.end_date,
    p_event.discount_rate,
    p_event.benefit_summary,
    p_event.benefit_detail,
    p_event.target_products,
    p_event.conditions,
    p_event.event_url,
    p_event.status,
    p_event.priority,
    p_event.tags
  ];
  
  await _v_pool.query(_v_query, _v_values);
}

/**
 * 메인 실행 함수
 */
async function main() {
  try {
    console.log('='.repeat(60));
    console.log('🚀 이니스프리 이벤트 데이터 삽입 시작');
    console.log('='.repeat(60));
    
    // 1. 채널 ID 조회
    console.log('\n📌 Step 1: 채널 정보 조회');
    const _v_channel_id = await getChannelId('INNISFREE_MALL');
    console.log(`   ✅ 채널 ID: ${_v_channel_id}`);
    
    // 2. 이벤트 데이터 삽입/업데이트
    console.log('\n📌 Step 2: 이벤트 데이터 처리');
    
    let _v_new_count = 0;
    let _v_update_count = 0;
    
    for (const _v_event of _v_innisfree_events) {
      console.log(`\n   📝 처리 중: ${_v_event.title}`);
      
      // 기존 이벤트 확인
      const _v_existing_id = await checkEventExists(_v_channel_id, _v_event.external_id);
      
      if (_v_existing_id) {
        // 업데이트
        await updateEvent(_v_existing_id, _v_event);
        console.log(`   ✅ 업데이트 완료 (Event ID: ${_v_existing_id})`);
        _v_update_count++;
      } else {
        // 신규 삽입
        const _v_new_id = await insertEvent(_v_channel_id, _v_event);
        console.log(`   ✅ 신규 삽입 완료 (Event ID: ${_v_new_id})`);
        _v_new_count++;
      }
    }
    
    // 3. 결과 조회
    console.log('\n📌 Step 3: 저장된 이벤트 확인');
    const _v_query = `
      SELECT e.event_id, e.title, e.start_date, e.end_date, e.discount_rate, e.status
      FROM events e
      WHERE e.channel_id = $1
      ORDER BY e.created_at DESC
      LIMIT 5
    `;
    const _v_result = await _v_pool.query(_v_query, [_v_channel_id]);
    
    console.log('\n   최근 이니스프리 이벤트:');
    _v_result.rows.forEach((_v_row, _v_index) => {
      console.log(`   ${_v_index + 1}. [ID: ${_v_row.event_id}] ${_v_row.title}`);
      console.log(`      기간: ${_v_row.start_date} ~ ${_v_row.end_date}`);
      console.log(`      할인율: ${_v_row.discount_rate}% | 상태: ${_v_row.status}`);
    });
    
    // 4. 완료
    console.log('\n' + '='.repeat(60));
    console.log('✅ 이니스프리 이벤트 데이터 삽입 완료!');
    console.log('='.repeat(60));
    console.log(`📊 처리 결과:`);
    console.log(`   - 신규 삽입: ${_v_new_count}개`);
    console.log(`   - 업데이트: ${_v_update_count}개`);
    console.log(`   - 총 처리: ${_v_new_count + _v_update_count}개`);
    console.log('='.repeat(60));
    console.log('\n🌐 상담 시스템에서 조회 가능:');
    console.log('   - 프론트엔드: http://localhost:3001/search');
    console.log('   - 검색어: 이니스프리, 레티놀, 비타민C');
    console.log('='.repeat(60));
    
  } catch (error) {
    console.error('\n' + '='.repeat(60));
    console.error('❌ 오류 발생');
    console.error('='.repeat(60));
    console.error(error);
    console.error('='.repeat(60));
    process.exit(1);
  } finally {
    // 연결 종료
    await _v_pool.end();
  }
}

// 스크립트 실행
main();


