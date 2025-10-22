"""
Currency Exchange Service
Fetches real-time cryptocurrency prices in USD and AED
"""

import requests
import time
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class CurrencyExchangeService:
    """Service for fetching cryptocurrency exchange rates"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
        self.usd_to_aed_rate = 3.67  # Fallback rate if API fails
        self._fetch_live_usd_aed_rate()  # Fetch real rate on initialization
        
    def get_crypto_prices(self, symbols: list) -> Dict[str, Dict[str, float]]:
        """
        Get cryptocurrency prices in USD and AED
        Batches requests to avoid rate limiting
        
        Args:
            symbols: List of crypto symbols (e.g., ['ETH', 'BTC', 'MATIC'])
            
        Returns:
            Dict with prices: {'ETH': {'usd': 2000.0, 'aed': 7340.0}, ...}
        """
        prices = {}
        symbols_to_fetch = []
        
        # Check cache first for all symbols
        for symbol in symbols:
            cache_key = f"{symbol}_price"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if time.time() - cached_data['timestamp'] < self.cache_duration:
                    prices[symbol] = cached_data['prices']
                    continue
            symbols_to_fetch.append(symbol)
        
        if not symbols_to_fetch:
            return prices
        
        # Map symbols to CoinGecko IDs
        symbol_map = {
            'ETH': 'ethereum', 'BTC': 'bitcoin', 'BNB': 'binancecoin',
            'AVAX': 'avalanche-2', 'SOL': 'solana', 'ADA': 'cardano', 'TRX': 'tron',
            'MATIC': 'polygon-ecosystem-token', 'POL': 'polygon-ecosystem-token',
            'WPOL': 'polygon-ecosystem-token', 'WMATIC': 'polygon-ecosystem-token',
            'USDT': 'tether', 'USDC': 'usd-coin', 'DAI': 'dai',
            'WBTC': 'wrapped-bitcoin', 'WETH': 'weth', 'WBNB': 'wbnb',
            'LINK': 'chainlink', 'UNI': 'uniswap', 'AAVE': 'aave',
            'ARB': 'arbitrum', 'aUSDT': 'tether', 'aUSDC': 'usd-coin',
            'HNST': 'honest-mining', 'PYTH': 'pyth-network',
        }
        
        # Build list of unique CoinGecko IDs
        coin_ids = []
        symbol_to_id = {}
        for symbol in symbols_to_fetch:
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            if coin_id not in coin_ids:
                coin_ids.append(coin_id)
            symbol_to_id[symbol] = coin_id
        
        # Batch fetch all prices in ONE request
        try:
            ids_str = ','.join(coin_ids)
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            # Get current USD/AED rate
            usd_to_aed = self.get_usd_to_aed_rate()
            
            # Map back to symbols
            for symbol in symbols_to_fetch:
                coin_id = symbol_to_id[symbol]
                if coin_id in data and 'usd' in data[coin_id]:
                    price_usd = float(data[coin_id]['usd'])
                    price_aed = price_usd * usd_to_aed
                    prices[symbol] = {'usd': price_usd, 'aed': price_aed}
                    
                    # Cache the result
                    cache_key = f"{symbol}_price"
                    self.cache[cache_key] = {
                        'prices': prices[symbol],
                        'timestamp': time.time()
                    }
                else:
                    logger.warning(f"Price not found for {symbol} (coin_id: {coin_id})")
                    prices[symbol] = {'usd': 0, 'aed': 0}
                    
        except Exception as e:
            logger.error(f"Error batch fetching prices: {str(e)}")
            # Fallback: set remaining to 0
            for symbol in symbols_to_fetch:
                if symbol not in prices:
                    prices[symbol] = {'usd': 0, 'aed': 0}
        
        return prices
    
    def _fetch_live_usd_aed_rate(self):
        """Fetch live USD to AED exchange rate from API"""
        try:
            # Use exchangerate-api.com (free, no key needed for basic usage)
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if 'rates' in data and 'AED' in data['rates']:
                self.usd_to_aed_rate = float(data['rates']['AED'])
                logger.info(f"Fetched live USD/AED rate: {self.usd_to_aed_rate}")
            else:
                logger.warning("AED rate not found in API response, using fallback rate")
        except Exception as e:
            logger.warning(f"Failed to fetch live USD/AED rate: {str(e)}, using fallback rate {self.usd_to_aed_rate}")
    
    def get_usd_to_aed_rate(self) -> float:
        """Get current USD to AED exchange rate (fetches live rate if cache expired)"""
        # Refresh rate if cache is old (every 5 minutes)
        cache_key = 'usd_aed_rate_timestamp'
        if cache_key not in self.cache or time.time() - self.cache[cache_key] > self.cache_duration:
            self._fetch_live_usd_aed_rate()
            self.cache[cache_key] = time.time()
        
        return self.usd_to_aed_rate
    
    def convert_to_usd(self, amount: float, crypto_price_usd: float) -> float:
        """Convert crypto amount to USD"""
        return amount * crypto_price_usd
    
    def convert_to_aed(self, amount: float, crypto_price_usd: float) -> float:
        """Convert crypto amount to AED"""
        usd_value = self.convert_to_usd(amount, crypto_price_usd)
        return usd_value * self.usd_to_aed_rate
