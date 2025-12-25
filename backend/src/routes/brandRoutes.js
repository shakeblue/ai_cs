/**
 * Brand Routes
 * API endpoints for brand management
 */

const express = require('express');
const router = express.Router();
const brandService = require('../services/brandService');
const logger = require('../config/logger');

/**
 * GET /api/brands
 * Get all brands
 * Query params:
 *  - platform_id (optional) - Filter by platform
 *  - status (optional) - Filter by status (active|inactive)
 *  - with_platform (optional) - Include platform details (default: true)
 */
router.get('/', async (req, res) => {
  try {
    const filters = {};

    // Filter by platform_id if provided
    if (req.query.platform_id) {
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(req.query.platform_id)) {
        return res.status(400).json({
          success: false,
          message: 'Invalid platform_id format',
        });
      }
      filters.platform_id = req.query.platform_id;
    }

    // Filter by status if provided
    if (req.query.status) {
      if (!['active', 'inactive'].includes(req.query.status)) {
        return res.status(400).json({
          success: false,
          message: 'Invalid status. Must be "active" or "inactive"',
        });
      }
      filters.status = req.query.status;
    }

    const withPlatform = req.query.with_platform !== 'false';
    const result = await brandService.getAllBrands(filters, withPlatform);

    res.json(result);
  } catch (error) {
    logger.error('GET /api/brands error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch brands',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/brands/active
 * Get only active brands
 * Query params: platform_id (optional)
 */
router.get('/active', async (req, res) => {
  try {
    let platformId = null;

    if (req.query.platform_id) {
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(req.query.platform_id)) {
        return res.status(400).json({
          success: false,
          message: 'Invalid platform_id format',
        });
      }
      platformId = req.query.platform_id;
    }

    const result = await brandService.getActiveBrands(platformId);

    res.json(result);
  } catch (error) {
    logger.error('GET /api/brands/active error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch active brands',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/brands/:id
 * Get brand by ID
 * Query params: with_platform (optional) - Include platform details (default: true)
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid brand ID format',
      });
    }

    const withPlatform = req.query.with_platform !== 'false';
    const result = await brandService.getBrandById(id, withPlatform);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error(`GET /api/brands/${req.params.id} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch brand',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/brands/:id/schedule
 * Get effective schedule for brand (inherits from platform if not set)
 */
router.get('/:id/schedule', async (req, res) => {
  try {
    const { id } = req.params;

    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid brand ID format',
      });
    }

    const result = await brandService.getEffectiveSchedule(id);

    res.json(result);
  } catch (error) {
    logger.error(`GET /api/brands/${req.params.id}/schedule error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch brand schedule',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * POST /api/brands
 * Create new brand
 * Body: { name, search_text, platform_id, status?, schedule_cron? }
 */
router.post('/', async (req, res) => {
  try {
    const { name, search_text, platform_id, status, schedule_cron } = req.body;

    // Validate required fields
    if (!name || !search_text || !platform_id) {
      return res.status(400).json({
        success: false,
        message: 'name, search_text, and platform_id are required',
      });
    }

    // Validate name (non-empty string)
    if (typeof name !== 'string' || name.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'name must be a non-empty string',
      });
    }

    // Validate search_text (non-empty string)
    if (typeof search_text !== 'string' || search_text.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'search_text must be a non-empty string',
      });
    }

    // Validate platform_id (UUID format)
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(platform_id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid platform_id format',
      });
    }

    // Validate status if provided
    if (status && !['active', 'inactive'].includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'status must be either "active" or "inactive"',
      });
    }

    // Validate schedule_cron if provided (basic check)
    if (schedule_cron && typeof schedule_cron !== 'string') {
      return res.status(400).json({
        success: false,
        message: 'schedule_cron must be a string',
      });
    }

    const brandData = {
      name,
      search_text,
      platform_id,
      status,
      schedule_cron,
    };

    const result = await brandService.createBrand(brandData);

    if (!result.success) {
      return res.status(400).json(result);
    }

    res.status(201).json(result);
  } catch (error) {
    logger.error('POST /api/brands error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create brand',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * PUT /api/brands/:id
 * Update brand
 * Body: { name?, search_text?, platform_id?, status?, schedule_cron? }
 */
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { name, search_text, platform_id, status, schedule_cron } = req.body;

    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid brand ID format',
      });
    }

    // Validate name if provided
    if (name !== undefined && (typeof name !== 'string' || name.trim().length === 0)) {
      return res.status(400).json({
        success: false,
        message: 'name must be a non-empty string',
      });
    }

    // Validate search_text if provided
    if (search_text !== undefined && (typeof search_text !== 'string' || search_text.trim().length === 0)) {
      return res.status(400).json({
        success: false,
        message: 'search_text must be a non-empty string',
      });
    }

    // Validate platform_id if provided
    if (platform_id !== undefined && !uuidRegex.test(platform_id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid platform_id format',
      });
    }

    // Validate status if provided
    if (status !== undefined && !['active', 'inactive'].includes(status)) {
      return res.status(400).json({
        success: false,
        message: 'status must be either "active" or "inactive"',
      });
    }

    // Validate schedule_cron if provided
    if (schedule_cron !== undefined && schedule_cron !== null && typeof schedule_cron !== 'string') {
      return res.status(400).json({
        success: false,
        message: 'schedule_cron must be a string or null',
      });
    }

    const updateData = {};
    if (name !== undefined) updateData.name = name;
    if (search_text !== undefined) updateData.search_text = search_text;
    if (platform_id !== undefined) updateData.platform_id = platform_id;
    if (status !== undefined) updateData.status = status;
    if (schedule_cron !== undefined) updateData.schedule_cron = schedule_cron;

    // Check if there's anything to update
    if (Object.keys(updateData).length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No valid fields to update',
      });
    }

    const result = await brandService.updateBrand(id, updateData);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error(`PUT /api/brands/${req.params.id} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to update brand',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * DELETE /api/brands/:id
 * Delete brand
 */
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid brand ID format',
      });
    }

    const result = await brandService.deleteBrand(id);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error(`DELETE /api/brands/${req.params.id} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete brand',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

module.exports = router;
