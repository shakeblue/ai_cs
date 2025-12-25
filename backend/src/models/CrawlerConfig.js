/**
 * CrawlerConfig Model
 * Manages system-wide crawler configuration settings
 */

const { supabase, insert, select, update } = require('../config/supabase');
const logger = require('../config/logger');

class CrawlerConfig {
  /**
   * Get configuration value by key
   * @param {string} key - Configuration key
   * @returns {Promise<string|null>}
   */
  static async get(key) {
    try {
      const result = await select('crawler_config', '*', { key });

      if (!result.success) {
        throw result.error;
      }

      if (result.rows.length === 0) {
        return null;
      }

      return result.rows[0].value;
    } catch (error) {
      logger.error(`Error getting config ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get all configuration settings
   * @returns {Promise<Array>}
   */
  static async getAll() {
    try {
      const result = await select('crawler_config', '*');

      if (!result.success) {
        throw result.error;
      }

      return result.rows;
    } catch (error) {
      logger.error('Error getting all configs:', error);
      throw error;
    }
  }

  /**
   * Get all configurations as key-value object
   * @returns {Promise<Object>}
   */
  static async getAllAsObject() {
    try {
      const configs = await this.getAll();
      const configObj = {};

      configs.forEach(config => {
        configObj[config.key] = config.value;
      });

      return configObj;
    } catch (error) {
      logger.error('Error getting configs as object:', error);
      throw error;
    }
  }

  /**
   * Set configuration value
   * @param {string} key - Configuration key
   * @param {string} value - Configuration value
   * @param {string} description - Configuration description (optional)
   * @returns {Promise<Object>}
   */
  static async set(key, value, description = null) {
    try {
      if (!key || value === undefined) {
        throw new Error('key and value are required');
      }

      // Check if config exists
      const existing = await this.get(key);

      if (existing !== null) {
        // Update existing
        const updateData = { value: String(value) };
        if (description) updateData.description = description;

        const result = await update('crawler_config', updateData, { key });

        if (!result.success) {
          throw result.error;
        }

        logger.info(`Config updated: ${key} = ${value}`);
        return result.data[0];
      } else {
        // Insert new
        const configData = {
          key,
          value: String(value),
          description: description || null,
        };

        const result = await insert('crawler_config', configData);

        if (!result.success) {
          throw result.error;
        }

        logger.info(`Config created: ${key} = ${value}`);
        return result.data[0];
      }
    } catch (error) {
      logger.error(`Error setting config ${key}:`, error);
      throw error;
    }
  }

  /**
   * Get past days range for event filtering
   * @returns {Promise<number>}
   */
  static async getPastDaysRange() {
    try {
      const value = await this.get('past_days_range');
      return value ? parseInt(value) : 7; // Default: 7 days
    } catch (error) {
      logger.error('Error getting past_days_range:', error);
      return 7; // Fallback
    }
  }

  /**
   * Get future days range for event filtering
   * @returns {Promise<number>}
   */
  static async getFutureDaysRange() {
    try {
      const value = await this.get('future_days_range');
      return value ? parseInt(value) : 14; // Default: 14 days
    } catch (error) {
      logger.error('Error getting future_days_range:', error);
      return 14; // Fallback
    }
  }

  /**
   * Get default schedule cron
   * @returns {Promise<string>}
   */
  static async getDefaultSchedule() {
    try {
      const value = await this.get('default_schedule_cron');
      return value || '0 */6 * * *'; // Default: every 6 hours
    } catch (error) {
      logger.error('Error getting default_schedule_cron:', error);
      return '0 */6 * * *'; // Fallback
    }
  }

  /**
   * Get crawler timeout in seconds
   * @returns {Promise<number>}
   */
  static async getCrawlerTimeout() {
    try {
      const value = await this.get('crawler_timeout_seconds');
      return value ? parseInt(value) : 600; // Default: 10 minutes
    } catch (error) {
      logger.error('Error getting crawler_timeout_seconds:', error);
      return 600; // Fallback
    }
  }

  /**
   * Get max concurrent jobs
   * @returns {Promise<number>}
   */
  static async getMaxConcurrentJobs() {
    try {
      const value = await this.get('max_concurrent_jobs');
      return value ? parseInt(value) : 5; // Default: 5
    } catch (error) {
      logger.error('Error getting max_concurrent_jobs:', error);
      return 5; // Fallback
    }
  }

  /**
   * Get time range configuration
   * @returns {Promise<Object>} {pastDays, futureDays}
   */
  static async getTimeRange() {
    try {
      const [pastDays, futureDays] = await Promise.all([
        this.getPastDaysRange(),
        this.getFutureDaysRange(),
      ]);

      return {
        pastDays,
        futureDays,
      };
    } catch (error) {
      logger.error('Error getting time range:', error);
      throw error;
    }
  }

  /**
   * Update time range configuration
   * @param {number} pastDays - Past days range
   * @param {number} futureDays - Future days range
   * @returns {Promise<Object>}
   */
  static async setTimeRange(pastDays, futureDays) {
    try {
      if (pastDays < 0 || futureDays < 0) {
        throw new Error('Time ranges must be positive numbers');
      }

      await Promise.all([
        this.set('past_days_range', String(pastDays)),
        this.set('future_days_range', String(futureDays)),
      ]);

      logger.info(`Time range updated: past=${pastDays}, future=${futureDays}`);

      return {
        pastDays,
        futureDays,
      };
    } catch (error) {
      logger.error('Error setting time range:', error);
      throw error;
    }
  }
}

module.exports = CrawlerConfig;
