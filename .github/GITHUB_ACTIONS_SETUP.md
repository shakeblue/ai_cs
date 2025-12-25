# GitHub Actions Setup Guide

This guide explains how to configure GitHub Actions for automated scheduled crawling of Naver Shopping Live broadcasts.

## Overview

The standalone crawler runs automatically on GitHub Actions runners using scheduled cron jobs. Each brand has its own workflow file with a customizable schedule.

## Prerequisites

1. GitHub repository with Actions enabled
2. Supabase project with crawler database tables created
3. API keys for LLM services (optional, if using LLM extraction)

## Step 1: Configure GitHub Secrets

Navigate to your repository settings: **Settings → Secrets and variables → Actions**

### Required Secrets

Add the following repository secrets:

| Secret Name | Description | Example | Required |
|------------|-------------|---------|----------|
| `SUPABASE_URL` | Your Supabase project URL | `https://xxxxx.supabase.co` | ✅ Yes |
| `SUPABASE_SECRET_KEY` | Supabase service role key | `eyJhbGc...` | ✅ Yes |
| `SUPABASE_SERVICE_KEY` | Same as SUPABASE_SECRET_KEY | `eyJhbGc...` | ✅ Yes |
| `OPENAI_API_KEY` | OpenAI API key (for LLM extraction) | `sk-proj-...` | ⚠️ Optional* |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | `sk-ant-...` | ⚠️ Optional* |
| `GOOGLE_API_KEY` | Google Gemini API key | `AIza...` | ⚠️ Optional* |

*LLM API keys are only needed if your crawler uses LLM-based content extraction. The broadcast crawler primarily uses API interception.

### How to Get Supabase Credentials

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click on your project
3. Navigate to **Settings → API**
4. Copy:
   - **Project URL** → Use for `SUPABASE_URL`
   - **service_role key** → Use for `SUPABASE_SECRET_KEY` and `SUPABASE_SERVICE_KEY`

⚠️ **Important:** Use the `service_role` key (not the `anon` key) for full database access from GitHub Actions.

### Adding Secrets to GitHub

1. Go to: **Your Repo → Settings → Secrets and variables → Actions**
2. Click **"New repository secret"**
3. Enter the secret name (e.g., `SUPABASE_URL`)
4. Paste the secret value
5. Click **"Add secret"**
6. Repeat for all required secrets

## Step 2: Verify Database Tables

Ensure the following tables exist in your Supabase project:

**Scheduled Crawler Tables:**
- `platforms`
- `brands`
- `crawler_config`
- `crawler_executions`

**Broadcast Data Tables:**
- `broadcasts`
- `broadcast_products`
- `broadcast_coupons`
- `broadcast_benefits`
- `broadcast_chat`
- `crawl_metadata`

**Seed Data:**
Run the SQL script to add initial platform and brands:
```bash
# See: database/seed_data.sql
```

## Step 3: Workflow Files

Workflows are located in `.github/workflows/` directory:

### Available Workflows

| Workflow File | Brand | Schedule | Description |
|--------------|-------|----------|-------------|
| `crawl-sulwhasoo.yml` | Sulwhasoo (설화수) | Every 6 hours | High-value brand |
| `crawl-innisfree.yml` | Innisfree (이니스프리) | Every 12 hours | Medium frequency |
| `crawl-laneige.yml` | Laneige (라네즈) | Daily at midnight | Low frequency |
| `crawl-amorepacific.yml` | Amorepacific (아모레퍼시픽) | Every 6 hours | High-value brand |

### Schedule Reference (Cron Syntax)

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *
```

**Common Schedules:**
- `0 */6 * * *` - Every 6 hours (at minute 0)
- `0 */12 * * *` - Every 12 hours (at midnight and noon)
- `0 0 * * *` - Daily at midnight UTC
- `0 8,20 * * *` - Daily at 8:00 AM and 8:00 PM UTC

## Step 4: Manual Testing

### Test via GitHub Actions UI

1. Go to **Actions** tab in your repository
2. Select a workflow (e.g., "Crawl Sulwhasoo")
3. Click **"Run workflow"** dropdown
4. (Optional) Enter a brand name to override default
5. Click **"Run workflow"** button
6. Watch the execution in real-time

### Monitor Execution

- **Logs:** Click on the workflow run → Click on the job → View step-by-step logs
- **Database:** Check `crawler_executions` table in Supabase for execution records
- **Data:** Check `broadcasts` and related tables for crawled data

## Step 5: Enable Scheduled Execution

Once manual testing succeeds:

1. Workflows will automatically run on their configured schedules
2. No additional configuration needed
3. GitHub Actions runs workflows in UTC timezone

### Monitor Usage

- **Free Tier:** 2,000 minutes/month for public repos, 500 minutes/month for private repos
- **Estimated Usage:** ~5 minutes per crawl × 4 runs/day × 4 brands = ~80 minutes/day (~2,400 min/month)
- **Recommendation:** Optimize schedules based on brand priority and usage limits

**View Usage:**
- Go to **Settings → Billing → Usage** to monitor GitHub Actions minutes

## Step 6: Troubleshooting

### Workflow Fails Immediately

**Symptom:** Workflow fails at "Run standalone crawler" step

**Solutions:**
1. Check that all required secrets are configured
2. Verify Supabase credentials are correct (try connecting manually)
3. Check that database tables exist
4. Review error logs in GitHub Actions

### Crawler Times Out

**Symptom:** Workflow runs for 15+ minutes and times out

**Solutions:**
1. Reduce `--limit` parameter (default: 50 broadcasts)
2. Increase `timeout-minutes` in workflow file
3. Check if Naver website is accessible from GitHub Actions runners

### No Data in Database

**Symptom:** Workflow succeeds but no data in `broadcasts` table

**Solutions:**
1. Check `crawler_executions` table for execution status and error messages
2. Verify brand exists in `brands` table with `status = 'active'`
3. Check that brand's `search_text` matches actual Naver search results
4. Review detailed logs in GitHub Actions

### SSL Certificate Errors

**Symptom:** SSL certificate verification failures

**Solution:**
The standalone crawler is configured to bypass SSL verification in the database client. This is expected for development environments.

## Step 7: Adding New Brands

To add a new brand:

### 1. Add Brand to Database

```sql
-- Insert into brands table
INSERT INTO brands (name, search_text, platform_id, status, schedule_cron)
VALUES (
    'New Brand Name',
    '새브랜드',
    (SELECT id FROM platforms WHERE name = 'Naver Shopping Live'),
    'active',
    '0 */6 * * *'
);
```

### 2. Create Workflow File

Copy an existing workflow (e.g., `crawl-sulwhasoo.yml`) and modify:

```yaml
name: Crawl New Brand

on:
  schedule:
    - cron: '0 */6 * * *'  # Customize schedule
  workflow_dispatch:

jobs:
  crawl:
    runs-on: ubuntu-latest
    # ... rest of the workflow

      - name: Run standalone crawler
        run: |
          python standalone_crawler.py \
            --brand-name "New Brand Name" \  # ← Update this
            --trigger scheduled \
            --limit 50 \
            --verbose
```

### 3. Test and Enable

1. Commit the new workflow file
2. Test manually via GitHub Actions UI
3. Enable scheduled execution once verified

## Architecture

### Execution Flow

```
GitHub Actions Workflow
  ↓
  1. Checkout code
  2. Set up Python 3.11
  3. Install system dependencies (Chrome, ChromeDriver)
  4. Install Python dependencies
  5. Install Playwright browsers
  ↓
Standalone Crawler
  ↓
  1. Load brand/platform config from Supabase
  2. Create crawler_execution record
  3. Search for broadcasts (Selenium)
  4. Extract broadcast details (Playwright)
  5. Save to broadcasts tables (BroadcastSaver)
  6. Update execution status
  ↓
Supabase Database
  - broadcasts
  - broadcast_products
  - broadcast_coupons
  - broadcast_benefits
  - broadcast_chat
  - crawler_executions
```

### Benefits of GitHub Actions Approach

✅ **Serverless** - No server maintenance required
✅ **Free** - 2,000 minutes/month for public repos
✅ **Reliable** - GitHub's infrastructure
✅ **Scalable** - Add brands by adding workflow files
✅ **Isolated** - Each brand runs independently
✅ **Monitored** - Built-in logging and notifications
✅ **Version Controlled** - Workflows stored in git

## Support

For issues:
1. Check GitHub Actions logs for detailed error messages
2. Review `crawler_executions` table in Supabase
3. Test crawler locally first: `python standalone_crawler.py --brand-name "BrandName" --verbose`
4. Check that secrets are configured correctly

## Security Notes

- ✅ Secrets are encrypted by GitHub and not exposed in logs
- ✅ GitHub automatically masks secret values in workflow logs
- ✅ Use service role key (not anon key) for database access
- ⚠️ Never commit secrets to git
- ⚠️ Review workflow files before running to ensure no secret logging
