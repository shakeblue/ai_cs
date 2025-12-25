/**
 * Brand Model
 * Manages brand configurations for monitoring specific brands
 */

const { supabase, insert, select, update, remove } = require('../config/supabase');
const logger = require('../config/logger');

class Brand {
  /**
   * Create a new brand
   * @param {Object} data - Brand data
   * @param {string} data.name - Brand name
   * @param {string} data.search_text - Search query text
   * @param {string} data.platform_id - Platform UUID
   * @param {string} data.status - Brand status (active|inactive)
   * @param {string} data.schedule_cron - Cron schedule (optional, overrides platform)
   * @returns {Promise<Object>}
   */
  static async create(data) {
    try {
      // Validate required fields
      if (!data.name || !data.search_text || !data.platform_id) {
        throw new Error('name, search_text, and platform_id are required');
      }

      // Validate status
      if (data.status && !['active', 'inactive'].includes(data.status)) {
        throw new Error('status must be either "active" or "inactive"');
      }

      const brandData = {
        name: data.name.trim(),
        search_text: data.search_text.trim(),
        platform_id: data.platform_id,
        status: data.status || 'active',
        schedule_cron: data.schedule_cron || null,
      };

      const result = await insert('brands', brandData);

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Brand created: ${brandData.name} (Platform: ${brandData.platform_id})`);
      return result.data[0];
    } catch (error) {
      logger.error('Error creating brand:', error);
      throw error;
    }
  }

  /**
   * Get all brands
   * @param {Object} filters - Filter options
   * @param {string} filters.platform_id - Filter by platform (optional)
   * @param {string} filters.status - Filter by status (optional)
   * @returns {Promise<Array>}
   */
  static async findAll(filters = {}) {
    try {
      const result = await select('brands', '*', filters, {
        orderBy: 'created_at',
        ascending: false,
      });

      if (!result.success) {
        throw result.error;
      }

      return result.rows;
    } catch (error) {
      logger.error('Error fetching brands:', error);
      throw error;
    }
  }

  /**
   * Get brand by ID
   * @param {string} id - Brand UUID
   * @returns {Promise<Object|null>}
   */
  static async findById(id) {
    try {
      const result = await select('brands', '*', { id });

      if (!result.success) {
        throw result.error;
      }

      return result.rows.length > 0 ? result.rows[0] : null;
    } catch (error) {
      logger.error(`Error fetching brand ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get brands by platform ID
   * @param {string} platformId - Platform UUID
   * @returns {Promise<Array>}
   */
  static async findByPlatform(platformId) {
    return this.findAll({ platform_id: platformId });
  }

  /**
   * Get brand with platform details
   * @param {string} id - Brand UUID
   * @returns {Promise<Object|null>}
   */
  static async findByIdWithPlatform(id) {
    try {
      const { data, error } = await supabase
        .from('brands')
        .select('*, platforms(*)')
        .eq('id', id)
        .single();

      if (error) {
        throw error;
      }

      return data;
    } catch (error) {
      logger.error(`Error fetching brand with platform ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get all brands with platform details
   * @param {Object} filters - Filter options
   * @returns {Promise<Array>}
   */
  static async findAllWithPlatform(filters = {}) {
    try {
      let query = supabase
        .from('brands')
        .select('*, platforms(*)');

      // Apply filters
      Object.keys(filters).forEach(key => {
        query = query.eq(key, filters[key]);
      });

      query = query.order('created_at', { ascending: false });

      const { data, error } = await query;

      if (error) {
        throw error;
      }

      return data || [];
    } catch (error) {
      logger.error('Error fetching brands with platforms:', error);
      throw error;
    }
  }

  /**
   * Update brand
   * @param {string} id - Brand UUID
   * @param {Object} data - Updated data
   * @returns {Promise<Object>}
   */
  static async update(id, data) {
    try {
      // Validate status if provided
      if (data.status && !['active', 'inactive'].includes(data.status)) {
        throw new Error('status must be either "active" or "inactive"');
      }

      // Remove undefined values
      const updateData = {};
      if (data.name !== undefined) updateData.name = data.name.trim();
      if (data.search_text !== undefined) updateData.search_text = data.search_text.trim();
      if (data.platform_id !== undefined) updateData.platform_id = data.platform_id;
      if (data.status !== undefined) updateData.status = data.status;
      if (data.schedule_cron !== undefined) updateData.schedule_cron = data.schedule_cron;

      const result = await update('brands', updateData, { id });

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Brand updated: ${id}`);
      return result.data[0];
    } catch (error) {
      logger.error(`Error updating brand ${id}:`, error);
      throw error;
    }
  }

  /**
   * Delete brand
   * @param {string} id - Brand UUID
   * @returns {Promise<Object>}
   */
  static async delete(id) {
    try {
      const result = await remove('brands', { id });

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Brand deleted: ${id}`);
      return result.data[0];
    } catch (error) {
      logger.error(`Error deleting brand ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get active brands
   * @param {string} platformId - Platform UUID (optional)
   * @returns {Promise<Array>}
   */
  static async findActive(platformId = null) {
    const filters = { status: 'active' };
    if (platformId) {
      filters.platform_id = platformId;
    }
    return this.findAll(filters);
  }

  /**
   * Get effective schedule for a brand
   * Inherits from platform if brand schedule is not set
   * @param {string} id - Brand UUID
   * @returns {Promise<string|null>}
   */
  static async getEffectiveSchedule(id) {
    try {
      const brand = await this.findByIdWithPlatform(id);

      if (!brand) {
        throw new Error(`Brand not found: ${id}`);
      }

      // Return brand schedule if set, otherwise platform schedule
      return brand.schedule_cron || brand.platforms?.schedule_cron || null;
    } catch (error) {
      logger.error(`Error getting effective schedule for brand ${id}:`, error);
      throw error;
    }
  }
}

module.exports = Brand;
