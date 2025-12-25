/**
 * CrawlerExecution Model
 * Manages crawler execution logs and status
 */

const { supabase, insert, select, update } = require('../config/supabase');
const logger = require('../config/logger');

class CrawlerExecution {
  /**
   * Create a new crawler execution record
   * @param {Object} data - Execution data
   * @param {string} data.brand_id - Brand UUID
   * @param {string} data.platform_id - Platform UUID
   * @param {string} data.trigger_type - Trigger type (scheduled|manual)
   * @returns {Promise<Object>}
   */
  static async create(data) {
    try {
      // Validate required fields
      if (!data.brand_id || !data.platform_id || !data.trigger_type) {
        throw new Error('brand_id, platform_id, and trigger_type are required');
      }

      // Validate trigger_type
      if (!['scheduled', 'manual'].includes(data.trigger_type)) {
        throw new Error('trigger_type must be either "scheduled" or "manual"');
      }

      const executionData = {
        brand_id: data.brand_id,
        platform_id: data.platform_id,
        trigger_type: data.trigger_type,
        status: 'pending',
        started_at: new Date().toISOString(),
      };

      const result = await insert('crawler_executions', executionData);

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Crawler execution created: ${result.data[0].id} (${data.trigger_type})`);
      return result.data[0];
    } catch (error) {
      logger.error('Error creating crawler execution:', error);
      throw error;
    }
  }

  /**
   * Update execution status
   * @param {string} id - Execution UUID
   * @param {string} status - New status (pending|running|success|failed)
   * @param {Object} additionalData - Additional data to update
   * @returns {Promise<Object>}
   */
  static async updateStatus(id, status, additionalData = {}) {
    try {
      // Validate status
      if (!['pending', 'running', 'success', 'failed'].includes(status)) {
        throw new Error('status must be one of: pending, running, success, failed');
      }

      const updateData = {
        status,
        ...additionalData,
      };

      // Add completed_at timestamp if status is success or failed
      if (status === 'success' || status === 'failed') {
        updateData.completed_at = new Date().toISOString();
      }

      const result = await update('crawler_executions', updateData, { id });

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Execution ${id} status updated to: ${status}`);
      return result.data[0];
    } catch (error) {
      logger.error(`Error updating execution status ${id}:`, error);
      throw error;
    }
  }

  /**
   * Mark execution as running
   * @param {string} id - Execution UUID
   * @returns {Promise<Object>}
   */
  static async markAsRunning(id) {
    return this.updateStatus(id, 'running');
  }

  /**
   * Mark execution as success
   * @param {string} id - Execution UUID
   * @param {number} itemsFound - Number of items found
   * @returns {Promise<Object>}
   */
  static async markAsSuccess(id, itemsFound) {
    return this.updateStatus(id, 'success', {
      items_found: itemsFound,
    });
  }

  /**
   * Mark execution as failed
   * @param {string} id - Execution UUID
   * @param {string} errorMessage - Error message
   * @returns {Promise<Object>}
   */
  static async markAsFailed(id, errorMessage) {
    return this.updateStatus(id, 'failed', {
      error_message: errorMessage,
    });
  }

  /**
   * Get all executions
   * @param {Object} filters - Filter options
   * @param {Object} options - Query options
   * @returns {Promise<Array>}
   */
  static async findAll(filters = {}, options = {}) {
    try {
      const result = await select('crawler_executions', '*', filters, {
        orderBy: options.orderBy || 'started_at',
        ascending: options.ascending !== undefined ? options.ascending : false,
        limit: options.limit,
      });

      if (!result.success) {
        throw result.error;
      }

      return result.rows;
    } catch (error) {
      logger.error('Error fetching executions:', error);
      throw error;
    }
  }

  /**
   * Get execution by ID
   * @param {string} id - Execution UUID
   * @returns {Promise<Object|null>}
   */
  static async findById(id) {
    try {
      const result = await select('crawler_executions', '*', { id });

      if (!result.success) {
        throw result.error;
      }

      return result.rows.length > 0 ? result.rows[0] : null;
    } catch (error) {
      logger.error(`Error fetching execution ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get executions by brand
   * @param {string} brandId - Brand UUID
   * @param {Object} options - Query options
   * @returns {Promise<Array>}
   */
  static async findByBrand(brandId, options = {}) {
    return this.findAll({ brand_id: brandId }, options);
  }

  /**
   * Get executions by platform
   * @param {string} platformId - Platform UUID
   * @param {Object} options - Query options
   * @returns {Promise<Array>}
   */
  static async findByPlatform(platformId, options = {}) {
    return this.findAll({ platform_id: platformId }, options);
  }

  /**
   * Get executions by status
   * @param {string} status - Execution status
   * @param {Object} options - Query options
   * @returns {Promise<Array>}
   */
  static async findByStatus(status, options = {}) {
    return this.findAll({ status }, options);
  }

  /**
   * Get recent executions
   * @param {number} limit - Number of executions to return
   * @returns {Promise<Array>}
   */
  static async findRecent(limit = 50) {
    return this.findAll({}, { limit, orderBy: 'started_at', ascending: false });
  }

  /**
   * Get executions with brand and platform details
   * @param {Object} filters - Filter options
   * @param {Object} options - Query options
   * @returns {Promise<Array>}
   */
  static async findAllWithDetails(filters = {}, options = {}) {
    try {
      let query = supabase
        .from('crawler_executions')
        .select('*, brands(*), platforms(*)');

      // Apply filters
      Object.keys(filters).forEach(key => {
        query = query.eq(key, filters[key]);
      });

      // Apply ordering
      query = query.order(options.orderBy || 'started_at', {
        ascending: options.ascending !== undefined ? options.ascending : false,
      });

      // Apply limit
      if (options.limit) {
        query = query.limit(options.limit);
      }

      const { data, error } = await query;

      if (error) {
        throw error;
      }

      return data || [];
    } catch (error) {
      logger.error('Error fetching executions with details:', error);
      throw error;
    }
  }

  /**
   * Get execution statistics
   * @param {Object} filters - Filter options (brand_id, platform_id, etc.)
   * @returns {Promise<Object>}
   */
  static async getStatistics(filters = {}) {
    try {
      const executions = await this.findAll(filters);

      const stats = {
        total: executions.length,
        pending: 0,
        running: 0,
        success: 0,
        failed: 0,
        totalItemsFound: 0,
        avgItemsFound: 0,
      };

      executions.forEach(exec => {
        stats[exec.status]++;
        if (exec.items_found) {
          stats.totalItemsFound += exec.items_found;
        }
      });

      const successCount = stats.success || 1; // Avoid division by zero
      stats.avgItemsFound = Math.round(stats.totalItemsFound / successCount);

      return stats;
    } catch (error) {
      logger.error('Error getting execution statistics:', error);
      throw error;
    }
  }

  /**
   * Check if there's a running execution for a brand/platform
   * @param {string} brandId - Brand UUID
   * @param {string} platformId - Platform UUID
   * @returns {Promise<boolean>}
   */
  static async hasRunningExecution(brandId, platformId) {
    try {
      const { data, error } = await supabase
        .from('crawler_executions')
        .select('id')
        .eq('brand_id', brandId)
        .eq('platform_id', platformId)
        .in('status', ['pending', 'running'])
        .limit(1);

      if (error) {
        throw error;
      }

      return data && data.length > 0;
    } catch (error) {
      logger.error('Error checking running execution:', error);
      throw error;
    }
  }
}

module.exports = CrawlerExecution;
