# Quick Deployment Checklist

## Overview
This checklist guides you through deploying the AI CS System to production using Netlify for the frontend.

---

## Phase 1: Database Setup ✅

### Option A: Use Existing Supabase (Recommended)
- [ ] Login to Supabase: https://app.supabase.com
- [ ] Verify database is running
- [ ] Note down connection details from **Settings** → **Database**
- [ ] Ensure all tables are created (run schema if needed)

### Option B: New Database on Render
- [ ] Create account on Render.com
- [ ] Create new PostgreSQL database
- [ ] Note down internal database URL
- [ ] Import schema: `psql $DATABASE_URL -f database/schema.sql`

**Status**: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Phase 2: Backend Deployment 🚀

### Choose Your Backend Host
- [ ] **Render.com** (Recommended - Free tier available)
- [ ] **Railway.app** (Alternative - Free tier)
- [ ] **Fly.io** (Alternative - Free tier)

### Deploy to Render (Recommended)

1. **Create Account**
   - [ ] Sign up at https://render.com
   - [ ] Connect your GitHub account

2. **Create Web Service**
   - [ ] Click **New** → **Web Service**
   - [ ] Connect to your `ai_cs` repository
   - [ ] Configure:
     - Name: `ai-cs-backend`
     - Region: Choose closest to you
     - Branch: `main`
     - Root Directory: `backend`
     - Runtime: `Node`
     - Build Command: `npm install`
     - Start Command: `npm start`
     - Plan: `Free`

3. **Set Environment Variables**
   - [ ] `NODE_ENV` = `production`
   - [ ] `PORT` = `3000`
   - [ ] `DATABASE_URL` = `[Your PostgreSQL connection string]`
   - [ ] `JWT_SECRET` = `[Generate random 32+ char string]`
   - [ ] `SUPABASE_URL` = `[Your Supabase URL]`
   - [ ] `SUPABASE_ANON_KEY` = `[Your Supabase anon key]`
   - [ ] `REDIS_HOST` = `[Optional - leave empty for now]`
   - [ ] `REDIS_PORT` = `6379`

4. **Deploy and Test**
   - [ ] Click **Create Web Service**
   - [ ] Wait for deployment (5-10 minutes)
   - [ ] **Copy the backend URL** (e.g., `https://ai-cs-backend.onrender.com`)
   - [ ] Test health endpoint: `curl https://your-backend-url.onrender.com/health`
   - [ ] Expected response: `{"success":true,"message":"Server is healthy"}`

**Backend URL**: `_________________________________`

**Status**: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Phase 3: Update Backend CORS 🔒

1. **Update CORS Configuration**
   - [ ] Edit `backend/src/server.js`
   - [ ] Add your Netlify domain to CORS origins
   - [ ] Commit changes:
     ```bash
     git add backend/src/server.js
     git commit -m "Update CORS for Netlify deployment"
     git push
     ```
   - [ ] Wait for backend to redeploy automatically

**Status**: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Phase 4: Frontend Deployment (Netlify) 🌐

### Prepare Frontend

1. **Create Production Environment File**
   - [ ] Copy `.env.production.example` to `.env.production`
   - [ ] Update `REACT_APP_API_URL` with your backend URL from Phase 2
   - [ ] Example: `REACT_APP_API_URL=https://ai-cs-backend.onrender.com`

2. **Test Build Locally** (Optional but recommended)
   ```bash
   cd frontend
   npm install
   npm run build
   # Verify build/static/ folder is created
   ```
   - [ ] Build completes without errors
   - [ ] `frontend/build` folder is created

### Deploy to Netlify

**Option A: Via Netlify UI (Easiest)**

1. **Login to Netlify**
   - [ ] Go to https://app.netlify.com
   - [ ] Sign up or login (GitHub OAuth recommended)

2. **Import Project**
   - [ ] Click **Add new site** → **Import an existing project**
   - [ ] Choose **GitHub** (or your Git provider)
   - [ ] Authorize Netlify to access your repositories
   - [ ] Select the `ai_cs` repository

3. **Configure Build Settings**
   - [ ] **Branch to deploy**: `main`
   - [ ] **Build command**: `cd frontend && npm install && npm run build`
   - [ ] **Publish directory**: `frontend/build`
   - [ ] **Builds**: Advanced build settings → Add environment variables:
     - Variable: `REACT_APP_API_URL`
     - Value: `[Your backend URL from Phase 2]`
   - [ ] Click **Deploy site**

4. **Wait for Deployment**
   - [ ] Monitor build logs (usually 2-5 minutes)
   - [ ] Look for "Site is live" message
   - [ ] **Copy your Netlify URL** (e.g., `https://funny-name-123456.netlify.app`)

**Option B: Via Netlify CLI**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy
cd /home/long/ai_cs
netlify deploy --prod

# Follow prompts and wait for deployment
```

**Netlify URL**: `_________________________________`

**Status**: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Phase 5: Post-Deployment Verification ✓

### Test Frontend

1. **Access Your Site**
   - [ ] Open your Netlify URL in browser
   - [ ] Verify homepage loads without errors

2. **Test Login**
   - [ ] Go to login page
   - [ ] Try logging in with test credentials:
     - Username: `agent001`
     - Password: `agent001`
   - [ ] Login should succeed and redirect to dashboard

3. **Test Dashboard**
   - [ ] Dashboard loads
   - [ ] Statistics are displayed
   - [ ] Charts render correctly

4. **Test Event Search**
   - [ ] Navigate to Search/Events page
   - [ ] Try searching for events
   - [ ] Verify results are displayed

5. **Check Browser Console**
   - [ ] Open DevTools (F12)
   - [ ] Check Console tab - should have no CORS errors
   - [ ] Check Network tab - API calls should succeed (status 200)

### Common Issues

**If login fails:**
- [ ] Check browser console for error messages
- [ ] Verify `REACT_APP_API_URL` is set correctly in Netlify
- [ ] Verify backend is running: `curl https://your-backend-url/health`
- [ ] Check backend logs in Render dashboard

**If you see CORS errors:**
- [ ] Verify backend CORS includes your Netlify URL
- [ ] Redeploy backend after updating CORS
- [ ] Clear browser cache and try again

**If build fails on Netlify:**
- [ ] Check Netlify build logs for specific errors
- [ ] Verify build command is correct
- [ ] Verify publish directory is `frontend/build`
- [ ] Check that `netlify.toml` exists in repo root

**Status**: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Phase 6: Optional Enhancements 🎨

### Custom Domain (Optional)

1. **Configure Custom Domain**
   - [ ] Go to Netlify **Site settings** → **Domain management**
   - [ ] Click **Add custom domain**
   - [ ] Follow DNS configuration instructions
   - [ ] Wait for SSL certificate (automatic, ~1-2 hours)

**Custom Domain**: `_________________________________`

### Analytics (Optional)

1. **Enable Netlify Analytics** (Paid)
   - [ ] Go to Netlify **Site settings** → **Analytics**
   - [ ] Enable analytics ($9/month)

2. **Or Add Google Analytics** (Free)
   - [ ] Create GA4 property
   - [ ] Add tracking code to `frontend/public/index.html`
   - [ ] Redeploy frontend

### Error Monitoring (Optional)

1. **Set up Sentry**
   - [ ] Create account at https://sentry.io
   - [ ] Create new React project
   - [ ] Add Sentry DSN to frontend
   - [ ] Redeploy

**Status**: ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## Phase 7: Crawler Deployment (Future) 🤖

*The Python crawler can be deployed separately when needed*

**Options:**
- PythonAnywhere (easiest for Python)
- Google Cloud Run (serverless)
- Railway (if using for backend)
- Separate VPS/server

**Status**: ⬜ Not Needed Now | ⬜ Planned | ✅ Complete

---

## Final Checklist ✅

Before marking as complete, verify:

- [x] Database is accessible and has data
- [x] Backend is deployed and healthy
- [x] Backend health endpoint responds
- [x] Frontend builds successfully
- [x] Frontend is deployed to Netlify
- [x] Frontend loads in browser
- [x] User can login successfully
- [x] Dashboard displays correctly
- [x] API calls work (no CORS errors)
- [x] HTTPS is enabled (automatic on Netlify)
- [x] No console errors in browser
- [x] All routes work (no 404 on refresh)

---

## URLs Reference

| Service | URL | Status |
|---------|-----|--------|
| **Frontend (Netlify)** | `____________________` | ⬜ |
| **Backend (Render)** | `____________________` | ⬜ |
| **Database (Supabase)** | `____________________` | ⬜ |
| **Custom Domain** | `____________________` | ⬜ |

---

## Estimated Time

| Phase | Time |
|-------|------|
| Database Setup | 5-10 min |
| Backend Deployment | 15-20 min |
| Update CORS | 5 min |
| Frontend Deployment | 10-15 min |
| Testing | 10-15 min |
| **Total** | **45-65 min** |

---

## Support Resources

- **Full Guide**: `/guide/NETLIFY_DEPLOYMENT_GUIDE.md`
- **Netlify Docs**: https://docs.netlify.com
- **Render Docs**: https://render.com/docs
- **Supabase Docs**: https://supabase.com/docs

---

**Good luck with your deployment! 🚀**

**Status Overview**:
- ⬜ Not Started
- ⏳ In Progress
- ✅ Complete
- ❌ Blocked
