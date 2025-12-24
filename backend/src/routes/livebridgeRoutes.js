/**
 * Livebridge Routes
 * API endpoints for livebridge promotional data
 */

const express = require('express');
const router = express.Router();
const livebridgeService = require('../services/livebridgeService');
const logger = require('../config/logger');

/**
 * GET /api/livebridge
 * Get paginated list of livebridges
 * Query params: page, limit, sort
 */
router.get('/', async (req, res) => {
  try {
    const {
      page = 1,
      limit = 20,
      sort = 'date_desc',
    } = req.query;

    logger.info(`GET /api/livebridge - page: ${page}, limit: ${limit}, sort: ${sort}`);

    const result = await livebridgeService.getLivebridges({
      page: parseInt(page),
      limit: parseInt(limit),
      sort,
    });

    if (!result.success) {
      return res.status(500).json({
        success: false,
        message: 'Failed to fetch livebridges',
        error: result.error,
      });
    }

    res.json({
      success: true,
      data: result.data,
      pagination: result.pagination,
    });
  } catch (error) {
    logger.error(`Error in GET /api/livebridge: ${error.message}`);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message,
    });
  }
});

/**
 * GET /api/livebridge/stats
 * Get livebridge statistics
 */
router.get('/stats', async (req, res) => {
  try {
    logger.info('GET /api/livebridge/stats');

    const result = await livebridgeService.getLivebridgeStats();

    if (!result.success) {
      return res.status(500).json({
        success: false,
        message: 'Failed to fetch statistics',
        error: result.error,
      });
    }

    res.json({
      success: true,
      data: result.data,
    });
  } catch (error) {
    logger.error(`Error in GET /api/livebridge/stats: ${error.message}`);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message,
    });
  }
});

/**
 * GET /api/livebridge/:id
 * Get livebridge data by ID with all related data
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    logger.info(`GET /api/livebridge/${id}`);

    // Validate ID
    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        success: false,
        message: 'Invalid livebridge ID',
      });
    }

    const result = await livebridgeService.getLivebridgeById(parseInt(id));

    if (!result.success) {
      const statusCode = result.error === 'Livebridge not found' ? 404 : 500;
      return res.status(statusCode).json({
        success: false,
        message: result.error,
      });
    }

    res.json({
      success: true,
      data: result.data,
    });
  } catch (error) {
    logger.error(`Error in GET /api/livebridge/:id: ${error.message}`);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message,
    });
  }
});

/**
 * GET /api/livebridge/url/:encodedUrl
 * Get livebridge data by URL
 * Note: URL should be URL-encoded
 */
router.get('/url/:encodedUrl', async (req, res) => {
  try {
    const { encodedUrl } = req.params;

    // Decode URL
    const url = decodeURIComponent(encodedUrl);

    logger.info(`GET /api/livebridge/url/${url}`);

    // Validate URL
    if (!url || !url.startsWith('https://shoppinglive.naver.com/livebridge/')) {
      return res.status(400).json({
        success: false,
        message: 'Invalid livebridge URL',
      });
    }

    const result = await livebridgeService.getLivebridgeByUrl(url);

    if (!result.success) {
      const statusCode = result.error === 'Livebridge not found' ? 404 : 500;
      return res.status(statusCode).json({
        success: false,
        message: result.error,
      });
    }

    res.json({
      success: true,
      data: result.data,
    });
  } catch (error) {
    logger.error(`Error in GET /api/livebridge/url/:encodedUrl: ${error.message}`);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message,
    });
  }
});

module.exports = router;
