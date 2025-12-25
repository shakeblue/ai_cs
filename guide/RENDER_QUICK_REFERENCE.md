# Render Deployment - Quick Reference Card

**📋 Print or keep this open while deploying!**

---

## 🔗 Quick Links

| Resource | URL |
|----------|-----|
| **Render Dashboard** | https://dashboard.render.com |
| **Your Repository** | https://github.com/shakeblue/ai_cs |
| **Supabase Dashboard** | https://app.supabase.com |
| **Full Guide** | `/guide/RENDER_DEPLOYMENT_STEP_BY_STEP.md` |

---

## ⚙️ Service Configuration

**Copy these values when creating your web service:**

```
Name:              ai-cs-backend
Region:            Oregon (US West)
Branch:            main
Root Directory:    backend
Runtime:           Node
Build Command:     npm install
Start Command:     npm start
Instance Type:     Free
```

---

## 🔐 Environment Variables

**Copy and paste these (replace [PASSWORD] with your Supabase DB password):**

```bash
NODE_ENV=production
PORT=3000
DATABASE_URL=postgresql://postgres:qB5vnHLgMf2hNQKD@db.yxndlrlwrcuikedvpkrj.supabase.co:5432/postgres
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

### 🔑 Get Supabase Password

1. Go to https://app.supabase.com
2. Select project: `yxndlrlwrcuikedvpkrj`
3. **Settings** → **Database** → **Connection string**
4. Copy password from URI or reset if forgotten

---

## ✅ Deployment Steps

### Step 1: Create Account
- [ ] Go to https://render.com
- [ ] Sign up with GitHub
- [ ] Authorize repository access

### Step 2: Create Web Service
- [ ] Click **New** → **Web Service**
- [ ] Connect `shakeblue/ai_cs` repository
- [ ] Fill in configuration (see above)
- [ ] Add all environment variables (see above)
- [ ] Click **Create Web Service**

### Step 3: Wait for Build
- [ ] Monitor build logs (3-7 minutes)
- [ ] Wait for "Live" status

### Step 4: Test
- [ ] Copy backend URL
- [ ] Test: `curl https://your-backend.onrender.com/health`
- [ ] Should return: `{"success":true,"message":"Server is healthy"}`

---

## 🧪 Test Commands

```bash
# Health check
curl https://your-backend.onrender.com/health

# API root
curl https://your-backend.onrender.com/

# Events API
curl https://your-backend.onrender.com/api/events/search
```

---

## ⚠️ Common Issues

### Build fails - "Cannot find module"
**Fix**: Ensure Root Directory = `backend`

### "Error: connect ECONNREFUSED"
**Fix**: Check DATABASE_URL, verify Supabase password

### "This service is not responding"
**Fix**: Free tier sleep - wait 30 seconds and retry

### CORS errors later
**Already configured!** ✅ Your code already includes Netlify

---

## 📝 Your Deployment Info

Fill in after deployment:

```
Backend URL: _________________________________

Deployed at: ______________ (date/time)

Build time: _________ minutes

Status: ⬜ Building | ⬜ Live | ⬜ Failed
```

---

## 🎯 Next Steps After Backend Deploy

1. ✅ Save backend URL
2. ⬜ Deploy frontend to Netlify
3. ⬜ Add backend URL to frontend env vars
4. ⬜ Test full application

---

## 🆘 Need Help?

- **Build logs**: Render Dashboard → Your service → **Logs** tab
- **Full guide**: `cat guide/RENDER_DEPLOYMENT_STEP_BY_STEP.md`
- **Status**: https://status.render.com (check if Render is down)

---

**Good luck! 🚀**
