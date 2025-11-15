from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from blockchain_service import BlockchainService
from database_service import DatabaseService
from currency_service import CurrencyExchangeService
# from pdf_generator import PDFReportGenerator  # Old RPC-based generator
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

# Database configuration
DB_HOST = os.getenv('DB_HOST', '217.216.110.33')
DB_PORT = int(os.getenv('DB_PORT', '3306'))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'nobicuan888')
DB_NAME = os.getenv('DB_NAME', 'nobi_wallet_tracker')

if not ETHERSCAN_API_KEY:
    logger.warning("ETHERSCAN_API_KEY not found in environment variables!")
if not SOLSCAN_API_KEY:
    logger.warning("SOLSCAN_API_KEY not found in environment variables - Solana support will be limited!")
if not TRONSCAN_API_KEY:
    logger.warning("TRONSCAN_API_KEY not found - Tron support will use free tier with limits!")
if not CARDANOSCAN_API_KEY:
    logger.warning("CARDANOSCAN_API_KEY not found - Cardano support will use free tier with limits!")

# Initialize services
blockchain_service = BlockchainService(
    api_key=ETHERSCAN_API_KEY, 
    solscan_api_key=SOLSCAN_API_KEY,
    tronscan_api_key=TRONSCAN_API_KEY,
    cardanoscan_api_key=CARDANOSCAN_API_KEY
)
currency_service = CurrencyExchangeService()
# pdf_generator = PDFReportGenerator()  # Old generator - now using database-based generation
csv_generator = CSVGenerator()

# Initialize database service
database_service = DatabaseService(
    host=DB_HOST,
    port=DB_PORT,
    username=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

# Connect to database on startup
if not database_service.connect():
    logger.error("Failed to connect to database on startup!")
else:
    logger.info("✅ Database service connected successfully")

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


@app.route('/api/analyze-db/<address>', methods=['GET'])
def analyze_wallet_from_database(address):
    """
    Analyze wallet using database (replaces RPC-based approach)
    
    Query Parameters:
        - start_date: Opening balance date (YYYY-MM-DD)
        - end_date: Current balance date (YYYY-MM-DD)
        - network: Optional network filter (eth-mainnet, sol-mainnet, etc.)
    
    Returns:
        {
            "success": true,
            "wallet_address": "0x...",
            "opening_date": "2025-03-31",
            "end_date": "2025-11-15",
            "network": "eth-mainnet",
            "opening_balance": {"ETH": 10.5, "USDC": 1000},
            "current_balance": {"ETH": 15.2, "USDC": 1200},
            "transactions": [...],
            "transactions_counted_for_opening": 150,
            "total_transactions_in_period": 25
        }
    """
    try:
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        network = request.args.get('network')
        
        if not start_date:
            return jsonify({
                'success': False,
                'error': 'start_date parameter is required (format: YYYY-MM-DD)'
            }), 400
        
        logger.info(f"Analyzing wallet {address} from database")
        logger.info(f"  Opening date: {start_date}")
        logger.info(f"  End date: {end_date or 'current'}")
        logger.info(f"  Network: {network or 'all'}")
        
        # Calculate opening balance
        opening_balance_result = database_service.calculate_opening_balance(
            address, 
            start_date, 
            network
        )
        
        # Calculate current balance
        current_balance_result = database_service.get_current_balance(
            address, 
            end_date, 
            network
        )
        
        # Get transactions in period
        transactions = database_service.get_transactions_in_period(
            address, 
            start_date, 
            end_date or current_balance_result['current_date'],
            network
        )
        
        # Format response
        response = {
            'success': True,
            'wallet_address': address,
            'opening_date': opening_balance_result['opening_date'],
            'end_date': current_balance_result['current_date'],
            'network': network or 'all',
            'opening_balance': opening_balance_result['balances'],
            'current_balance': current_balance_result['balances'],
            'transactions': transactions,
            'transactions_counted_for_opening': opening_balance_result['transactions_counted'],
            'total_transactions_in_period': len(transactions)
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error analyzing wallet from database: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/export-pdf-db/<address>', methods=['GET'])
def export_pdf_db(address):
    """Export wallet statement as PDF using database data"""
    try:
        # Import PDF generator
        from pdf_generator import generate_pdf_statement
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        network = request.args.get('network')
        
        if not start_date:
            return jsonify({
                'success': False,
                'error': 'start_date parameter is required'
            }), 400
        
        logger.info(f"Generating PDF for wallet {address}")
        
        # Get data from database
        opening_balance_result = database_service.calculate_opening_balance(address, start_date, network)
        current_balance_result = database_service.get_current_balance(address, end_date, network)
        transactions = database_service.get_transactions_in_period(
            address, 
            start_date, 
            end_date or current_balance_result['current_date'],
            network
        )
        
        # Generate PDF
        pdf_bytes = generate_pdf_statement(
            wallet_address=address,
            opening_date=start_date,
            end_date=end_date or current_balance_result['current_date'],
            opening_balance=opening_balance_result['balances'],
            current_balance=current_balance_result['balances'],
            transactions=transactions,
            network=network
        )
        
        # Return PDF file
        from flask import make_response
        response = make_response(pdf_bytes)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=statement_{address[:8]}_{start_date}.pdf'
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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
        
        transactions = data.get('transactions', [])
        
        # Generate CSV
        csv_content = csv_generator.generate_transaction_csv(
            address=address,
            blockchain=blockchain,
            transactions=transactions,  # Use the transactions variable (might be manual override)
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
