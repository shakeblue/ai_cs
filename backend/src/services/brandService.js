/**
 * Brand Service
 * Business logic for brand management
 */

const Brand = require('../models/Brand');
const Platform = require('../models/Platform');
const logger = require('../config/logger');

class BrandService {
  /**
   * Get all brands with optional filters
   * @param {Object} filters - Filter options
   * @param {boolean} withPlatform - Include platform details
   * @returns {Promise<Object>}
   */
  async getAllBrands(filters = {}, withPlatform = true) {
    try {
      const brands = withPlatform
        ? await Brand.findAllWithPlatform(filters)
        : await Brand.findAll(filters);

      return {
        success: true,
        data: brands,
        count: brands.length,
      };
    } catch (error) {
      logger.error('BrandService.getAllBrands error:', error);
      throw error;
    }
  }

  /**
   * Get brand by ID
   * @param {string} id - Brand UUID
   * @param {boolean} withPlatform - Include platform details
   * @returns {Promise<Object>}
   */
  async getBrandById(id, withPlatform = true) {
    try {
      const brand = withPlatform
        ? await Brand.findByIdWithPlatform(id)
        : await Brand.findById(id);

      if (!brand) {
        return {
          success: false,
          message: 'Brand not found',
        };
      }

      return {
        success: true,
        data: brand,
      };
    } catch (error) {
      logger.error(`BrandService.getBrandById error (${id}):`, error);
      throw error;
    }
  }

  /**
   * Get brands by platform ID
   * @param {string} platformId - Platform UUID
   * @returns {Promise<Object>}
   */
  async getBrandsByPlatform(platformId) {
    try {
      // Verify platform exists
      const platform = await Platform.findById(platformId);
      if (!platform) {
        return {
          success: false,
          message: 'Platform not found',
        };
      }

      const brands = await Brand.findByPlatform(platformId);

      return {
        success: true,
        data: brands,
        count: brands.length,
      };
    } catch (error) {
      logger.error(`BrandService.getBrandsByPlatform error (${platformId}):`, error);
      throw error;
    }
  }

  /**
   * Create new brand
   * @param {Object} data - Brand data
   * @returns {Promise<Object>}
   */
  async createBrand(data) {
    try {
      // Verify platform exists
      const platform = await Platform.findById(data.platform_id);
      if (!platform) {
        return {
          success: false,
          message: 'Platform not found',
        };
      }

      // Check if brand with same name and platform already exists
      const brands = await Brand.findAll({
        name: data.name,
        platform_id: data.platform_id,
      });

      if (brands.length > 0) {
        return {
          success: false,
          message: `Brand "${data.name}" already exists for this platform`,
        };
      }

      const brand = await Brand.create(data);

      return {
        success: true,
        data: brand,
        message: 'Brand created successfully',
      };
    } catch (error) {
      logger.error('BrandService.createBrand error:', error);
      throw error;
    }
  }

  /**
   * Update brand
   * @param {string} id - Brand UUID
   * @param {Object} data - Updated data
   * @returns {Promise<Object>}
   */
  async updateBrand(id, data) {
    try {
      // Check if brand exists
      const existing = await Brand.findById(id);
      if (!existing) {
        return {
          success: false,
          message: 'Brand not found',
        };
      }

      // If platform_id is being changed, verify new platform exists
      if (data.platform_id && data.platform_id !== existing.platform_id) {
        const platform = await Platform.findById(data.platform_id);
        if (!platform) {
          return {
            success: false,
            message: 'Platform not found',
          };
        }
      }

      // If name is being changed, check if new name already exists for the platform
      if (data.name && data.name !== existing.name) {
        const platformId = data.platform_id || existing.platform_id;
        const brands = await Brand.findAll({
          name: data.name,
          platform_id: platformId,
        });

        if (brands.length > 0) {
          return {
            success: false,
            message: `Brand "${data.name}" already exists for this platform`,
          };
        }
      }

      const brand = await Brand.update(id, data);

      return {
        success: true,
        data: brand,
        message: 'Brand updated successfully',
      };
    } catch (error) {
      logger.error(`BrandService.updateBrand error (${id}):`, error);
      throw error;
    }
  }

  /**
   * Delete brand
   * @param {string} id - Brand UUID
   * @returns {Promise<Object>}
   */
  async deleteBrand(id) {
    try {
      // Check if brand exists
      const existing = await Brand.findById(id);
      if (!existing) {
        return {
          success: false,
          message: 'Brand not found',
        };
      }

      await Brand.delete(id);

      return {
        success: true,
        message: 'Brand deleted successfully',
      };
    } catch (error) {
      logger.error(`BrandService.deleteBrand error (${id}):`, error);
      throw error;
    }
  }

  /**
   * Get active brands only
   * @param {string} platformId - Optional platform filter
   * @returns {Promise<Object>}
   */
  async getActiveBrands(platformId = null) {
    try {
      const brands = await Brand.findActive(platformId);

      return {
        success: true,
        data: brands,
        count: brands.length,
      };
    } catch (error) {
      logger.error('BrandService.getActiveBrands error:', error);
      throw error;
    }
  }

  /**
   * Get effective schedule for brand
   * @param {string} id - Brand UUID
   * @returns {Promise<Object>}
   */
  async getEffectiveSchedule(id) {
    try {
      const schedule = await Brand.getEffectiveSchedule(id);

      return {
        success: true,
        data: {
          schedule,
        },
      };
    } catch (error) {
      logger.error(`BrandService.getEffectiveSchedule error (${id}):`, error);
      throw error;
    }
  }
}

module.exports = new BrandService();
