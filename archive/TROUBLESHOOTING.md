# 🔧 Troubleshooting Guide

## System Status Check

### ✅ What's Working

1. **Backend is running** on port 8085
2. **API health check** returns healthy status
3. **Blockchain API** successfully fetches data (tested with Polygon)
4. **Frontend files** are properly organized in `frontend/` folder
5. **File structure** is clean and organized

### 🧪 Quick Tests

#### Test 1: Backend Health
```bash
curl http://localhost:8085/api/health
```
**Expected:** `{"service": "Blockchain Monitoring API", "status": "healthy", "version": "1.0.0"}`

#### Test 2: Fetch Balance
```bash
curl "http://localhost:8085/api/balance/polygon/0x5350E1068f0E138ff306990B16fA4910d970c692"
```
**Expected:** JSON with balance and transactions

#### Test 3: Generate PDF
```bash
curl "http://localhost:8085/api/export/pdf/polygon/0x5350E1068f0E138ff306990B16fA4910d970c692?start_date=2024-01-01&end_date=2024-12-31" -o test.pdf
```
**Expected:** PDF file downloads

### 🌐 Frontend Access

The frontend should be opened in your browser. To manually open it:

1. **Option A: Direct file**
   ```bash
   open frontend/index.html
   ```

2. **Option B: Local server** (better for API calls)
   ```bash
   cd frontend
   python3 -m http.server 3000
   # Then open: http://localhost:3000
   ```

### 🐛 Common Issues & Solutions

#### Issue 1: "API keys not configured"
**Symptom:** Error message in browser console
**Solution:** 
```bash
# Check .env file exists
cat .env | grep ETHERSCAN_API_KEY

# If missing, copy from example
cp .env.example .env
# Edit .env and add your Etherscan API key
```

#### Issue 2: CORS Errors in Browser Console
**Symptom:** "Access-Control-Allow-Origin" error
**Solution:** Use a local web server instead of opening file directly:
```bash
cd frontend
python3 -m http.server 3000
# Open: http://localhost:3000
```

#### Issue 3: Backend not responding
**Symptom:** Connection refused or timeout
**Solution:**
```bash
# Check if backend is running
lsof -ti:8085

# If not running, start it
cd backend
python3 backend.py
```

#### Issue 4: PDF generation fails
**Symptom:** Error when clicking "Export to PDF"
**Solution:**
```bash
# Check backend logs in terminal
# Common issues:
# 1. Missing reportlab: pip3 install reportlab
# 2. No transactions in date range: Expand date range
# 3. Invalid address: Check address format
```

#### Issue 5: Charts not displaying
**Symptom:** Blank chart areas in frontend
**Solution:**
1. Open browser console (F12)
2. Check for JavaScript errors
3. Verify Chart.js is loading:
   - Check internet connection (Chart.js loads from CDN)
   - Or download Chart.js locally

#### Issue 6: No transactions showing
**Symptom:** "No transactions found"
**Solution:**
1. Expand date range (try last 365 days)
2. Verify address has transactions on that blockchain
3. Check blockchain is correct (Ethereum vs Polygon, etc.)
4. Check API key is valid and has quota remaining

### 📊 Testing Workflow

1. **Start Backend**
   ```bash
   cd backend
   python3 backend.py
   ```
   Wait for: "Running on http://127.0.0.1:8085"

2. **Open Frontend**
   ```bash
   # From root directory
   open frontend/index.html
   # Or with server:
   cd frontend && python3 -m http.server 3000
   ```

3. **Test Analysis**
   - Enter address: `0x5350E1068f0E138ff306990B16fA4910d970c692`
   - Select: Polygon
   - Date: Last 30 days
   - Click: "Analyze Balance"
   - Wait: 5-10 seconds
   - Should see: Charts and transaction list

4. **Test PDF Export**
   - After analysis completes
   - Click: "Export to PDF"
   - Should: Download PDF automatically
   - Check: PDF has all transactions (not limited to 100)
   - Verify: Only whitelisted tokens appear

### 🔍 Debug Mode

To see detailed logs:

**Backend:**
```bash
cd backend
# Logs are printed to terminal
python3 backend.py
```

**Frontend:**
Open browser console (F12 → Console tab)

### 📋 System Requirements Checklist

- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] pip3 installed (`pip3 --version`)
- [ ] Requirements installed (`pip3 install -r backend/requirements.txt`)
- [ ] .env file exists with ETHERSCAN_API_KEY
- [ ] Port 8085 is not in use by another app
- [ ] Internet connection active (for API calls)
- [ ] Modern browser (Chrome, Firefox, Safari, Edge)

### 🆘 Still Not Working?

Tell me specifically:

1. **What are you trying to do?**
   - View balance?
   - See transactions?
   - Export PDF?
   - View charts?

2. **What happens instead?**
   - Error message?
   - Blank page?
   - Loading forever?
   - Wrong data?

3. **What do you see in:**
   - Browser console (F12)?
   - Backend terminal logs?
   - Network tab (F12 → Network)?

4. **What's your setup?**
   - How are you opening frontend (file:// or http://)?
   - Which blockchain are you testing?
   - Which address are you using?

### 🎯 Quick Fix Commands

**Restart everything:**
```bash
cd "/Users/frederickmarvel/Blockchain Monitoring"

# Kill any running backend
lsof -ti:8085 | xargs kill -9 2>/dev/null

# Start backend
cd backend
python3 backend.py &

# Open frontend
cd ..
open frontend/index.html
```

**Fresh install:**
```bash
cd "/Users/frederickmarvel/Blockchain Monitoring"

# Reinstall Python packages
pip3 install -r backend/requirements.txt --upgrade

# Verify .env file
cat .env

# Start backend
cd backend
python3 backend.py
```

### ✅ Verification Steps

Run these commands to verify everything:

```bash
# 1. Check Python version
python3 --version  # Should be 3.8+

# 2. Check packages installed
pip3 list | grep -E "Flask|reportlab|requests"

# 3. Check backend files exist
ls -la backend/

# 4. Check frontend files exist  
ls -la frontend/

# 5. Check .env file
cat .env | grep ETHERSCAN

# 6. Test backend
curl http://localhost:8085/api/health

# 7. Test API call
curl "http://localhost:8085/api/balance/ethereum/0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" | head -50
```

If all these pass, the system is working correctly!

---

## Current Status (as of now):

✅ Backend is **RUNNING** on port 8085
✅ API health check **PASSES**
✅ Blockchain API **WORKING** (tested with Polygon)
✅ Frontend files **EXIST** in correct location
✅ File structure **ORGANIZED** properly

**Next step:** Open `frontend/index.html` in browser and test the UI!
