/**
 * Scheduled Event Service
 * Business logic for crawled events from scheduled crawler
 * Note: Different from the main eventService which handles general platform events
 */

const Event = require('../models/Event');
const logger = require('../config/logger');

class ScheduledEventService {
  /**
   * Get all events with optional filters
   * @param {Object} filters - Filter options
   * @param {Object} options - Query options
   * @returns {Promise<Object>}
   */
  async getAllEvents(filters = {}, options = {}) {
    try {
      const events = await Event.findAll(filters, options);

      return {
        success: true,
        data: events,
        count: events.length,
      };
    } catch (error) {
      logger.error('ScheduledEventService.getAllEvents error:', error);
      throw error;
    }
  }

  /**
   * Get event by ID
   * @param {string} id - Event UUID
   * @returns {Promise<Object>}
   */
  async getEventById(id) {
    try {
      const event = await Event.findById(id);

      if (!event) {
        return {
          success: false,
          message: 'Event not found',
        };
      }

      return {
        success: true,
        data: event,
      };
    } catch (error) {
      logger.error(`ScheduledEventService.getEventById error (${id}):`, error);
      throw error;
    }
  }

  /**
   * Get events by brand
   * @param {string} brandId - Brand UUID
   * @param {Object} options - Query options
   * @returns {Promise<Object>}
   */
  async getEventsByBrand(brandId, options = {}) {
    try {
      const events = await Event.findByBrand(brandId, options);

      return {
        success: true,
        data: events,
        count: events.length,
      };
    } catch (error) {
      logger.error(`ScheduledEventService.getEventsByBrand error (${brandId}):`, error);
      throw error;
    }
  }

  /**
   * Get events by platform
   * @param {string} platformId - Platform UUID
   * @param {Object} options - Query options
   * @returns {Promise<Object>}
   */
  async getEventsByPlatform(platformId, options = {}) {
    try {
      const events = await Event.findByPlatform(platformId, options);

      return {
        success: true,
        data: events,
        count: events.length,
      };
    } catch (error) {
      logger.error(`ScheduledEventService.getEventsByPlatform error (${platformId}):`, error);
      throw error;
    }
  }

  /**
   * Get events by execution ID
   * @param {string} executionId - Execution UUID
   * @returns {Promise<Object>}
   */
  async getEventsByExecution(executionId) {
    try {
      const events = await Event.findByExecution(executionId);

      return {
        success: true,
        data: events,
        count: events.length,
      };
    } catch (error) {
      logger.error(`ScheduledEventService.getEventsByExecution error (${executionId}):`, error);
      throw error;
    }
  }
}

module.exports = new ScheduledEventService();
