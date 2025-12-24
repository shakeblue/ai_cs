/**
 * Livebridge Service
 * Handles all livebridge-related database operations
 */

const { supabase } = require('../config/supabase');
const logger = require('../config/logger');

/**
 * Get livebridge data by ID with all related data
 * @param {number} id - Livebridge ID
 * @returns {Promise<Object>} Livebridge data with related records
 */
async function getLivebridgeById(id) {
  try {
    logger.info(`Getting livebridge data by ID: ${id}`);

    // Fetch main livebridge record
    const { data: livebridge, error: mainError } = await supabase
      .from('livebridge')
      .select('*')
      .eq('id', id)
      .single();

    if (mainError) {
      logger.error(`Error fetching livebridge: ${mainError.message}`);
      return {
        success: false,
        error: mainError.message,
        data: null,
      };
    }

    if (!livebridge) {
      logger.warn(`Livebridge not found with ID: ${id}`);
      return {
        success: false,
        error: 'Livebridge not found',
        data: null,
      };
    }

    // Fetch all related data in parallel
    const [
      couponsResult,
      productsResult,
      liveBenefitsResult,
      benefitsByAmountResult,
      simpleCouponsResult,
    ] = await Promise.all([
      supabase.from('livebridge_coupons').select('*').eq('livebridge_id', id),
      supabase.from('livebridge_products').select('*').eq('livebridge_id', id),
      supabase.from('livebridge_live_benefits').select('*').eq('livebridge_id', id),
      supabase.from('livebridge_benefits_by_amount').select('*').eq('livebridge_id', id),
      supabase.from('livebridge_simple_coupons').select('*').eq('livebridge_id', id),
    ]);

    // Check for errors in related data fetches
    if (couponsResult.error) {
      logger.error(`Error fetching coupons: ${couponsResult.error.message}`);
    }
    if (productsResult.error) {
      logger.error(`Error fetching products: ${productsResult.error.message}`);
    }
    if (liveBenefitsResult.error) {
      logger.error(`Error fetching live benefits: ${liveBenefitsResult.error.message}`);
    }
    if (benefitsByAmountResult.error) {
      logger.error(`Error fetching benefits by amount: ${benefitsByAmountResult.error.message}`);
    }
    if (simpleCouponsResult.error) {
      logger.error(`Error fetching simple coupons: ${simpleCouponsResult.error.message}`);
    }

    // Build complete response
    const result = {
      ...livebridge,
      special_coupons: couponsResult.data || [],
      products: productsResult.data || [],
      live_benefits: liveBenefitsResult.data?.map((b) => b.benefit_text) || [],
      benefits_by_amount: benefitsByAmountResult.data?.map((b) => b.benefit_text) || [],
      coupons: simpleCouponsResult.data?.map((c) => c.coupon_text) || [],
    };

    logger.info(`Successfully fetched livebridge data: ${id}`);
    return {
      success: true,
      data: result,
      error: null,
    };
  } catch (error) {
    logger.error(`Unexpected error in getLivebridgeById: ${error.message}`);
    return {
      success: false,
      error: error.message,
      data: null,
    };
  }
}

/**
 * Get livebridge data by URL
 * @param {string} url - Livebridge URL
 * @returns {Promise<Object>} Livebridge data with related records
 */
async function getLivebridgeByUrl(url) {
  try {
    logger.info(`Getting livebridge data by URL: ${url}`);

    // Fetch main livebridge record by URL
    const { data: livebridge, error } = await supabase
      .from('livebridge')
      .select('*')
      .eq('url', url)
      .single();

    if (error) {
      logger.error(`Error fetching livebridge by URL: ${error.message}`);
      return {
        success: false,
        error: error.message,
        data: null,
      };
    }

    if (!livebridge) {
      logger.warn(`Livebridge not found with URL: ${url}`);
      return {
        success: false,
        error: 'Livebridge not found',
        data: null,
      };
    }

    // Fetch complete data using ID
    return getLivebridgeById(livebridge.id);
  } catch (error) {
    logger.error(`Unexpected error in getLivebridgeByUrl: ${error.message}`);
    return {
      success: false,
      error: error.message,
      data: null,
    };
  }
}

/**
 * Get all livebridge records with pagination
 * @param {Object} options - Query options (page, limit, sort)
 * @returns {Promise<Object>} Livebridge list with pagination info
 */
async function getLivebridges(options = {}) {
  try {
    const { page = 1, limit = 20, sort = 'date_desc' } = options;

    // Calculate offset
    const offset = (page - 1) * limit;

    // Build query
    let query = supabase
      .from('livebridge')
      .select('*, livebridge_products(id), livebridge_coupons(id)', { count: 'exact' });

    // Apply sorting
    switch (sort) {
      case 'date_asc':
        query = query.order('live_datetime', { ascending: true, nullsFirst: false });
        break;
      case 'date_desc':
      default:
        query = query.order('live_datetime', { ascending: false, nullsFirst: false });
        break;
      case 'title_asc':
        query = query.order('title', { ascending: true });
        break;
      case 'title_desc':
        query = query.order('title', { ascending: false });
        break;
    }

    // Apply pagination
    query = query.range(offset, offset + limit - 1);

    const { data, error, count } = await query;

    if (error) {
      logger.error(`Error fetching livebridges: ${error.message}`);
      return {
        success: false,
        error: error.message,
        data: [],
        pagination: null,
      };
    }

    // Calculate pagination info
    const totalPages = Math.ceil(count / limit);
    const hasNextPage = page < totalPages;
    const hasPrevPage = page > 1;

    logger.info(`Successfully fetched ${data.length} livebridges (page ${page}/${totalPages})`);

    return {
      success: true,
      data: data || [],
      pagination: {
        currentPage: page,
        totalPages,
        totalItems: count,
        itemsPerPage: limit,
        hasNextPage,
        hasPrevPage,
      },
      error: null,
    };
  } catch (error) {
    logger.error(`Unexpected error in getLivebridges: ${error.message}`);
    return {
      success: false,
      error: error.message,
      data: [],
      pagination: null,
    };
  }
}

/**
 * Get livebridge summary statistics
 * @returns {Promise<Object>} Summary stats
 */
async function getLivebridgeStats() {
  try {
    logger.info('Getting livebridge statistics');

    // Get total count
    const { count: totalCount, error: countError } = await supabase
      .from('livebridge')
      .select('*', { count: 'exact', head: true });

    if (countError) {
      logger.error(`Error getting count: ${countError.message}`);
      return {
        success: false,
        error: countError.message,
        data: null,
      };
    }

    // Get count by brand
    const { data: brandData, error: brandError } = await supabase
      .from('livebridge')
      .select('brand_name')
      .not('brand_name', 'is', null);

    const brandCounts = {};
    if (!brandError && brandData) {
      brandData.forEach((item) => {
        brandCounts[item.brand_name] = (brandCounts[item.brand_name] || 0) + 1;
      });
    }

    // Get recent livebridges
    const { data: recentData, error: recentError } = await supabase
      .from('livebridge')
      .select('id, title, brand_name, live_datetime, created_at')
      .order('created_at', { ascending: false })
      .limit(5);

    return {
      success: true,
      data: {
        total: totalCount || 0,
        byBrand: brandCounts,
        recent: recentData || [],
      },
      error: null,
    };
  } catch (error) {
    logger.error(`Unexpected error in getLivebridgeStats: ${error.message}`);
    return {
      success: false,
      error: error.message,
      data: null,
    };
  }
}

module.exports = {
  getLivebridgeById,
  getLivebridgeByUrl,
  getLivebridges,
  getLivebridgeStats,
};
