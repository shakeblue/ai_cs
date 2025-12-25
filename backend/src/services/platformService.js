/**
 * Platform Service
 * Business logic for platform management
 */

const Platform = require('../models/Platform');
const logger = require('../config/logger');

class PlatformService {
  /**
   * Get all platforms with optional filters
   * @param {Object} filters - Filter options
   * @returns {Promise<Object>}
   */
  async getAllPlatforms(filters = {}) {
    try {
      const platforms = await Platform.findAll(filters);

      return {
        success: true,
        data: platforms,
        count: platforms.length,
      };
    } catch (error) {
      logger.error('PlatformService.getAllPlatforms error:', error);
      throw error;
    }
  }

  /**
   * Get platform by ID
   * @param {string} id - Platform UUID
   * @returns {Promise<Object>}
   */
  async getPlatformById(id) {
    try {
      const platform = await Platform.findById(id);

      if (!platform) {
        return {
          success: false,
          message: 'Platform not found',
        };
      }

      return {
        success: true,
        data: platform,
      };
    } catch (error) {
      logger.error(`PlatformService.getPlatformById error (${id}):`, error);
      throw error;
    }
  }

  /**
   * Create new platform
   * @param {Object} data - Platform data
   * @returns {Promise<Object>}
   */
  async createPlatform(data) {
    try {
      // Check if platform with same name already exists
      const existing = await Platform.findByName(data.name);
      if (existing) {
        return {
          success: false,
          message: `Platform with name "${data.name}" already exists`,
        };
      }

      const platform = await Platform.create(data);

      return {
        success: true,
        data: platform,
        message: 'Platform created successfully',
      };
    } catch (error) {
      logger.error('PlatformService.createPlatform error:', error);
      throw error;
    }
  }

  /**
   * Update platform
   * @param {string} id - Platform UUID
   * @param {Object} data - Updated data
   * @returns {Promise<Object>}
   */
  async updatePlatform(id, data) {
    try {
      // Check if platform exists
      const existing = await Platform.findById(id);
      if (!existing) {
        return {
          success: false,
          message: 'Platform not found',
        };
      }

      // If name is being changed, check if new name already exists
      if (data.name && data.name !== existing.name) {
        const nameExists = await Platform.findByName(data.name);
        if (nameExists) {
          return {
            success: false,
            message: `Platform with name "${data.name}" already exists`,
          };
        }
      }

      const platform = await Platform.update(id, data);

      return {
        success: true,
        data: platform,
        message: 'Platform updated successfully',
      };
    } catch (error) {
      logger.error(`PlatformService.updatePlatform error (${id}):`, error);
      throw error;
    }
  }

  /**
   * Delete platform
   * @param {string} id - Platform UUID
   * @returns {Promise<Object>}
   */
  async deletePlatform(id) {
    try {
      // Check if platform exists
      const existing = await Platform.findById(id);
      if (!existing) {
        return {
          success: false,
          message: 'Platform not found',
        };
      }

      await Platform.delete(id);

      return {
        success: true,
        message: 'Platform deleted successfully',
      };
    } catch (error) {
      logger.error(`PlatformService.deletePlatform error (${id}):`, error);
      throw error;
    }
  }

  /**
   * Get active platforms only
   * @returns {Promise<Object>}
   */
  async getActivePlatforms() {
    try {
      const platforms = await Platform.findActive();

      return {
        success: true,
        data: platforms,
        count: platforms.length,
      };
    } catch (error) {
      logger.error('PlatformService.getActivePlatforms error:', error);
      throw error;
    }
  }
}

module.exports = new PlatformService();
