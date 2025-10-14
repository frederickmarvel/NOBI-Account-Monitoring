# 🚀 Vercel Deployment Guide

## ⚠️ Important Considerations

### Vercel Architecture
Vercel is designed for **serverless functions** and **static sites**. Your Flask app will be converted to serverless functions, which means:

- ✅ **Automatic scaling**
- ✅ **Global CDN distribution**
- ✅ **HTTPS included**
- ⚠️ **Function timeout limits** (10s on Hobby, 60s on Pro)
- ⚠️ **Cold starts** (first request may be slow)

### Limitations for This Project
- **PDF Generation:** May timeout for large transaction histories (use Pro plan for 60s timeout)
- **API Rate Limits:** Blockchain API calls may hit timeout limits
- **Concurrent Requests:** Each request is a new serverless function instance

### Recommended: Hybrid Approach
For production, consider:
1. **Frontend on Vercel** (static hosting)
2. **Backend on Railway/Render/Heroku** (persistent server)

But if you want to try Vercel, here's how:

---

## 🛠️ Setup Steps

### Step 1: Install Vercel CLI

```bash
# Install globally
npm install -g vercel

# Or using pnpm
pnpm install -g vercel

# Or using yarn
yarn global add vercel
```

### Step 2: Login to Vercel

```bash
vercel login
```

This will open your browser to authenticate.

### Step 3: Prepare Your Project

The project is already configured with `vercel.json`, but let's verify:

```bash
cd "/Users/frederickmarvel/Blockchain Monitoring"

# Check vercel.json exists
cat vercel.json
```

### Step 4: Set Environment Variables

Before deploying, you need to add your API key to Vercel:

```bash
# Add environment variable
vercel env add ETHERSCAN_API_KEY

# When prompted:
# - Environment: Production, Preview, Development (select all)
# - Value: Paste your Etherscan API key
```

### Step 5: Deploy to Vercel

```bash
# From project root
cd "/Users/frederickmarvel/Blockchain Monitoring"

# Deploy (this will ask configuration questions)
vercel

# Or deploy directly to production
vercel --prod
```

During first deployment, Vercel will ask:
- **Set up and deploy?** → Yes
- **Which scope?** → Your username
- **Link to existing project?** → No
- **Project name?** → `nobi-account-monitoring` (or your choice)
- **Directory with code?** → `./` (current directory)
- **Override settings?** → No

### Step 6: Verify Deployment

After deployment, Vercel will give you a URL like:
```
https://nobi-account-monitoring.vercel.app
```

Test the API:
```bash
curl https://your-project.vercel.app/api/health
```

---

## 📝 Configuration Files Explained

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/backend.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/backend.py"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

**Explanation:**
- `builds`: Tells Vercel to build Python backend
- `routes`: 
  - API calls go to Flask backend
  - All other requests serve static files from frontend/

### Environment Variables in Vercel

Set these in Vercel dashboard or CLI:
- `ETHERSCAN_API_KEY`: Your Etherscan API key
- `FLASK_ENV`: production

---

## 🌐 Using Vercel Dashboard (Alternative Method)

### Option A: Deploy via GitHub

1. **Push to GitHub** (already done ✅)
   ```bash
   git push origin main
   ```

2. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Click "Add New" → "Project"

3. **Import Repository**
   - Select "Import Git Repository"
   - Choose: `frederickmarvel/NOBI-Account-Monitoring`
   - Click "Import"

4. **Configure Project**
   - **Framework Preset:** Other
   - **Build Command:** (leave empty)
   - **Output Directory:** `frontend`
   - **Install Command:** `pip install -r backend/requirements.txt`

5. **Add Environment Variables**
   - Click "Environment Variables"
   - Add: `ETHERSCAN_API_KEY` = your key
   - Environment: Production, Preview, Development

6. **Deploy**
   - Click "Deploy"
   - Wait 1-2 minutes
   - Get your live URL!

---

## 🔧 Update Frontend API URL

After deployment, update the API endpoint in your frontend:

**Edit `frontend/api-service-new.js`:**

```javascript
class BlockchainAPIService {
  constructor() {
    // For Vercel deployment
    this.backendUrl = window.location.origin + '/api';
    
    // For local development
    // this.backendUrl = 'http://localhost:8085/api';
    
    this.cache = new Map();
  }
  // ... rest of code
}
```

Or make it environment-aware:

```javascript
constructor() {
  // Auto-detect environment
  const isDevelopment = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1';
  
  this.backendUrl = isDevelopment 
    ? 'http://localhost:8085/api'
    : window.location.origin + '/api';
  
  this.cache = new Map();
}
```

---

## 🚨 Known Issues & Solutions

### Issue 1: PDF Generation Timeout
**Problem:** Large transaction histories cause timeout (10s limit on free plan)

**Solutions:**
- Upgrade to Vercel Pro (60s timeout)
- Limit transactions in PDF to 1000
- Or: Use separate backend service for PDF generation

### Issue 2: Cold Starts
**Problem:** First request is slow (5-10 seconds)

**Solutions:**
- Use Vercel Pro for faster cold starts
- Implement loading states in frontend
- Consider keeping backend warm with cron job

### Issue 3: Python Package Size
**Problem:** Some packages may exceed Vercel limits

**Solutions:**
- Already optimized with minimal dependencies
- If issues, remove unnecessary packages from requirements.txt

### Issue 4: CORS Errors
**Problem:** Cross-origin issues between frontend and API

**Solutions:**
- Already handled with Flask-CORS
- Verify in `backend.py`: `CORS(app)`

---

## 📊 Testing Your Deployment

### Test API Endpoints

```bash
# Replace with your Vercel URL
VERCEL_URL="https://your-project.vercel.app"

# 1. Health check
curl "$VERCEL_URL/api/health"

# 2. Get balance
curl "$VERCEL_URL/api/balance/ethereum/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

# 3. Test PDF (may timeout on free plan)
curl "$VERCEL_URL/api/export/pdf/polygon/0x5350E1068f0E138ff306990B16fA4910d970c692?start_date=2024-01-01&end_date=2024-12-31" -o test.pdf
```

### Test Frontend

1. Open: `https://your-project.vercel.app`
2. Enter test address
3. Select blockchain
4. Click "Analyze Balance"
5. Try "Export to PDF"

---

## 💰 Vercel Pricing

### Hobby (Free)
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Automatic HTTPS
- ⚠️ 10s function timeout
- ⚠️ Slower cold starts

### Pro ($20/month)
- ✅ Everything in Hobby
- ✅ 60s function timeout
- ✅ Faster cold starts
- ✅ Priority support
- ✅ Team collaboration

**Recommendation for this project:** Start with Hobby, upgrade if PDF generation times out.

---

## 🔄 Continuous Deployment

Once connected to GitHub, Vercel automatically deploys on every push:

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push origin main

# Vercel automatically:
# 1. Detects push
# 2. Builds project
# 3. Deploys to preview URL
# 4. Deploys to production (on main branch)
```

---

## 🎯 Alternative: Hybrid Approach (Recommended)

### Best Architecture for Production

**Frontend: Vercel** (free)
- Static hosting
- Global CDN
- Fast load times

**Backend: Railway/Render** ($5-10/month)
- Persistent Python server
- No timeout issues
- Better for long-running tasks

### Quick Setup:

1. **Deploy Frontend to Vercel:**
   ```bash
   # Only deploy frontend folder
   vercel --cwd frontend
   ```

2. **Deploy Backend to Railway:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway init
   railway up
   ```

3. **Update Frontend API URL:**
   ```javascript
   this.backendUrl = 'https://your-railway-app.railway.app/api';
   ```

This gives you:
- ✅ Fast frontend (Vercel CDN)
- ✅ Reliable backend (Railway persistent server)
- ✅ No timeout issues
- ✅ Better for this use case

---

## 📚 Resources

- **Vercel Docs:** https://vercel.com/docs
- **Vercel Python:** https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **Railway:** https://railway.app (alternative backend hosting)
- **Render:** https://render.com (alternative backend hosting)

---

## ✅ Deployment Checklist

- [ ] Install Vercel CLI
- [ ] Login to Vercel
- [ ] Set `ETHERSCAN_API_KEY` environment variable
- [ ] Update frontend API URL
- [ ] Test locally first
- [ ] Deploy with `vercel`
- [ ] Test all API endpoints
- [ ] Test PDF generation (may need Pro plan)
- [ ] Set up custom domain (optional)
- [ ] Monitor function logs in Vercel dashboard

---

## 🚀 Quick Deploy Command

```bash
# One-command deploy (after setup)
cd "/Users/frederickmarvel/Blockchain Monitoring" && vercel --prod
```

After deployment, your app will be live at:
**https://nobi-account-monitoring.vercel.app**

(URL may vary based on your project name)
