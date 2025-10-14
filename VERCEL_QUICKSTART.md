# ⚡ Quick Start: Deploy to Vercel in 5 Minutes

## Prerequisites
- GitHub repository already set up ✅
- Etherscan API key ready

---

## Method 1: Deploy via Vercel Dashboard (Easiest)

### Step 1: Go to Vercel
Visit: **https://vercel.com/new**

### Step 2: Import Repository
1. Click **"Import Git Repository"**
2. Select: `frederickmarvel/NOBI-Account-Monitoring`
3. Click **"Import"**

### Step 3: Configure
1. **Project Name:** `nobi-account-monitoring` (or your choice)
2. **Framework Preset:** Other
3. **Root Directory:** `./` (leave as is)
4. **Build Command:** Leave empty
5. **Output Directory:** Leave empty

### Step 4: Add Environment Variable
1. Click **"Environment Variables"**
2. Add variable:
   - **Name:** `ETHERSCAN_API_KEY`
   - **Value:** Your Etherscan API key
   - **Environments:** Check all (Production, Preview, Development)
3. Click **"Add"**

### Step 5: Deploy!
1. Click **"Deploy"**
2. Wait 1-2 minutes ⏳
3. Your app is live! 🎉

**Your URL:** `https://nobi-account-monitoring.vercel.app`

---

## Method 2: Deploy via CLI (Advanced)

### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

### Step 2: Login
```bash
vercel login
```

### Step 3: Add Environment Variable
```bash
vercel env add ETHERSCAN_API_KEY
# Paste your API key when prompted
# Select: Production, Preview, Development (all three)
```

### Step 4: Deploy
```bash
cd "/Users/frederickmarvel/Blockchain Monitoring"
vercel --prod
```

---

## After Deployment

### Test Your Live App

1. **Open your Vercel URL**
   ```
   https://your-project.vercel.app
   ```

2. **Test API Health**
   ```bash
   curl https://your-project.vercel.app/api/health
   ```

3. **Try the Interface**
   - Enter a wallet address
   - Select blockchain
   - Click "Analyze Balance"
   - Try "Export to PDF"

### If Something Doesn't Work

**Check Function Logs:**
1. Go to Vercel dashboard
2. Select your project
3. Click "Functions"
4. Click on any function to see logs

**Common Issues:**
- **Timeout Error:** PDF generation may timeout on free plan
  - Solution: Upgrade to Pro plan or use smaller date ranges
- **API Not Found:** Check `vercel.json` configuration
- **CORS Error:** Already handled, but check browser console

---

## Update & Redeploy

### Automatic (via GitHub)
```bash
git add .
git commit -m "Update"
git push origin main
```
Vercel auto-deploys every push! ✨

### Manual (via CLI)
```bash
vercel --prod
```

---

## Custom Domain (Optional)

### In Vercel Dashboard:
1. Go to your project
2. Click "Settings" → "Domains"
3. Add your domain
4. Update DNS records (Vercel provides instructions)

---

## Pricing

**Hobby (Free):**
- ✅ Perfect for personal use
- ✅ Automatic HTTPS
- ✅ Global CDN
- ⚠️ 10s function timeout (may affect PDF generation)

**Pro ($20/month):**
- ✅ 60s function timeout (better for PDF)
- ✅ Faster cold starts
- ✅ Team features

**Recommendation:** Start with free, upgrade if needed.

---

## ⚠️ Important Notes

### PDF Generation
- May timeout with large transaction histories on free plan
- Solutions:
  1. Upgrade to Pro ($20/month)
  2. Limit date range
  3. Use alternative backend (Railway/Render)

### Cold Starts
- First request after inactivity may take 5-10 seconds
- Normal for serverless architecture
- Pro plan has faster cold starts

---

## Alternative: Hybrid Setup (Recommended)

For best performance:

**Frontend:** Vercel (free, fast CDN)
**Backend:** Railway/Render ($5-10/month, no timeouts)

This avoids PDF timeout issues while keeping frontend fast.

---

## Quick Commands

```bash
# Deploy to production
vercel --prod

# Deploy to preview
vercel

# Check deployments
vercel ls

# View logs
vercel logs

# Environment variables
vercel env ls
vercel env add ETHERSCAN_API_KEY
vercel env rm ETHERSCAN_API_KEY

# Link to project
vercel link

# Get help
vercel help
```

---

## Success Checklist

- [ ] Vercel account created
- [ ] Repository imported
- [ ] ETHERSCAN_API_KEY added
- [ ] First deployment successful
- [ ] Can access frontend URL
- [ ] `/api/health` endpoint works
- [ ] Can analyze blockchain address
- [ ] PDF export works (or known limitation)

---

## 🎉 You're Live!

Your blockchain account statement generator is now deployed on Vercel with:
- ✅ Global CDN distribution
- ✅ Automatic HTTPS
- ✅ Auto-deploy on every push
- ✅ Professional URL
- ✅ Zero maintenance

**Share your app:**
`https://your-project.vercel.app`

---

For detailed documentation, see: **VERCEL_DEPLOYMENT.md**
