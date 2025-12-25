/**
 * Platform Routes
 * API endpoints for platform management
 */

const express = require('express');
const router = express.Router();
const platformService = require('../services/platformService');
const logger = require('../config/logger');

/**
 * GET /api/platforms
 * Get all platforms
 * Query params: status (optional) - Filter by status (active|inactive)
 */
router.get('/', async (req, res) => {
  try {
    const filters = {};

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

    const result = await platformService.getAllPlatforms(filters);

    res.json(result);
  } catch (error) {
    logger.error('GET /api/platforms error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch platforms',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/platforms/active
 * Get only active platforms
 */
router.get('/active', async (req, res) => {
  try {
    const result = await platformService.getActivePlatforms();

    res.json(result);
  } catch (error) {
    logger.error('GET /api/platforms/active error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch active platforms',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/platforms/:id
 * Get platform by ID
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid platform ID format',
      });
    }

    const result = await platformService.getPlatformById(id);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error(`GET /api/platforms/${req.params.id} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch platform',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * POST /api/platforms
 * Create new platform
 * Body: { name, url_pattern, status?, schedule_cron? }
 */
router.post('/', async (req, res) => {
  try {
    const { name, url_pattern, status, schedule_cron } = req.body;

    // Validate required fields
    if (!name || !url_pattern) {
      return res.status(400).json({
        success: false,
        message: 'name and url_pattern are required',
      });
    }

    // Validate name (non-empty string)
    if (typeof name !== 'string' || name.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'name must be a non-empty string',
      });
    }

    // Validate url_pattern (must contain {query} placeholder)
    if (typeof url_pattern !== 'string' || !url_pattern.includes('{query}')) {
      return res.status(400).json({
        success: false,
        message: 'url_pattern must be a string containing {query} placeholder',
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

    const platformData = {
      name,
      url_pattern,
      status,
      schedule_cron,
    };

    const result = await platformService.createPlatform(platformData);

    if (!result.success) {
      return res.status(400).json(result);
    }

    res.status(201).json(result);
  } catch (error) {
    logger.error('POST /api/platforms error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create platform',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * PUT /api/platforms/:id
 * Update platform
 * Body: { name?, url_pattern?, status?, schedule_cron? }
 */
router.put('/:id', async (req, res) => {
  try {
    const { id } = req.params;
    const { name, url_pattern, status, schedule_cron } = req.body;

    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid platform ID format',
      });
    }

    // Validate name if provided
    if (name !== undefined && (typeof name !== 'string' || name.trim().length === 0)) {
      return res.status(400).json({
        success: false,
        message: 'name must be a non-empty string',
      });
    }

    // Validate url_pattern if provided
    if (url_pattern !== undefined && (typeof url_pattern !== 'string' || !url_pattern.includes('{query}'))) {
      return res.status(400).json({
        success: false,
        message: 'url_pattern must be a string containing {query} placeholder',
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
    if (url_pattern !== undefined) updateData.url_pattern = url_pattern;
    if (status !== undefined) updateData.status = status;
    if (schedule_cron !== undefined) updateData.schedule_cron = schedule_cron;

    // Check if there's anything to update
    if (Object.keys(updateData).length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No valid fields to update',
      });
    }

    const result = await platformService.updatePlatform(id, updateData);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error(`PUT /api/platforms/${req.params.id} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to update platform',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * DELETE /api/platforms/:id
 * Delete platform
 */
router.delete('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid platform ID format',
      });
    }

    const result = await platformService.deletePlatform(id);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error(`DELETE /api/platforms/${req.params.id} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete platform',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

module.exports = router;
