/**
 * Crawler API Routes
 * Trigger Naver broadcast crawler from admin interface
 */

const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');
const path = require('path');
const logger = require('../config/logger');

// Path to Python crawler script and virtual environment
const CRAWLER_DIR = path.join(__dirname, '../../../crawler/cj');
const CRAWLER_SCRIPT = path.join(CRAWLER_DIR, 'naver_broadcast_crawler.py');
const PYTHON_CMD = path.join(CRAWLER_DIR, 'venv/bin/python');

/**
 * POST /api/crawler/crawl
 * Trigger crawler for a given Naver broadcast URL
 *
 * Body: { url: string, saveToDb: boolean }
 * Response: { success: boolean, data: object, message: string }
 */
router.post('/crawl', async (req, res) => {
  const { url, saveToDb = true } = req.body;

  // Validate URL
  if (!url || typeof url !== 'string') {
    return res.status(400).json({
      success: false,
      error: 'URL is required and must be a string'
    });
  }

  // Validate URL format (Naver Shopping Live)
  const validUrlPattern = /^https:\/\/view\.shoppinglive\.naver\.com\/(replays|lives|shortclips)\/\d+/;
  if (!validUrlPattern.test(url)) {
    return res.status(400).json({
      success: false,
      error: 'Invalid Naver Shopping Live URL. Expected format: https://view.shoppinglive.naver.com/{replays|lives|shortclips}/{id}'
    });
  }

  logger.info(`Crawler triggered for URL: ${url}`);

  try {
    // Build command arguments
    const args = [CRAWLER_SCRIPT, url];
    if (saveToDb) {
      args.push('--save-to-db');
    }

    // Spawn Python process with correct Playwright browser path
    const pythonProcess = spawn(PYTHON_CMD, args, {
      cwd: path.dirname(CRAWLER_SCRIPT),
      env: {
        ...process.env,
        PLAYWRIGHT_BROWSERS_PATH: '/home/long/.cache/ms-playwright'
      }
    });

    let stdout = '';
    let stderr = '';

    // Collect stdout
    pythonProcess.stdout.on('data', (data) => {
      const output = data.toString();
      stdout += output;
      // Don't log every line to avoid spam
    });

    // Collect stderr
    pythonProcess.stderr.on('data', (data) => {
      const output = data.toString();
      stderr += output;
      // Stderr often contains INFO logs from Python
    });

    // Handle process completion
    pythonProcess.on('close', (code) => {
      if (code === 0) {
        // Python logging goes to stderr, so combine both for parsing
        const combinedOutput = stderr + stdout;
        const summary = parseCrawlerOutput(combinedOutput);

        logger.info(`Crawler completed successfully for URL: ${url}`);
        logger.info(`Summary: ${JSON.stringify(summary)}`);

        res.json({
          success: true,
          message: 'Crawl completed successfully',
          data: {
            url,
            summary,
            logs: combinedOutput.substring(0, 500) // Limit log size
          }
        });
      } else {
        const combinedOutput = stderr + stdout;
        logger.error(`Crawler failed with exit code ${code}`);
        logger.error(`Stderr: ${stderr.substring(0, 1000)}`);
        logger.error(`Stdout: ${stdout.substring(0, 1000)}`);

        res.status(500).json({
          success: false,
          error: `Crawler failed with exit code ${code}`,
          details: combinedOutput.substring(0, 2000),
          stderr: stderr.substring(0, 1000),
          stdout: stdout.substring(0, 1000)
        });
      }
    });

    // Handle process errors
    pythonProcess.on('error', (error) => {
      logger.error(`Failed to start crawler: ${error.message}`);
      res.status(500).json({
        success: false,
        error: 'Failed to start crawler process',
        details: error.message
      });
    });

  } catch (error) {
    logger.error(`Crawler error: ${error.message}`);
    res.status(500).json({
      success: false,
      error: 'Internal server error',
      details: error.message
    });
  }
});

/**
 * Parse crawler output to extract summary information
 */
function parseCrawlerOutput(output) {
  const summary = {
    broadcastId: null,
    title: null,
    brandName: null,
    products: 0,
    coupons: 0,
    benefits: 0,
    chatMessages: 0
  };

  try {
    // Extract broadcast ID
    const idMatch = output.match(/Broadcast ID: (\d+)/);
    if (idMatch) {
      summary.broadcastId = idMatch[1];
    }

    // Extract URL type
    const typeMatch = output.match(/Detected URL type: (\w+)/);
    if (typeMatch) {
      summary.urlType = typeMatch[1];
    }

    // Extract from "Extracted X products, Y coupons, Z benefits, W comments" format
    const extractedMatch = output.match(/Extracted (\d+) products?, (\d+) coupons?, (\d+) benefits?, (\d+) comments?/);
    if (extractedMatch) {
      summary.products = parseInt(extractedMatch[1], 10);
      summary.coupons = parseInt(extractedMatch[2], 10);
      summary.benefits = parseInt(extractedMatch[3], 10);
      summary.chatMessages = parseInt(extractedMatch[4], 10);
    }

    // Also try database save format: "Products: X"
    if (summary.products === 0) {
      const productsMatch = output.match(/Products: (\d+)/);
      if (productsMatch) {
        summary.products = parseInt(productsMatch[1], 10);
      }
    }

    if (summary.coupons === 0) {
      const couponsMatch = output.match(/Coupons: (\d+)/);
      if (couponsMatch) {
        summary.coupons = parseInt(couponsMatch[1], 10);
      }
    }

    if (summary.benefits === 0) {
      const benefitsMatch = output.match(/Benefits: (\d+)/);
      if (benefitsMatch) {
        summary.benefits = parseInt(benefitsMatch[1], 10);
      }
    }

    if (summary.chatMessages === 0) {
      const chatMatch = output.match(/Chat messages: (\d+)/);
      if (chatMatch) {
        summary.chatMessages = parseInt(chatMatch[1], 10);
      }
    }

    // Check for success indicators
    if (output.includes('Crawl completed successfully')) {
      summary.status = 'success';
    }

  } catch (error) {
    logger.error(`Error parsing crawler output: ${error.message}`);
  }

  return summary;
}

module.exports = router;
