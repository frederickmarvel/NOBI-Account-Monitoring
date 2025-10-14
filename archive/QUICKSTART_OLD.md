# Quick Start Guide - Blockchain Balance Screener

## ⚡ Get Started in 5 Minutes

### Step 1: Get Your First API Key (Free)

For the quickest start, get an Etherscan API key:

1. **Visit**: https://etherscan.io/register
2. **Sign up** with your email (free, no credit card)
3. **Verify** your email
4. **Get API Key**: https://etherscan.io/myapikey
5. **Copy** the API key (looks like: `ABC123XYZ456...`)

### Step 2: Add the API Key

1. Open `config.js` in a text editor
2. Find this line at the top:
   ```javascript
   const ETHERSCAN_API_KEY = '9FJFBY6T13DP36JEFRETADMIC6KA6ZCRZX';
   ```
3. Replace with your actual key:
   ```javascript
   const ETHERSCAN_API_KEY = 'ABC123XYZ456...';
   ```
4. Save the file

✨ **That's it!** This one key now works for 50+ EVM chains including Ethereum, Base, Arbitrum, Optimism, Polygon, BSC, and more!

### Step 3: Run the App

**Option A - Python (Easiest)**
```bash
cd "/Users/frederickmarvel/Blockchain Monitoring"
python3 -m http.server 8000
```
Open: http://localhost:8000

**Option B - Just Open It**
Double-click `index.html` (some features may be limited)

### Step 4: Try It Out

1. Enter a wallet address (or click a sample address)
2. Select "Ethereum" from the dropdown
3. Choose a date range (last 30 days is good)
4. Click "Analyze Balance"
5. Wait 5-15 seconds for real data to load

### 🎯 Test Addresses

Try these popular Ethereum addresses:

- **Vitalik Buterin**: `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`
- **Ethereum Foundation**: `0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe`
- **USDC Contract**: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`

## 📊 What You'll See

After analysis completes:

✅ **Current Balance** - Real wallet balance in ETH and USD  
✅ **Transaction History** - All transactions in your date range  
✅ **Interactive Charts** - Balance trends and transaction types  
✅ **Export Options** - Download PDF reports or CSV files  
✅ **Token Transfers** - ERC-20 tokens like USDC, DAI, etc.

## 🌐 All Supported Chains

With your single Etherscan API key, you can now analyze:

**Layer 1 Networks:**
- Ethereum, Polygon, BNB Smart Chain, Avalanche

**Layer 2 Solutions:**
- Base, Arbitrum, Optimism, Blast, Linea, Scroll, zkSync Era

**And 40+ more EVM chains!**

No additional setup needed - just select the chain from the dropdown and start analyzing!

## ⚠️ Troubleshooting

**"API keys not configured" message?**
- Make sure you saved `config.js` after adding your key
- Check for typos in the API key
- Refresh the page

**No transactions found?**
- Try a different wallet address
- Expand the date range
- Make sure the address is correct

**Rate limit errors?**
- Free tier: 5 calls/second, 100,000/day
- Wait 60 seconds and try again
- This is normal for very active wallets

## 🚀 Next Steps

1. **Add more API keys** for other blockchains
2. **Try different addresses** to analyze
3. **Export reports** as PDF or CSV
4. **Share** with your team

## 💡 Pro Tips

- The app caches data for 60 seconds to save API calls
- Transaction hashes are clickable - they open in the blockchain explorer
- Use filters to find specific transaction types
- Dark mode is automatic based on your system preferences

## 📞 Need Help?

1. Check the full `README.md` for detailed documentation
2. Look at browser console (F12) for error messages
3. Verify your API keys are correct

---

**Ready to monitor blockchain transactions like a pro! 🎉**
