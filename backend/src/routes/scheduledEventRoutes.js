/**
 * Scheduled Event Routes
 * API endpoints for events crawled by the scheduled crawler
 * Note: Different from /api/events which handles general platform events
 */

const express = require('express');
const router = express.Router();
const scheduledEventService = require('../services/scheduledEventService');
const logger = require('../config/logger');

/**
 * GET /api/scheduled-events
 * Get all crawled events
 * Query params:
 *  - brand_id (optional) - Filter by brand
 *  - platform_id (optional) - Filter by platform
 *  - status (optional) - Filter by status (upcoming|ongoing|ended)
 *  - event_type (optional) - Filter by type (live|replay)
 *  - limit (optional) - Limit number of results
 */
router.get('/', async (req, res) => {
  try {
    const filters = {};
    const options = {};

    // UUID validation regex
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

    // Filter by brand_id if provided
    if (req.query.brand_id) {
      if (!uuidRegex.test(req.query.brand_id)) {
        return res.status(400).json({
          success: false,
          message: 'Invalid brand_id format',
        });
      }
      filters.brand_id = req.query.brand_id;
    }

    // Filter by platform_id if provided
    if (req.query.platform_id) {
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
      if (!['upcoming', 'ongoing', 'ended'].includes(req.query.status)) {
        return res.status(400).json({
          success: false,
          message: 'Invalid status. Must be one of: upcoming, ongoing, ended',
        });
      }
      filters.status = req.query.status;
    }

    // Filter by event_type if provided
    if (req.query.event_type) {
      if (!['live', 'replay'].includes(req.query.event_type)) {
        return res.status(400).json({
          success: false,
          message: 'Invalid event_type. Must be either "live" or "replay"',
        });
      }
      filters.event_type = req.query.event_type;
    }

    // Apply limit if provided
    if (req.query.limit) {
      const limit = parseInt(req.query.limit);
      if (isNaN(limit) || limit <= 0) {
        return res.status(400).json({
          success: false,
          message: 'limit must be a positive number',
        });
      }
      options.limit = limit;
    }

    const result = await scheduledEventService.getAllEvents(filters, options);

    res.json(result);
  } catch (error) {
    logger.error('GET /api/scheduled-events error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch scheduled events',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/scheduled-events/:id
 * Get event by ID
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid event ID format',
      });
    }

    const result = await scheduledEventService.getEventById(id);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error(`GET /api/scheduled-events/${req.params.id} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch scheduled event',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

module.exports = router;
