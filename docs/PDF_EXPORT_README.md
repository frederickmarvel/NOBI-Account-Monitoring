# 🎯 PDF Account Statement Generator with USD/AED Conversions

## Overview

This blockchain monitoring system is designed to **export cryptocurrency account statements as professional PDF reports** with automatic currency conversions to **USD and AED** (United Arab Emirates Dirham).

## 🌟 Core Purpose

The main goal is to provide detailed financial reports for cryptocurrency accounts that include:

1. **Account Balance** - Current holdings in crypto, USD, and AED
2. **Transaction History** - All incoming and outgoing transactions
3. **Currency Conversions** - Real-time exchange rates for USD and AED
4. **Summary Statistics** - Total received, sent, net change in all currencies
5. **Professional Format** - Print-ready PDF reports

## 💰 Currency Support

### Cryptocurrencies:
- **Ethereum (ETH)**
- **Bitcoin (BTC)**  
- **Polygon (MATIC)**
- **BNB (BSC)**
- **Avalanche (AVAX)**
- **Solana (SOL)**
- And 10+ other EVM chains

### Fiat Currencies:
- **USD** - US Dollar
- **AED** - UAE Dirham (1 USD = 3.67 AED)

## 📊 PDF Report Contents

### 1. Account Information Section
- Blockchain network
- Wallet address
- Date range of report
- Current balance in:
  - Native cryptocurrency
  - USD equivalent
  - AED equivalent

### 2. Summary Statistics Section
- **Total Received**: Amount in crypto, USD, AED
- **Total Sent**: Amount in crypto, USD, AED
- **Net Change**: Profit/loss in all currencies
- **Total Transactions**: Count of all activities

### 3. Transaction History Section
- Date and time of each transaction
- Transaction type (Transfer, Token Transfer, etc.)
- Amount in cryptocurrency
- USD value at current rates
- AED value at current rates
- From/To addresses
- Status (Success/Failed)

### 4. Exchange Rate Information
- Current cryptocurrency price in USD
- USD to AED conversion rate
- Report generation timestamp

## 🚀 How to Use

### 1. Start the Backend

```bash
cd "/Users/frederickmarvel/Blockchain Monitoring"
python3 backend.py
```

The server will start on: `http://localhost:8085`

### 2. Open the Web Interface

Navigate to: `http://localhost:8085`

### 3. Generate an Account Statement

1. **Select Blockchain**: Choose from dropdown (Ethereum, Polygon, Bitcoin, etc.)
2. **Enter Address**: Paste the wallet address to analyze
3. **Select Date Range**: Choose start and end dates
4. **Click "Analyze"**: Fetch transaction data
5. **Click "Export PDF"**: Generate professional PDF report with USD/AED conversions

### 4. View the PDF Report

The PDF will automatically download with:
- Filename: `{blockchain}_{address}_statement_{start_date}_to_{end_date}.pdf`
- Example: `ethereum_0x28C6c06_statement_2024-01-01_to_2024-12-31.pdf`

## 🔧 API Endpoints

### Generate PDF Report

```bash
GET /api/export/pdf/{blockchain}/{address}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

**Example:**
```bash
curl "http://localhost:8085/api/export/pdf/ethereum/0x28C6c06298d514Db089934071355E5743bf21d60?start_date=2024-01-01&end_date=2024-12-31" --output statement.pdf
```

**Supported Blockchains:**
- `ethereum`, `polygon`, `bsc`, `arbitrum`, `optimism`
- `avalanche`, `base`, `blast`, `linea`, `scroll`, `zksync`
- `bitcoin`, `solana`

### Get Analysis Data (JSON)

```bash
GET /api/analyze/{blockchain}/{address}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

Returns JSON with:
- Balance
- Transactions list
- Statistics (total in/out, net flow)
- Token breakdown

## 💡 Use Cases

### 1. **Tax Reporting**
Generate detailed transaction history with USD/AED values for tax filing purposes.

### 2. **Portfolio Management**
Track your cryptocurrency holdings and their value in fiat currencies.

### 3. **Accounting**
Professional reports for business cryptocurrency accounts.

### 4. **Financial Audits**
Comprehensive account statements for auditors and financial advisors.

### 5. **Personal Records**
Keep organized records of your cryptocurrency transactions.

## 📁 Files Overview

### Backend (Python)
- **`backend.py`** - Flask API server with PDF export endpoint
- **`blockchain_service.py`** - Fetches data from blockchain APIs
- **`currency_service.py`** - Gets real-time crypto prices in USD/AED
- **`pdf_generator.py`** - Creates professional PDF reports

### Frontend (JavaScript)
- **`index.html`** - User interface
- **`app.js`** - Main application logic
- **`api-service-new.js`** - API client with PDF export function
- **`style.css`** - Styling

### Configuration
- **`.env`** - API keys and settings
- **`requirements.txt`** - Python dependencies

## 🔐 Configuration

Edit `.env` file:

```bash
# Etherscan API Key (for blockchain data)
ETHERSCAN_API_KEY=your_api_key_here

# Server Port
PORT=8085

# Debug Mode
DEBUG=True
```

## 📦 Dependencies

### Python Packages:
```
Flask==3.0.0
Flask-CORS==4.0.0
requests==2.31.0
python-dotenv==1.0.0
reportlab==4.0.7
```

Install with:
```bash
pip3 install -r requirements.txt
```

### External APIs:
- **Etherscan V2 API** - Blockchain transaction data
- **CoinGecko API** - Cryptocurrency prices (free, no API key)

## 🎨 PDF Report Features

✅ **Professional Design** - Clean, organized layout  
✅ **Color-Coded Sections** - Easy to navigate  
✅ **Multi-Currency Display** - Crypto, USD, and AED  
✅ **Transaction Limits** - First 100 transactions (prevents huge files)  
✅ **Pagination** - Multiple pages if needed  
✅ **Headers & Footers** - Page numbers and timestamps  
✅ **Print-Ready** - A4 size, high quality  

## 🧪 Example Test

```bash
# 1. Start the backend
python3 backend.py

# 2. Generate PDF for Binance hot wallet (very active address)
curl "http://localhost:8085/api/export/pdf/ethereum/0x28C6c06298d514Db089934071355E5743bf21d60?start_date=2024-12-01&end_date=2024-12-31" \
  --output binance_statement.pdf

# 3. Open the PDF
open binance_statement.pdf  # macOS
# OR
xdg-open binance_statement.pdf  # Linux
```

## 📊 Exchange Rate Sources

### Cryptocurrency Prices:
- **Source**: CoinGecko API
- **Update Frequency**: Every 5 minutes (cached)
- **Supported**: 100+ cryptocurrencies
- **Cost**: Free (no API key required)

### USD to AED:
- **Fixed Rate**: 1 USD = 3.67 AED
- **Source**: Official UAE Central Bank rate
- **Note**: Can be updated in `currency_service.py`

## 🎯 Key Features

1. **Real-Time Data** - Fetches actual blockchain transactions
2. **Multi-Blockchain** - Supports 13+ blockchains
3. **Currency Conversion** - Automatic USD/AED calculations
4. **Professional PDFs** - Print-ready account statements
5. **Transaction Details** - Every transaction with full information
6. **Summary Statistics** - Financial overview at a glance
7. **Date Filtering** - Custom date ranges
8. **Export Options** - PDF and CSV formats
9. **No Sign-Up Required** - Works with any public address
10. **Privacy-Focused** - All processing is local

## 🚨 Important Notes

### Transaction Limits:
- PDF reports show **first 100 transactions** to keep file size manageable
- For complete history, use CSV export or JSON API

### API Rate Limits:
- Etherscan: 5 requests/second, 100K requests/day
- CoinGecko: 50 calls/minute (free tier)

### Supported Networks:
- ✅ EVM chains (Ethereum, Polygon, BSC, etc.) - Full support
- ✅ Bitcoin - Full support via blockchain.info
- ⏳ Solana - Coming soon

## 📞 Support

For issues or questions about PDF export:
1. Check backend logs: `tail -f backend.log`
2. Verify API key is configured in `.env`
3. Test with active address: `0x28C6c06298d514Db089934071355E5743bf21d60`
4. Check browser console (F12) for errors

## 🎉 Success!

Your blockchain account statement system with USD/AED conversions is now ready to use!

**Open**: http://localhost:8085  
**Test Address**: `0x28C6c06298d514Db089934071355E5743bf21d60`  
**Click**: "Export PDF" to get your professional report!
