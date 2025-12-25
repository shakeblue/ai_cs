/**
 * Config Routes
 * API endpoints for crawler configuration management
 */

const express = require('express');
const router = express.Router();
const configService = require('../services/configService');
const logger = require('../config/logger');

/**
 * GET /api/config
 * Get all configuration settings
 */
router.get('/', async (req, res) => {
  try {
    const result = await configService.getAllConfigs();

    res.json(result);
  } catch (error) {
    logger.error('GET /api/config error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch configurations',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/config/time-range
 * Get time range configuration (past_days, future_days)
 */
router.get('/time-range', async (req, res) => {
  try {
    const result = await configService.getTimeRange();

    res.json(result);
  } catch (error) {
    logger.error('GET /api/config/time-range error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch time range configuration',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * PUT /api/config/time-range
 * Update time range configuration
 * Body: { pastDays, futureDays }
 */
router.put('/time-range', async (req, res) => {
  try {
    const { pastDays, futureDays } = req.body;

    // Validate required fields
    if (pastDays === undefined || futureDays === undefined) {
      return res.status(400).json({
        success: false,
        message: 'pastDays and futureDays are required',
      });
    }

    // Validate types and values
    const pastDaysNum = Number(pastDays);
    const futureDaysNum = Number(futureDays);

    if (isNaN(pastDaysNum) || isNaN(futureDaysNum)) {
      return res.status(400).json({
        success: false,
        message: 'pastDays and futureDays must be valid numbers',
      });
    }

    if (pastDaysNum < 0 || futureDaysNum < 0) {
      return res.status(400).json({
        success: false,
        message: 'pastDays and futureDays must be positive numbers',
      });
    }

    if (!Number.isInteger(pastDaysNum) || !Number.isInteger(futureDaysNum)) {
      return res.status(400).json({
        success: false,
        message: 'pastDays and futureDays must be integers',
      });
    }

    const result = await configService.updateTimeRange(pastDaysNum, futureDaysNum);

    res.json(result);
  } catch (error) {
    logger.error('PUT /api/config/time-range error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update time range configuration',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/config/default-schedule
 * Get default cron schedule
 */
router.get('/default-schedule', async (req, res) => {
  try {
    const result = await configService.getDefaultSchedule();

    res.json(result);
  } catch (error) {
    logger.error('GET /api/config/default-schedule error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch default schedule',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/config/crawler-timeout
 * Get crawler timeout in seconds
 */
router.get('/crawler-timeout', async (req, res) => {
  try {
    const result = await configService.getCrawlerTimeout();

    res.json(result);
  } catch (error) {
    logger.error('GET /api/config/crawler-timeout error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch crawler timeout',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/config/max-concurrent-jobs
 * Get max concurrent jobs
 */
router.get('/max-concurrent-jobs', async (req, res) => {
  try {
    const result = await configService.getMaxConcurrentJobs();

    res.json(result);
  } catch (error) {
    logger.error('GET /api/config/max-concurrent-jobs error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch max concurrent jobs',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * GET /api/config/:key
 * Get configuration value by key
 */
router.get('/:key', async (req, res) => {
  try {
    const { key } = req.params;

    if (!key || typeof key !== 'string' || key.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid configuration key',
      });
    }

    const result = await configService.getConfig(key);

    if (!result.success) {
      return res.status(404).json(result);
    }

    res.json(result);
  } catch (error) {
    logger.error(`GET /api/config/${req.params.key} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch configuration',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * PUT /api/config/:key
 * Update configuration value
 * Body: { value, description? }
 */
router.put('/:key', async (req, res) => {
  try {
    const { key } = req.params;
    const { value, description } = req.body;

    // Validate key
    if (!key || typeof key !== 'string' || key.trim().length === 0) {
      return res.status(400).json({
        success: false,
        message: 'Invalid configuration key',
      });
    }

    // Validate value
    if (value === undefined || value === null) {
      return res.status(400).json({
        success: false,
        message: 'value is required',
      });
    }

    // Convert value to string if not already
    const valueStr = typeof value === 'string' ? value : String(value);

    // Validate description if provided
    if (description !== undefined && typeof description !== 'string') {
      return res.status(400).json({
        success: false,
        message: 'description must be a string',
      });
    }

    const result = await configService.updateConfig(key, valueStr, description);

    res.json(result);
  } catch (error) {
    logger.error(`PUT /api/config/${req.params.key} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Failed to update configuration',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

module.exports = router;
