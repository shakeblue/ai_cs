/**
 * Execution Service
 * Business logic for crawler execution management
 */

const CrawlerExecution = require('../models/CrawlerExecution');
const logger = require('../config/logger');

class ExecutionService {
  /**
   * Get all executions with optional filters
   * @param {Object} filters - Filter options
   * @param {Object} options - Query options
   * @param {boolean} withDetails - Include brand and platform details
   * @returns {Promise<Object>}
   */
  async getAllExecutions(filters = {}, options = {}, withDetails = true) {
    try {
      const executions = withDetails
        ? await CrawlerExecution.findAllWithDetails(filters, options)
        : await CrawlerExecution.findAll(filters, options);

      return {
        success: true,
        data: executions,
        count: executions.length,
      };
    } catch (error) {
      logger.error('ExecutionService.getAllExecutions error:', error);
      throw error;
    }
  }

  /**
   * Get execution by ID
   * @param {string} id - Execution UUID
   * @returns {Promise<Object>}
   */
  async getExecutionById(id) {
    try {
      const execution = await CrawlerExecution.findById(id);

      if (!execution) {
        return {
          success: false,
          message: 'Execution not found',
        };
      }

      return {
        success: true,
        data: execution,
      };
    } catch (error) {
      logger.error(`ExecutionService.getExecutionById error (${id}):`, error);
      throw error;
    }
  }

  /**
   * Get executions by brand
   * @param {string} brandId - Brand UUID
   * @param {Object} options - Query options
   * @returns {Promise<Object>}
   */
  async getExecutionsByBrand(brandId, options = {}) {
    try {
      const executions = await CrawlerExecution.findByBrand(brandId, options);

      return {
        success: true,
        data: executions,
        count: executions.length,
      };
    } catch (error) {
      logger.error(`ExecutionService.getExecutionsByBrand error (${brandId}):`, error);
      throw error;
    }
  }

  /**
   * Get executions by platform
   * @param {string} platformId - Platform UUID
   * @param {Object} options - Query options
   * @returns {Promise<Object>}
   */
  async getExecutionsByPlatform(platformId, options = {}) {
    try {
      const executions = await CrawlerExecution.findByPlatform(platformId, options);

      return {
        success: true,
        data: executions,
        count: executions.length,
      };
    } catch (error) {
      logger.error(`ExecutionService.getExecutionsByPlatform error (${platformId}):`, error);
      throw error;
    }
  }

  /**
   * Get executions by status
   * @param {string} status - Execution status
   * @param {Object} options - Query options
   * @returns {Promise<Object>}
   */
  async getExecutionsByStatus(status, options = {}) {
    try {
      const executions = await CrawlerExecution.findByStatus(status, options);

      return {
        success: true,
        data: executions,
        count: executions.length,
      };
    } catch (error) {
      logger.error(`ExecutionService.getExecutionsByStatus error (${status}):`, error);
      throw error;
    }
  }

  /**
   * Get recent executions
   * @param {number} limit - Number of executions to return
   * @returns {Promise<Object>}
   */
  async getRecentExecutions(limit = 50) {
    try {
      const executions = await CrawlerExecution.findRecent(limit);

      return {
        success: true,
        data: executions,
        count: executions.length,
      };
    } catch (error) {
      logger.error('ExecutionService.getRecentExecutions error:', error);
      throw error;
    }
  }

  /**
   * Get execution statistics
   * @param {Object} filters - Filter options
   * @returns {Promise<Object>}
   */
  async getStatistics(filters = {}) {
    try {
      const stats = await CrawlerExecution.getStatistics(filters);

      return {
        success: true,
        data: stats,
      };
    } catch (error) {
      logger.error('ExecutionService.getStatistics error:', error);
      throw error;
    }
  }

  /**
   * Check if there's a running execution
   * @param {string} brandId - Brand UUID
   * @param {string} platformId - Platform UUID
   * @returns {Promise<Object>}
   */
  async checkRunningExecution(brandId, platformId) {
    try {
      const isRunning = await CrawlerExecution.hasRunningExecution(brandId, platformId);

      return {
        success: true,
        data: {
          isRunning,
        },
      };
    } catch (error) {
      logger.error('ExecutionService.checkRunningExecution error:', error);
      throw error;
    }
  }
}

module.exports = new ExecutionService();
