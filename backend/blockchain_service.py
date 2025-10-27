"""
Blockchain Service Module
Handles all blockchain API interactions for multiple chains
"""

import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, max_calls_per_second: int = 5):
        self.max_calls = max_calls_per_second
        self.calls = []
    
    def wait_if_needed(self):
        now = time.time()
        self.calls = [call_time for call_time in self.calls if now - call_time < 1]
        
        if len(self.calls) >= self.max_calls:
            sleep_time = 1 - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                self.calls = []
        
        self.calls.append(time.time())


class BlockchainService:
    """Main service for fetching blockchain data"""
    
    # Chain-specific token whitelists
    WHITELISTED_TOKENS_BY_CHAIN = {
        # Ethereum Mainnet (Chain ID 1)
        1: {
            '0xdac17f958d2ee523a2206206994597c13d831ec7': {'symbol': 'USDT', 'name': 'Tether USD', 'decimals': 6},
            '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': {'symbol': 'USDC', 'name': 'USD Coin', 'decimals': 6},
            '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2': {'symbol': 'WETH', 'name': 'Wrapped Ether', 'decimals': 18},
            '0x6b175474e89094c44da98b954eedeac495271d0f': {'symbol': 'DAI', 'name': 'Dai Stablecoin', 'decimals': 18},
            '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599': {'symbol': 'WBTC', 'name': 'Wrapped Bitcoin', 'decimals': 8},
            '0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0': {'symbol': 'MATIC', 'name': 'Matic Token (Legacy)', 'decimals': 18},
            '0x455e53cbb86018ac2b8092fdcd39d8444affc3f6': {'symbol': 'POL', 'name': 'Polygon Ecosystem Token', 'decimals': 18},
            '0x514910771af9ca656af840dff83e8264ecf986ca': {'symbol': 'LINK', 'name': 'ChainLink Token', 'decimals': 18},
            '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984': {'symbol': 'UNI', 'name': 'Uniswap', 'decimals': 18},
        },
        
        # Polygon (Chain ID 137) - Native token is POL
        137: {
            '0xc2132d05d31c914a87c6611c10748aeb04b58e8f': {'symbol': 'USDT', 'name': 'Tether USD', 'decimals': 6},
            '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359': {'symbol': 'USDC', 'name': 'USD Coin', 'decimals': 6},
            '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619': {'symbol': 'WETH', 'name': 'Wrapped Ether', 'decimals': 18},
            '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270': {'symbol': 'WPOL', 'name': 'Wrapped POL', 'decimals': 18},
            '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063': {'symbol': 'DAI', 'name': 'Dai Stablecoin', 'decimals': 18},
            '0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6': {'symbol': 'WBTC', 'name': 'Wrapped Bitcoin', 'decimals': 8},
            '0x53e0bca35ec356bd5dddfebbd1fc0fd03fabad39': {'symbol': 'LINK', 'name': 'ChainLink Token', 'decimals': 18},
            '0xb33eaad8d922b1083446dc23f610c2567fb5180f': {'symbol': 'UNI', 'name': 'Uniswap', 'decimals': 18},
            '0xd6df932a45c0f255f85145f286ea0b292b21c90b': {'symbol': 'AAVE', 'name': 'Aave Token', 'decimals': 18},
        },
        
        # BSC (Chain ID 56)
        56: {
            '0x55d398326f99059ff775485246999027b3197955': {'symbol': 'USDT', 'name': 'Tether USD', 'decimals': 18},
            '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d': {'symbol': 'USDC', 'name': 'USD Coin', 'decimals': 18},
            '0x2170ed0880ac9a755fd29b2688956bd959f933f8': {'symbol': 'ETH', 'name': 'Ethereum Token', 'decimals': 18},
            '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c': {'symbol': 'WBNB', 'name': 'Wrapped BNB', 'decimals': 18},
            '0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3': {'symbol': 'DAI', 'name': 'Dai Token', 'decimals': 18},
        },
        
        # Arbitrum (Chain ID 42161)
        42161: {
            '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9': {'symbol': 'USDT', 'name': 'Tether USD', 'decimals': 6},
            '0xaf88d065e77c8cc2239327c5edb3a432268e5831': {'symbol': 'USDC', 'name': 'USD Coin', 'decimals': 6},
            '0x82af49447d8a07e3bd95bd0d56f35241523fbab1': {'symbol': 'WETH', 'name': 'Wrapped Ether', 'decimals': 18},
            '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1': {'symbol': 'DAI', 'name': 'Dai Stablecoin', 'decimals': 18},
            '0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f': {'symbol': 'WBTC', 'name': 'Wrapped BTC', 'decimals': 8},
            '0xba5ddd1f9d7f570dc94a51479a000e3bce967196': {'symbol': 'AAVE', 'name': 'Aave Token', 'decimals': 18},
            '0x6ab707aca953edaefbc4fd23ba73294241490620': {'symbol': 'aUSDT', 'name': 'Aave v3 USDT', 'decimals': 6},
            '0x724dc807b04555b71ed48a6896b6f41593b8c637': {'symbol': 'aUSDC', 'name': 'Aave v3 USDC', 'decimals': 6},
            '0x912ce59144191c1204e64559fe8253a0e49e6548': {'symbol': 'ARB', 'name': 'Arbitrum', 'decimals': 18},
        },
        
        # Optimism (Chain ID 10)
        10: {
            '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58': {'symbol': 'USDT', 'name': 'Tether USD', 'decimals': 6},
            '0x0b2c639c533813f4aa9d7837caf62653d097ff85': {'symbol': 'USDC', 'name': 'USD Coin', 'decimals': 6},
            '0x4200000000000000000000000000000000000006': {'symbol': 'WETH', 'name': 'Wrapped Ether', 'decimals': 18},
            '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1': {'symbol': 'DAI', 'name': 'Dai Stablecoin', 'decimals': 18},
        },
        
        # Base (Chain ID 8453)
        8453: {
            '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913': {'symbol': 'USDC', 'name': 'USD Coin', 'decimals': 6},
            '0x4200000000000000000000000000000000000006': {'symbol': 'WETH', 'name': 'Wrapped Ether', 'decimals': 18},
            '0x50c5725949a6f0c72e6c4a641f24049a917db0cb': {'symbol': 'DAI', 'name': 'Dai Stablecoin', 'decimals': 18},
        },
    }
    
    # Backwards compatibility - flatten all tokens
    WHITELISTED_TOKENS = {}
    for chain_id, tokens in WHITELISTED_TOKENS_BY_CHAIN.items():
        WHITELISTED_TOKENS.update(tokens)
    
    # Solana SPL Token Whitelist (stored in lowercase for case-insensitive comparison)
    WHITELISTED_SOLANA_TOKENS = {
        'hnstrzjneey2qoyd5d6t48kw2xymyhwvgt61hm5bahj': {'symbol': 'HNST', 'name': 'Honest', 'decimals': 6},
        'es9vmdgxea8x2fdjrqstqdh7j3z4ntfct3wkxyazxmwg': {'symbol': 'USDC', 'name': 'USD Coin', 'decimals': 6},
        'es9vmfrzacrknmyfld9ryqo9q64i3dqvdwpgvtkdnkp': {'symbol': 'USDT', 'name': 'Tether USD', 'decimals': 6},
        'hz1jovnivvgrgniiyveozevgz58xau3rkwx8eacqbct3': {'symbol': 'PYTH', 'name': 'Pyth Network', 'decimals': 6},
    }
    
    # Tron TRC-20 Token Whitelist (Mainnet)
    WHITELISTED_TRON_TOKENS = {
        'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t': {'symbol': 'USDT', 'name': 'Tether USD', 'decimals': 6},
        'TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8': {'symbol': 'USDC', 'name': 'USD Coin', 'decimals': 6},
        'TNUC9Qb1rRpS5CbWLmNMxXBjyFoydXjWFR': {'symbol': 'WTRX', 'name': 'Wrapped TRX', 'decimals': 6},
        'TKfjV9RNKJJCqPvBtK8L7Knykh7DNWvnYt': {'symbol': 'WBTC', 'name': 'Wrapped BTC', 'decimals': 8},
        'TXpw8XeWYeTUd4quDskoUqeQPowRh4jY65': {'symbol': 'WETH', 'name': 'Wrapped ETH', 'decimals': 18},
    }
    
    def __init__(self, api_key: str, solscan_api_key: str = None, tronscan_api_key: str = None, cardanoscan_api_key: str = None):
        self.api_key = api_key
        self.solscan_api_key = solscan_api_key
        self.tronscan_api_key = tronscan_api_key
        self.cardanoscan_api_key = cardanoscan_api_key
        self.rate_limiter = RateLimiter(max_calls_per_second=2)  # SLOWER to avoid rate limits
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        })
    
    def fetch_with_retry(self, url: str, max_retries: int = 3) -> Dict:
        """Fetch data with automatic retry on failure"""
        for attempt in range(max_retries):
            try:
                self.rate_limiter.wait_if_needed()
                logger.info(f"Fetching: {url[:100]}...")
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                return data
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return {'status': '0', 'result': [], 'message': str(e)}
        
        return {'status': '0', 'result': [], 'message': 'Max retries exceeded'}
    
    def get_token_balances(self, address: str, chain_id: int) -> Dict[str, Dict]:
        """
        Fetch ERC-20 token balances for major tokens
        
        Args:
            address: Wallet address
            chain_id: EVM chain ID
            
        Returns:
            Dict with token balances: {'USDT': {'balance': 1000.50, 'contract': '0x...'}, ...}
        """
        base_url = "https://api.etherscan.io/v2/api"
        token_balances = {}
        
        # Get tokens for this specific chain only
        chain_tokens = self.WHITELISTED_TOKENS_BY_CHAIN.get(chain_id, {})
        
        if not chain_tokens:
            logger.warning(f"No whitelisted tokens configured for chain {chain_id}")
            return {}
        
        logger.info(f"Checking {len(chain_tokens)} tokens for chain {chain_id}")
        
        for contract_address, token_info in chain_tokens.items():
            try:
                # Fetch token balance using Etherscan API
                params = {
                    'chainid': chain_id,
                    'module': 'account',
                    'action': 'tokenbalance',
                    'contractaddress': contract_address,
                    'address': address,
                    'tag': 'latest',
                    'apikey': self.api_key
                }
                
                url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in params.items()])
                data = self.fetch_with_retry(url)
                
                # Check for API errors
                if data.get('status') != '1':
                    error_msg = data.get('message', 'Unknown error')
                    logger.warning(f"API error for {token_info['symbol']}: {error_msg}")
                    if 'rate limit' in error_msg.lower():
                        logger.error(f"⚠️ RATE LIMIT HIT! Slowing down...")
                        time.sleep(1)  # Extra delay on rate limit
                    continue
                
                if data.get('status') == '1' and data.get('result'):
                    # Use decimals from token info (now stored in whitelist)
                    decimals = token_info.get('decimals', 18)
                    
                    balance_raw = int(data['result'])
                    balance = balance_raw / (10 ** decimals)
                    
                    # ONLY include tokens with balance > 0
                    if balance > 0:
                        token_symbol = token_info['symbol']
                        
                        token_balances[token_symbol] = {
                            'balance': balance,
                            'contract': contract_address,
                            'name': token_info['name'],
                            'decimals': decimals
                        }
                        logger.info(f"✅ Token {token_symbol}: balance={balance}")
                    else:
                        logger.debug(f"Skipping {token_info['symbol']} - zero balance")
                else:
                    logger.debug(f"No balance for {token_info['symbol']} at {contract_address}")
                
            except Exception as e:
                logger.warning(f"Error fetching {token_info['symbol']} balance at {contract_address}: {str(e)}")
                continue
        
        logger.info(f"Total tokens with balance: {len(token_balances)}")
        return token_balances
    
    def get_ethereum_transactions(self, address: str, chain_id: int, start_date: str, end_date: str) -> Dict:
        """
        Fetch transactions for Ethereum-like chains using Etherscan V2 API
        
        Args:
            address: Wallet address
            chain_id: EVM chain ID (1=Ethereum, 137=Polygon, 8453=Base, etc.)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Dict with balance and transactions
        """
        base_url = "https://api.etherscan.io/v2/api"
        
        # Convert dates to timestamps
        start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
        end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
        
        # Build API URLs
        params = {
            'chainid': chain_id,
            'apikey': self.api_key,
            'address': address,
            'startblock': 0,
            'endblock': 99999999,
            'sort': 'desc'
        }
        
        # Fetch normal transactions
        normal_params = {**params, 'module': 'account', 'action': 'txlist'}
        normal_url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in normal_params.items()])
        normal_data = self.fetch_with_retry(normal_url)
        
        # Fetch internal transactions
        internal_params = {**params, 'module': 'account', 'action': 'txlistinternal'}
        internal_url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in internal_params.items()])
        internal_data = self.fetch_with_retry(internal_url)
        
        # Fetch token transfers
        token_params = {**params, 'module': 'account', 'action': 'tokentx'}
        token_url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in token_params.items()])
        token_data = self.fetch_with_retry(token_url)
        
        # Fetch current balance
        balance_params = {
            'chainid': chain_id,
            'module': 'account',
            'action': 'balance',
            'address': address,
            'tag': 'latest',
            'apikey': self.api_key
        }
        balance_url = f"{base_url}?" + "&".join([f"{k}={v}" for k, v in balance_params.items()])
        balance_data = self.fetch_with_retry(balance_url)
        
        logger.info(f"Chain {chain_id} responses - Normal: {normal_data.get('status')}, "
                   f"Internal: {internal_data.get('status')}, Token: {token_data.get('status')}, "
                   f"Balance: {balance_data.get('status')}")
        
        # Parse transactions
        transactions = []
        
        # Parse normal transactions
        if normal_data.get('status') == '1' and isinstance(normal_data.get('result'), list):
            for tx in normal_data['result']:
                if start_ts <= int(tx.get('timeStamp', 0)) <= end_ts:
                    transactions.append(self._parse_normal_tx(tx, address))
        
        # Parse internal transactions
        if internal_data.get('status') == '1' and isinstance(internal_data.get('result'), list):
            for tx in internal_data['result']:
                if start_ts <= int(tx.get('timeStamp', 0)) <= end_ts:
                    transactions.append(self._parse_internal_tx(tx, address))
        
        # Parse token transactions (filter out non-whitelisted tokens)
        if token_data.get('status') == '1' and isinstance(token_data.get('result'), list):
            for tx in token_data['result']:
                if start_ts <= int(tx.get('timeStamp', 0)) <= end_ts:
                    parsed_tx = self._parse_token_tx(tx, address)
                    if parsed_tx:  # Only add if token is whitelisted
                        transactions.append(parsed_tx)
        
        # Sort by timestamp
        transactions.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Get native balance
        balance = '0'
        if balance_data.get('status') == '1':
            balance = balance_data.get('result', '0')
        
        # Get token balances (USDT, USDC, WBTC, WETH)
        token_balances = self.get_token_balances(address, chain_id)
        
        return {
            'success': True,
            'balance': balance,
            'token_balances': token_balances,
            'transactions': transactions,
            'count': len(transactions)
        }
    
    def _parse_normal_tx(self, tx: Dict, user_address: str) -> Dict:
        """Parse normal transaction"""
        is_incoming = tx.get('to', '').lower() == user_address.lower()
        value_eth = float(tx.get('value', 0)) / 1e18
        
        return {
            'hash': tx.get('hash'),
            'timestamp': int(tx.get('timeStamp', 0)),
            'date': datetime.fromtimestamp(int(tx.get('timeStamp', 0))).isoformat(),
            'type': 'Transfer',
            'direction': 'in' if is_incoming else 'out',
            'from': tx.get('from', 'Unknown'),
            'to': tx.get('to', 'Unknown'),
            'amount': value_eth,
            'token': None,
            'tokenSymbol': None,
            'status': 'Success' if tx.get('isError') == '0' else 'Failed',
            'gasUsed': int(tx.get('gasUsed', 0)),
            'gasPrice': float(tx.get('gasPrice', 0)) / 1e9,
            'blockNumber': int(tx.get('blockNumber', 0)),
            'confirmations': int(tx.get('confirmations', 0))
        }
    
    def _parse_internal_tx(self, tx: Dict, user_address: str) -> Dict:
        """Parse internal transaction"""
        is_incoming = tx.get('to', '').lower() == user_address.lower()
        value_eth = float(tx.get('value', 0)) / 1e18
        
        return {
            'hash': tx.get('hash'),
            'timestamp': int(tx.get('timeStamp', 0)),
            'date': datetime.fromtimestamp(int(tx.get('timeStamp', 0))).isoformat(),
            'type': 'Internal Transfer',
            'direction': 'in' if is_incoming else 'out',
            'from': tx.get('from', 'Unknown'),
            'to': tx.get('to', 'Unknown'),
            'amount': value_eth,
            'token': None,
            'tokenSymbol': None,
            'status': 'Success' if tx.get('isError') == '0' else 'Failed',
            'gasUsed': 0,
            'gasPrice': 0,
            'blockNumber': int(tx.get('blockNumber', 0)),
            'confirmations': 0
        }
    
    def _is_whitelisted_token(self, contract_address: str) -> bool:
        """Check if a token contract address is in the whitelist"""
        if not contract_address:
            return False
        return contract_address.lower() in self.WHITELISTED_TOKENS
    
    def _parse_token_tx(self, tx: Dict, user_address: str) -> Optional[Dict]:
        """Parse token transaction - returns None if token is not whitelisted"""
        contract_address = tx.get('contractAddress', '')
        
        # Filter out non-whitelisted tokens (spam/dusting attacks)
        if not self._is_whitelisted_token(contract_address):
            logger.debug(f"Filtering out non-whitelisted token: {tx.get('tokenSymbol', 'Unknown')} at {contract_address}")
            return None
        
        is_incoming = tx.get('to', '').lower() == user_address.lower()
        decimals = int(tx.get('tokenDecimal', 18))
        value = float(tx.get('value', 0)) / (10 ** decimals)
        
        return {
            'hash': tx.get('hash'),
            'timestamp': int(tx.get('timeStamp', 0)),
            'date': datetime.fromtimestamp(int(tx.get('timeStamp', 0))).isoformat(),
            'type': 'Token Transfer',
            'direction': 'in' if is_incoming else 'out',
            'from': tx.get('from', 'Unknown'),
            'to': tx.get('to', 'Unknown'),
            'amount': value,
            'token': tx.get('tokenSymbol', 'Unknown'),
            'tokenSymbol': tx.get('tokenSymbol', 'Unknown'),
            'tokenName': tx.get('tokenName', 'Unknown Token'),
            'status': 'Success',
            'gasUsed': int(tx.get('gasUsed', 0)),
            'gasPrice': float(tx.get('gasPrice', 0)) / 1e9,
            'blockNumber': int(tx.get('blockNumber', 0)),
            'confirmations': int(tx.get('confirmations', 0)),
            'contractAddress': contract_address
        }
    
    def get_bitcoin_transactions(self, address: str, start_date: str, end_date: str) -> Dict:
        """Fetch Bitcoin transactions using blockchain.info API"""
        try:
            url = f"https://blockchain.info/rawaddr/{address}"
            data = self.fetch_with_retry(url)
            
            if not data or 'txs' not in data:
                return {'success': False, 'error': 'No data found', 'transactions': []}
            
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            transactions = []
            for tx in data.get('txs', []):
                if start_ts <= tx.get('time', 0) <= end_ts:
                    transactions.append(self._parse_bitcoin_tx(tx, address))
            
            balance = data.get('final_balance', 0) / 1e8  # Convert satoshis to BTC
            
            return {
                'success': True,
                'balance': str(int(balance * 1e8)),  # Return as satoshis string
                'transactions': transactions,
                'count': len(transactions)
            }
        except Exception as e:
            logger.error(f"Bitcoin fetch error: {str(e)}")
            return {'success': False, 'error': str(e), 'transactions': []}
    
    def _parse_bitcoin_tx(self, tx: Dict, user_address: str) -> Dict:
        """Parse Bitcoin transaction"""
        # Calculate if incoming or outgoing
        value_in = sum(out.get('value', 0) for out in tx.get('inputs', []))
        value_out = sum(out.get('value', 0) for out in tx.get('out', []))
        
        # Check if user received funds
        user_received = sum(
            out.get('value', 0) for out in tx.get('out', [])
            if out.get('addr') == user_address
        )
        
        is_incoming = user_received > 0
        amount = user_received / 1e8 if is_incoming else (value_out / 1e8)
        
        return {
            'hash': tx.get('hash'),
            'timestamp': tx.get('time', 0),
            'date': datetime.fromtimestamp(tx.get('time', 0)).isoformat(),
            'type': 'Transfer',
            'direction': 'in' if is_incoming else 'out',
            'from': 'Multiple' if len(tx.get('inputs', [])) > 1 else 'Bitcoin Network',
            'to': 'Multiple' if len(tx.get('out', [])) > 1 else 'Bitcoin Network',
            'amount': amount,
            'token': None,
            'tokenSymbol': None,
            'status': 'Success',
            'gasUsed': 0,
            'gasPrice': 0,
            'blockNumber': tx.get('block_height', 0),
            'confirmations': 0
        }
    
    def get_solana_transactions(self, address: str, start_date: str, end_date: str) -> Dict:
        """
        Fetch Solana transactions using public Solana RPC
        Note: Solscan Pro API v2.0 requires paid subscription, using free RPC instead
        """
        try:
            # Use public Solana RPC endpoint (FREE)
            rpc_url = "https://api.mainnet-beta.solana.com"
            
            # Get account balance
            balance_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getBalance",
                "params": [address]
            }
            
            self.rate_limiter.wait_if_needed()
            balance_response = requests.post(rpc_url, json=balance_payload, timeout=30)
            balance_response.raise_for_status()
            balance_data = balance_response.json()
            
            # Get lamports balance
            lamports = 0
            if 'result' in balance_data and 'value' in balance_data['result']:
                lamports = balance_data['result']['value']
            
            # Get transaction signatures
            sig_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getSignaturesForAddress",
                "params": [
                    address,
                    {
                        "limit": 100  # Max signatures to fetch
                    }
                ]
            }
            
            self.rate_limiter.wait_if_needed()
            sig_response = requests.post(rpc_url, json=sig_payload, timeout=30)
            sig_response.raise_for_status()
            sig_data = sig_response.json()
            
            # Parse transactions
            transactions = []
            if 'result' in sig_data:
                # Convert dates to timestamps
                start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
                end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
                
                for sig_info in sig_data['result'][:20]:  # Limit to 20 transactions to avoid timeout
                    # Check if transaction is in date range
                    tx_time = sig_info.get('blockTime', 0)
                    if tx_time and start_ts <= tx_time <= end_ts:
                        # Get transaction details
                        tx_payload = {
                            "jsonrpc": "2.0",
                            "id": 1,
                            "method": "getTransaction",
                            "params": [
                                sig_info['signature'],
                                {
                                    "encoding": "jsonParsed",
                                    "maxSupportedTransactionVersion": 0
                                }
                            ]
                        }
                        
                        self.rate_limiter.wait_if_needed()
                        tx_response = requests.post(rpc_url, json=tx_payload, timeout=30)
                        if tx_response.status_code == 200:
                            tx_data = tx_response.json()
                            if 'result' in tx_data and tx_data['result']:
                                parsed_tx = self._parse_solana_tx(tx_data['result'], address, sig_info['signature'])
                                if parsed_tx:
                                    transactions.append(parsed_tx)
            
            logger.info(f"Found {len(transactions)} Solana transactions for {address}")
            
            # Get SPL token balances
            token_balances = self.get_solana_token_balances(address)
            
            return {
                'success': True,
                'balance': str(int(lamports)),  # Return as lamports string
                'transactions': transactions,
                'token_balances': token_balances,
                'count': len(transactions)
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Solana RPC error: {str(e)}")
            return {
                'success': False,
                'error': f'Solana RPC error: {str(e)}',
                'balance': '0',
                'transactions': [],
                'count': 0
            }
        except Exception as e:
            logger.error(f"Solana fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'balance': '0',
                'transactions': [],
                'count': 0
            }
    
    def get_solana_token_balances(self, address: str) -> Dict[str, Dict]:
        """
        Get SPL token balances for a Solana address
        Returns dict of token_symbol -> balance info
        """
        try:
            rpc_url = "https://api.mainnet-beta.solana.com"
            token_balances = {}
            
            # Get all token accounts for this address
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "getTokenAccountsByOwner",
                "params": [
                    address,
                    {
                        "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # SPL Token Program
                    },
                    {
                        "encoding": "jsonParsed"
                    }
                ]
            }
            
            self.rate_limiter.wait_if_needed()
            response = requests.post(rpc_url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'result' in data and 'value' in data['result']:
                for account in data['result']['value']:
                    try:
                        account_data = account.get('account', {})
                        parsed_data = account_data.get('data', {}).get('parsed', {})
                        info = parsed_data.get('info', {})
                        
                        # Get mint address (token contract)
                        mint = info.get('mint', '').lower()
                        
                        # Check if token is whitelisted
                        if mint in self.WHITELISTED_SOLANA_TOKENS:
                            token_info = self.WHITELISTED_SOLANA_TOKENS[mint]
                            
                            # Get token balance
                            token_amount = info.get('tokenAmount', {})
                            balance = float(token_amount.get('uiAmount', 0))
                            decimals = token_amount.get('decimals', token_info.get('decimals', 6))
                            
                            if balance > 0:  # Only include tokens with balance
                                token_balances[token_info['symbol']] = {
                                    'balance': balance,
                                    'contract': mint,
                                    'name': token_info['name'],
                                    'decimals': decimals
                                }
                                logger.info(f"Found {token_info['symbol']} balance: {balance}")
                    
                    except Exception as e:
                        logger.warning(f"Error parsing token account: {str(e)}")
                        continue
            
            return token_balances
            
        except Exception as e:
            logger.error(f"Error fetching Solana token balances: {str(e)}")
            return {}
    
    def _parse_solana_tx(self, tx: Dict, user_address: str, signature: str) -> Dict:
        """Parse Solana transaction from RPC response"""
        try:
            meta = tx.get('meta', {})
            transaction = tx.get('transaction', {})
            message = transaction.get('message', {})
            
            # Get timestamp
            block_time = tx.get('blockTime', 0)
            
            # Get account keys
            account_keys = message.get('accountKeys', [])
            if not account_keys:
                return None
            
            # Check for SPL token transfers in parsed instructions
            token_transfer = None
            token_info = None
            instructions = message.get('instructions', [])
            
            for instruction in instructions:
                if isinstance(instruction, dict):
                    parsed = instruction.get('parsed', {})
                    if isinstance(parsed, dict):
                        instruction_type = parsed.get('type', '')
                        
                        # Check for SPL token transfer
                        if instruction_type in ['transfer', 'transferChecked']:
                            info = parsed.get('info', {})
                            mint = info.get('mint', '').lower()
                            
                            # Check if token is whitelisted
                            if mint in self.WHITELISTED_SOLANA_TOKENS:
                                token_info = self.WHITELISTED_SOLANA_TOKENS[mint]
                                token_transfer = {
                                    'mint': mint,
                                    'source': info.get('source', ''),
                                    'destination': info.get('destination', ''),
                                    'amount': info.get('amount', '0'),
                                    'tokenAmount': info.get('tokenAmount', {}),
                                    'authority': info.get('authority', '')
                                }
                                break
            
            # If this is a whitelisted SPL token transfer
            if token_transfer and token_info:
                # Get amount with proper decimals
                token_amount_info = token_transfer.get('tokenAmount', {})
                if token_amount_info:
                    amount = float(token_amount_info.get('uiAmount', 0))
                else:
                    # Fallback: use raw amount and decimals
                    raw_amount = int(token_transfer.get('amount', 0))
                    decimals = token_info.get('decimals', 6)
                    amount = raw_amount / (10 ** decimals)
                
                # Determine direction
                destination = token_transfer.get('destination', '')
                source = token_transfer.get('source', '')
                is_incoming = destination.lower() == user_address.lower()
                
                return {
                    'hash': signature,
                    'timestamp': block_time,
                    'date': datetime.fromtimestamp(block_time).isoformat() if block_time else 'Unknown',
                    'type': 'Token Transfer',
                    'direction': 'in' if is_incoming else 'out',
                    'from': source,
                    'to': destination,
                    'amount': amount,
                    'token': token_info['symbol'],
                    'tokenSymbol': token_info['symbol'],
                    'tokenName': token_info['name'],
                    'status': 'Failed' if meta.get('err') else 'Success',
                    'gasUsed': 0,
                    'gasPrice': 0,
                    'blockNumber': tx.get('slot', 0),
                    'confirmations': 0,
                    'fee': meta.get('fee', 0) / 1e9
                }
            
            # Otherwise, parse as SOL transfer
            # Get pre and post balances
            pre_balances = meta.get('preBalances', [])
            post_balances = meta.get('postBalances', [])
            
            # Find user's account index
            user_index = -1
            for i, key in enumerate(account_keys):
                key_str = key if isinstance(key, str) else key.get('pubkey', '')
                if key_str == user_address:
                    user_index = i
                    break
            
            if user_index == -1:
                return None
            
            # Calculate balance change
            balance_change = 0
            if user_index < len(pre_balances) and user_index < len(post_balances):
                balance_change = post_balances[user_index] - pre_balances[user_index]
            
            # Determine direction
            is_incoming = balance_change > 0
            amount = abs(balance_change) / 1e9  # Convert lamports to SOL
            
            # Get fee
            fee = meta.get('fee', 0) / 1e9
            
            # Try to find sender and receiver
            from_address = ''
            to_address = ''
            if len(account_keys) >= 2:
                from_key = account_keys[0] if isinstance(account_keys[0], str) else account_keys[0].get('pubkey', '')
                to_key = account_keys[1] if isinstance(account_keys[1], str) else account_keys[1].get('pubkey', '')
                from_address = from_key
                to_address = to_key
            
            # Check if it's an error transaction
            err = meta.get('err')
            status = 'Failed' if err else 'Success'
            
            return {
                'hash': signature,
                'timestamp': block_time,
                'date': datetime.fromtimestamp(block_time).isoformat() if block_time else 'Unknown',
                'type': 'SOL Transfer',
                'direction': 'in' if is_incoming else 'out',
                'from': from_address,
                'to': to_address,
                'amount': amount,
                'token': None,
                'tokenSymbol': None,
                'tokenName': None,
                'status': status,
                'gasUsed': 0,
                'gasPrice': 0,
                'blockNumber': tx.get('slot', 0),
                'confirmations': 0,
                'fee': fee
            }
        except Exception as e:
            logger.error(f"Error parsing Solana transaction: {str(e)}")
            return None
    
    def get_tron_transactions(self, address: str, start_date: str, end_date: str) -> Dict:
        """
        Fetch Tron transactions using TronScan API
        
        Args:
            address: Tron wallet address (base58 format)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Dict with balance and transactions
        """
        try:
            base_url = "https://apilist.tronscanapi.com/api"
            
            # Convert dates to timestamps (milliseconds)
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp() * 1000)
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp() * 1000)
            
            # Get account info (balance)
            account_url = f"{base_url}/account?address={address}"
            self.rate_limiter.wait_if_needed()
            account_response = self.session.get(account_url, timeout=30)
            account_response.raise_for_status()
            account_data = account_response.json()
            
            # Get balance in SUN (1 TRX = 1,000,000 SUN)
            balance_sun = account_data.get('balance', 0)
            
            # Get TRX transfers
            transactions = []
            trx_url = f"{base_url}/transaction?sort=-timestamp&count=true&limit=50&start=0&address={address}"
            self.rate_limiter.wait_if_needed()
            trx_response = self.session.get(trx_url, timeout=30)
            trx_response.raise_for_status()
            trx_data = trx_response.json()
            
            # Parse TRX transactions
            if trx_data.get('data'):
                for tx in trx_data['data']:
                    tx_time = tx.get('timestamp', 0)
                    if start_ts <= tx_time <= end_ts:
                        parsed_tx = self._parse_tron_tx(tx, address)
                        if parsed_tx:
                            transactions.append(parsed_tx)
            
            # Get TRC-20 token transfers
            trc20_url = f"{base_url}/token_trc20/transfers?relatedAddress={address}&limit=50&start=0"
            self.rate_limiter.wait_if_needed()
            trc20_response = self.session.get(trc20_url, timeout=30)
            trc20_response.raise_for_status()
            trc20_data = trc20_response.json()
            
            # Parse TRC-20 transactions
            if trc20_data.get('token_transfers'):
                for tx in trc20_data['token_transfers']:
                    tx_time = tx.get('block_ts', 0)
                    if start_ts <= tx_time <= end_ts:
                        parsed_tx = self._parse_tron_trc20_tx(tx, address)
                        if parsed_tx:
                            transactions.append(parsed_tx)
            
            # Sort by timestamp
            transactions.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Get TRC-20 token balances
            token_balances = self.get_tron_token_balances(address)
            
            return {
                'success': True,
                'balance': str(balance_sun),  # Return as SUN string
                'token_balances': token_balances,
                'transactions': transactions,
                'count': len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Tron fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'balance': '0',
                'transactions': [],
                'count': 0
            }
    
    def get_tron_token_balances(self, address: str) -> Dict[str, Dict]:
        """Get TRC-20 token balances for a Tron address"""
        try:
            base_url = "https://apilist.tronscanapi.com/api"
            token_balances = {}
            
            # Get account tokens
            url = f"{base_url}/account/tokens?address={address}&start=0&limit=20"
            self.rate_limiter.wait_if_needed()
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('data'):
                for token in data['data']:
                    contract_address = token.get('tokenId', '').strip()
                    
                    # Check if token is whitelisted
                    if contract_address in self.WHITELISTED_TRON_TOKENS:
                        token_info = self.WHITELISTED_TRON_TOKENS[contract_address]
                        
                        # Get balance
                        balance_raw = float(token.get('balance', 0))
                        decimals = token_info.get('decimals', 6)
                        balance = balance_raw / (10 ** decimals)
                        
                        if balance > 0:
                            token_balances[token_info['symbol']] = {
                                'balance': balance,
                                'contract': contract_address,
                                'name': token_info['name'],
                                'decimals': decimals
                            }
                            logger.info(f"Found Tron {token_info['symbol']} balance: {balance}")
            
            return token_balances
            
        except Exception as e:
            logger.error(f"Error fetching Tron token balances: {str(e)}")
            return {}
    
    def _parse_tron_tx(self, tx: Dict, user_address: str) -> Optional[Dict]:
        """Parse Tron TRX transaction"""
        try:
            # Get transaction details
            tx_hash = tx.get('hash', '')
            timestamp = tx.get('timestamp', 0) // 1000  # Convert ms to seconds
            
            # Determine direction and amount
            owner_address = tx.get('ownerAddress', '')
            to_address = tx.get('toAddress', '')
            is_incoming = to_address == user_address
            
            # Get amount (in SUN, convert to TRX)
            amount_sun = tx.get('amount', 0)
            amount_trx = amount_sun / 1_000_000
            
            # Check contract type
            contract_type = tx.get('contractType', '')
            
            return {
                'hash': tx_hash,
                'timestamp': timestamp,
                'date': datetime.fromtimestamp(timestamp).isoformat() if timestamp else 'Unknown',
                'type': 'TRX Transfer',
                'direction': 'in' if is_incoming else 'out',
                'from': owner_address,
                'to': to_address,
                'amount': amount_trx,
                'token': None,
                'tokenSymbol': None,
                'status': 'Success' if tx.get('confirmed') else 'Pending',
                'gasUsed': 0,
                'gasPrice': 0,
                'blockNumber': tx.get('block', 0),
                'confirmations': 0
            }
        except Exception as e:
            logger.error(f"Error parsing Tron transaction: {str(e)}")
            return None
    
    def _parse_tron_trc20_tx(self, tx: Dict, user_address: str) -> Optional[Dict]:
        """Parse Tron TRC-20 token transaction"""
        try:
            contract_address = tx.get('contract_address', '').strip()
            
            # Filter out non-whitelisted tokens
            if contract_address not in self.WHITELISTED_TRON_TOKENS:
                return None
            
            token_info = self.WHITELISTED_TRON_TOKENS[contract_address]
            
            # Get transaction details
            tx_hash = tx.get('transaction_id', '')
            timestamp = tx.get('block_ts', 0) // 1000  # Convert ms to seconds
            
            from_address = tx.get('from_address', '')
            to_address = tx.get('to_address', '')
            is_incoming = to_address == user_address
            
            # Get amount with decimals
            amount_raw = float(tx.get('quant', 0))
            decimals = token_info.get('decimals', 6)
            amount = amount_raw / (10 ** decimals)
            
            return {
                'hash': tx_hash,
                'timestamp': timestamp,
                'date': datetime.fromtimestamp(timestamp).isoformat() if timestamp else 'Unknown',
                'type': 'TRC-20 Transfer',
                'direction': 'in' if is_incoming else 'out',
                'from': from_address,
                'to': to_address,
                'amount': amount,
                'token': token_info['symbol'],
                'tokenSymbol': token_info['symbol'],
                'tokenName': token_info['name'],
                'status': 'Success' if tx.get('confirmed') else 'Pending',
                'gasUsed': 0,
                'gasPrice': 0,
                'blockNumber': tx.get('block', 0),
                'confirmations': 0,
                'contractAddress': contract_address
            }
        except Exception as e:
            logger.error(f"Error parsing Tron TRC-20 transaction: {str(e)}")
            return None
    
    def get_cardano_transactions(self, address: str, start_date: str, end_date: str) -> Dict:
        """
        Fetch Cardano transactions using CardanoScan API
        
        Args:
            address: Cardano wallet address (stake address or payment address)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            Dict with balance and transactions
        """
        try:
            base_url = "https://api.cardanoscan.io/api/v1"
            headers = {}
            if self.cardanoscan_api_key:
                headers['apiKey'] = self.cardanoscan_api_key
            
            # Convert dates to timestamps
            start_ts = int(datetime.strptime(start_date, '%Y-%m-%d').timestamp())
            end_ts = int(datetime.strptime(end_date, '%Y-%m-%d').timestamp())
            
            # Get account info
            account_url = f"{base_url}/account/{address}"
            self.rate_limiter.wait_if_needed()
            account_response = self.session.get(account_url, headers=headers, timeout=30)
            account_response.raise_for_status()
            account_data = account_response.json()
            
            # Get balance in lovelace (1 ADA = 1,000,000 lovelace)
            balance_lovelace = account_data.get('balance', 0)
            
            # Get transactions
            transactions = []
            tx_url = f"{base_url}/account/{address}/transactions?page=1&pageSize=50"
            self.rate_limiter.wait_if_needed()
            tx_response = self.session.get(tx_url, headers=headers, timeout=30)
            tx_response.raise_for_status()
            tx_data = tx_response.json()
            
            # Parse transactions
            if tx_data.get('data'):
                for tx in tx_data['data']:
                    tx_time = tx.get('time', 0)
                    if start_ts <= tx_time <= end_ts:
                        parsed_tx = self._parse_cardano_tx(tx, address)
                        if parsed_tx:
                            transactions.append(parsed_tx)
            
            # Sort by timestamp
            transactions.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return {
                'success': True,
                'balance': str(balance_lovelace),  # Return as lovelace string
                'token_balances': {},  # Native tokens can be added later
                'transactions': transactions,
                'count': len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Cardano fetch error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'balance': '0',
                'transactions': [],
                'count': 0
            }
    
    def _parse_cardano_tx(self, tx: Dict, user_address: str) -> Optional[Dict]:
        """Parse Cardano transaction"""
        try:
            tx_hash = tx.get('hash', '')
            timestamp = tx.get('time', 0)
            
            # Get inputs and outputs
            inputs = tx.get('inputs', [])
            outputs = tx.get('outputs', [])
            
            # Calculate if incoming or outgoing
            user_input_sum = sum(
                int(inp.get('value', 0)) for inp in inputs 
                if inp.get('address') == user_address
            )
            user_output_sum = sum(
                int(out.get('value', 0)) for out in outputs 
                if out.get('address') == user_address
            )
            
            # Net change for user
            net_change = user_output_sum - user_input_sum
            is_incoming = net_change > 0
            amount_lovelace = abs(net_change)
            amount_ada = amount_lovelace / 1_000_000
            
            # Get from/to addresses
            from_address = inputs[0].get('address', 'Multiple') if inputs else 'Unknown'
            to_address = outputs[0].get('address', 'Multiple') if outputs else 'Unknown'
            
            return {
                'hash': tx_hash,
                'timestamp': timestamp,
                'date': datetime.fromtimestamp(timestamp).isoformat() if timestamp else 'Unknown',
                'type': 'ADA Transfer',
                'direction': 'in' if is_incoming else 'out',
                'from': from_address,
                'to': to_address,
                'amount': amount_ada,
                'token': None,
                'tokenSymbol': None,
                'status': 'Success',
                'gasUsed': 0,
                'gasPrice': 0,
                'blockNumber': tx.get('block', 0),
                'confirmations': tx.get('confirmations', 0),
                'fee': tx.get('fee', 0) / 1_000_000  # Convert lovelace to ADA
            }
        except Exception as e:
            logger.error(f"Error parsing Cardano transaction: {str(e)}")
            return None


