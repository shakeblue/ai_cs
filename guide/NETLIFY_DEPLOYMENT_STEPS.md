# Netlify Frontend Deployment - Step-by-Step

**Prerequisites**: ✅ Backend is deployed and running on Render

---

## Step 1: Prepare Frontend Environment (2 minutes)

### 1.1 Create Production Environment File

We need to tell the frontend where your backend is.

**I'll create this file for you once you provide your backend URL.**

The file will be: `frontend/.env.production`

```env
# Backend API URL from Render
REACT_APP_API_URL=https://your-backend-url.onrender.com/api

# Environment
REACT_APP_ENV=production
```

⚠️ **Important**: The URL must end with `/api` since that's your API base path!

---

## Step 2: Deploy to Netlify (10 minutes)

### Option A: Deploy via Netlify UI (Recommended - Easiest)

#### 2.1 Create Netlify Account

1. Go to https://app.netlify.com
2. Click **Sign up**
3. Choose **Sign up with GitHub** (recommended)
4. Authorize Netlify to access your repositories

#### 2.2 Import Project

1. Click **Add new site** → **Import an existing project**
2. Choose **Deploy with GitHub**
3. Authorize Netlify if prompted
4. Search and select: `shakeblue/ai_cs`
5. Click **Install** (if first time) or **Connect**

#### 2.3 Configure Build Settings

**Fill in these values:**

| Setting | Value |
|---------|-------|
| **Branch to deploy** | `main` |
| **Base directory** | Leave empty |
| **Build command** | `cd frontend && npm install && npm run build` |
| **Publish directory** | `frontend/build` |

#### 2.4 Add Environment Variables

1. Click **Show advanced** → **New variable**
2. Add this variable:

```
Key:   REACT_APP_API_URL
Value: https://your-backend-url.onrender.com/api
```

⚠️ **Replace with your actual backend URL + /api at the end!**

#### 2.5 Deploy

1. Click **Deploy site**
2. Netlify will assign a random name like: `amazing-lovelace-123456.netlify.app`
3. Wait 3-5 minutes for build

#### 2.6 Monitor Build

Click on the deploying site to see build logs:

**Expected output:**
```
Building
────────
npm install
npm run build
Creating optimized production build...
Compiled successfully!
Build complete
────────
Deploy complete!
```

#### 2.7 Get Your Frontend URL

Once deployed, you'll see:
```
🎉 Site is live!
https://your-site-name.netlify.app
```

**Copy this URL!**

---

### Option B: Deploy via Netlify CLI (Advanced)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Navigate to project root
cd /home/long/ai_cs

# Initialize Netlify (first time)
netlify init

# Follow prompts:
# - Create & configure a new site
# - Team: Choose your team
# - Site name: ai-cs-frontend (or your choice)
# - Build command: cd frontend && npm install && npm run build
# - Publish directory: frontend/build

# Deploy to production
netlify deploy --prod

# Set environment variable (in Netlify UI after deploy)
```

---

## Step 3: Test Your Deployment (5 minutes)

### 3.1 Open Your Site

Click the Netlify URL or open in browser:
```
https://your-site.netlify.app
```

**Expected**: Login page loads

### 3.2 Test Login

Use test credentials:
```
Username: agent001
Password: agent001
```

**Expected**:
- Login succeeds
- Redirects to dashboard
- Dashboard shows statistics and charts

### 3.3 Check Browser Console

1. Press **F12** to open DevTools
2. Go to **Console** tab
3. **Expected**: No errors, especially no CORS errors

### 3.4 Test API Calls

1. Open **Network** tab in DevTools
2. Refresh the page
3. Look for API calls to your backend
4. **Expected**: All API calls show Status 200 (green)

### 3.5 Test All Features

- [ ] Dashboard loads with data
- [ ] Search/Events page works
- [ ] Can view event details
- [ ] No console errors

---

## Troubleshooting

### Issue: Build Fails - "Command not found"

**Error in logs:**
```
npm: command not found
```

**Fix:**
1. Verify build command: `cd frontend && npm install && npm run build`
2. Check Node version in **Build settings**
3. Add environment variable: `NODE_VERSION=18`

### Issue: Build Fails - "react-scripts: not found"

**Error:**
```
react-scripts: command not found
```

**Fix:**
1. Build command should include `npm install`
2. Full command: `cd frontend && npm install && npm run build`

### Issue: Build Succeeds but Shows Blank Page

**Symptoms:**
- Site loads but shows white screen
- Console shows errors

**Check:**
1. Open browser console (F12)
2. Look for specific errors
3. Common causes:
   - Missing environment variable
   - Wrong build directory
   - JavaScript errors

**Fix:**
1. Verify publish directory is `frontend/build` (not just `build`)
2. Check `REACT_APP_API_URL` is set in Netlify environment variables
3. Trigger new deploy: **Deploys** → **Trigger deploy** → **Deploy site**

### Issue: CORS Errors in Console

**Error:**
```
Access to fetch at 'https://backend.onrender.com/api/...'
from origin 'https://your-site.netlify.app' has been blocked by CORS
```

**Fix:**
1. Your backend CORS is already configured for `*.netlify.app`
2. If still failing, check backend logs in Render
3. Verify backend is running: `curl https://backend-url/health`
4. May need to redeploy backend if CORS was updated

### Issue: API Calls Return 404

**Symptoms:**
- Login fails
- Data doesn't load
- Network tab shows 404 errors

**Fix:**
1. Verify `REACT_APP_API_URL` ends with `/api`
2. Check backend is running
3. Test backend directly: `curl https://backend-url/api/events/search`

### Issue: Environment Variables Not Working

**Symptoms:**
- `process.env.REACT_APP_API_URL` is undefined
- App tries to connect to localhost

**Fix:**
1. Environment variables MUST start with `REACT_APP_`
2. Set in **Site settings** → **Environment variables**
3. After adding/changing variables, **trigger new deploy**
4. Clear deploy cache: **Deploys** → **Trigger deploy** → **Clear cache and deploy**

### Issue: Routes Show 404 on Refresh

**Symptoms:**
- Dashboard works when navigating from home
- Refreshing `/dashboard` shows 404

**Fix:**
This should be handled by `netlify.toml` (already created).

**Verify:**
1. `netlify.toml` exists in project root
2. Contains redirect rule: `from = "/*"` → `to = "/index.html"`
3. Redeploy if needed

---

## Post-Deployment

### Update Site Name (Optional)

1. Go to **Site settings** → **General** → **Site details**
2. Click **Change site name**
3. Enter new name: `ai-cs-system` (must be unique)
4. Your URL becomes: `https://ai-cs-system.netlify.app`

### Add Custom Domain (Optional)

1. **Site settings** → **Domain management**
2. Click **Add custom domain**
3. Enter your domain: `app.yourdomain.com`
4. Follow DNS setup instructions
5. SSL certificate auto-provisions (1-2 hours)

### Enable Deploy Notifications

1. **Site settings** → **Build & deploy** → **Deploy notifications**
2. Add notifications:
   - Email on deploy success
   - Email on deploy failure
   - Slack webhook (optional)

### Set Up Branch Deploys

**Production** (main branch):
- Deploys to: `https://your-site.netlify.app`

**Preview** (feature branches):
- Deploys to: `https://branch-name--your-site.netlify.app`

**Configure:**
1. **Site settings** → **Build & deploy** → **Branches**
2. Enable **Branch deploys**
3. Choose: **All branches** or **Specific branches**

---

## Success Checklist

- [ ] Netlify account created
- [ ] Repository connected
- [ ] Build settings configured correctly
- [ ] `REACT_APP_API_URL` environment variable set
- [ ] Build completed successfully
- [ ] Site is live
- [ ] Frontend URL copied
- [ ] Login works
- [ ] Dashboard loads with data
- [ ] No CORS errors
- [ ] All routes work

---

## Your Deployment URLs

| Service | URL | Status |
|---------|-----|--------|
| **Backend (Render)** | `______________________` | ✅ |
| **Frontend (Netlify)** | `______________________` | ⬜ |

---

## Next Steps

After frontend deployment:

1. ✅ **Test the full application**
2. ⬜ **Optional: Add custom domain**
3. ⬜ **Optional: Set up monitoring/analytics**
4. ⬜ **Optional: Deploy crawler (later)**

---

## Quick Reference

### Netlify Dashboard
https://app.netlify.com

### Build Logs
Netlify Dashboard → Your site → **Deploys** → Click latest deploy

### Environment Variables
Netlify Dashboard → Your site → **Site settings** → **Environment variables**

### Trigger Deploy
Netlify Dashboard → Your site → **Deploys** → **Trigger deploy**

---

**You're almost done! Let's deploy the frontend! 🚀**
