# 🔗 Blockchain Account Statement Generator

Professional blockchain account statement system with PDF export, multi-currency conversion, and spam token filtering.

## 🎯 Purpose

Generate comprehensive account statements for cryptocurrency wallets with:
- **Complete transaction history** (no limits)
- **USD and AED currency conversion** using real-time rates
- **Spam token filtering** - only whitelisted legitimate tokens included
- **Professional PDF reports** for accounting and compliance
- **Multi-chain support** - 50+ blockchains with single API key

## 📁 Project Structure

```
Blockchain Monitoring/
│
├── frontend/                      # Web Interface
│   ├── index.html                # Main UI
│   ├── app.js                    # Chart rendering & logic
│   ├── api-service-new.js        # Backend API client
│   └── style.css                 # Styling
│
├── backend/                       # Python Flask API
│   ├── backend.py                # Flask REST server (port 8085)
│   ├── blockchain_service.py     # Blockchain data fetching
│   ├── currency_service.py       # USD/AED conversion (CoinGecko)
│   ├── pdf_generator.py          # PDF report generation (ReportLab)
│   └── requirements.txt          # Python dependencies
│
├── docs/                          # Documentation
│   ├── BACKEND_README.md         # Backend API documentation
│   ├── DEPLOYMENT.md             # Production deployment guide
│   ├── PDF_EXPORT_README.md      # PDF feature guide
│   ├── TOKEN_FILTERING_README.md # Token whitelist system
│   └── V2_UPGRADE.md             # Etherscan V2 migration
│
├── archive/                       # Old/deprecated files
│
├── .env                          # API keys (git-ignored)
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── start.sh                      # Quick start script
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. Get API Key (Free)

1. Visit [Etherscan](https://etherscan.io/register)
2. Create free account
3. Get API key from [https://etherscan.io/myapikey](https://etherscan.io/myapikey)
4. **One key works for 50+ chains!** (Ethereum, Polygon, Base, Arbitrum, BSC, etc.)

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
ETHERSCAN_API_KEY=your_key_here
FLASK_PORT=8085
```

### 3. Install Dependencies

```bash
# Install Python dependencies
pip3 install -r backend/requirements.txt
```

### 4. Start the System

**Option A: Use start script (Recommended)**
```bash
./start.sh
```

**Option B: Manual start**
```bash
# Start backend
cd backend
python3 backend.py &

# Open frontend
open frontend/index.html
```

### 5. Generate Account Statement

1. Open `frontend/index.html` in browser
2. Enter wallet address
3. Select blockchain (Ethereum, Polygon, etc.)
4. Choose date range
5. Click **"Export to PDF"**
6. PDF downloads automatically with complete transaction history

## 📊 Supported Blockchains

**With Single Etherscan API Key:**
- **Layer 1**: Ethereum, Polygon, BNB Smart Chain, Avalanche
- **Layer 2**: Base, Arbitrum, Optimism, Blast, Linea, Scroll, zkSync Era
- **And 40+ more EVM chains**

**Additional:**
- Bitcoin (no API key needed - uses blockchain.info)

## 🎨 Features

### ✅ Complete Transaction History
- **No 100 transaction limit** - all transactions included in PDF
- Native transactions (ETH, MATIC, BNB, etc.) always included
- Token transfers filtered by whitelist

### 🛡️ Spam Token Filtering
- **50+ whitelisted tokens** across all major chains
- Includes: USDT, USDC, WETH, DAI, WBTC, LINK, UNI, AAVE
- Automatically filters dusting attacks and scam tokens
- Transparent - PDF shows which tokens were included

### 💱 Multi-Currency Support
- **Real-time prices** from CoinGecko API
- **USD conversion** for all cryptocurrencies
- **AED conversion** (1 USD = 3.67 AED fixed rate)
- All amounts displayed in crypto, USD, and AED

### 📄 Professional PDF Reports
Include:
- Account information and current balance
- Date range and blockchain
- List of included whitelisted tokens
- Summary statistics (total in, total out, net change)
- Complete transaction table with all details
- USD and AED values for every transaction
- Clean formatting without encoding issues

### 📈 Interactive Charts
- Balance trends over time
- Transaction type distribution
- Interactive date filtering
- Real-time chart updates

## 🔧 Configuration

### Adding More Tokens to Whitelist

Edit `backend/blockchain_service.py`:

```python
WHITELISTED_TOKENS = {
    # Ethereum
    '0xcontract_address': {'symbol': 'TOKEN', 'name': 'Token Name'},
    
    # Polygon
    '0xcontract_address': {'symbol': 'TOKEN', 'name': 'Token Name'},
    
    # ... add more tokens
}
```

**Note:** Contract addresses must be lowercase!

### Currency Conversion Rates

**USD Rates:** Real-time from CoinGecko API (free tier, updates every 5 minutes)
**AED Rate:** Fixed at 3.67 AED per 1 USD (edit `backend/currency_service.py` to change)

## 📡 API Endpoints

### Backend REST API (Port 8085)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/balance/<blockchain>/<address>` | GET | Get current balance |
| `/api/transactions/<blockchain>/<address>` | GET | Get transactions with date filter |
| `/api/export/pdf/<blockchain>/<address>` | GET | Download PDF report |

**Query Parameters:**
- `start_date`: YYYY-MM-DD format
- `end_date`: YYYY-MM-DD format

**Example:**
```bash
curl "http://localhost:8085/api/export/pdf/polygon/0xYourAddress?start_date=2024-01-01&end_date=2024-12-31"
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8085 is in use
lsof -ti:8085 | xargs kill -9

# Restart backend
cd backend && python3 backend.py
```

### PDF shows wrong amounts
- Blockchain amounts are already converted from wei/satoshi
- Check debug output in terminal for transaction values
- Verify date range includes transactions

### AED shows wrong symbol
- Fixed in latest version - should show "AED" not "د.إ"
- Update to latest code if seeing ■■ symbols

### Token not showing in PDF
- Check if token is in whitelist: `backend/blockchain_service.py`
- Add contract address to `WHITELISTED_TOKENS` dictionary
- Address must be lowercase

### Rate limit errors
- Free tier: 5 calls/second, 100,000 calls/day
- Wait 60 seconds and try again
- Consider paid Etherscan plan for high volume

## 📚 Documentation

- **[Backend API](docs/BACKEND_README.md)** - Complete API documentation
- **[PDF Export](docs/PDF_EXPORT_README.md)** - PDF generation system
- **[Token Filtering](docs/TOKEN_FILTERING_README.md)** - Whitelist configuration
- **[Deployment](docs/DEPLOYMENT.md)** - Production deployment guide
- **[V2 Upgrade](docs/V2_UPGRADE.md)** - Etherscan V2 API migration

## 🔐 Security Notes

- **Never commit `.env` file** to Git (already in .gitignore)
- **API keys** should be environment variables in production
- **CORS** is enabled for development (disable in production)
- **Rate limiting** recommended for production API

## 📦 Dependencies

### Backend (Python 3.8+)
- Flask 3.0.0 - Web framework
- requests 2.31.0 - HTTP client
- python-dotenv 1.0.0 - Environment variables
- reportlab 4.0.7 - PDF generation

### Frontend
- Chart.js 4.4.0 - Charting library
- date-fns 2.30.0 - Date formatting
- Vanilla JavaScript (no framework)

## 🎯 Use Cases

1. **Personal Accounting** - Track all crypto transactions with USD/AED values
2. **Tax Reporting** - Generate complete transaction history for tax filing
3. **Business Records** - Professional statements for business accounting
4. **Portfolio Tracking** - Monitor multiple wallets across chains
5. **Compliance** - Provide transaction records to auditors

## 🤝 Contributing

To add support for new blockchains or tokens:

1. Add token contract to `WHITELISTED_TOKENS` in `blockchain_service.py`
2. Update chain mappings if adding new blockchain
3. Test with real addresses
4. Update documentation

## 📝 License

This project is for personal and internal business use.

## ✨ Recent Updates

- ✅ Removed 100 transaction limit in PDFs
- ✅ Added token whitelist filtering system
- ✅ Fixed AED currency display (removed Arabic characters)
- ✅ Added transparency section showing included tokens
- ✅ Migrated to Etherscan V2 API (50+ chains with one key)
- ✅ Complete folder reorganization for better maintainability

---

**Built with ❤️ for clean, professional blockchain accounting**
