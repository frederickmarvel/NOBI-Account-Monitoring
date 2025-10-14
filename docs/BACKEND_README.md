# Python Backend for Blockchain Monitoring

This application now uses a **Python Flask backend** to handle all blockchain API calls server-side.

## Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Start the Backend

```bash
python3 backend.py
```

The server will start on `http://localhost:5000`

### 3. Open the Application

Open your browser to: `http://localhost:5000` (or open index.html directly if using CORS)

## API Endpoints

### Health Check
```
GET /api/health
```

### Get Balance
```
GET /api/balance/<blockchain>/<address>?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

### Get Transactions
```
GET /api/transactions/<blockchain>/<address>?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

### Complete Analysis
```
GET /api/analyze/<blockchain>/<address>?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

## Supported Blockchains

### Ethereum-Compatible (Etherscan V2 API)
- ethereum (Chain ID: 1)
- polygon (Chain ID: 137)
- bsc (Chain ID: 56)
- arbitrum (Chain ID: 42161)
- optimism (Chain ID: 10)
- avalanche (Chain ID: 43114)
- base (Chain ID: 8453)
- blast (Chain ID: 81457)
- linea (Chain ID: 59144)
- scroll (Chain ID: 534352)
- zksync (Chain ID: 324)

### Other Blockchains
- bitcoin (blockchain.info API)
- solana (coming soon)

## Configuration

Edit `.env` file:

```bash
ETHERSCAN_API_KEY=your_api_key_here
PORT=5000
DEBUG=True
```

## Architecture

### Backend (Python)
- **backend.py**: Flask REST API server
- **blockchain_service.py**: Blockchain API integration layer
- Rate limiting (5 req/sec)
- Automatic retries with exponential backoff
- Response caching

### Frontend (JavaScript)
- **api-service-new.js**: Simplified API client (calls Python backend)
- **app.js**: UI logic and data visualization
- **index.html**: Main interface

## Testing

### Test the Backend

```bash
# Health check
curl http://localhost:5000/api/health

# Test Ethereum address
curl "http://localhost:5000/api/analyze/ethereum/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb?start_date=2024-01-01&end_date=2024-12-31"
```

### Test Addresses

- **Ethereum**: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb` (Vitalik)
- **Polygon**: `0x7ceb23fd6bc0add59e62ac25578270cff1b9f619` (WETH)
- **Base**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (USDC)
- **Bitcoin**: `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa` (Genesis)

## Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.8+)
python3 --version

# Install dependencies
pip3 install -r requirements.txt
```

### CORS errors
Make sure to access via `http://localhost:5000` not file:// protocol

### API errors
- Check `.env` file has valid ETHERSCAN_API_KEY
- Check rate limits (5 req/sec, 100K req/day)
- Check backend logs for detailed error messages

## Advantages of Python Backend

✅ **No CORS issues** - All API calls from server  
✅ **Better error handling** - Proper retry logic  
✅ **Rate limiting** - Controlled request rate  
✅ **Caching** - Reduced API calls  
✅ **Logging** - Better debugging  
✅ **Security** - API keys hidden from frontend  
✅ **Performance** - Server-side processing  

## Next Steps

1. Deploy to production server (Heroku, Railway, DigitalOcean)
2. Add authentication/authorization
3. Implement database for caching
4. Add WebSocket for real-time updates
5. Expand blockchain support
