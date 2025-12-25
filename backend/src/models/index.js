/**
 * Models Index
 * Export all database models for easy importing
 */

const Platform = require('./Platform');
const Brand = require('./Brand');
const CrawlerConfig = require('./CrawlerConfig');
const Event = require('./Event');
const CrawlerExecution = require('./CrawlerExecution');

module.exports = {
  Platform,
  Brand,
  CrawlerConfig,
  Event,
  CrawlerExecution,
};
