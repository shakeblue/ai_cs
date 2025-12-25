/**
 * Config Service
 * Business logic for crawler configuration management
 */

const CrawlerConfig = require('../models/CrawlerConfig');
const logger = require('../config/logger');

class ConfigService {
  /**
   * Get all configuration settings
   * @returns {Promise<Object>}
   */
  async getAllConfigs() {
    try {
      const configs = await CrawlerConfig.getAll();

      // Transform to key-value pairs for easier consumption
      const configMap = {};
      configs.forEach(config => {
        configMap[config.key] = {
          value: config.value,
          description: config.description,
          updated_at: config.updated_at,
        };
      });

      return {
        success: true,
        data: configMap,
        count: configs.length,
      };
    } catch (error) {
      logger.error('ConfigService.getAllConfigs error:', error);
      throw error;
    }
  }

  /**
   * Get configuration value by key
   * @param {string} key - Configuration key
   * @returns {Promise<Object>}
   */
  async getConfig(key) {
    try {
      const value = await CrawlerConfig.get(key);

      if (value === null) {
        return {
          success: false,
          message: `Configuration key "${key}" not found`,
        };
      }

      return {
        success: true,
        data: {
          key,
          value,
        },
      };
    } catch (error) {
      logger.error(`ConfigService.getConfig error (${key}):`, error);
      throw error;
    }
  }

  /**
   * Update configuration value
   * @param {string} key - Configuration key
   * @param {string} value - New value
   * @param {string} description - Description (optional)
   * @returns {Promise<Object>}
   */
  async updateConfig(key, value, description = null) {
    try {
      const config = await CrawlerConfig.set(key, value, description);

      return {
        success: true,
        data: config,
        message: 'Configuration updated successfully',
      };
    } catch (error) {
      logger.error(`ConfigService.updateConfig error (${key}):`, error);
      throw error;
    }
  }

  /**
   * Get time range configuration
   * @returns {Promise<Object>}
   */
  async getTimeRange() {
    try {
      const timeRange = await CrawlerConfig.getTimeRange();

      return {
        success: true,
        data: timeRange,
      };
    } catch (error) {
      logger.error('ConfigService.getTimeRange error:', error);
      throw error;
    }
  }

  /**
   * Update time range configuration
   * @param {number} pastDays - Past days range
   * @param {number} futureDays - Future days range
   * @returns {Promise<Object>}
   */
  async updateTimeRange(pastDays, futureDays) {
    try {
      const timeRange = await CrawlerConfig.setTimeRange(pastDays, futureDays);

      return {
        success: true,
        data: timeRange,
        message: 'Time range updated successfully',
      };
    } catch (error) {
      logger.error('ConfigService.updateTimeRange error:', error);
      throw error;
    }
  }

  /**
   * Get default schedule
   * @returns {Promise<Object>}
   */
  async getDefaultSchedule() {
    try {
      const schedule = await CrawlerConfig.getDefaultSchedule();

      return {
        success: true,
        data: {
          schedule,
        },
      };
    } catch (error) {
      logger.error('ConfigService.getDefaultSchedule error:', error);
      throw error;
    }
  }

  /**
   * Get crawler timeout
   * @returns {Promise<Object>}
   */
  async getCrawlerTimeout() {
    try {
      const timeout = await CrawlerConfig.getCrawlerTimeout();

      return {
        success: true,
        data: {
          timeout,
        },
      };
    } catch (error) {
      logger.error('ConfigService.getCrawlerTimeout error:', error);
      throw error;
    }
  }

  /**
   * Get max concurrent jobs
   * @returns {Promise<Object>}
   */
  async getMaxConcurrentJobs() {
    try {
      const maxJobs = await CrawlerConfig.getMaxConcurrentJobs();

      return {
        success: true,
        data: {
          maxJobs,
        },
      };
    } catch (error) {
      logger.error('ConfigService.getMaxConcurrentJobs error:', error);
      throw error;
    }
  }
}

module.exports = new ConfigService();
