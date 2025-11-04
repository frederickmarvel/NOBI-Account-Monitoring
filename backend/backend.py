from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from blockchain_service import BlockchainService
from currency_service import CurrencyExchangeService
from pdf_generator import PDFReportGenerator
from csv_generator import CSVGenerator
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
TRONSCAN_API_KEY = os.getenv('TRONSCAN_API_KEY')
CARDANOSCAN_API_KEY = os.getenv('CARDANOSCAN_API_KEY')

if not ETHERSCAN_API_KEY:
    logger.warning("ETHERSCAN_API_KEY not found in environment variables!")
if not SOLSCAN_API_KEY:
    logger.warning("SOLSCAN_API_KEY not found in environment variables - Solana support will be limited!")
if not TRONSCAN_API_KEY:
    logger.warning("TRONSCAN_API_KEY not found - Tron support will use free tier with limits!")
if not CARDANOSCAN_API_KEY:
    logger.warning("CARDANOSCAN_API_KEY not found - Cardano support will use free tier with limits!")

blockchain_service = BlockchainService(
    api_key=ETHERSCAN_API_KEY, 
    solscan_api_key=SOLSCAN_API_KEY,
    tronscan_api_key=TRONSCAN_API_KEY,
    cardanoscan_api_key=CARDANOSCAN_API_KEY
)
currency_service = CurrencyExchangeService()
pdf_generator = PDFReportGenerator()
csv_generator = CSVGenerator()

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
        elif blockchain == 'tron':
            result = blockchain_service.get_tron_transactions(address, start_date, end_date)
        elif blockchain == 'cardano':
            result = blockchain_service.get_cardano_transactions(address, start_date, end_date)
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
        elif blockchain == 'tron':
            data = blockchain_service.get_tron_transactions(address, start_date, end_date)
        elif blockchain == 'cardano':
            data = blockchain_service.get_cardano_transactions(address, start_date, end_date)
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
        elif blockchain == 'tron':
            data = blockchain_service.get_tron_transactions(address, start_date, end_date)
            crypto_symbol = 'TRX'
        elif blockchain == 'cardano':
            data = blockchain_service.get_cardano_transactions(address, start_date, end_date)
            crypto_symbol = 'ADA'
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
        opening_balance_raw = data.get('opening_balance')
        opening_balance_date = data.get('opening_balance_date')
        
        if blockchain == 'bitcoin':
            balance = balance_raw / 1e8
            opening_balance = float(opening_balance_raw) / 1e8 if opening_balance_raw else None
        elif blockchain == 'solana':
            balance = balance_raw / 1e9  # lamports to SOL
            opening_balance = float(opening_balance_raw) / 1e9 if opening_balance_raw else None
        elif blockchain == 'tron':
            balance = balance_raw / 1e6  # SUN to TRX
            opening_balance = float(opening_balance_raw) / 1e6 if opening_balance_raw else None
        elif blockchain == 'cardano':
            balance = balance_raw / 1e6  # lovelace to ADA
            opening_balance = float(opening_balance_raw) / 1e6 if opening_balance_raw else None
        elif blockchain == 'ethereum' or blockchain in ['polygon', 'bsc', 'arbitrum', 'optimism', 'base', 'blast', 'linea', 'scroll', 'zksync']:
            balance = balance_raw / 1e18
            opening_balance = float(opening_balance_raw) / 1e18 if opening_balance_raw else None
        else:
            balance = balance_raw
            opening_balance = float(opening_balance_raw) if opening_balance_raw else None
        
        transactions = data.get('transactions', [])
        if transactions:
            print(f"DEBUG BACKEND: First 3 transaction amounts: {[tx.get('amount', 'N/A') for tx in transactions[:3]]}")
            print(f"DEBUG BACKEND: Balance raw: {balance_raw}, Balance converted: {balance}")
            if opening_balance:
                print(f"DEBUG BACKEND: Opening balance (as of {opening_balance_date}): {opening_balance}")
        
        # Get token balances and prices for EVM chains and Solana
        token_balances_with_prices = {}
        token_balances = data.get('token_balances', {})
        
        # Get opening token balances (for Solana)
        opening_token_balances = data.get('opening_token_balances', {})
        opening_token_balances_with_prices = {}
        
        # CRITICAL DEBUG: Log what we received from blockchain service
        logger.info(f"🔍 DEBUG: Received {len(token_balances)} tokens from blockchain_service")
        for sym, info in token_balances.items():
            logger.info(f"   → {sym}: balance={info.get('balance', 0)}, contract={info.get('contract', 'N/A')[:20]}...")
        
        if opening_token_balances:
            logger.info(f"🔍 DEBUG: Received {len(opening_token_balances)} opening token balances")
            for sym, info in opening_token_balances.items():
                logger.info(f"   → Opening {sym}: balance={info.get('balance', 0)}")
        
        # Collect all unique token symbols from transactions for price fetching
        transaction_token_symbols = set()
        for tx in transactions:
            token_symbol = tx.get('tokenSymbol') or tx.get('token')
            if token_symbol:
                transaction_token_symbols.add(token_symbol)
        
        # Combine token symbols from balances and transactions
        all_token_symbols = set(token_balances.keys()) | transaction_token_symbols | set(opening_token_balances.keys())
        
        # Fetch prices for all tokens at once (avoids rate limiting in PDF generation)
        token_prices_dict = {}
        if all_token_symbols:
            logger.info(f"Fetching prices for tokens: {all_token_symbols}")
            token_prices_dict = currency_service.get_crypto_prices(list(all_token_symbols))
            logger.info(f"Fetched prices: {token_prices_dict}")
        
        # Get USD to AED exchange rate from currency service
        usd_to_aed_rate = currency_service.get_usd_to_aed_rate()
        logger.info(f"Using USD/AED rate: {usd_to_aed_rate}")
        
        # Combine balance and price data for current token balances
        if token_balances:
            logger.info(f"🔍 DEBUG: Processing {len(token_balances)} tokens for PDF")
            for token_symbol, token_info in token_balances.items():
                token_prices = token_prices_dict.get(token_symbol, {'usd': 0, 'aed': 0})
                
                # Log if price is 0
                if token_prices['usd'] == 0:
                    logger.warning(f"Price for {token_symbol} is 0! Token info: {token_info}")
                
                value_usd = token_info['balance'] * token_prices['usd']
                token_balances_with_prices[token_symbol] = {
                    'balance': token_info['balance'],
                    'contract': token_info['contract'],
                    'name': token_info['name'],
                    'decimals': token_info['decimals'],
                    'price_usd': token_prices['usd'],
                    'price_aed': token_prices['usd'] * usd_to_aed_rate,  # Correct AED price
                    'value_usd': value_usd,
                    'value_aed': value_usd * usd_to_aed_rate  # Correct AED value
                }
                logger.info(f"✅ Added to PDF: {token_symbol}: balance={token_info['balance']}, price_usd={token_prices['usd']}, value_usd={value_usd}")
        
        # Combine balance and price data for opening token balances
        if opening_token_balances:
            logger.info(f"🔍 DEBUG: Processing {len(opening_token_balances)} opening tokens for PDF")
            for token_symbol, token_info in opening_token_balances.items():
                token_prices = token_prices_dict.get(token_symbol, {'usd': 0, 'aed': 0})
                
                value_usd = token_info['balance'] * token_prices['usd']
                opening_token_balances_with_prices[token_symbol] = {
                    'balance': token_info['balance'],
                    'contract': token_info['contract'],
                    'name': token_info['name'],
                    'decimals': token_info['decimals'],
                    'price_usd': token_prices['usd'],
                    'price_aed': token_prices['usd'] * usd_to_aed_rate,
                    'value_usd': value_usd,
                    'value_aed': value_usd * usd_to_aed_rate
                }
                logger.info(f"✅ Added opening balance to PDF: {token_symbol}: balance={token_info['balance']}, value_usd={value_usd}")
        else:
            logger.info("No opening token balances to process")
        
        if not token_balances:
            logger.error("❌ NO TOKEN BALANCES TO PROCESS!")
        
        pdf_bytes = pdf_generator.generate_account_statement(
            address=address,
            blockchain=blockchain,
            transactions=data.get('transactions', []),
            balance=balance,
            crypto_symbol=crypto_symbol,
            prices=prices,
            date_range={'start': start_date, 'end': end_date},
            token_balances=token_balances_with_prices,
            token_prices=token_prices_dict,  # Pass pre-fetched token prices
            usd_to_aed_rate=usd_to_aed_rate,  # Pass exchange rate
            opening_balance=opening_balance,  # Pass opening balance if available
            opening_balance_date=opening_balance_date,  # Pass opening balance date
            opening_token_balances=opening_token_balances_with_prices  # Pass opening token balances
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


@app.route('/api/export-csv', methods=['POST'])
def export_csv():
    """
    Generate CSV export with opening balance and transactions
    Simple format: Opening Balance at START date + All Transactions
    """
    try:
        data = request.json
        blockchain = data.get('blockchain', '').lower()
        address = data.get('address', '')
        start_date = data.get('startDate', '')
        end_date = data.get('endDate', '')
        
        logger.info(f"CSV export request - Chain: {blockchain}, Address: {address}, Period: {start_date} to {end_date}")
        
        if not all([blockchain, address, start_date, end_date]):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Get crypto symbol
        if blockchain == 'bitcoin':
            data = blockchain_service.get_bitcoin_transactions(address, start_date, end_date)
            crypto_symbol = 'BTC'
        elif blockchain == 'solana':
            data = blockchain_service.get_solana_transactions(address, start_date, end_date)
            crypto_symbol = 'SOL'
        elif blockchain == 'tron':
            data = blockchain_service.get_tron_transactions(address, start_date, end_date)
            crypto_symbol = 'TRX'
        elif blockchain == 'cardano':
            data = blockchain_service.get_cardano_transactions(address, start_date, end_date)
            crypto_symbol = 'ADA'
        elif blockchain in CHAIN_IDS:
            chain_id = CHAIN_IDS[blockchain]
            data = blockchain_service.get_ethereum_transactions(address, chain_id, start_date, end_date)
            
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
        
        # Convert balances
        balance_raw = float(data.get('balance', 0))
        opening_balance_raw = data.get('opening_balance')
        
        if blockchain == 'bitcoin':
            current_balance = balance_raw / 1e8
            opening_balance = float(opening_balance_raw) / 1e8 if opening_balance_raw else current_balance
        elif blockchain == 'solana':
            current_balance = balance_raw / 1e9
            opening_balance = float(opening_balance_raw) / 1e9 if opening_balance_raw else current_balance
        elif blockchain == 'tron':
            current_balance = balance_raw / 1e6
            opening_balance = float(opening_balance_raw) / 1e6 if opening_balance_raw else current_balance
        elif blockchain == 'cardano':
            current_balance = balance_raw / 1e6
            opening_balance = float(opening_balance_raw) / 1e6 if opening_balance_raw else current_balance
        elif blockchain in CHAIN_IDS:
            current_balance = balance_raw / 1e18
            opening_balance = float(opening_balance_raw) / 1e18 if opening_balance_raw else current_balance
        else:
            current_balance = balance_raw
            opening_balance = float(opening_balance_raw) if opening_balance_raw else current_balance
        
        # Generate CSV
        csv_content = csv_generator.generate_transaction_csv(
            address=address,
            blockchain=blockchain,
            transactions=data.get('transactions', []),
            opening_balance=opening_balance,
            current_balance=current_balance,
            crypto_symbol=crypto_symbol,
            opening_token_balances=data.get('opening_token_balances'),
            current_token_balances=data.get('token_balances'),
            start_date=start_date,
            end_date=end_date
        )
        
        # Create file buffer
        csv_buffer = io.BytesIO(csv_content.encode('utf-8'))
        csv_buffer.seek(0)
        
        filename = f"{blockchain}_{address[:8]}_transactions_{start_date}_to_{end_date}.csv"
        
        return send_file(
            csv_buffer,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        logger.error(f"Error generating CSV: {str(e)}")
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
