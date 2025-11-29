/**
 * 크롤링된 데이터를 Supabase에 저장하는 스크립트
 * 
 * 사용법:
 *   node scripts/import-to-supabase.js
 */

require('dotenv').config();
const { supabase, insert, select, update } = require('../src/config/supabase');
const { getRealCollectedEvents, getRealCollectedDetail } = require('../../frontend/src/mockData/realCollectedData');
const logger = require('../src/config/logger');

/**
 * 채널 코드를 채널 ID로 변환
 */
async function getChannelIdByCode(channelCode) {
  try {
    const { rows } = await select('channels', 'channel_id', { channel_code: channelCode });
    if (rows && rows.length > 0) {
      return rows[0].channel_id;
    }
    return null;
  } catch (error) {
    logger.error(`채널 ID 조회 실패 (${channelCode}):`, error);
    return null;
  }
}

/**
 * 라이브 방송 데이터를 Supabase에 저장
 */
async function saveLiveBroadcast(liveData) {
  try {
    // meta와 metadata 둘 다 지원
    const meta = liveData.meta || liveData.metadata;
    const schedule = liveData.schedule || {};
    
    if (!meta || !meta.live_id) {
      logger.warn('라이브 ID가 없습니다:', liveData);
      return null;
    }

    // 채널 코드 결정
    let channelCode = 'NAVER';
    if (meta.platform_name === '카카오') channelCode = 'KAKAO';
    else if (meta.platform_name === '11번가') channelCode = '11ST';
    else if (meta.platform_name === 'G마켓') channelCode = 'GMARKET';
    else if (meta.platform_name === '올리브영') channelCode = 'OLIVEYOUNG';
    else if (meta.platform_name === '그립') channelCode = 'GRIP';
    else if (meta.platform_name === '무신사') channelCode = 'MUSINSA';
    else if (meta.platform_name === '롯데온') channelCode = 'LOTTEON';
    else if (meta.platform_name === '아모레몰') channelCode = 'AMOREMALL';

    // 채널 ID 조회
    const channelId = await getChannelIdByCode(channelCode);
    if (!channelId) {
      logger.warn(`채널을 찾을 수 없습니다: ${channelCode}`);
      return null;
    }

    // 날짜 파싱
    const broadcastDate = schedule.broadcast_date || meta.collected_at?.split('T')[0] || new Date().toISOString().split('T')[0];
    const benefitStart = schedule.benefit_start_datetime || null;
    const benefitEnd = schedule.benefit_end_datetime || null;

    // 라이브 방송 기본 정보 저장
    const broadcastData = {
      live_id: meta.live_id,
      channel_id: channelId,
      channel_code: channelCode,
      platform_name: meta.platform_name || '',
      brand_name: meta.brand_name || '',
      live_title_customer: meta.live_title_customer || meta.live_title_cs || '',
      live_title_cs: meta.live_title_cs || '',
      source_url: meta.source_url || '',
      thumbnail_url: meta.thumbnail_url || '',
      broadcast_date: broadcastDate,
      broadcast_start_time: schedule.broadcast_start_time || null,
      broadcast_end_time: schedule.broadcast_end_time || null,
      benefit_valid_type: schedule.benefit_valid_type || null,
      benefit_start_datetime: benefitStart || null,
      benefit_end_datetime: benefitEnd || null,
      broadcast_type: schedule.broadcast_type || schedule.broadcast_format || null,
      status: meta.status || 'PENDING',
      collected_at: meta.collected_at || new Date().toISOString(),
    };

    // 기존 데이터 확인
    const { rows: existing } = await select('live_broadcasts', 'live_id', { live_id: meta.live_id });
    
    if (existing && existing.length > 0) {
      // 업데이트
      await update('live_broadcasts', broadcastData, { live_id: meta.live_id });
      logger.info(`✅ 업데이트: ${meta.live_id} - ${meta.live_title_customer}`);
    } else {
      // 삽입
      await insert('live_broadcasts', broadcastData);
      logger.info(`✅ 삽입: ${meta.live_id} - ${meta.live_title_customer}`);
    }

    // 상품 정보 저장
    if (liveData.products) {
      const products = Array.isArray(liveData.products) 
        ? liveData.products 
        : (liveData.products.product_list || liveData.products.product_details || []);
      
      // 기존 상품 삭제 후 재삽입
      // (Supabase는 직접 DELETE를 지원하지 않으므로, RPC 함수를 사용하거나 개별 삭제 필요)
      
      for (const product of products) {
        const productData = {
          live_id: meta.live_id,
          product_order: product.product_order || 0,
          product_name: product.product_name || '',
          sku: product.sku || null,
          original_price: product.original_price || null,
          sale_price: product.sale_price || null,
          discount_rate: product.discount_rate || null,
          product_type: product.product_type || null,
          stock_info: product.stock_info || null,
          set_composition: product.set_composition || null,
          product_url: product.product_url || null,
        };
        
        await insert('live_products', productData);
      }
      logger.info(`   상품 ${products.length}개 저장 완료`);
    }

    // 혜택 정보 저장
    if (liveData.benefits) {
      const benefits = liveData.benefits;
      
      // 할인 정보
      if (benefits.discounts && Array.isArray(benefits.discounts)) {
        for (const discount of benefits.discounts) {
          await insert('live_benefits', {
            live_id: meta.live_id,
            benefit_type: '할인',
            benefit_name: discount.discount_type || discount.benefit_name || '',
            benefit_detail: discount.discount_detail || discount.benefit_detail || '',
            benefit_condition: discount.discount_condition || discount.benefit_condition || null,
            benefit_valid_period: discount.discount_valid_period || discount.benefit_valid_period || null,
            quantity_limit: discount.quantity_limit || null,
          });
        }
      }
      
      // 사은품 정보
      if (benefits.gifts && Array.isArray(benefits.gifts)) {
        for (const gift of benefits.gifts) {
          await insert('live_benefits', {
            live_id: meta.live_id,
            benefit_type: '사은품',
            benefit_name: gift.gift_name || gift.benefit_name || '',
            benefit_detail: gift.gift_detail || gift.benefit_detail || '',
            benefit_condition: gift.gift_condition || gift.benefit_condition || null,
            quantity_limit: gift.gift_quantity_limit || gift.quantity_limit || null,
          });
        }
      }
      
      // 쿠폰 정보
      if (benefits.coupons && Array.isArray(benefits.coupons)) {
        for (const coupon of benefits.coupons) {
          await insert('live_benefits', {
            live_id: meta.live_id,
            benefit_type: '쿠폰',
            benefit_name: coupon.coupon_name || coupon.coupon_detail || '',
            benefit_detail: coupon.coupon_detail || coupon.benefit_detail || '',
            benefit_condition: coupon.coupon_issue_condition || coupon.benefit_condition || null,
          });
        }
      }
      
      // 포인트 정보
      if (benefits.points && Array.isArray(benefits.points)) {
        for (const point of benefits.points) {
          await insert('live_benefits', {
            live_id: meta.live_id,
            benefit_type: '포인트',
            benefit_name: point.point_name || point.benefit_name || '',
            benefit_detail: point.point_detail || point.benefit_detail || '',
            benefit_condition: point.point_condition || point.benefit_condition || null,
          });
        }
      }
      
      // 배송 정보
      if (benefits.shipping && Array.isArray(benefits.shipping)) {
        for (const shipping of benefits.shipping) {
          await insert('live_benefits', {
            live_id: meta.live_id,
            benefit_type: '배송',
            benefit_name: shipping.shipping_type || shipping.benefit_name || '',
            benefit_detail: shipping.shipping_detail || shipping.benefit_detail || '',
            benefit_condition: shipping.shipping_condition || shipping.benefit_condition || null,
          });
        }
      }
      
      const totalBenefits = 
        (benefits.discounts?.length || 0) +
        (benefits.gifts?.length || 0) +
        (benefits.coupons?.length || 0) +
        (benefits.points?.length || 0) +
        (benefits.shipping?.length || 0);
      logger.info(`   혜택 ${totalBenefits}개 저장 완료`);
    }

    // 키 멘션 저장
    if (liveData.live_specific?.key_mentions) {
      for (const mention of liveData.live_specific.key_mentions) {
        const [time, content] = mention.split('] ').length > 1 
          ? [mention.match(/\[(.*?)\]/)?.[1] || '', mention.split('] ')[1] || mention]
          : ['', mention];
        
        await insert('live_chat_messages', {
          live_id: meta.live_id,
          message_time: time,
          message_content: content,
          message_type: 'MENTION',
        });
      }
      logger.info(`   키 멘션 ${liveData.live_specific.key_mentions.length}개 저장 완료`);
    }

    // Q&A 저장
    if (liveData.live_specific?.broadcast_qa) {
      for (const qa of liveData.live_specific.broadcast_qa) {
        await insert('live_qa', {
          live_id: meta.live_id,
          question: qa.question || '',
          answer: qa.answer || '',
          questioner: null,
          answerer: null,
          question_date: null,
          answer_date: null,
          is_answered: !!qa.answer,
          helpful_count: 0,
          status: qa.answer ? '답변완료' : '답변대기',
        });
      }
      logger.info(`   Q&A ${liveData.live_specific.broadcast_qa.length}개 저장 완료`);
    }

    // 타임라인 저장
    if (liveData.live_specific?.timeline) {
      for (const timeline of liveData.live_specific.timeline) {
        await insert('live_timeline', {
          live_id: meta.live_id,
          time: timeline.time || '',
          content: timeline.content || '',
        });
      }
      logger.info(`   타임라인 ${liveData.live_specific.timeline.length}개 저장 완료`);
    }

    // 중복 정책 저장
    if (liveData.duplicate_policy) {
      const policy = liveData.duplicate_policy;
      await insert('live_duplicate_policy', {
        live_id: meta.live_id,
        coupon_duplicate: policy.coupon_duplicate || null,
        point_duplicate: policy.point_duplicate || null,
        other_promotion_duplicate: policy.other_promotion_duplicate || null,
        employee_discount: policy.employee_discount || null,
        duplicate_note: policy.duplicate_note || null,
      });
    }

    // 제한사항 저장
    if (liveData.restrictions) {
      const restrictions = liveData.restrictions;
      
      if (restrictions.excluded_products && Array.isArray(restrictions.excluded_products)) {
        for (const product of restrictions.excluded_products) {
          await insert('live_restrictions', {
            live_id: meta.live_id,
            restriction_type: '제외상품',
            restriction_detail: product,
          });
        }
      }
      
      if (restrictions.channel_restrictions && Array.isArray(restrictions.channel_restrictions)) {
        for (const restriction of restrictions.channel_restrictions) {
          await insert('live_restrictions', {
            live_id: meta.live_id,
            restriction_type: '채널제한',
            restriction_detail: restriction,
          });
        }
      }
      
      if (restrictions.payment_restrictions && Array.isArray(restrictions.payment_restrictions)) {
        for (const restriction of restrictions.payment_restrictions) {
          await insert('live_restrictions', {
            live_id: meta.live_id,
            restriction_type: '결제제한',
            restriction_detail: restriction,
          });
        }
      }
      
      if (restrictions.region_restrictions && Array.isArray(restrictions.region_restrictions)) {
        for (const restriction of restrictions.region_restrictions) {
          await insert('live_restrictions', {
            live_id: meta.live_id,
            restriction_type: '지역제한',
            restriction_detail: restriction,
          });
        }
      }
      
      if (restrictions.other_restrictions && Array.isArray(restrictions.other_restrictions)) {
        for (const restriction of restrictions.other_restrictions) {
          await insert('live_restrictions', {
            live_id: meta.live_id,
            restriction_type: '기타제한',
            restriction_detail: restriction,
          });
        }
      }
    }

    // CS 정보 저장
    if (liveData.cs_info) {
      const csInfo = liveData.cs_info;
      await insert('live_cs_info', {
        live_id: meta.live_id,
        expected_questions: csInfo.expected_questions || [],
        response_scripts: csInfo.response_scripts || [],
        risk_points: csInfo.risk_points || [],
        cs_note: csInfo.cs_note || null,
      });
    }

    // 공지사항 저장 (올리브영, 아모레몰 등)
    if (liveData.notice_section?.notices) {
      for (const notice of liveData.notice_section.notices) {
        await insert('live_notices', {
          notice_id: notice.notice_id || `NOTICE_${meta.live_id}_${Date.now()}`,
          live_id: meta.live_id,
          title: notice.title || '',
          content: notice.content || '',
          post_date: notice.post_date || null,
          view_count: notice.view_count || 0,
          is_important: notice.is_important || false,
        });
      }
    }

    // FAQ 저장 (올리브영, 아모레몰 등)
    if (liveData.faq_section?.categories) {
      for (const category of liveData.faq_section.categories) {
        if (category.faqs && Array.isArray(category.faqs)) {
          for (const faq of category.faqs) {
            await insert('live_faqs', {
              faq_id: faq.faq_id || `FAQ_${meta.live_id}_${Date.now()}`,
              live_id: meta.live_id,
              category: category.category_name || faq.category || null,
              question: faq.question || '',
              answer: faq.answer || '',
              view_count: faq.view_count || 0,
              helpful_count: faq.helpful_count || 0,
            });
          }
        }
      }
    }

    return meta.live_id;
  } catch (error) {
    logger.error(`라이브 방송 저장 실패 (${liveData.meta?.live_id || liveData.metadata?.live_id}):`, error);
    throw error;
  }
}

/**
 * 모든 크롤링 데이터를 Supabase에 저장
 */
async function importAllData() {
  try {
    logger.info('='.repeat(60));
    logger.info('크롤링 데이터 Supabase 저장 시작');
    logger.info('='.repeat(60));

    // 실제 수집 데이터 가져오기
    const { getAllBrandsData } = require('../../frontend/src/mockData/realCollectedData');
    const allLiveData = getAllBrandsData();

    logger.info(`총 ${allLiveData.length}개의 라이브 방송 데이터를 처리합니다.`);

    let successCount = 0;
    let errorCount = 0;

    // 배치 처리 (한 번에 너무 많이 처리하지 않도록)
    const batchSize = 10;
    for (let i = 0; i < allLiveData.length; i += batchSize) {
      const batch = allLiveData.slice(i, i + batchSize);
      
      logger.info(`\n[${i + 1}-${Math.min(i + batchSize, allLiveData.length)}/${allLiveData.length}] 배치 처리 중...`);
      
      for (const liveData of batch) {
        try {
          await saveLiveBroadcast(liveData);
          successCount++;
        } catch (error) {
          errorCount++;
          logger.error(`저장 실패:`, error.message);
        }
      }
      
      // 배치 간 짧은 대기 (API Rate Limit 방지)
      if (i + batchSize < allLiveData.length) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    logger.info('\n' + '='.repeat(60));
    logger.info('데이터 저장 완료!');
    logger.info(`  ✅ 성공: ${successCount}개`);
    logger.info(`  ❌ 실패: ${errorCount}개`);
    logger.info('='.repeat(60));

  } catch (error) {
    logger.error('데이터 저장 중 오류 발생:', error);
    process.exit(1);
  }
}

// 스크립트 실행
if (require.main === module) {
  importAllData()
    .then(() => {
      logger.info('모든 작업이 완료되었습니다.');
      process.exit(0);
    })
    .catch((error) => {
      logger.error('작업 실패:', error);
      process.exit(1);
    });
}

module.exports = { importAllData, saveLiveBroadcast };

