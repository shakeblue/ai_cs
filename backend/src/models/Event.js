/**
 * Event Model
 * Manages crawled live and replay events from platforms
 */

const { supabase, insert, select, update, upsert } = require('../config/supabase');
const logger = require('../config/logger');

class Event {
  /**
   * Create a new event
   * @param {Object} data - Event data
   * @returns {Promise<Object>}
   */
  static async create(data) {
    try {
      // Validate required fields
      if (!data.external_id || !data.brand_id || !data.platform_id) {
        throw new Error('external_id, brand_id, and platform_id are required');
      }

      // Validate status
      if (data.status && !['upcoming', 'ongoing', 'ended'].includes(data.status)) {
        throw new Error('status must be one of: upcoming, ongoing, ended');
      }

      // Validate event_type
      if (data.event_type && !['live', 'replay'].includes(data.event_type)) {
        throw new Error('event_type must be either "live" or "replay"');
      }

      const eventData = {
        external_id: data.external_id,
        brand_id: data.brand_id,
        platform_id: data.platform_id,
        execution_id: data.execution_id || null,
        title: data.title || null,
        url: data.url || null,
        start_date: data.start_date || null,
        end_date: data.end_date || null,
        status: data.status || null,
        event_type: data.event_type || null,
        raw_data: data.raw_data || null,
        extracted_data: data.extracted_data || null,
      };

      const result = await insert('events', eventData);

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Event created: ${eventData.external_id} (Brand: ${eventData.brand_id})`);
      return result.data[0];
    } catch (error) {
      logger.error('Error creating event:', error);
      throw error;
    }
  }

  /**
   * Upsert event (insert or update based on platform_id + external_id)
   * Implements "last write wins" strategy for duplicates
   * @param {Object} data - Event data
   * @returns {Promise<Object>}
   */
  static async upsert(data) {
    try {
      // Validate required fields
      if (!data.external_id || !data.brand_id || !data.platform_id) {
        throw new Error('external_id, brand_id, and platform_id are required');
      }

      const eventData = {
        external_id: data.external_id,
        brand_id: data.brand_id,
        platform_id: data.platform_id,
        execution_id: data.execution_id || null,
        title: data.title || null,
        url: data.url || null,
        start_date: data.start_date || null,
        end_date: data.end_date || null,
        status: data.status || null,
        event_type: data.event_type || null,
        raw_data: data.raw_data || null,
        extracted_data: data.extracted_data || null,
      };

      // Upsert based on unique constraint (platform_id, external_id)
      const { data: result, error } = await supabase
        .from('events')
        .upsert(eventData, {
          onConflict: 'platform_id,external_id',
        })
        .select();

      if (error) {
        throw error;
      }

      logger.info(`Event upserted: ${eventData.external_id}`);
      return result[0];
    } catch (error) {
      logger.error('Error upserting event:', error);
      throw error;
    }
  }

  /**
   * Bulk upsert events
   * @param {Array} events - Array of event data objects
   * @returns {Promise<Array>}
   */
  static async bulkUpsert(events) {
    try {
      if (!Array.isArray(events) || events.length === 0) {
        return [];
      }

      const { data, error } = await supabase
        .from('events')
        .upsert(events, {
          onConflict: 'platform_id,external_id',
        })
        .select();

      if (error) {
        throw error;
      }

      logger.info(`Bulk upserted ${events.length} events`);
      return data;
    } catch (error) {
      logger.error('Error bulk upserting events:', error);
      throw error;
    }
  }

  /**
   * Get all events
   * @param {Object} filters - Filter options
   * @param {Object} options - Query options (limit, orderBy)
   * @returns {Promise<Array>}
   */
  static async findAll(filters = {}, options = {}) {
    try {
      const result = await select('events', '*', filters, {
        orderBy: options.orderBy || 'start_date',
        ascending: options.ascending !== undefined ? options.ascending : false,
        limit: options.limit,
      });

      if (!result.success) {
        throw result.error;
      }

      return result.rows;
    } catch (error) {
      logger.error('Error fetching events:', error);
      throw error;
    }
  }

  /**
   * Get event by ID
   * @param {string} id - Event UUID
   * @returns {Promise<Object|null>}
   */
  static async findById(id) {
    try {
      const result = await select('events', '*', { id });

      if (!result.success) {
        throw result.error;
      }

      return result.rows.length > 0 ? result.rows[0] : null;
    } catch (error) {
      logger.error(`Error fetching event ${id}:`, error);
      throw error;
    }
  }

  /**
   * Get events by brand
   * @param {string} brandId - Brand UUID
   * @param {Object} options - Query options
   * @returns {Promise<Array>}
   */
  static async findByBrand(brandId, options = {}) {
    return this.findAll({ brand_id: brandId }, options);
  }

  /**
   * Get events by platform
   * @param {string} platformId - Platform UUID
   * @param {Object} options - Query options
   * @returns {Promise<Array>}
   */
  static async findByPlatform(platformId, options = {}) {
    return this.findAll({ platform_id: platformId }, options);
  }

  /**
   * Get events by execution ID
   * @param {string} executionId - Execution UUID
   * @returns {Promise<Array>}
   */
  static async findByExecution(executionId) {
    return this.findAll({ execution_id: executionId });
  }

  /**
   * Get events within date range
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   * @param {Object} filters - Additional filters
   * @returns {Promise<Array>}
   */
  static async findByDateRange(startDate, endDate, filters = {}) {
    try {
      let query = supabase
        .from('events')
        .select('*')
        .gte('start_date', startDate.toISOString())
        .lte('start_date', endDate.toISOString());

      // Apply additional filters
      Object.keys(filters).forEach(key => {
        query = query.eq(key, filters[key]);
      });

      query = query.order('start_date', { ascending: false });

      const { data, error } = await query;

      if (error) {
        throw error;
      }

      return data || [];
    } catch (error) {
      logger.error('Error fetching events by date range:', error);
      throw error;
    }
  }

  /**
   * Get upcoming events
   * @param {Object} filters - Additional filters
   * @returns {Promise<Array>}
   */
  static async findUpcoming(filters = {}) {
    try {
      const now = new Date();
      let query = supabase
        .from('events')
        .select('*')
        .gte('start_date', now.toISOString())
        .eq('status', 'upcoming');

      Object.keys(filters).forEach(key => {
        query = query.eq(key, filters[key]);
      });

      query = query.order('start_date', { ascending: true });

      const { data, error } = await query;

      if (error) {
        throw error;
      }

      return data || [];
    } catch (error) {
      logger.error('Error fetching upcoming events:', error);
      throw error;
    }
  }

  /**
   * Update event
   * @param {string} id - Event UUID
   * @param {Object} data - Updated data
   * @returns {Promise<Object>}
   */
  static async update(id, data) {
    try {
      // Remove id and timestamps from update data
      const { id: _, created_at, updated_at, ...updateData } = data;

      const result = await update('events', updateData, { id });

      if (!result.success) {
        throw result.error;
      }

      logger.info(`Event updated: ${id}`);
      return result.data[0];
    } catch (error) {
      logger.error(`Error updating event ${id}:`, error);
      throw error;
    }
  }

  /**
   * Count events by filters
   * @param {Object} filters - Filter options
   * @returns {Promise<number>}
   */
  static async count(filters = {}) {
    try {
      let query = supabase
        .from('events')
        .select('*', { count: 'exact', head: true });

      Object.keys(filters).forEach(key => {
        query = query.eq(key, filters[key]);
      });

      const { count, error } = await query;

      if (error) {
        throw error;
      }

      return count || 0;
    } catch (error) {
      logger.error('Error counting events:', error);
      throw error;
    }
  }
}

module.exports = Event;
