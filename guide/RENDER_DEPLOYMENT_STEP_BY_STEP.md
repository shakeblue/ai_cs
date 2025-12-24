# Render Backend Deployment - Step-by-Step Guide

**Estimated Time**: 15-20 minutes

---

## Pre-Deployment Checklist

✅ **Repository**: https://github.com/shakeblue/ai_cs.git
✅ **Database**: Supabase (already configured)
✅ **Backend Code**: Ready in `/backend` folder

---

## Step 1: Create Render Account (2 minutes)

1. **Go to**: https://render.com
2. **Click**: "Get Started" or "Sign Up"
3. **Sign up with GitHub** (recommended for easy repo access)
   - Click "Sign up with GitHub"
   - Authorize Render to access your repositories
4. **Complete profile** if prompted

✅ **Done?** You should now be at the Render Dashboard

---

## Step 2: Create PostgreSQL Database (5 minutes)

### 2.1 Decide on Database Strategy

You have **two options**:

#### Option A: Use Existing Supabase (Recommended - Already configured)
- ✅ Already have data and schema
- ✅ No additional setup needed
- ✅ Free tier suitable
- ⚠️ Will use Supabase connection string

#### Option B: Create New PostgreSQL on Render
- New fresh database
- Need to import schema
- Need to migrate data from Supabase

**👉 I recommend Option A (Use Supabase)** since it's already working.

### 2.2 If Using Supabase (Option A)

**Get your Supabase connection string:**

**Method 1: From your .env file (already have it):**
```
Database Host: yxndlrlwrcuikedvpkrj.supabase.co
```

**Method 2: From Supabase Dashboard:**
1. Go to https://app.supabase.com
2. Select your project: `yxndlrlwrcuikedvpkrj`
3. Go to **Settings** → **Database**
4. Scroll to **Connection string** → **URI**
5. Copy the connection string

**Your Supabase connection string format:**
```
postgresql://postgres:[YOUR-PASSWORD]@db.yxndlrlwrcuikedvpkrj.supabase.co:5432/postgres
```

⚠️ **Replace `[YOUR-PASSWORD]` with your actual Supabase database password**

### 2.3 If Creating New PostgreSQL on Render (Option B)

1. In Render Dashboard, click **New** → **PostgreSQL**
2. Configure:
   - **Name**: `ai-cs-database`
   - **Database**: `cosmetic_consultation_system`
   - **User**: `cs_user`
   - **Region**: Oregon (or closest to you)
   - **Plan**: Free
3. Click **Create Database**
4. Wait 2-3 minutes for provisioning
5. Copy **Internal Database URL** (starts with `postgresql://`)

---

## Step 3: Create Web Service (3 minutes)

### 3.1 Start Service Creation

1. In Render Dashboard, click **New** → **Web Service**
2. Choose **"Build and deploy from a Git repository"**
3. Click **Next**

### 3.2 Connect Repository

**If you see your repository `ai_cs`:**
- Click **Connect** next to it

**If you DON'T see it:**
1. Click **Configure account** (top right)
2. Grant Render access to the repository
3. Return and click **Connect**

### 3.3 Configure Service

Fill in these settings:

| Setting | Value |
|---------|-------|
| **Name** | `ai-cs-backend` (or your preferred name) |
| **Region** | Oregon (or closest to you) |
| **Branch** | `main` |
| **Root Directory** | `backend` |
| **Runtime** | `Node` (auto-detected) |
| **Build Command** | `npm install` |
| **Start Command** | `npm start` |
| **Instance Type** | `Free` |

⚠️ **Important**: Set **Root Directory** to `backend` since your backend code is in a subfolder!

---

## Step 4: Configure Environment Variables (5 minutes)

### 4.1 Click "Advanced" to expand environment variables section

### 4.2 Add Environment Variables

Click **Add Environment Variable** for each of these:

#### Required Variables:

```bash
# 1. Node Environment
Key: NODE_ENV
Value: production

# 2. Port (Render provides this automatically, but good to set)
Key: PORT
Value: 3000

# 3. Database URL (Choose based on your database choice)
Key: DATABASE_URL
Value: postgresql://postgres:[PASSWORD]@db.yxndlrlwrcuikedvpkrj.supabase.co:5432/postgres
# ⚠️ Replace [PASSWORD] with your actual Supabase password

# OR if using Render PostgreSQL:
# Click "Generate" button next to DATABASE_URL and select your database

# 4. Individual Database Credentials (for compatibility)
Key: DB_HOST
Value: db.yxndlrlwrcuikedvpkrj.supabase.co

Key: DB_PORT
Value: 5432

Key: DB_NAME
Value: postgres

Key: DB_USER
Value: postgres

Key: DB_PASSWORD
Value: [Your Supabase database password]

# 5. JWT Secret (IMPORTANT: Use secure random string)
Key: JWT_SECRET
Value: 92f6a1f3ff6c5508c31b04ca98a1d2700999fd2c3706c24298082484e7d8dae9
# ⚠️ Generated secure secret above - use this exactly

# 6. Supabase Configuration
Key: SUPABASE_URL
Value: https://yxndlrlwrcuikedvpkrj.supabase.co

Key: SUPABASE_ANON_KEY
Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4bmRscmx3cmN1aWtlZHZwa3JqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU4NTA5MzEsImV4cCI6MjA4MTQyNjkzMX0.3cU2cHvLNeucknp-VjEaBCV9NUL8HGsAbeq0433p4IQ

Key: SUPABASE_SECRET_KEY
Value: sb_secret_eZqCXmATq9eCiND6RZ3-dw_TxGPxStp

Key: SUPABASE_PUBLISHABLE_KEY
Value: sb_publishable_YxsJeGlIiNhhmf2fPni4xw_8KxffDXa

# 7. Redis Configuration (Optional - can skip for now)
Key: REDIS_HOST
Value: (leave empty)

Key: REDIS_PORT
Value: 6379
```

### 4.3 Quick Copy Format

For easier copying, here's the key=value format:

```bash
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.yxndlrlwrcuikedvpkrj.supabase.co:5432/postgres
DB_HOST=db.yxndlrlwrcuikedvpkrj.supabase.co
DB_PORT=5432
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=[Your Supabase password]
JWT_SECRET=92f6a1f3ff6c5508c31b04ca98a1d2700999fd2c3706c24298082484e7d8dae9
SUPABASE_URL=https://yxndlrlwrcuikedvpkrj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inl4bmRscmx3cmN1aWtlZHZwa3JqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU4NTA5MzEsImV4cCI6MjA4MTQyNjkzMX0.3cU2cHvLNeucknp-VjEaBCV9NUL8HGsAbeq0433p4IQ
SUPABASE_SECRET_KEY=sb_secret_eZqCXmATq9eCiND6RZ3-dw_TxGPxStp
SUPABASE_PUBLISHABLE_KEY=sb_publishable_YxsJeGlIiNhhmf2fPni4xw_8KxffDXa
```

⚠️ **Don't forget to replace `[PASSWORD]` with your actual Supabase database password!**

---

## Step 5: Deploy! (5-10 minutes)

### 5.1 Create Web Service

1. Scroll down and click **Create Web Service**
2. Render will start building your app

### 5.2 Monitor Build

You'll see the build logs in real-time:

**Expected log output:**
```
==> Cloning from https://github.com/shakeblue/ai_cs...
==> Checking out commit xxx in branch main
==> Using Node version 18.x
==> Running build command 'npm install'...
    Installing dependencies...
==> Build completed successfully
==> Starting service with 'npm start'...
    Server listening on port 3000
```

**Build Status:**
- 🟡 **Building**: In progress (3-7 minutes)
- 🟢 **Live**: Deploy successful!
- 🔴 **Build failed**: Check logs for errors

### 5.3 Get Your Backend URL

Once deployed, you'll see:
```
Your service is live at https://ai-cs-backend.onrender.com
```

**✅ Copy this URL - you'll need it for frontend deployment!**

---

## Step 6: Test Your Backend (2 minutes)

### 6.1 Test Health Endpoint

Open a new terminal and run:

```bash
curl https://ai-cs-backend.onrender.com/health
```

**Expected response:**
```json
{
  "success": true,
  "message": "Server is healthy",
  "timestamp": "2025-12-24T..."
}
```

### 6.2 Test API Endpoint

```bash
curl https://ai-cs-backend.onrender.com/api/events/search
```

Should return event data (or authentication error if route requires auth).

### 6.3 Check in Browser

Open in your browser:
```
https://ai-cs-backend.onrender.com
```

Should see:
```json
{
  "success": true,
  "message": "AI CS 시스템 백엔드 API 서버",
  "version": "1.0.0",
  ...
}
```

---

## Step 7: Update CORS for Netlify (2 minutes)

Your backend needs to allow requests from Netlify.

### 7.1 Edit CORS Configuration

The file `backend/src/server.js` already has Netlify configured (line 54), but let's add a wildcard to allow all Netlify preview deployments:

```javascript
const _v_cors_options = {
  origin: [
    'http://localhost:3000',
    'http://localhost:3001',
    'https://ai-cs-bf933.web.app',
    'https://ai-cs-bf933.firebaseapp.com',
    'https://aics1.netlify.app',
    'https://*.netlify.app',  // ← Add this line if not present
  ],
  credentials: true,
  optionsSuccessStatus: 200,
};
```

✅ **Good news**: This is already configured in your code! No changes needed.

---

## Troubleshooting

### Issue: Build Fails - "npm install failed"

**Check:**
1. Verify `package.json` is in the `backend` folder
2. Root Directory is set to `backend`
3. Build command is `npm install`

**Fix:**
- Check build logs for specific error
- Ensure `package.json` is valid JSON

### Issue: Build Succeeds but App Crashes

**Check Logs:**
1. Click **Logs** tab in Render dashboard
2. Look for error messages

**Common causes:**
- Database connection failed → Check DATABASE_URL
- Missing environment variables → Verify all vars are set
- Port binding issue → Ensure app uses `process.env.PORT`

**Your server.js already handles this correctly:**
```javascript
const _v_port = process.env.PORT || 3000;
```

### Issue: Database Connection Failed

**Error in logs:**
```
Error: connect ECONNREFUSED
FATAL: password authentication failed
```

**Fix:**
1. Verify DATABASE_URL is correct
2. Check Supabase password is correct
3. Ensure Supabase project is active (not paused)
4. Go to Supabase → Settings → Database → Check connection pooling

### Issue: Health Endpoint Returns 404

**Possible causes:**
1. Server not fully started yet (wait 30 seconds)
2. Routes not properly loaded

**Check:**
```bash
# Check server logs in Render dashboard
# Should see: "Server listening on port 3000"
```

### Issue: "This service is not responding"

**Free tier limitation:**
- Render free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds to wake up
- Subsequent requests are fast

**Solutions:**
1. Wait 30-60 seconds and try again
2. Upgrade to paid tier ($7/mo) for always-on
3. Use a cron job to ping every 10 minutes (keeps it awake)

---

## Post-Deployment

### Monitor Your Service

**View Logs:**
1. Render Dashboard → Your service → **Logs** tab
2. Real-time logs for debugging

**View Metrics:**
1. **Metrics** tab shows:
   - CPU usage
   - Memory usage
   - Response times
   - Request counts

### Auto-Deploys

Render automatically deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update backend"
git push

# Render detects the push and automatically deploys
```

**Disable auto-deploy:**
1. Service settings → **Build & Deploy**
2. Toggle off "Auto-Deploy"

### Environment Variable Updates

**To update env vars:**
1. Service → **Environment** tab
2. Edit values
3. Click **Save Changes**
4. Render will automatically restart service

---

## Success Checklist

- [ ] Render account created
- [ ] Repository connected
- [ ] Web service created with correct settings
- [ ] All environment variables added
- [ ] Build completed successfully
- [ ] Service shows "Live" status
- [ ] Backend URL copied: `________________________________`
- [ ] Health endpoint returns 200 OK
- [ ] API endpoint responds correctly
- [ ] CORS is configured for Netlify

---

## Your Backend URL

**🎉 Once deployed, your backend will be at:**

```
https://ai-cs-backend.onrender.com
```

(or whatever name you chose)

**Important URLs:**
- **Health check**: `https://your-backend.onrender.com/health`
- **API base**: `https://your-backend.onrender.com/api`
- **Root**: `https://your-backend.onrender.com/`

**Save this URL - you'll need it for:**
- Frontend deployment (REACT_APP_API_URL)
- Testing
- Monitoring

---

## What's Next?

After backend deployment:

1. ✅ **Backend is live on Render**
2. ⬜ **Deploy frontend to Netlify** (use the Quick Start guide)
3. ⬜ **Update frontend env vars** with backend URL
4. ⬜ **Test full application** end-to-end

---

## Quick Reference

### Render Dashboard
https://dashboard.render.com

### Your Repository
https://github.com/shakeblue/ai_cs

### Supabase Dashboard
https://app.supabase.com

### Service Logs
Render Dashboard → ai-cs-backend → Logs tab

---

**Need help?** Check the logs first, they usually show the exact error!

**Last Updated**: 2025-12-24
