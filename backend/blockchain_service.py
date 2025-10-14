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
    
    WHITELISTED_TOKENS = {
        # Ethereum Mainnet (Chain ID 1)
        '0xdac17f958d2ee523a2206206994597c13d831ec7': {'symbol': 'USDT', 'name': 'Tether USD'},
        '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': {'symbol': 'USDC', 'name': 'USD Coin'},
        '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2': {'symbol': 'WETH', 'name': 'Wrapped Ether'},
        '0x6b175474e89094c44da98b954eedeac495271d0f': {'symbol': 'DAI', 'name': 'Dai Stablecoin'},
        '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599': {'symbol': 'WBTC', 'name': 'Wrapped Bitcoin'},
        '0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0': {'symbol': 'MATIC', 'name': 'Matic Token'},
        '0x514910771af9ca656af840dff83e8264ecf986ca': {'symbol': 'LINK', 'name': 'ChainLink Token'},
        '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984': {'symbol': 'UNI', 'name': 'Uniswap'},
        
        # Polygon (Chain ID 137)
        '0xc2132d05d31c914a87c6611c10748aeb04b58e8f': {'symbol': 'USDT', 'name': 'Tether USD'},
        '0x2791bca1f2de4661ed88a30c99a7a9449aa84174': {'symbol': 'USDC', 'name': 'USD Coin'},
        '0x7ceb23fd6bc0add59e62ac25578270cff1b9f619': {'symbol': 'WETH', 'name': 'Wrapped Ether'},
        '0x0d500b1d8e8ef31e21c99d1db9a6444d3adf1270': {'symbol': 'WMATIC', 'name': 'Wrapped Matic'},
        '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063': {'symbol': 'DAI', 'name': 'Dai Stablecoin'},
        '0x1bfd67037b42cf73acf2047067bd4f2c47d9bfd6': {'symbol': 'WBTC', 'name': 'Wrapped Bitcoin'},
        '0x53e0bca35ec356bd5dddfebbd1fc0fd03fabad39': {'symbol': 'LINK', 'name': 'ChainLink Token'},
        '0xb33eaad8d922b1083446dc23f610c2567fb5180f': {'symbol': 'UNI', 'name': 'Uniswap'},
        '0xd6df932a45c0f255f85145f286ea0b292b21c90b': {'symbol': 'AAVE', 'name': 'Aave Token'},
        
        # BSC (Chain ID 56)
        '0x55d398326f99059ff775485246999027b3197955': {'symbol': 'USDT', 'name': 'Tether USD'},
        '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d': {'symbol': 'USDC', 'name': 'USD Coin'},
        '0x2170ed0880ac9a755fd29b2688956bd959f933f8': {'symbol': 'ETH', 'name': 'Ethereum Token'},
        '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c': {'symbol': 'WBNB', 'name': 'Wrapped BNB'},
        '0x1af3f329e8be154074d8769d1ffa4ee058b1dbc3': {'symbol': 'DAI', 'name': 'Dai Token'},
        
        # Arbitrum (Chain ID 42161)
        '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9': {'symbol': 'USDT', 'name': 'Tether USD'},
        '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8': {'symbol': 'USDC', 'name': 'USD Coin'},
        '0x82af49447d8a07e3bd95bd0d56f35241523fbab1': {'symbol': 'WETH', 'name': 'Wrapped Ether'},
        '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1': {'symbol': 'DAI', 'name': 'Dai Stablecoin'},
        '0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f': {'symbol': 'WBTC', 'name': 'Wrapped BTC'},
        
        # Optimism (Chain ID 10)
        '0x94b008aa00579c1307b0ef2c499ad98a8ce58e58': {'symbol': 'USDT', 'name': 'Tether USD'},
        '0x7f5c764cbc14f9669b88837ca1490cca17c31607': {'symbol': 'USDC', 'name': 'USD Coin'},
        '0x4200000000000000000000000000000000000006': {'symbol': 'WETH', 'name': 'Wrapped Ether'},
        '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1': {'symbol': 'DAI', 'name': 'Dai Stablecoin'},
        
        # Base (Chain ID 8453)
        '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913': {'symbol': 'USDC', 'name': 'USD Coin'},
        '0x4200000000000000000000000000000000000006': {'symbol': 'WETH', 'name': 'Wrapped Ether'},
        '0x50c5725949a6f0c72e6c4a641f24049a917db0cb': {'symbol': 'DAI', 'name': 'Dai Stablecoin'},
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rate_limiter = RateLimiter(max_calls_per_second=5)
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
        Fetch ERC-20 token balances for major tokens (USDT, USDC, WBTC, WETH)
        
        Args:
            address: Wallet address
            chain_id: EVM chain ID
            
        Returns:
            Dict with token balances: {'USDT': {'balance': 1000.50, 'contract': '0x...'}, ...}
        """
        base_url = "https://api.etherscan.io/v2/api"
        token_balances = {}
        
        # Get tokens for this chain
        chain_tokens = {addr: info for addr, info in self.WHITELISTED_TOKENS.items() 
                       if info['symbol'] in ['USDT', 'USDC', 'WBTC', 'WETH', 'WMATIC']}
        
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
                
                if data.get('status') == '1' and data.get('result'):
                    # Get token decimals (usually 18 for WETH, 6 for USDT/USDC, 8 for WBTC)
                    decimals = 18  # default
                    if token_info['symbol'] in ['USDT', 'USDC']:
                        decimals = 6
                    elif token_info['symbol'] == 'WBTC':
                        decimals = 8
                    
                    balance_raw = int(data['result'])
                    balance = balance_raw / (10 ** decimals)
                    
                    if balance > 0:  # Only include if balance exists
                        token_balances[token_info['symbol']] = {
                            'balance': balance,
                            'contract': contract_address,
                            'name': token_info['name'],
                            'decimals': decimals
                        }
                        logger.info(f"Found {token_info['symbol']} balance: {balance}")
                
            except Exception as e:
                logger.warning(f"Error fetching {token_info['symbol']} balance: {str(e)}")
                continue
        
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
        """Fetch Solana transactions (simplified version)"""
        # Solana requires more complex setup with RPC calls
        # For now, return empty result
        return {
            'success': True,
            'balance': '0',
            'transactions': [],
            'count': 0,
            'message': 'Solana support coming soon'
        }
