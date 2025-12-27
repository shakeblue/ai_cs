# GitHub Actions Setup for Brand Shopping Story Crawler

## Overview

This guide explains how to set up automatic crawler execution using GitHub Actions.

## Workflow Features

- ✅ **Scheduled Runs**: Automatically runs daily at 2 AM UTC
- ✅ **Manual Trigger**: Run anytime with custom parameters
- ✅ **Results Archive**: Saves results as artifacts for 30 days
- ✅ **Summary Reports**: Shows success rate and costs in GitHub UI
- ✅ **Optional Git Commits**: Archives results to repository
- ✅ **Failure Notifications**: Alerts when crawler fails

## Setup Steps

### 1. Configure GitHub Secrets

Go to your repository settings:
**Settings → Secrets and variables → Actions → New repository secret**

Add the following secrets:

| Secret Name | Description | Required |
|-------------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o Mini | Yes (default) |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Optional |
| `GOOGLE_API_KEY` | Google API key for Gemini | Optional |
| `SUPABASE_URL` | Supabase project URL | Optional |
| `SUPABASE_KEY` | Supabase API key | Optional |

**Example:**
```
Name: OPENAI_API_KEY
Value: sk-proj-xxxxxxxxxxxxx
```

### 2. Enable GitHub Actions

1. Go to repository **Settings → Actions → General**
2. Under "Actions permissions", select **Allow all actions**
3. Under "Workflow permissions", select **Read and write permissions**
4. Click **Save**

### 3. Verify Workflow File

Ensure the workflow file exists at:
```
.github/workflows/brand-shopping-story-crawler.yml
```

### 4. Test Manual Run

1. Go to **Actions** tab in your repository
2. Click **Brand Shopping Story Crawler** workflow
3. Click **Run workflow** button
4. Configure parameters (optional):
   - **Max brands**: 1-10 (default: 10)
   - **Provider**: gpt/claude/gemini (default: gpt)
   - **Strategy**: gentle/moderate/aggressive (default: gentle)
5. Click **Run workflow**

## Workflow Configuration

### Schedule Configuration

The workflow runs automatically at **2 AM UTC daily**.

To change the schedule, edit the cron expression in the workflow file:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

**Common schedules:**
```yaml
# Every 6 hours
- cron: '0 */6 * * *'

# Every Monday at 3 AM
- cron: '0 3 * * 1'

# Twice daily (8 AM and 8 PM)
- cron: '0 8,20 * * *'

# First day of every month
- cron: '0 0 1 * *'
```

### Timeout Configuration

Default timeout is 4 hours (240 minutes). To adjust:

```yaml
timeout-minutes: 240  # Change this value
```

### Results Retention

Results are kept for 30 days. To change:

```yaml
retention-days: 30  # Change this value
```

## Usage

### Automatic Scheduled Runs

The workflow runs automatically based on the schedule. No action needed!

Check the **Actions** tab to monitor progress.

### Manual Runs

#### Run with Defaults (10 brands, GPT, Gentle)
1. Go to **Actions** → **Brand Shopping Story Crawler**
2. Click **Run workflow** → **Run workflow**

#### Run with Custom Parameters
1. Go to **Actions** → **Brand Shopping Story Crawler**
2. Click **Run workflow**
3. Set parameters:
   ```
   Max brands: 3
   Provider: gpt
   Strategy: gentle
   ```
4. Click **Run workflow**

#### Run via GitHub CLI
```bash
# Install GitHub CLI first: https://cli.github.com/

# Run with defaults
gh workflow run brand-shopping-story-crawler.yml

# Run with custom parameters
gh workflow run brand-shopping-story-crawler.yml \
  -f max_brands=5 \
  -f provider=gpt \
  -f strategy=gentle
```

## Monitoring

### View Workflow Run

1. Go to **Actions** tab
2. Click on the workflow run
3. Click on the **crawl-shopping-stories** job
4. Expand steps to see detailed logs

### View Summary Report

After the workflow completes, scroll to the bottom of the workflow run page to see the summary:

```
Shopping Story Crawler Results

| Metric | Value |
|--------|-------|
| Brands Processed | 10 |
| Stories Found | 47 |
| Successes | 39 |
| Failures | 8 |
| Success Rate | 83.0% |
| Total Cost | $0.092 |
```

### Download Results

1. Scroll to **Artifacts** section at the bottom of the workflow run
2. Download **shopping-story-results-XXX**
3. Extract the ZIP file to access:
   - `shopping_story_results.json` - Statistics
   - `shopping_story_images/` - Downloaded images
   - `crawler_output.log` - Full execution log

## Archived Results

If you enabled git commits (enabled by default), results are archived in:
```
crawler/cj/results_archive/results_YYYYMMDD_HHMMSS.json
```

These are committed to the repository with message:
```
chore: Add crawler results from 20250127_020015 [skip ci]
```

The `[skip ci]` tag prevents the commit from triggering another workflow run.

## Cost Estimation

### Per Run (10 brands, ~50 stories)

| Provider | Cost per Story | Total Cost | Quality |
|----------|----------------|------------|---------|
| GPT-4o Mini (default) | $0.0023 | ~$0.12 | Good |
| Claude Haiku | $0.0040 | ~$0.20 | Better |
| Gemini Flash | $0.0015 | ~$0.08 | Fast |

### Monthly Costs (Daily Runs)

| Provider | Daily | Monthly (30 days) | Notes |
|----------|-------|-------------------|-------|
| GPT-4o Mini | $0.12 | **$3.60** | Recommended |
| Claude Haiku | $0.20 | $6.00 | Higher accuracy |
| Gemini Flash | $0.08 | $2.40 | Budget option |

**GitHub Actions free tier:** 2,000 minutes/month for public repos, 500 minutes/month for private repos on free plan.

Estimated minutes per run: 120-180 minutes (2-3 hours)
- **Public repos:** ~13 runs/month free
- **Private repos:** ~3 runs/month free

## Troubleshooting

### Workflow Doesn't Start

**Check:**
1. Is GitHub Actions enabled? (Settings → Actions)
2. Is the workflow file in the correct location?
3. Is the cron schedule correct?
4. Are there any syntax errors in the YAML?

### API Key Errors

**Error:** `Error: OPENAI_API_KEY not found`

**Solution:**
1. Verify secret is added in Settings → Secrets
2. Secret name must match exactly (case-sensitive)
3. Re-add the secret if it was recently changed

### High Failure Rate

**If success rate < 70%:**
1. Check if Naver is blocking requests
2. Try running during different time of day
3. Reduce max_brands to 5 instead of 10
4. Change strategy to `gentle` if using `moderate`

### Timeout Errors

**Error:** `The job running on runner has exceeded the maximum execution time`

**Solution:**
1. Increase timeout: `timeout-minutes: 360` (6 hours)
2. Reduce brands: `max_brands: 5`
3. Split into multiple workflows for different brand groups

### Out of Free Minutes

**Solution:**
1. Reduce frequency: Run weekly instead of daily
2. Reduce brands per run
3. Upgrade to GitHub Pro for more free minutes
4. Run on self-hosted runner (free, but requires setup)

## Advanced Configuration

### Run Different Brands at Different Times

Create multiple workflow files:

**.github/workflows/crawler-cosmetics.yml**
```yaml
name: Cosmetics Brands Crawler
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM
# Modify brands.json or use --max-brands parameter
```

**.github/workflows/crawler-skincare.yml**
```yaml
name: Skincare Brands Crawler
on:
  schedule:
    - cron: '0 14 * * *'  # 2 PM
# Modify brands.json or use --max-brands parameter
```

### Conditional Runs

Only run on specific branches:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'
  push:
    branches:
      - main  # Only run on main branch
```

### Slack/Discord Notifications

Add notification step:

```yaml
- name: Send Slack notification
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'Crawler completed with ${{ env.SUCCESS_RATE }}% success rate'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Matrix Strategy (Multiple Providers in Parallel)

```yaml
strategy:
  matrix:
    provider: [gpt, claude, gemini]

steps:
  - name: Run crawler
    run: |
      python brand_shopping_story_crawler.py \
        --max-brands 3 \
        --provider ${{ matrix.provider }}
```

## Security Best Practices

1. **Never commit API keys** to the repository
2. **Use GitHub Secrets** for all sensitive data
3. **Limit workflow permissions** to minimum required
4. **Review workflow logs** for exposed secrets
5. **Rotate API keys** regularly
6. **Use dependabot** for dependency updates

## Maintenance

### Weekly Tasks
- [ ] Review workflow run logs
- [ ] Check success rates
- [ ] Monitor API costs
- [ ] Download and analyze results

### Monthly Tasks
- [ ] Archive old artifacts
- [ ] Review and optimize schedule
- [ ] Update dependencies
- [ ] Audit API key usage

### Quarterly Tasks
- [ ] Review crawler performance
- [ ] Optimize delay strategies
- [ ] Update brand list
- [ ] Rotate API keys

## Sample GitHub Actions Run Output

```
Run brand shopping story crawler
  Running crawler with:
    Max brands: 10
    Provider: gpt
    Strategy: gentle

  ╔══════════════════════════════════════════════════════════════════╗
  ║          Brand Shopping Story Crawler                            ║
  ╚══════════════════════════════════════════════════════════════════╝

  📋 Loaded 10 brands:
    - 설화수 (SULWHASOO)
    - 라네즈 (LANEIGE)
    ...

  ======================================================================
  BRAND 1/10
  ======================================================================

  ✓ Found 5 shopping stories for SULWHASOO
  ✓ Success: Story 1 processed (Cost: $0.002995)
  ...

  ======================================================================
  FINAL SUMMARY
  ======================================================================

  Brands processed: 10/10
  Shopping stories found: 47
  Shopping stories processed: 47
  Successes: 39
  Failures: 8
  Total cost: $0.092450
```

## Support

For issues with:
- **GitHub Actions setup**: Check GitHub documentation
- **Crawler functionality**: See main README.md
- **API issues**: Contact respective API providers

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Encrypted Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Cron Schedule Expression](https://crontab.guru/)
