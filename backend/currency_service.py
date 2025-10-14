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
        self.usd_to_aed_rate = 3.67  # Fixed AED/USD rate
        
    def get_crypto_prices(self, symbols: list) -> Dict[str, Dict[str, float]]:
        """
        Get cryptocurrency prices in USD and AED
        
        Args:
            symbols: List of crypto symbols (e.g., ['ETH', 'BTC', 'MATIC'])
            
        Returns:
            Dict with prices: {'ETH': {'usd': 2000.0, 'aed': 7340.0}, ...}
        """
        prices = {}
        
        for symbol in symbols:
            # Check cache first
            cache_key = f"{symbol}_price"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if time.time() - cached_data['timestamp'] < self.cache_duration:
                    prices[symbol] = cached_data['prices']
                    continue
            
            # Fetch from CoinGecko API (free, no API key needed)
            try:
                price_usd = self._fetch_coingecko_price(symbol)
                if price_usd:
                    price_aed = price_usd * self.usd_to_aed_rate
                    prices[symbol] = {
                        'usd': price_usd,
                        'aed': price_aed
                    }
                    
                    # Cache the result
                    self.cache[cache_key] = {
                        'prices': prices[symbol],
                        'timestamp': time.time()
                    }
                else:
                    prices[symbol] = {'usd': 0, 'aed': 0}
                    
            except Exception as e:
                logger.error(f"Error fetching price for {symbol}: {str(e)}")
                prices[symbol] = {'usd': 0, 'aed': 0}
        
        return prices
    
    def _fetch_coingecko_price(self, symbol: str) -> float:
        """Fetch price from CoinGecko API"""
        # Map common symbols to CoinGecko IDs
        symbol_map = {
            'ETH': 'ethereum',
            'BTC': 'bitcoin',
            'MATIC': 'matic-network',
            'BNB': 'binancecoin',
            'AVAX': 'avalanche-2',
            'SOL': 'solana',
            'ADA': 'cardano',
            'TRX': 'tron'
        }
        
        coin_id = symbol_map.get(symbol.upper(), symbol.lower())
        
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if coin_id in data and 'usd' in data[coin_id]:
                return float(data[coin_id]['usd'])
            
            return 0
            
        except Exception as e:
            logger.warning(f"CoinGecko API error for {symbol}: {str(e)}")
            return 0
    
    def get_usd_to_aed_rate(self) -> float:
        """Get current USD to AED exchange rate"""
        return self.usd_to_aed_rate
    
    def convert_to_usd(self, amount: float, crypto_price_usd: float) -> float:
        """Convert crypto amount to USD"""
        return amount * crypto_price_usd
    
    def convert_to_aed(self, amount: float, crypto_price_usd: float) -> float:
        """Convert crypto amount to AED"""
        usd_value = self.convert_to_usd(amount, crypto_price_usd)
        return usd_value * self.usd_to_aed_rate
