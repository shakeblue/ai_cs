# Quick Start: Deploy to Netlify in 30 Minutes

A streamlined guide to get your AI CS System live on Netlify quickly.

---

## What You're Deploying

```
Frontend (React) → Netlify ✅ FREE
Backend (Node.js) → Render ✅ FREE
Database → Supabase ✅ Already setup
```

---

## Prerequisites (5 minutes)

1. **Create accounts** (all free):
   - Netlify: https://netlify.com
   - Render: https://render.com

2. **Have ready**:
   - Your GitHub repository URL
   - Supabase credentials (already have)

---

## Step 1: Deploy Backend to Render (15 minutes)

### 1.1 Login and Connect Repository
1. Go to https://dashboard.render.com
2. Click **New** → **Web Service**
3. Connect GitHub and select `ai_cs` repository

### 1.2 Configure Service
```
Name: ai-cs-backend
Region: Oregon (or closest to you)
Branch: main
Root Directory: backend
Runtime: Node
Build Command: npm install
Start Command: npm start
Instance Type: Free
```

### 1.3 Add Environment Variables
Click **Advanced** → **Add Environment Variable**:

```bash
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
JWT_SECRET=GENERATE_RANDOM_32_CHARS_HERE
SUPABASE_URL=https://[project].supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
```

**Get Supabase credentials:**
- Login to https://app.supabase.com
- Select your project
- Go to **Settings** → **Database** → Copy connection string
- Go to **Settings** → **API** → Copy URL and anon key

**Generate JWT_SECRET:**
```bash
# Run in terminal:
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 1.4 Deploy
1. Click **Create Web Service**
2. Wait 5-10 minutes for deployment
3. **Copy the URL** (e.g., `https://ai-cs-backend.onrender.com`)
4. **Test it**:
   ```bash
   curl https://your-backend-url.onrender.com/health
   # Should return: {"success":true,"message":"Server is healthy"}
   ```

**✅ Backend URL**: `_________________________________`

---

## Step 2: Update Backend CORS (2 minutes)

1. **Edit** `backend/src/server.js` line 54
2. **Add** your Netlify domain (you'll get this in Step 3, or use wildcard):
   ```javascript
   origin: [
     'http://localhost:3000',
     'http://localhost:3001',
     'https://ai-cs-bf933.web.app',
     'https://ai-cs-bf933.firebaseapp.com',
     'https://aics1.netlify.app',
     'https://*.netlify.app',  // ← Add this line (allows all Netlify domains)
   ],
   ```
3. **Commit and push**:
   ```bash
   git add backend/src/server.js
   git commit -m "Add Netlify to CORS whitelist"
   git push
   ```
4. Render will auto-deploy the changes

---

## Step 3: Deploy Frontend to Netlify (10 minutes)

### 3.1 Login and Import Project
1. Go to https://app.netlify.com
2. Click **Add new site** → **Import an existing project**
3. Choose **GitHub**
4. Select `ai_cs` repository

### 3.2 Configure Build Settings
```
Branch to deploy: main
Build command: cd frontend && npm install && npm run build
Publish directory: frontend/build
```

### 3.3 Add Environment Variables
Click **Show advanced** → **New variable**:

```
Key: REACT_APP_API_URL
Value: [Your backend URL from Step 1]/api
```

**Example**: `https://ai-cs-backend.onrender.com/api`

### 3.4 Deploy
1. Click **Deploy site**
2. Wait 3-5 minutes
3. Netlify will give you a URL like: `https://random-name-123456.netlify.app`

**✅ Frontend URL**: `_________________________________`

---

## Step 4: Test Your Deployment (5 minutes)

### 4.1 Open Frontend
1. Click the Netlify URL
2. Should see the login page

### 4.2 Test Login
```
Username: agent001
Password: agent001
```

### 4.3 Check Dashboard
- Should see statistics and charts
- Should see event data from database

### 4.4 Debug if Issues
**Open browser DevTools (F12)**:
- **Console tab**: Should have no errors
- **Network tab**: Click on API calls, should see Status 200

**Common issues:**
- **CORS error**: Verify Step 2 was completed and backend redeployed
- **API timeout**: Render free tier sleeps after inactivity, first request takes ~30 seconds
- **404 errors**: Verify build completed successfully in Netlify deploy logs

---

## Step 5: Optional - Custom Domain (5 minutes)

### 5.1 In Netlify
1. Go to **Site settings** → **Domain management**
2. Click **Add custom domain**
3. Enter your domain (e.g., `aics.yourdomain.com`)

### 5.2 Update DNS
Add these records at your domain provider:

```
Type: CNAME
Name: aics (or your subdomain)
Value: [your-site].netlify.app
```

### 5.3 Wait for SSL
- Netlify automatically provisions SSL (1-2 hours)
- You'll get `https://aics.yourdomain.com`

---

## What's Next?

### Monitoring
- **Netlify**: https://app.netlify.com/sites/[your-site]/deploys
- **Render**: https://dashboard.render.com

### Make Changes
```bash
# Make changes to code
git add .
git commit -m "Your changes"
git push

# Both Netlify and Render will auto-deploy
```

### Update Frontend Environment Variables
1. Go to Netlify **Site settings** → **Environment variables**
2. Edit `REACT_APP_API_URL` if backend URL changes
3. Trigger new deploy: **Deploys** → **Trigger deploy** → **Deploy site**

### View Logs
**Backend logs (Render):**
```
Dashboard → Your service → Logs tab
```

**Frontend build logs (Netlify):**
```
Deploys → Click a deploy → Deploy log
```

### Scaling Up
When you need better performance:

| Service | Free → Paid | Cost | Benefits |
|---------|------------|------|----------|
| Netlify | Pro | $19/mo | More bandwidth, priority builds |
| Render | Starter | $7/mo | No sleep, better performance |
| Supabase | Pro | $25/mo | More database & bandwidth |

---

## Troubleshooting

### Backend Takes Long to Respond
**Cause**: Render free tier sleeps after 15 min of inactivity
**Fix**: First request wakes it up (~30 sec), subsequent requests are fast
**Permanent Fix**: Upgrade to Render Starter ($7/mo) for always-on

### CORS Error in Browser Console
**Cause**: Backend doesn't allow Netlify domain
**Fix**:
1. Check backend CORS in `backend/src/server.js`
2. Ensure your Netlify URL is in the `origin` array
3. Push changes and wait for Render to redeploy

### Build Fails on Netlify
**Cause**: Missing dependencies or wrong build command
**Fix**:
1. Check Netlify build logs for specific error
2. Verify build command: `cd frontend && npm install && npm run build`
3. Verify publish directory: `frontend/build`
4. Try building locally: `cd frontend && npm run build`

### Environment Variables Not Working
**Cause**: Variables not set or not prefixed with `REACT_APP_`
**Fix**:
1. All React env vars MUST start with `REACT_APP_`
2. Set in Netlify UI under **Site settings** → **Environment variables**
3. After adding/changing, **trigger new deploy**

### API Returns 404
**Cause**: Backend route not found or backend down
**Fix**:
1. Check backend is healthy: `curl https://backend-url/health`
2. Check backend logs in Render dashboard
3. Verify API URL in frontend has `/api` suffix

---

## Resources

- **Full Guide**: `/guide/NETLIFY_DEPLOYMENT_GUIDE.md`
- **Checklist**: `/guide/DEPLOYMENT_CHECKLIST.md`
- **Netlify Docs**: https://docs.netlify.com
- **Render Docs**: https://render.com/docs

---

## Success Checklist

- [ ] Backend deployed to Render
- [ ] Backend health check passes
- [ ] Frontend deployed to Netlify
- [ ] Can login successfully
- [ ] Dashboard loads with data
- [ ] No CORS errors in console

**If all checked, you're live! 🎉**

---

## Support

**Stuck?** Check the full deployment guide at `/guide/NETLIFY_DEPLOYMENT_GUIDE.md` for detailed troubleshooting and advanced configuration options.

**Backend sleeping on free tier?** Consider:
1. Upgrading to paid tier ($7/mo for always-on)
2. Using a cron job to ping it every 10 minutes
3. Accepting the ~30 second delay on first request

**Need help?** Review:
- Browser DevTools Console (F12)
- Netlify deploy logs
- Render service logs
- Backend health endpoint

---

**Last Updated**: 2025-12-24
