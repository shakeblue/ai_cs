/**
 * Broadcast Service
 * Handles all broadcast-related database operations
 */

const { supabase } = require('../config/supabase');
const logger = require('../config/logger');

/**
 * Get broadcasts with pagination, filters, and search
 * @param {Object} options - Query options
 * @returns {Promise<Object>} Broadcasts with pagination info
 */
async function getBroadcasts(options = {}) {
  try {
    const {
      page = 1,
      limit = 20,
      search = '',
      brand = '',
      status = '',
      broadcast_type = '',
      start_date = '',
      end_date = '',
      sort = 'date_desc',
    } = options;

    // Calculate offset
    const offset = (page - 1) * limit;

    // Build query
    let query = supabase
      .from('broadcasts')
      .select('*, broadcast_products(id), broadcast_coupons(id)', { count: 'exact' });

    // Apply search filter (search in title, brand_name, description)
    if (search) {
      query = query.or(`title.ilike.%${search}%,brand_name.ilike.%${search}%,description.ilike.%${search}%`);
    }

    // Apply brand filter
    if (brand) {
      query = query.ilike('brand_name', brand);
    }

    // Apply status filter
    if (status) {
      query = query.eq('status', status);
    }

    // Apply broadcast type filter
    if (broadcast_type) {
      query = query.eq('broadcast_type', broadcast_type);
    }

    // Apply date range filter
    if (start_date) {
      query = query.gte('broadcast_date', start_date);
    }
    if (end_date) {
      query = query.lte('broadcast_date', end_date);
    }

    // Apply sorting
    switch (sort) {
      case 'date_asc':
        query = query.order('broadcast_date', { ascending: true });
        break;
      case 'date_desc':
      default:
        query = query.order('broadcast_date', { ascending: false });
        break;
    }

    // Apply pagination
    query = query.range(offset, offset + limit - 1);

    const { data, error, count } = await query;

    if (error) {
      logger.error('Error fetching broadcasts:', error);
      throw error;
    }

    // Transform data to include counts
    const broadcasts = data.map(broadcast => ({
      ...broadcast,
      product_count: broadcast.broadcast_products?.length || 0,
      coupon_count: broadcast.broadcast_coupons?.length || 0,
    }));

    // Remove the nested arrays to clean up response
    broadcasts.forEach(b => {
      delete b.broadcast_products;
      delete b.broadcast_coupons;
    });

    // Calculate pagination
    const totalPages = Math.ceil(count / limit);

    return {
      success: true,
      data: broadcasts,
      pagination: {
        page: parseInt(page),
        limit: parseInt(limit),
        total: count,
        pages: totalPages,
      },
    };
  } catch (error) {
    logger.error('getBroadcasts error:', error);
    return {
      success: false,
      error: error.message,
      data: [],
      pagination: { page: 1, limit: 20, total: 0, pages: 0 },
    };
  }
}

/**
 * Get single broadcast with all related data
 * @param {number} broadcastId - Broadcast ID
 * @returns {Promise<Object>} Complete broadcast data
 */
async function getBroadcastById(broadcastId) {
  try {
    // Get broadcast base data
    const { data: broadcast, error: broadcastError } = await supabase
      .from('broadcasts')
      .select('*')
      .eq('id', broadcastId)
      .single();

    if (broadcastError) {
      logger.error('Error fetching broadcast:', broadcastError);
      throw broadcastError;
    }

    if (!broadcast) {
      return {
        success: false,
        error: 'Broadcast not found',
        data: null,
      };
    }

    // Get products
    const { data: products, error: productsError } = await supabase
      .from('broadcast_products')
      .select('*')
      .eq('broadcast_id', broadcastId)
      .order('id', { ascending: true });

    if (productsError) {
      logger.error('Error fetching products:', productsError);
    }

    // Get coupons
    const { data: coupons, error: couponsError } = await supabase
      .from('broadcast_coupons')
      .select('*')
      .eq('broadcast_id', broadcastId)
      .order('id', { ascending: true });

    if (couponsError) {
      logger.error('Error fetching coupons:', couponsError);
    }

    // Get benefits
    const { data: benefits, error: benefitsError } = await supabase
      .from('broadcast_benefits')
      .select('*')
      .eq('broadcast_id', broadcastId)
      .order('id', { ascending: true });

    if (benefitsError) {
      logger.error('Error fetching benefits:', benefitsError);
    }

    // Get chat messages (limit to recent 500 to avoid large payloads)
    const { data: chat, error: chatError } = await supabase
      .from('broadcast_chat')
      .select('*')
      .eq('broadcast_id', broadcastId)
      .order('created_at_source', { ascending: false })
      .limit(500);

    if (chatError) {
      logger.error('Error fetching chat:', chatError);
    }

    // Get livebridge data if livebridge_url exists
    let livebridgeData = null;
    if (broadcast.livebridge_url) {
      try {
        // Get livebridge main record
        const { data: livebridge, error: livebridgeError } = await supabase
          .from('livebridge')
          .select('*')
          .eq('url', broadcast.livebridge_url)
          .single();

        if (!livebridgeError && livebridge) {
          const livebridgeId = livebridge.id;

          // Get livebridge special coupons
          const { data: specialCoupons, error: specialCouponsError } = await supabase
            .from('livebridge_coupons')
            .select('*')
            .eq('livebridge_id', livebridgeId)
            .order('id', { ascending: true });

          // Get livebridge products
          const { data: livebridgeProducts, error: livebridgeProductsError } = await supabase
            .from('livebridge_products')
            .select('*')
            .eq('livebridge_id', livebridgeId)
            .order('id', { ascending: true });

          // Get livebridge live benefits
          const { data: liveBenefits, error: liveBenefitsError } = await supabase
            .from('livebridge_live_benefits')
            .select('*')
            .eq('livebridge_id', livebridgeId)
            .order('id', { ascending: true });

          // Get livebridge benefits by amount
          const { data: benefitsByAmount, error: benefitsByAmountError } = await supabase
            .from('livebridge_benefits_by_amount')
            .select('*')
            .eq('livebridge_id', livebridgeId)
            .order('id', { ascending: true });

          // Get livebridge simple coupons
          const { data: simpleCoupons, error: simpleCouponsError } = await supabase
            .from('livebridge_simple_coupons')
            .select('*')
            .eq('livebridge_id', livebridgeId)
            .order('id', { ascending: true });

          livebridgeData = {
            ...livebridge,
            special_coupons: specialCoupons || [],
            products: livebridgeProducts || [],
            live_benefits: liveBenefits || [],
            benefits_by_amount: benefitsByAmount || [],
            simple_coupons: simpleCoupons || [],
          };

          logger.info(`Fetched livebridge data for broadcast ${broadcastId}: ${livebridgeData.special_coupons.length} coupons, ${livebridgeData.products.length} products`);
        }
      } catch (livebridgeErr) {
        logger.error('Error fetching livebridge data:', livebridgeErr);
        // Continue without livebridge data - non-critical
      }
    }

    // Combine all data
    const result = {
      ...broadcast,
      products: products || [],
      coupons: coupons || [],
      live_benefits: benefits || [],
      live_chat: chat || [],
      livebridge: livebridgeData,
    };

    return {
      success: true,
      data: result,
    };
  } catch (error) {
    logger.error('getBroadcastById error:', error);
    return {
      success: false,
      error: error.message,
      data: null,
    };
  }
}

/**
 * Get broadcast statistics
 * @returns {Promise<Object>} Statistics
 */
async function getBroadcastStats() {
  try {
    // Get total broadcasts
    const { count: totalBroadcasts, error: broadcastError } = await supabase
      .from('broadcasts')
      .select('*', { count: 'exact', head: true });

    if (broadcastError) throw broadcastError;

    // Get total products
    const { count: totalProducts, error: productsError } = await supabase
      .from('broadcast_products')
      .select('*', { count: 'exact', head: true });

    if (productsError) throw productsError;

    // Get total coupons
    const { count: totalCoupons, error: couponsError } = await supabase
      .from('broadcast_coupons')
      .select('*', { count: 'exact', head: true });

    if (couponsError) throw couponsError;

    // Get broadcasts by status
    const { data: statusCounts, error: statusError } = await supabase
      .from('broadcasts')
      .select('status');

    if (statusError) throw statusError;

    const broadcastsByStatus = statusCounts.reduce((acc, b) => {
      acc[b.status] = (acc[b.status] || 0) + 1;
      return acc;
    }, {});

    // Get latest crawl time
    const { data: latestCrawl, error: crawlError } = await supabase
      .from('crawl_metadata')
      .select('crawled_at')
      .order('crawled_at', { ascending: false })
      .limit(1);

    if (crawlError) throw crawlError;

    return {
      success: true,
      data: {
        total_broadcasts: totalBroadcasts || 0,
        total_products: totalProducts || 0,
        total_coupons: totalCoupons || 0,
        last_crawl: latestCrawl?.[0]?.crawled_at || null,
        broadcasts_by_status: broadcastsByStatus,
      },
    };
  } catch (error) {
    logger.error('getBroadcastStats error:', error);
    return {
      success: false,
      error: error.message,
      data: null,
    };
  }
}

/**
 * Search broadcasts
 * @param {string} query - Search query
 * @param {Object} filters - Additional filters
 * @returns {Promise<Object>} Search results
 */
async function searchBroadcasts(query, filters = {}) {
  try {
    const { brand = '', limit = 20 } = filters;

    let searchQuery = supabase
      .from('broadcasts')
      .select('*, broadcast_products(name), broadcast_coupons(title)')
      .or(`title.ilike.%${query}%,brand_name.ilike.%${query}%,description.ilike.%${query}%`)
      .limit(limit);

    if (brand) {
      searchQuery = searchQuery.eq('brand_name', brand);
    }

    const { data, error } = await searchQuery;

    if (error) {
      logger.error('Error searching broadcasts:', error);
      throw error;
    }

    return {
      success: true,
      query,
      results: data || [],
    };
  } catch (error) {
    logger.error('searchBroadcasts error:', error);
    return {
      success: false,
      error: error.message,
      query,
      results: [],
    };
  }
}

/**
 * Get unique brands from broadcasts
 * @returns {Promise<Array>} List of unique brands
 */
async function getBrands() {
  try {
    const { data, error } = await supabase
      .from('broadcasts')
      .select('brand_name')
      .order('brand_name');

    if (error) throw error;

    // Get unique brands
    const brands = [...new Set(data.map(b => b.brand_name))].filter(Boolean);

    return {
      success: true,
      data: brands,
    };
  } catch (error) {
    logger.error('getBrands error:', error);
    return {
      success: false,
      error: error.message,
      data: [],
    };
  }
}

module.exports = {
  getBroadcasts,
  getBroadcastById,
  getBroadcastStats,
  searchBroadcasts,
  getBrands,
};
