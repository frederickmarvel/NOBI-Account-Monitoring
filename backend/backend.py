from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from blockchain_service import BlockchainService
from currency_service import CurrencyExchangeService
from pdf_generator import PDFReportGenerator
import os
from dotenv import load_dotenv
import logging
import io

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='.')
CORS(app)  

# Get API keys from environment variables (required for production)
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
SOLSCAN_API_KEY = os.getenv('SOLSCAN_API_KEY')

if not ETHERSCAN_API_KEY:
    logger.warning("ETHERSCAN_API_KEY not found in environment variables!")
if not SOLSCAN_API_KEY:
    logger.warning("SOLSCAN_API_KEY not found in environment variables - Solana support will be limited!")

blockchain_service = BlockchainService(api_key=ETHERSCAN_API_KEY, solscan_api_key=SOLSCAN_API_KEY)
currency_service = CurrencyExchangeService()
pdf_generator = PDFReportGenerator()

CHAIN_IDS = {
    'ethereum': 1,
    'polygon': 137,
    'bsc': 56,
    'arbitrum': 42161,
    'optimism': 10,
    'avalanche': 43114,
    'base': 8453,
    'blast': 81457,
    'linea': 59144,
    'scroll': 534352,
    'zksync': 324
}


# Static file serving is handled by Vercel's routing in vercel.json
# No need for these routes in serverless deployment


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Blockchain Monitoring API',
        'version': '1.0.0'
    })


@app.route('/api/balance/<blockchain>/<address>', methods=['GET'])
def get_balance(blockchain, address):
    try:
        start_date = request.args.get('start_date', '2020-01-01')
        end_date = request.args.get('end_date', '2025-12-31')
        
        logger.info(f"Fetching balance for {blockchain} address {address}")
        
        if blockchain == 'bitcoin':
            result = blockchain_service.get_bitcoin_transactions(address, start_date, end_date)
        elif blockchain == 'solana':
            result = blockchain_service.get_solana_transactions(address, start_date, end_date)
        elif blockchain in CHAIN_IDS:
            chain_id = CHAIN_IDS[blockchain]
            result = blockchain_service.get_ethereum_transactions(address, chain_id, start_date, end_date)
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported blockchain: {blockchain}'
            }), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/transactions/<blockchain>/<address>', methods=['GET'])
def get_transactions(blockchain, address):
    try:
        start_date = request.args.get('start_date', '2020-01-01')
        end_date = request.args.get('end_date', '2025-12-31')
        
        logger.info(f"Fetching transactions for {blockchain} address {address} "
                   f"from {start_date} to {end_date}")
        
        if blockchain == 'bitcoin':
            result = blockchain_service.get_bitcoin_transactions(address, start_date, end_date)
        elif blockchain == 'solana':
            result = blockchain_service.get_solana_transactions(address, start_date, end_date)
        elif blockchain in CHAIN_IDS:
            chain_id = CHAIN_IDS[blockchain]
            result = blockchain_service.get_ethereum_transactions(address, chain_id, start_date, end_date)
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported blockchain: {blockchain}'
            }), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error fetching transactions: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze/<blockchain>/<address>', methods=['GET'])
def analyze_address(blockchain, address):
    try:
        start_date = request.args.get('start_date', '2020-01-01')
        end_date = request.args.get('end_date', '2025-12-31')
        
        logger.info(f"Analyzing {blockchain} address {address}")
        
        # Get transactions (which includes balance)
        if blockchain == 'bitcoin':
            data = blockchain_service.get_bitcoin_transactions(address, start_date, end_date)
        elif blockchain == 'solana':
            data = blockchain_service.get_solana_transactions(address, start_date, end_date)
        elif blockchain in CHAIN_IDS:
            chain_id = CHAIN_IDS[blockchain]
            data = blockchain_service.get_ethereum_transactions(address, chain_id, start_date, end_date)
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported blockchain: {blockchain}'
            }), 400
        
        if not data.get('success'):
            return jsonify(data), 500
        
        # Calculate statistics
        transactions = data.get('transactions', [])
        
        # Calculate volumes
        total_in = sum(tx['amount'] for tx in transactions if tx['direction'] == 'in')
        total_out = sum(tx['amount'] for tx in transactions if tx['direction'] == 'out')
        
        # Transaction types
        tx_types = {}
        for tx in transactions:
            tx_type = tx.get('type', 'Unknown')
            tx_types[tx_type] = tx_types.get(tx_type, 0) + 1
        
        # Token breakdown
        tokens = {}
        for tx in transactions:
            if tx.get('tokenSymbol'):
                token = tx['tokenSymbol']
                if token not in tokens:
                    tokens[token] = {'count': 0, 'volume': 0}
                tokens[token]['count'] += 1
                tokens[token]['volume'] += tx['amount']
        
        return jsonify({
            'success': True,
            'blockchain': blockchain,
            'address': address,
            'balance': data.get('balance', '0'),
            'transactions': transactions,
            'statistics': {
                'total_transactions': len(transactions),
                'total_in': total_in,
                'total_out': total_out,
                'net_flow': total_in - total_out,
                'transaction_types': tx_types,
                'tokens': tokens
            },
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        })
        
    except Exception as e:
        logger.error(f"Error analyzing address: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export/pdf/<blockchain>/<address>', methods=['GET'])
def export_pdf(blockchain, address):
    try:
        start_date = request.args.get('start_date', '2020-01-01')
        end_date = request.args.get('end_date', '2025-12-31')
        
        logger.info(f"Generating PDF for {blockchain} address {address}")
        
        # Get blockchain data
        if blockchain == 'bitcoin':
            data = blockchain_service.get_bitcoin_transactions(address, start_date, end_date)
            crypto_symbol = 'BTC'
        elif blockchain == 'solana':
            data = blockchain_service.get_solana_transactions(address, start_date, end_date)
            crypto_symbol = 'SOL'
        elif blockchain in CHAIN_IDS:
            chain_id = CHAIN_IDS[blockchain]
            data = blockchain_service.get_ethereum_transactions(address, chain_id, start_date, end_date)
            
            # Get crypto symbol
            # Note: Polygon migrated from MATIC to POL as native token
            symbol_map = {
                'ethereum': 'ETH', 'polygon': 'POL', 'bsc': 'BNB',
                'arbitrum': 'ETH', 'optimism': 'ETH', 'avalanche': 'AVAX',
                'base': 'ETH', 'blast': 'ETH', 'linea': 'ETH',
                'scroll': 'ETH', 'zksync': 'ETH'
            }
            crypto_symbol = symbol_map.get(blockchain, 'ETH')
        else:
            return jsonify({
                'success': False,
                'error': f'Unsupported blockchain: {blockchain}'
            }), 400
        
        if not data.get('success'):
            return jsonify(data), 500
        
        # Get native token price
        prices_data = currency_service.get_crypto_prices([crypto_symbol])
        prices = prices_data.get(crypto_symbol, {'usd': 0, 'aed': 0})
        
        balance_raw = float(data.get('balance', 0))
        if blockchain == 'bitcoin':
            balance = balance_raw / 1e8
        elif blockchain == 'solana':
            balance = balance_raw / 1e9  # lamports to SOL
        elif blockchain == 'ethereum' or blockchain in ['polygon', 'bsc', 'arbitrum', 'optimism', 'base', 'blast', 'linea', 'scroll', 'zksync']:
            balance = balance_raw / 1e18
        else:
            balance = balance_raw
        
        transactions = data.get('transactions', [])
        if transactions:
            print(f"DEBUG BACKEND: First 3 transaction amounts: {[tx.get('amount', 'N/A') for tx in transactions[:3]]}")
            print(f"DEBUG BACKEND: Balance raw: {balance_raw}, Balance converted: {balance}")
        
        # Get token balances and prices for EVM chains and Solana
        token_balances_with_prices = {}
        token_balances = data.get('token_balances', {})
        
        if token_balances:
            # Get all token symbols
            token_symbols = list(token_balances.keys())
            
            # Fetch prices for all tokens
            token_prices_data = currency_service.get_crypto_prices(token_symbols)
            
            # Combine balance and price data
            for token_symbol, token_info in token_balances.items():
                token_prices = token_prices_data.get(token_symbol, {'usd': 0, 'aed': 0})
                token_balances_with_prices[token_symbol] = {
                    'balance': token_info['balance'],
                    'contract': token_info['contract'],
                    'name': token_info['name'],
                    'decimals': token_info['decimals'],
                    'price_usd': token_prices['usd'],
                    'price_aed': token_prices['aed'],
                    'value_usd': token_info['balance'] * token_prices['usd'],
                    'value_aed': token_info['balance'] * token_prices['aed']
                }
        
        pdf_bytes = pdf_generator.generate_account_statement(
            address=address,
            blockchain=blockchain,
            transactions=data.get('transactions', []),
            balance=balance,
            crypto_symbol=crypto_symbol,
            prices=prices,
            date_range={'start': start_date, 'end': end_date},
            token_balances=token_balances_with_prices
        )
        
        pdf_buffer = io.BytesIO(pdf_bytes)
        pdf_buffer.seek(0)
        
        filename = f"{blockchain}_{address[:8]}_statement_{start_date}_to_{end_date}.pdf"
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    
    logger.info(f"Starting Flask server on port {port}")
    logger.info(f"API Key configured: {'Yes' if ETHERSCAN_API_KEY else 'No'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
