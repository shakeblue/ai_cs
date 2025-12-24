/**
 * Naver SmartStore Event Routes
 * API endpoints for Naver SmartStore event data
 */

const express = require('express');
const router = express.Router();
const { supabase } = require('../src/config/supabase');
const logger = require('../src/config/logger');

/**
 * GET /api/naver-smartstore-events
 * Get all Naver SmartStore events with filtering and pagination
 */
router.get('/', async (req, res) => {
  try {
    const {
      brand_name,
      limit = 20,
      offset = 0,
      sort_by = 'created_at',
      sort_order = 'desc'
    } = req.query;

    logger.info('Fetching Naver SmartStore events', {
      brand_name,
      limit,
      offset,
      sort_by,
      sort_order
    });

    // Build query
    let query = supabase
      .from('naver_smartstore_event')
      .select('*', { count: 'exact' });

    // Apply filters
    if (brand_name) {
      query = query.eq('brand_name', brand_name);
    }

    // Apply sorting
    const ascending = sort_order.toLowerCase() === 'asc';
    query = query.order(sort_by, { ascending });

    // Apply pagination
    query = query.range(
      parseInt(offset),
      parseInt(offset) + parseInt(limit) - 1
    );

    // Execute query
    const { data, error, count } = await query;

    if (error) {
      logger.error('Supabase query error:', error);
      throw error;
    }

    // Parse JSON fields
    const events = data.map(event => ({
      ...event,
      benefits_by_purchase_amount: typeof event.benefits_by_purchase_amount === 'string'
        ? JSON.parse(event.benefits_by_purchase_amount)
        : event.benefits_by_purchase_amount || [],
      coupon_benefits: typeof event.coupon_benefits === 'string'
        ? JSON.parse(event.coupon_benefits)
        : event.coupon_benefits || [],
      image_urls: typeof event.image_urls === 'string'
        ? JSON.parse(event.image_urls)
        : event.image_urls || [],
      raw_ocr_data: typeof event.raw_ocr_data === 'string'
        ? JSON.parse(event.raw_ocr_data)
        : event.raw_ocr_data || {}
    }));

    res.json({
      success: true,
      data: events,
      pagination: {
        total: count,
        limit: parseInt(limit),
        offset: parseInt(offset),
        total_pages: Math.ceil(count / parseInt(limit))
      }
    });

  } catch (error) {
    logger.error('Error fetching Naver SmartStore events:', error);
    res.status(500).json({
      success: false,
      message: '이벤트 조회 중 오류가 발생했습니다.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

/**
 * GET /api/naver-smartstore-events/:id
 * Get a specific event by ID
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    logger.info('Fetching Naver SmartStore event by ID', { id });

    const { data, error } = await supabase
      .from('naver_smartstore_event')
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return res.status(404).json({
          success: false,
          message: '이벤트를 찾을 수 없습니다.'
        });
      }
      throw error;
    }

    // Parse JSON fields
    const event = {
      ...data,
      benefits_by_purchase_amount: typeof data.benefits_by_purchase_amount === 'string'
        ? JSON.parse(data.benefits_by_purchase_amount)
        : data.benefits_by_purchase_amount || [],
      coupon_benefits: typeof data.coupon_benefits === 'string'
        ? JSON.parse(data.coupon_benefits)
        : data.coupon_benefits || [],
      image_urls: typeof data.image_urls === 'string'
        ? JSON.parse(data.image_urls)
        : data.image_urls || [],
      raw_ocr_data: typeof data.raw_ocr_data === 'string'
        ? JSON.parse(data.raw_ocr_data)
        : data.raw_ocr_data || {}
    };

    res.json({
      success: true,
      data: event
    });

  } catch (error) {
    logger.error('Error fetching Naver SmartStore event:', error);
    res.status(500).json({
      success: false,
      message: '이벤트 조회 중 오류가 발생했습니다.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

/**
 * GET /api/naver-smartstore-events/brands/list
 * Get list of unique brands
 */
router.get('/brands/list', async (req, res) => {
  try {
    logger.info('Fetching unique brands from Naver SmartStore events');

    const { data, error } = await supabase
      .from('naver_smartstore_event')
      .select('brand_name')
      .not('brand_name', 'is', null);

    if (error) {
      throw error;
    }

    // Get unique brands
    const brands = [...new Set(data.map(item => item.brand_name))].filter(Boolean).sort();

    res.json({
      success: true,
      data: brands
    });

  } catch (error) {
    logger.error('Error fetching brands:', error);
    res.status(500).json({
      success: false,
      message: '브랜드 목록 조회 중 오류가 발생했습니다.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

/**
 * POST /api/naver-smartstore-events
 * Create a new event (for admin/crawler use)
 */
router.post('/', async (req, res) => {
  try {
    const eventData = req.body;

    logger.info('Creating new Naver SmartStore event', {
      brand_name: eventData.brand_name,
      event_title: eventData.event_title
    });

    const { data, error } = await supabase
      .from('naver_smartstore_event')
      .insert([eventData])
      .select()
      .single();

    if (error) {
      throw error;
    }

    res.status(201).json({
      success: true,
      data: data,
      message: '이벤트가 성공적으로 생성되었습니다.'
    });

  } catch (error) {
    logger.error('Error creating Naver SmartStore event:', error);
    res.status(500).json({
      success: false,
      message: '이벤트 생성 중 오류가 발생했습니다.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

/**
 * PUT /api/naver-smartstore-events/:id
 * Update an existing event
 */
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const updateData = req.body;

    logger.info('Updating Naver SmartStore event', { id });

    const { data, error } = await supabase
      .from('naver_smartstore_event')
      .update(updateData)
      .eq('id', id)
      .select()
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return res.status(404).json({
          success: false,
          message: '이벤트를 찾을 수 없습니다.'
        });
      }
      throw error;
    }

    res.json({
      success: true,
      data: data,
      message: '이벤트가 성공적으로 업데이트되었습니다.'
    });

  } catch (error) {
    logger.error('Error updating Naver SmartStore event:', error);
    res.status(500).json({
      success: false,
      message: '이벤트 업데이트 중 오류가 발생했습니다.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

/**
 * DELETE /api/naver-smartstore-events/:id
 * Delete an event
 */
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    logger.info('Deleting Naver SmartStore event', { id });

    const { error } = await supabase
      .from('naver_smartstore_event')
      .delete()
      .eq('id', id);

    if (error) {
      throw error;
    }

    res.json({
      success: true,
      message: '이벤트가 성공적으로 삭제되었습니다.'
    });

  } catch (error) {
    logger.error('Error deleting Naver SmartStore event:', error);
    res.status(500).json({
      success: false,
      message: '이벤트 삭제 중 오류가 발생했습니다.',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined
    });
  }
});

module.exports = router;
