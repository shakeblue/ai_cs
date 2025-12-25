/**
 * Platform Model
 * Manages platform configurations for crawler
 */

const { supabase, insert, select, update, remove } = require('../config/supabase');
const logger = require('../config/logger');

class Platform {
  /**
   * Create a new platform
   * @param {Object} data - Platform data
   * @param {string} data.name - Platform name (unique)
   * @param {string} data.url_pattern - URL pattern with {query} placeholder
   * @param {string} data.status - Platform status (active|inactive)
   * @param {string} data.schedule_cron - Cron schedule (optional)
   * @returns {Promise<Object>}
   */
  static async create(data) {
    try {
      // Validate required fields
      if (!data.name || !data.url_pattern) {
        throw new Error('name and url_pattern are required');
      }

      // Validate status
      if (data.status && !['active', 'inactive'].includes(data.status)) {
        throw new Error('status must be either "active" or "inactive"');
      }

      // Validate URL pattern contains {query} placeholder
      if (!data.url_pattern.includes('{query}')) {
        throw new Error('url_pattern must contain {query} placeholder');
      }

      const platformData = {
        name: data.name.trim(),
        url_pattern: data.url_pattern.trim(),
        status: data.status || 'active',
        schedule_cron: data.schedule_cron || null,
      };

      const result = await insert('platforms', platformData);

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Platform created: ${platformData.name}`);
      return result.data[0];
    } catch (error) {
      logger.error('Error creating platform:', error);
      throw error;
    }
  }

  /**
   * Get all platforms
   * @param {Object} filters - Filter options
   * @param {string} filters.status - Filter by status (optional)
   * @returns {Promise<Array>}
   */
  static async findAll(filters = {}) {
    try {
      const result = await select('platforms', '*', filters, {
        orderBy: 'created_at',
        ascending: false,
      });

      if (!result.success) {
        throw result.error;
      }

      return result.rows;
    } catch (error) {
      logger.error('Error fetching platforms:', error);
      throw error;
    }
  }

  /**
   * Get platform by ID
   * @param {string} id - Platform UUID
   * @returns {Promise<Object|null>}
   */
  static async findById(id) {
    try {
      const result = await select('platforms', '*', { id });

      if (!result.success) {
        throw result.error;
      }

      return result.rows.length > 0 ? result.rows[0] : null;
    } catch (error) {
      logger.error(`Error fetching platform ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get platform by name
   * @param {string} name - Platform name
   * @returns {Promise<Object|null>}
   */
  static async findByName(name) {
    try {
      const result = await select('platforms', '*', { name });

      if (!result.success) {
        throw result.error;
      }

      return result.rows.length > 0 ? result.rows[0] : null;
    } catch (error) {
      logger.error(`Error fetching platform by name ${name}:`, error);
      throw error;
    }
  }

  /**
   * Update platform
   * @param {string} id - Platform UUID
   * @param {Object} data - Updated data
   * @returns {Promise<Object>}
   */
  static async update(id, data) {
    try {
      // Validate status if provided
      if (data.status && !['active', 'inactive'].includes(data.status)) {
        throw new Error('status must be either "active" or "inactive"');
      }

      // Validate URL pattern if provided
      if (data.url_pattern && !data.url_pattern.includes('{query}')) {
        throw new Error('url_pattern must contain {query} placeholder');
      }

      // Remove undefined values
      const updateData = {};
      if (data.name !== undefined) updateData.name = data.name.trim();
      if (data.url_pattern !== undefined) updateData.url_pattern = data.url_pattern.trim();
      if (data.status !== undefined) updateData.status = data.status;
      if (data.schedule_cron !== undefined) updateData.schedule_cron = data.schedule_cron;

      const result = await update('platforms', updateData, { id });

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Platform updated: ${id}`);
      return result.data[0];
    } catch (error) {
      logger.error(`Error updating platform ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete platform
   * @param {string} id - Platform UUID
   * @returns {Promise<Object>}
   */
  static async delete(id) {
    try {
      const result = await remove('platforms', { id });

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Platform deleted: ${id}`);
      return result.data[0];
    } catch (error) {
      logger.error(`Error deleting platform ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get active platforms
   * @returns {Promise<Array>}
   */
  static async findActive() {
    return this.findAll({ status: 'active' });
  }
}

module.exports = Platform;
