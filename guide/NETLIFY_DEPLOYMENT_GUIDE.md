# Netlify Deployment Guide - AI CS System

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Prerequisites](#prerequisites)
- [Frontend Deployment to Netlify](#frontend-deployment-to-netlify)
- [Backend Deployment Options](#backend-deployment-options)
- [Environment Configuration](#environment-configuration)
- [Deployment Steps](#deployment-steps)
- [Post-Deployment Configuration](#post-deployment-configuration)
- [Troubleshooting](#troubleshooting)
- [Monitoring & Maintenance](#monitoring--maintenance)

---

## Architecture Overview

### What Can Be Deployed to Netlify?
- **Frontend (React)**: ✅ **YES** - Perfect fit for Netlify
- **Backend (Node.js/Express)**: ⚠️ **NO** - Needs separate hosting (see alternatives below)
- **Database (PostgreSQL)**: ❌ **NO** - Needs database hosting service
- **Crawler (Python)**: ❌ **NO** - Needs server/container hosting

### Deployment Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         Netlify                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Frontend (React SPA)                                      │  │
│  │  - Static files from /frontend/build                       │  │
│  │  - CDN distribution globally                               │  │
│  │  - HTTPS automatically configured                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ REST API calls
┌──────────────────────────┴──────────────────────────────────────┐
│              Backend Hosting (Render/Railway/Heroku)             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Node.js/Express API Server                                │  │
│  │  - /backend code                                           │  │
│  │  - Port 3000 or dynamic PORT                               │  │
│  └───────────────────────┬───────────────────────────────────┘  │
└────────────────────────────┼──────────────────────────────────────┘
                             │
┌────────────────────────────┴──────────────────────────────────────┐
│              Database (Supabase/Neon/Railway)                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL Database                                       │  │
│  │  - Events, Users, Channels, etc.                           │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                             │
┌────────────────────────────┴──────────────────────────────────────┐
│              Crawler Hosting (PythonAnywhere/Cloud Run)           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Python Crawler System                                     │  │
│  │  - Scheduled jobs for web scraping                         │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### 1. Accounts Required
- **Netlify Account**: https://netlify.com (free tier available)
- **Backend Hosting** (choose one):
  - **Render.com** (Recommended, free tier): https://render.com
  - **Railway.app** (Free tier): https://railway.app
  - **Heroku** (Paid plans only): https://heroku.com
  - **Fly.io** (Free tier): https://fly.io
- **Database Hosting** (choose one):
  - **Supabase** (Already integrated, free tier): https://supabase.com
  - **Neon** (Free PostgreSQL): https://neon.tech
  - **Railway** (if using Railway for backend)
- **Git Repository**: GitHub, GitLab, or Bitbucket

### 2. Local Setup
```bash
# Install Netlify CLI (optional but recommended)
npm install -g netlify-cli

# Verify installation
netlify --version
```

---

## Frontend Deployment to Netlify

### Step 1: Create netlify.toml Configuration

Create a file at the project root (`/home/long/ai_cs/netlify.toml`):

```toml
# Netlify Build Configuration
[build]
  # Build command
  command = "cd frontend && npm install && npm run build"

  # Publish directory (where the built files are)
  publish = "frontend/build"

  # Functions directory (optional, for serverless functions)
  # functions = "netlify/functions"

# Environment variables (set in Netlify UI instead for security)
# [build.environment]
#   NODE_VERSION = "18"

# Redirects and rewrites for Single Page Application
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
  force = false

# Headers for security and caching
[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-XSS-Protection = "1; mode=block"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"

# Cache static assets
[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

# Cache images
[[headers]]
  for = "/*.png"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.jpg"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

### Step 2: Configure Frontend Environment Variables

Create `/home/long/ai_cs/frontend/.env.production`:

```env
# Backend API URL (will be replaced with actual backend URL after deployment)
REACT_APP_API_URL=https://your-backend-url.onrender.com

# Other environment variables
REACT_APP_ENV=production
```

### Step 3: Update Frontend API Configuration

Update `/home/long/ai_cs/frontend/src/api/axios.js` to use environment variable:

```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001';

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// ... rest of the file
```

### Step 4: Deploy to Netlify

#### Option A: Deploy via Netlify UI (Recommended)

1. **Login to Netlify**: https://app.netlify.com
2. **Click "Add new site"** → "Import an existing project"
3. **Connect to Git provider** (GitHub/GitLab/Bitbucket)
4. **Select your repository**: `ai_cs`
5. **Configure build settings**:
   - **Branch to deploy**: `main`
   - **Build command**: `cd frontend && npm install && npm run build`
   - **Publish directory**: `frontend/build`
   - **Advanced build settings** → **New variable**:
     - Key: `REACT_APP_API_URL`
     - Value: `https://your-backend-url.onrender.com` (add after backend deployment)
6. **Click "Deploy site"**

#### Option B: Deploy via Netlify CLI

```bash
# Login to Netlify
netlify login

# Initialize Netlify site
cd /home/long/ai_cs
netlify init

# Follow prompts:
# - Create & configure a new site
# - Choose your team
# - Site name: ai-cs-system (or your preferred name)
# - Build command: cd frontend && npm install && npm run build
# - Publish directory: frontend/build

# Deploy
netlify deploy --prod

# Or for preview deployment
netlify deploy
```

### Step 5: Configure Custom Domain (Optional)

1. Go to **Site settings** → **Domain management**
2. Click **Add custom domain**
3. Follow DNS configuration instructions
4. Netlify will automatically provision SSL certificate

---

## Backend Deployment Options

Since Netlify doesn't support full Node.js servers, deploy the backend separately.

### Recommended: Deploy Backend to Render.com

#### Step 1: Create render.yaml

Create `/home/long/ai_cs/render.yaml`:

```yaml
services:
  # Backend API Service
  - type: web
    name: ai-cs-backend
    env: node
    region: oregon
    plan: free
    buildCommand: cd backend && npm install
    startCommand: cd backend && npm start
    envVars:
      - key: NODE_ENV
        value: production
      - key: PORT
        value: 3000
      - key: DATABASE_URL
        fromDatabase:
          name: ai-cs-db
          property: connectionString
      - key: JWT_SECRET
        generateValue: true
      - key: REDIS_HOST
        sync: false
      - key: REDIS_PORT
        value: 6379
    healthCheckPath: /health

# PostgreSQL Database
databases:
  - name: ai-cs-db
    plan: free
    databaseName: cosmetic_consultation_system
    user: cs_user
```

#### Step 2: Deploy to Render

1. **Login to Render**: https://dashboard.render.com
2. **New** → **Blueprint**
3. **Connect repository** and select `ai_cs`
4. Render will automatically detect `render.yaml` and create services
5. **Add environment variables** in Render dashboard:
   - `JWT_SECRET`: Generate a secure random string
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_ANON_KEY`: Your Supabase anon key
6. **Deploy**

#### Step 3: Get Backend URL

After deployment, Render provides a URL like:
```
https://ai-cs-backend.onrender.com
```

### Alternative: Deploy Backend to Railway

1. **Login to Railway**: https://railway.app
2. **New Project** → **Deploy from GitHub repo**
3. **Select** `ai_cs` repository
4. **Configure**:
   - **Root directory**: `backend`
   - **Build command**: `npm install`
   - **Start command**: `npm start`
5. **Add PostgreSQL database** from Railway marketplace
6. **Set environment variables**
7. **Deploy**

### Alternative: Deploy Backend to Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Initialize and deploy
cd /home/long/ai_cs/backend
flyctl launch

# Follow prompts and deploy
flyctl deploy
```

---

## Environment Configuration

### Frontend Environment Variables (Netlify)

Set in **Netlify Dashboard** → **Site settings** → **Environment variables**:

| Variable | Value | Description |
|----------|-------|-------------|
| `REACT_APP_API_URL` | `https://your-backend.onrender.com` | Backend API URL |
| `REACT_APP_ENV` | `production` | Environment |
| `NODE_VERSION` | `18` | Node.js version for build |

### Backend Environment Variables (Render/Railway)

Set in backend hosting dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `NODE_ENV` | `production` | Environment |
| `PORT` | `3000` (or dynamic) | Server port |
| `DATABASE_URL` | From database service | PostgreSQL connection |
| `JWT_SECRET` | Random secure string | JWT signing secret |
| `REDIS_HOST` | Redis host (optional) | Redis cache host |
| `REDIS_PORT` | `6379` | Redis port |
| `SUPABASE_URL` | Your Supabase URL | Supabase project URL |
| `SUPABASE_ANON_KEY` | Your Supabase key | Supabase anon key |

---

## Deployment Steps

### Complete Deployment Workflow

#### Step 1: Deploy Database First

**Option A: Use Supabase (Already Configured)**
1. Login to Supabase: https://app.supabase.com
2. Your database is already running
3. Get connection string from **Settings** → **Database**

**Option B: Use Render PostgreSQL**
1. Create new PostgreSQL database on Render
2. Import schema:
```bash
# Download connection string from Render
psql $DATABASE_URL -f /home/long/ai_cs/database/schema.sql
```

#### Step 2: Deploy Backend

1. **Choose hosting provider** (Render recommended)
2. **Connect repository**
3. **Configure environment variables**
4. **Deploy**
5. **Test backend**:
```bash
curl https://your-backend-url.onrender.com/health
```
6. **Note the backend URL** for frontend configuration

#### Step 3: Update Backend CORS

Before deploying frontend, update `/home/long/ai_cs/backend/src/server.js` CORS to include your Netlify URL:

```javascript
const _v_cors_options = {
  origin: [
    'http://localhost:3000',
    'http://localhost:3001',
    'https://ai-cs-bf933.web.app',
    'https://ai-cs-bf933.firebaseapp.com',
    'https://aics1.netlify.app',  // Your production Netlify URL
    'https://*.netlify.app',  // All Netlify preview deployments
  ],
  credentials: true,
  optionsSuccessStatus: 200,
};
```

Commit and push this change so backend redeploys with new CORS settings.

#### Step 4: Deploy Frontend to Netlify

1. **Add backend URL** to Netlify environment variables:
   - `REACT_APP_API_URL` = `https://your-backend-url.onrender.com`
2. **Deploy via Netlify UI or CLI** (see above)
3. **Wait for build** (usually 2-5 minutes)
4. **Get Netlify URL**: e.g., `https://ai-cs-system.netlify.app`

#### Step 5: Deploy Crawler (Optional)

**Option A: Use PythonAnywhere**
1. Upload crawler code
2. Set up scheduled tasks
3. Configure database connection

**Option B: Use Google Cloud Run**
```bash
# Build and deploy
gcloud run deploy ai-cs-crawler \
  --source ./crawler \
  --platform managed \
  --region us-central1
```

#### Step 6: Verify Deployment

```bash
# Test frontend
curl https://your-site.netlify.app

# Test backend health
curl https://your-backend.onrender.com/health

# Test API through frontend
# Open browser and test login
```

---

## Post-Deployment Configuration

### 1. Update DNS (if using custom domain)

```
# Netlify DNS settings
Type: A
Name: @
Value: 75.2.60.5

Type: CNAME
Name: www
Value: your-site.netlify.app
```

### 2. Enable HTTPS (Automatic on Netlify)

Netlify automatically provisions SSL certificates via Let's Encrypt.

### 3. Configure Redirects for SPA

Already configured in `netlify.toml`:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### 4. Set up Deploy Hooks (Optional)

Create deploy hooks in Netlify to trigger builds:
1. **Site settings** → **Build & deploy** → **Build hooks**
2. **Add build hook**: Name it "Backend Deploy Trigger"
3. Use the webhook URL in your CI/CD pipeline

### 5. Configure Branch Deploys

- **Production**: `main` branch → `https://your-site.netlify.app`
- **Preview**: Feature branches → `https://feature--your-site.netlify.app`

---

## Troubleshooting

### Issue 1: Build Fails on Netlify

**Symptoms**: Build logs show npm install errors

**Solutions**:
```bash
# Check Node version
# In netlify.toml, set:
[build.environment]
  NODE_VERSION = "18"

# Or in Netlify UI: Environment variables
NODE_VERSION = 18
```

### Issue 2: API Calls Fail (CORS Errors)

**Symptoms**: Browser console shows CORS errors

**Solutions**:
1. Verify backend CORS includes Netlify URL
2. Check `REACT_APP_API_URL` environment variable in Netlify
3. Ensure backend is deployed and healthy
4. Check browser DevTools → Network tab for actual API URL

### Issue 3: Environment Variables Not Working

**Symptoms**: `process.env.REACT_APP_API_URL` is undefined

**Solutions**:
1. In Netlify, go to **Site settings** → **Environment variables**
2. Variables MUST start with `REACT_APP_` prefix
3. After adding variables, **trigger a new deploy**
4. Clear deploy cache: **Deploys** → **Trigger deploy** → **Clear cache and deploy**

### Issue 4: Routes Return 404

**Symptoms**: Refreshing `/dashboard` returns 404

**Solutions**:
This is already configured in `netlify.toml`:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

If still failing:
1. Verify `netlify.toml` is in repository root
2. Check publish directory is `frontend/build`
3. Verify `build` folder contains `index.html`

### Issue 5: Backend Connection Timeout

**Symptoms**: API requests timeout

**Solutions**:
1. Check backend logs in Render/Railway dashboard
2. Verify database connection is configured
3. Check backend health endpoint: `https://backend-url/health`
4. Ensure backend is not in sleep mode (free tier services sleep after inactivity)
5. In Render free tier, first request after sleep takes ~30 seconds

### Issue 6: Images/Assets Not Loading

**Symptoms**: Static assets return 404

**Solutions**:
1. Verify build command includes `npm run build`
2. Check `frontend/build/static` folder exists after build
3. Review Netlify deploy logs for file structure
4. Ensure assets are referenced with relative paths in React

---

## Monitoring & Maintenance

### 1. Monitor Deploys

- **Netlify Dashboard**: https://app.netlify.com/sites/your-site/deploys
- **Build logs**: Available for each deploy
- **Deploy notifications**: Configure in **Site settings** → **Build & deploy** → **Deploy notifications**

### 2. Monitor Backend

- **Render Dashboard**: https://dashboard.render.com
- **Logs**: Real-time logs for debugging
- **Metrics**: CPU, memory, response times

### 3. Performance Monitoring

**Netlify Analytics** (Paid):
- Page views
- Bandwidth usage
- Top pages
- Unique visitors

**Google Analytics** (Free):
Add to `frontend/public/index.html`:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### 4. Backup Strategy

**Database Backups**:
- **Supabase**: Automatic daily backups (paid plans)
- **Render**: Automatic backups on paid plans
- **Manual**: Use `pg_dump` regularly

```bash
# Manual PostgreSQL backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
```

### 5. Update Dependencies

```bash
# Frontend
cd frontend
npm outdated
npm update

# Backend
cd backend
npm outdated
npm update
```

### 6. Cache Management

**Clear Netlify Deploy Cache**:
1. **Deploys** → **Trigger deploy** → **Clear cache and deploy**

**Clear CDN Cache**:
1. **Post processing** → **Asset optimization** → **Clear cache**

---

## Cost Estimates

### Free Tier Deployment

| Service | Tier | Cost | Limits |
|---------|------|------|--------|
| **Netlify** | Free | $0/month | 100GB bandwidth, 300 build minutes |
| **Render** | Free | $0/month | 750 hours/month, sleeps after inactivity |
| **Supabase** | Free | $0/month | 500MB database, 1GB bandwidth |
| **Total** | - | **$0/month** | Suitable for development/testing |

### Production Tier Deployment

| Service | Tier | Cost | Features |
|---------|------|------|----------|
| **Netlify** | Pro | $19/month | 1TB bandwidth, unlimited build minutes |
| **Render** | Starter | $7/month | Always-on, 512MB RAM |
| **Supabase** | Pro | $25/month | 8GB database, 50GB bandwidth |
| **Total** | - | **$51/month** | Production-ready |

---

## Quick Reference Commands

```bash
# Local build test
cd frontend
npm install
npm run build

# Deploy frontend to Netlify
netlify deploy --prod

# Test backend locally
cd backend
npm run dev

# Check Netlify site status
netlify status

# View Netlify logs
netlify logs

# Open Netlify dashboard
netlify open

# Link local repo to Netlify site
netlify link
```

---

## Additional Resources

- **Netlify Documentation**: https://docs.netlify.com
- **Render Documentation**: https://render.com/docs
- **Railway Documentation**: https://docs.railway.app
- **Supabase Documentation**: https://supabase.com/docs
- **Create React App Deployment**: https://create-react-app.dev/docs/deployment

---

## Deployment Checklist

### Pre-Deployment
- [ ] Database is deployed and accessible
- [ ] Database schema is imported
- [ ] Backend is deployed and healthy
- [ ] Backend CORS includes Netlify URL
- [ ] Environment variables are configured
- [ ] `netlify.toml` is created
- [ ] Frontend `.env.production` is configured

### Deployment
- [ ] Frontend builds successfully locally
- [ ] Netlify site is created
- [ ] Build settings are configured
- [ ] Environment variables are set in Netlify
- [ ] Deploy is triggered
- [ ] Build completes successfully

### Post-Deployment
- [ ] Frontend loads in browser
- [ ] Login functionality works
- [ ] API calls succeed
- [ ] Dashboard displays data
- [ ] All routes work (no 404s)
- [ ] HTTPS is enabled
- [ ] Custom domain configured (if applicable)
- [ ] Analytics configured (if applicable)

---

## Support

For deployment issues:
1. Check Netlify deploy logs
2. Check backend logs in hosting provider dashboard
3. Verify environment variables
4. Test API endpoints directly with curl/Postman
5. Check browser DevTools console and network tab

---

**Last Updated**: 2025-12-24
**Author**: AI DevKit Team
