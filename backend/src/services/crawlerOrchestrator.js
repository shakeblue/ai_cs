/**
 * Crawler Orchestrator Service
 * Orchestrates the scheduled crawler execution:
 * - Constructs search URLs from platform patterns + brand search text
 * - Executes Python crawler scripts
 * - Handles LLM extraction
 * - Stores events with duplicate detection
 * - Logs execution status
 */

const { spawn } = require('child_process');
const path = require('path');
const logger = require('../config/logger');
const Brand = require('../models/Brand');
const Platform = require('../models/Platform');
const Event = require('../models/Event');
const CrawlerExecution = require('../models/CrawlerExecution');
const CrawlerConfig = require('../models/CrawlerConfig');

class CrawlerOrchestrator {
  constructor() {
    // Path to Python virtual environment and scripts
    this.crawlerDir = path.join(__dirname, '../../../crawler/cj');
    this.pythonCmd = path.join(this.crawlerDir, 'venv/bin/python');
    this.searchCrawlerScript = path.join(this.crawlerDir, 'naver_search_crawler.py');
    this.broadcasterCrawlerScript = path.join(this.crawlerDir, 'naver_broadcast_crawler.py');
    this.livebridgeCrawlerScript = path.join(this.crawlerDir, 'run_livebridge_crawler.py');
  }

  /**
   * Execute crawler for a brand
   * @param {string} brandId - Brand UUID
   * @param {string} triggerType - 'scheduled' or 'manual'
   * @returns {Promise<Object>} Execution result
   */
  async executeCrawl(brandId, triggerType = 'manual') {
    let execution = null;

    try {
      logger.info(`Starting crawler for brand ${brandId} (${triggerType})`);

      // 1. Load brand and platform info
      const brand = await Brand.findByIdWithPlatform(brandId);
      if (!brand) {
        throw new Error(`Brand not found: ${brandId}`);
      }

      const platform = brand.platforms;
      if (!platform) {
        throw new Error(`Platform not found for brand ${brandId}`);
      }

      // Check if brand and platform are active
      if (brand.status !== 'active') {
        throw new Error(`Brand is inactive: ${brand.name}`);
      }
      if (platform.status !== 'active') {
        throw new Error(`Platform is inactive: ${platform.name}`);
      }

      // 2. Check if there's already a running execution
      const isRunning = await CrawlerExecution.hasRunningExecution(brandId, platform.id);
      if (isRunning) {
        logger.warn(`Crawler already running for brand ${brandId}, skipping`);
        return {
          success: false,
          message: 'Crawler already running for this brand',
        };
      }

      // 3. Create execution record
      execution = await CrawlerExecution.create({
        brand_id: brandId,
        platform_id: platform.id,
        trigger_type: triggerType,
      });

      logger.info(`Created execution record: ${execution.id}`);

      // 4. Mark execution as running
      await CrawlerExecution.markAsRunning(execution.id);

      // 5. Construct search URL
      const searchUrl = this.constructSearchUrl(platform.url_pattern, brand.search_text);
      logger.info(`Search URL: ${searchUrl}`);

      // 6. Get time range configuration
      const timeRange = await CrawlerConfig.getTimeRange();
      logger.info(`Time range: ${timeRange.pastDays} days past, ${timeRange.futureDays} days future`);

      // 7. Execute crawler and collect events
      const events = await this.crawlSearchResults(searchUrl, {
        brandId: brand.id,
        platformId: platform.id,
        executionId: execution.id,
        timeRange,
      });

      logger.info(`Found ${events.length} events for brand ${brand.name}`);

      // 8. Store events with duplicate handling
      const storedEvents = await this.storeEvents(events);

      // 9. Mark execution as success
      await CrawlerExecution.markAsSuccess(execution.id, storedEvents.length);

      logger.info(`Crawler execution completed successfully: ${execution.id}`);

      return {
        success: true,
        data: {
          execution_id: execution.id,
          events_found: events.length,
          events_stored: storedEvents.length,
          brand: brand.name,
          platform: platform.name,
        },
      };
    } catch (error) {
      logger.error('Crawler execution failed:', error);

      // Mark execution as failed
      if (execution) {
        await CrawlerExecution.markAsFailed(execution.id, error.message);
      }

      return {
        success: false,
        error: error.message,
        execution_id: execution?.id,
      };
    }
  }

  /**
   * Construct search URL from platform pattern and brand search text
   * @param {string} urlPattern - Platform URL pattern with {query} placeholder
   * @param {string} searchText - Brand search text
   * @returns {string} Complete search URL
   */
  constructSearchUrl(urlPattern, searchText) {
    if (!urlPattern.includes('{query}')) {
      throw new Error('URL pattern must contain {query} placeholder');
    }

    // URL encode the search text
    const encodedQuery = encodeURIComponent(searchText);

    // Replace {query} placeholder with encoded search text
    return urlPattern.replace('{query}', encodedQuery);
  }

  /**
   * Crawl search results and get list of broadcasts
   * @param {string} searchUrl - Search URL to crawl
   * @param {Object} options - Crawl options
   * @returns {Promise<Array>} List of events
   */
  async crawlSearchResults(searchUrl, options) {
    try {
      logger.info('Step 1: Crawling search results to get broadcast list');

      // 1. Call search crawler to get list of broadcasts
      const searchResults = await this.executePythonScript(this.searchCrawlerScript, [
        searchUrl,
        '--json',
        '--limit',
        '50',
      ]);

      if (!searchResults.success || !searchResults.broadcasts) {
        logger.warn('Search crawler returned no broadcasts');
        return [];
      }

      const broadcasts = searchResults.broadcasts;
      logger.info(`Found ${broadcasts.length} broadcasts from search`);

      // 2. Filter broadcasts by time range
      const filteredBroadcasts = this.filterBroadcastsByType(broadcasts);
      logger.info(`After filtering: ${filteredBroadcasts.length} broadcasts`);

      // 3. For each broadcast, crawl details (limit to first 20 to avoid overwhelming)
      const maxDetails = Math.min(filteredBroadcasts.length, 20);
      const events = [];

      for (let i = 0; i < maxDetails; i++) {
        const broadcast = filteredBroadcasts[i];
        logger.info(`Crawling details [${i + 1}/${maxDetails}]: ${broadcast.title}`);

        try {
          const eventData = await this.crawlBroadcastDetails(broadcast, options);
          if (eventData) {
            events.push(eventData);
          }
        } catch (error) {
          logger.error(`Failed to crawl broadcast ${broadcast.url}:`, error.message);
          // Continue with next broadcast
        }

        // Add delay between requests to avoid rate limiting
        if (i < maxDetails - 1) {
          await this.sleep(2000); // 2 second delay
        }
      }

      // 4. Filter by date range
      const filteredEvents = this.filterEventsByDateRange(events, options.timeRange);
      logger.info(`After date filtering: ${filteredEvents.length} events`);

      return filteredEvents;
    } catch (error) {
      logger.error('Error crawling search results:', error);
      throw error;
    }
  }

  /**
   * Filter broadcasts by type (exclude livebridge for now)
   * @param {Array} broadcasts - List of broadcasts
   * @returns {Array} Filtered broadcasts
   */
  filterBroadcastsByType(broadcasts) {
    // For now, focus on lives and replays, skip livebridge and shortclips
    return broadcasts.filter((broadcast) => {
      return broadcast.event_type === 'live' || broadcast.event_type === 'replay';
    });
  }

  /**
   * Crawl broadcast details
   * @param {Object} broadcast - Broadcast info from search
   * @param {Object} options - Crawl options
   * @returns {Promise<Object>} Event data
   */
  async crawlBroadcastDetails(broadcast, options) {
    try {
      // Call broadcast crawler for this specific URL
      const result = await this.executePythonScript(this.broadcasterCrawlerScript, [
        broadcast.url,
        // Note: We're not using --save-to-db because we'll handle DB operations in Node.js
      ]);

      // The script should output JSON with broadcast details
      // For now, we'll use the basic info from search and enhance it
      const eventData = {
        external_id: broadcast.external_id,
        brand_id: options.brandId,
        platform_id: options.platformId,
        execution_id: options.executionId,
        title: broadcast.title,
        url: broadcast.url,
        start_date: this.parseDate(broadcast.start_date),
        end_date: null,
        status: this.normalizeEventStatus(broadcast.status),
        event_type: this.normalizeEventType(broadcast.event_type),
        raw_data: {
          search_data: broadcast,
          crawler_result: result.stdout || result,
        },
        extracted_data: null, // Will be filled by LLM later
      };

      return eventData;
    } catch (error) {
      logger.error(`Error crawling broadcast details: ${error.message}`);
      // Return basic event data even if detail crawl fails
      return {
        external_id: broadcast.external_id,
        brand_id: options.brandId,
        platform_id: options.platformId,
        execution_id: options.executionId,
        title: broadcast.title,
        url: broadcast.url,
        start_date: this.parseDate(broadcast.start_date),
        end_date: null,
        status: this.normalizeEventStatus(broadcast.status),
        event_type: this.normalizeEventType(broadcast.event_type),
        raw_data: { search_data: broadcast },
        extracted_data: null,
      };
    }
  }

  /**
   * Parse date string to ISO format
   * @param {string} dateStr - Date string
   * @returns {string|null} ISO date string or null
   */
  parseDate(dateStr) {
    if (!dateStr) return null;

    try {
      const date = new Date(dateStr);
      if (isNaN(date.getTime())) {
        return null;
      }
      return date.toISOString();
    } catch (error) {
      return null;
    }
  }

  /**
   * Sleep utility
   * @param {number} ms - Milliseconds to sleep
   * @returns {Promise}
   */
  sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  /**
   * Execute Python crawler script
   * @param {string} scriptPath - Path to Python script
   * @param {Array} args - Script arguments
   * @returns {Promise<Object>} Crawler output
   */
  async executePythonScript(scriptPath, args = []) {
    return new Promise((resolve, reject) => {
      const pythonProcess = spawn(this.pythonCmd, [scriptPath, ...args]);

      let stdout = '';
      let stderr = '';

      pythonProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      pythonProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          logger.error(`Python script failed with code ${code}: ${stderr}`);
          reject(new Error(`Crawler script failed: ${stderr}`));
        } else {
          try {
            // Try to parse JSON output from script
            const output = JSON.parse(stdout);
            resolve(output);
          } catch (error) {
            // If not JSON, return raw output
            resolve({ stdout, stderr });
          }
        }
      });

      pythonProcess.on('error', (error) => {
        logger.error('Failed to start Python crawler:', error);
        reject(error);
      });
    });
  }

  /**
   * Filter events by date range
   * @param {Array} events - List of events
   * @param {Object} timeRange - Time range configuration
   * @returns {Array} Filtered events
   */
  filterEventsByDateRange(events, timeRange) {
    const now = new Date();
    const pastDate = new Date();
    pastDate.setDate(pastDate.getDate() - timeRange.pastDays);

    const futureDate = new Date();
    futureDate.setDate(futureDate.getDate() + timeRange.futureDays);

    return events.filter((event) => {
      if (!event.start_date) {
        return true; // Include events without start date
      }

      const startDate = new Date(event.start_date);
      return startDate >= pastDate && startDate <= futureDate;
    });
  }

  /**
   * Store events with duplicate handling (upsert)
   * @param {Array} events - List of events
   * @returns {Promise<Array>} Stored events
   */
  async storeEvents(events) {
    try {
      if (events.length === 0) {
        return [];
      }

      // Use bulk upsert for efficiency
      const storedEvents = await Event.bulkUpsert(events);

      logger.info(`Stored ${storedEvents.length} events`);

      return storedEvents;
    } catch (error) {
      logger.error('Failed to store events:', error);
      throw error;
    }
  }

  /**
   * Extract event data from crawler output
   * @param {Object} crawlerOutput - Raw crawler output
   * @param {Object} context - Execution context (brand, platform, execution IDs)
   * @returns {Object} Normalized event data
   */
  extractEventData(crawlerOutput, context) {
    // Basic extraction logic
    // Will be enhanced in Phase 3.5 with LLM integration
    return {
      external_id: crawlerOutput.id || crawlerOutput.external_id,
      brand_id: context.brandId,
      platform_id: context.platformId,
      execution_id: context.executionId,
      title: crawlerOutput.title,
      url: crawlerOutput.url,
      start_date: crawlerOutput.start_date || crawlerOutput.broadcast_date,
      end_date: crawlerOutput.end_date,
      status: this.normalizeEventStatus(crawlerOutput.status),
      event_type: this.normalizeEventType(crawlerOutput.type || crawlerOutput.event_type),
      raw_data: crawlerOutput,
      extracted_data: null, // Will be filled by LLM in Phase 3.5
    };
  }

  /**
   * Normalize event status from various formats
   * @param {string} status - Raw status string
   * @returns {string} Normalized status (upcoming|ongoing|ended)
   */
  normalizeEventStatus(status) {
    if (!status) return null;

    const statusLower = status.toLowerCase();
    if (statusLower.includes('live') || statusLower.includes('진행') || statusLower.includes('라이브')) {
      return 'ongoing';
    }
    if (statusLower.includes('다시보기') || statusLower.includes('replay') || statusLower.includes('ended')) {
      return 'ended';
    }
    if (statusLower.includes('upcoming') || statusLower.includes('예정')) {
      return 'upcoming';
    }

    return null;
  }

  /**
   * Normalize event type from various formats
   * @param {string} type - Raw type string
   * @returns {string} Normalized type (live|replay)
   */
  normalizeEventType(type) {
    if (!type) return null;

    const typeLower = type.toLowerCase();
    if (typeLower.includes('replay') || typeLower.includes('다시보기')) {
      return 'replay';
    }
    if (typeLower.includes('live') || typeLower.includes('라이브')) {
      return 'live';
    }

    return null;
  }
}

module.exports = new CrawlerOrchestrator();
