/**
 * Execution Routes
 * API endpoints for crawler execution logs and monitoring
 */

const express = require('express');
const router = express.Router();
const executionService = require('../services/executionService');
const logger = require('../config/logger');

/**
 * GET /api/executions
 * Get all executions
 * Query params:
 *  - brand_id (optional) - Filter by brand
 *  - platform_id (optional) - Filter by platform
 *  - status (optional) - Filter by status (pending|running|success|failed)
 *  - trigger_type (optional) - Filter by trigger type (scheduled|manual)
 *  - limit (optional) - Limit number of results
 *  - with_details (optional) - Include brand and platform details (default: true)
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
      if (!['pending', 'running', 'success', 'failed'].includes(req.query.status)) {
        return res.status(400).json({
          success: false,
          message: 'Invalid status. Must be one of: pending, running, success, failed',
        });
      }
      filters.status = req.query.status;
    }

    // Filter by trigger_type if provided
    if (req.query.trigger_type) {
      if (!['scheduled', 'manual'].includes(req.query.trigger_type)) {
        return res.status(400).json({
          success: false,
          message: 'Invalid trigger_type. Must be either "scheduled" or "manual"',
        });
      }
      filters.trigger_type = req.query.trigger_type;
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

    const withDetails = req.query.with_details !== 'false';
    const result = await executionService.getAllExecutions(filters, options, withDetails);

    res.json(result);
  } catch (error) {
    logger.error('GET /api/executions error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch executions',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/executions/recent
 * Get recent executions
 * Query params: limit (optional, default: 50)
 */
router.get('/recent', async (req, res) => {
  try {
    let limit = 50;

    if (req.query.limit) {
      const parsedLimit = parseInt(req.query.limit);
      if (isNaN(parsedLimit) || parsedLimit <= 0) {
        return res.status(400).json({
          success: false,
          message: 'limit must be a positive number',
        });
      }
      limit = parsedLimit;
    }

    const result = await executionService.getRecentExecutions(limit);

    res.json(result);
  } catch (error) {
    logger.error('GET /api/executions/recent error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch recent executions',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/executions/stats
 * Get execution statistics
 * Query params:
 *  - brand_id (optional) - Filter by brand
 *  - platform_id (optional) - Filter by platform
 */
router.get('/stats', async (req, res) => {
  try {
    const filters = {};

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

    const result = await executionService.getStatistics(filters);

    res.json(result);
  } catch (error) {
    logger.error('GET /api/executions/stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch execution statistics',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/executions/check-running
 * Check if there's a running execution for a brand/platform
 * Query params: brand_id (required), platform_id (required)
 */
router.get('/check-running', async (req, res) => {
  try {
    const { brand_id, platform_id } = req.query;

    // Validate required params
    if (!brand_id || !platform_id) {
      return res.status(400).json({
        success: false,
        message: 'brand_id and platform_id are required',
      });
    }

    // UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(brand_id) || !uuidRegex.test(platform_id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid brand_id or platform_id format',
      });
    }

    const result = await executionService.checkRunningExecution(brand_id, platform_id);

    res.json(result);
  } catch (error) {
    logger.error('GET /api/executions/check-running error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to check running execution',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/executions/:id
 * Get execution by ID
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    // Basic UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid execution ID format',
      });
    }

    const result = await executionService.getExecutionById(id);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error(`GET /api/executions/${req.params.id} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch execution',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

module.exports = router;
