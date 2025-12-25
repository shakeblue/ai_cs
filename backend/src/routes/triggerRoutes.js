/**
 * Manual Trigger Routes
 * API endpoints for manually triggering crawler execution
 */

const express = require('express');
const router = express.Router();
const crawlerOrchestrator = require('../services/crawlerOrchestrator');
const logger = require('../config/logger');

/**
 * POST /api/trigger/crawl
 * Manually trigger crawler for a specific brand
 * Body: { brand_id }
 */
router.post('/crawl', async (req, res) => {
  try {
    const { brand_id } = req.body;

    // Validate brand_id
    if (!brand_id) {
      return res.status(400).json({
        success: false,
        message: 'brand_id is required',
      });
    }

    // UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(brand_id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid brand_id format',
      });
    }

    logger.info(`Manual crawler trigger requested for brand: ${brand_id}`);

    // Execute crawler (non-blocking - return immediately)
    // The crawler will run in the background
    setImmediate(async () => {
      try {
        await crawlerOrchestrator.executeCrawl(brand_id, 'manual');
        logger.info(`Manual crawler completed for brand: ${brand_id}`);
      } catch (error) {
        logger.error(`Manual crawler failed for brand: ${brand_id}:`, error);
      }
    });

    // Return immediately with pending status
    res.json({
      success: true,
      message: 'Crawler execution started',
      data: {
        brand_id,
        trigger_type: 'manual',
        status: 'pending',
      },
    });
  } catch (error) {
    logger.error('POST /api/trigger/crawl error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to trigger crawler',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

/**
 * POST /api/trigger/crawl/sync
 * Manually trigger crawler and wait for completion (synchronous)
 * Body: { brand_id }
 */
router.post('/crawl/sync', async (req, res) => {
  try {
    const { brand_id } = req.body;

    // Validate brand_id
    if (!brand_id) {
      return res.status(400).json({
        success: false,
        message: 'brand_id is required',
      });
    }

    // UUID validation
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(brand_id)) {
      return res.status(400).json({
        success: false,
        message: 'Invalid brand_id format',
      });
    }

    logger.info(`Synchronous manual crawler trigger for brand: ${brand_id}`);

    // Execute crawler and wait for completion
    const result = await crawlerOrchestrator.executeCrawl(brand_id, 'manual');

    res.json(result);
  } catch (error) {
    logger.error('POST /api/trigger/crawl/sync error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to execute crawler',
      error: process.env.NODE_ENV === 'development' ? error.message : undefined,
    });
  }
});

module.exports = router;
