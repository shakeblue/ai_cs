/**
 * Broadcast Routes
 * API endpoints for broadcast data
 */

const express = require('express');
const router = express.Router();
const broadcastService = require('../services/broadcastService');
const logger = require('../config/logger');

/**
 * GET /api/broadcasts
 * Get paginated list of broadcasts with filters
 * Query params: page, limit, search, brand, status, sort
 */
router.get('/', async (req, res) => {
  try {
    const {
      page = 1,
      limit = 20,
      search = '',
      brand = '',
      status = '',
      sort = 'date_desc',
    } = req.query;

    logger.info(`GET /api/broadcasts - page: ${page}, limit: ${limit}, search: ${search}, brand: ${brand}, status: ${status}, sort: ${sort}`);

    const result = await broadcastService.getBroadcasts({
      page: parseInt(page),
      limit: parseInt(limit),
      search,
      brand,
      status,
      sort,
    });

    if (!result.success) {
      return res.status(500).json({
        success: false,
        message: 'Failed to fetch broadcasts',
        error: result.error,
      });
    }

    res.json({
      success: true,
      data: result.data,
      pagination: result.pagination,
    });
  } catch (error) {
    logger.error('GET /api/broadcasts error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message,
    });
  }
});

/**
 * GET /api/broadcasts/stats
 * Get broadcast statistics
 */
router.get('/stats', async (req, res) => {
  try {
    logger.info('GET /api/broadcasts/stats');

    const result = await broadcastService.getBroadcastStats();

    if (!result.success) {
      return res.status(500).json({
        success: false,
        message: 'Failed to fetch stats',
        error: result.error,
      });
    }

    res.json({
      success: true,
      data: result.data,
    });
  } catch (error) {
    logger.error('GET /api/broadcasts/stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message,
    });
  }
});

/**
 * GET /api/broadcasts/brands
 * Get list of unique brands
 */
router.get('/brands', async (req, res) => {
  try {
    logger.info('GET /api/broadcasts/brands');

    const result = await broadcastService.getBrands();

    if (!result.success) {
      return res.status(500).json({
        success: false,
        message: 'Failed to fetch brands',
        error: result.error,
      });
    }

    res.json({
      success: true,
      data: result.data,
    });
  } catch (error) {
    logger.error('GET /api/broadcasts/brands error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message,
    });
  }
});

/**
 * GET /api/broadcasts/search
 * Search broadcasts
 * Query params: q (query), brand, limit
 */
router.get('/search', async (req, res) => {
  try {
    const { q = '', brand = '', limit = 20 } = req.query;

    logger.info(`GET /api/broadcasts/search - q: ${q}, brand: ${brand}, limit: ${limit}`);

    if (!q) {
      return res.status(400).json({
        success: false,
        message: 'Search query (q) is required',
      });
    }

    const result = await broadcastService.searchBroadcasts(q, {
      brand,
      limit: parseInt(limit),
    });

    if (!result.success) {
      return res.status(500).json({
        success: false,
        message: 'Search failed',
        error: result.error,
      });
    }

    res.json({
      success: true,
      query: result.query,
      results: result.results,
    });
  } catch (error) {
    logger.error('GET /api/broadcasts/search error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message,
    });
  }
});

/**
 * GET /api/broadcasts/:id
 * Get single broadcast with all related data
 */
router.get('/:id', async (req, res) => {
  try {
    const { id } = req.params;

    logger.info(`GET /api/broadcasts/${id}`);

    // Validate ID
    if (!id || isNaN(parseInt(id))) {
      return res.status(400).json({
        success: false,
        message: 'Invalid broadcast ID',
      });
    }

    const result = await broadcastService.getBroadcastById(parseInt(id));

    if (!result.success) {
      if (result.error === 'Broadcast not found') {
        return res.status(404).json({
          success: false,
          message: 'Broadcast not found',
        });
      }

      return res.status(500).json({
        success: false,
        message: 'Failed to fetch broadcast',
        error: result.error,
      });
    }

    res.json(result.data);
  } catch (error) {
    logger.error(`GET /api/broadcasts/${req.params.id} error:`, error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message,
    });
  }
});

module.exports = router;
