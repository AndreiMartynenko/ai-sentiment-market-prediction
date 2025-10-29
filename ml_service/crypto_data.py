"""
Crypto Data Service for Binance API Integration
Fetches real-time cryptocurrency market data and news from various sources
"""

import logging
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class BinanceDataService:
    """
    Service for fetching cryptocurrency data from Binance API
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.secret_key = os.getenv("BINANCE_SECRET_KEY", "")
        
    def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data from Binance
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT", "ETHUSDT")
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of data points (max 1000)
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            url = f"{self.base_url}/klines"
            params = {
                "symbol": symbol.upper(),
                "interval": interval,
                "limit": min(limit, 1000)
            }
            
            logger.info(f"Fetching {symbol} data from Binance (interval: {interval})")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.error(f"No data received for {symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(data, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Convert data types
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Select only OHLCV columns
            df = df[numeric_columns]
            df.columns = df.columns.str.lower()
            
            logger.info(f"Fetched {len(df)} data points for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Binance data for {symbol}: {e}")
            return None
    
    def get_24hr_ticker(self, symbol: str = None) -> Optional[Dict]:
        """
        Get 24hr price change statistics
        
        Args:
            symbol: Trading pair (optional, if None returns all symbols)
            
        Returns:
            Dict with price change data or None if error
        """
        try:
            url = f"{self.base_url}/ticker/24hr"
            params = {}
            if symbol:
                params["symbol"] = symbol.upper()
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if symbol:
                return data
            else:
                # Return top 10 by volume
                sorted_data = sorted(data, key=lambda x: float(x['volume']), reverse=True)
                return sorted_data[:10]
                
        except Exception as e:
            logger.error(f"Error fetching 24hr ticker for {symbol}: {e}")
            return None

class CryptoPanicService:
    """
    Service for fetching cryptocurrency news from CryptoPanic API
    """
    
    def __init__(self):
        self.base_url = "https://cryptopanic.com/api/v1"
        self.api_key = os.getenv("CRYPTOPANIC_API_KEY", "")
        
    def get_news(self, currencies: List[str] = None, limit: int = 20) -> Optional[List[Dict]]:
        """
        Fetch latest crypto news from CryptoPanic
        
        Args:
            currencies: List of currency codes (e.g., ["BTC", "ETH", "SOL"])
            limit: Number of news items to fetch
            
        Returns:
            List of news items or None if error
        """
        try:
            url = f"{self.base_url}/posts/"
            params = {
                "auth_token": self.api_key,
                "public": "true",
                "kind": "news",
                "currencies": ",".join(currencies) if currencies else "BTC,ETH,SOL,XRP",
                "limit": limit
            }
            
            logger.info(f"Fetching crypto news from CryptoPanic (currencies: {currencies})")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "results" not in data:
                logger.error("No results in CryptoPanic response")
                return None
            
            news_items = []
            for item in data["results"]:
                news_items.append({
                    "id": item.get("id"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "source": item.get("source", {}).get("title", "Unknown"),
                    "published_at": item.get("published_at"),
                    "currencies": [curr.get("code") for curr in item.get("currencies", [])],
                    "votes": item.get("votes", {}),
                    "domain": item.get("domain")
                })
            
            logger.info(f"Fetched {len(news_items)} news items")
            return news_items
            
        except Exception as e:
            logger.error(f"Error fetching news from CryptoPanic: {e}")
            return None

class CryptoDataManager:
    """
    Main crypto data manager combining Binance and CryptoPanic services
    """
    
    def __init__(self):
        self.binance = BinanceDataService()
        self.cryptopanic = CryptoPanicService()
        
    def get_crypto_market_data(self, symbol: str, period: str = "1d") -> Optional[pd.DataFrame]:
        """
        Get cryptocurrency market data
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT", "ETHUSDT")
            period: Time period (1h, 4h, 1d, 7d)
            
        Returns:
            DataFrame with OHLCV data
        """
        # Map period to Binance interval
        interval_map = {
            "1h": "1m",
            "4h": "5m", 
            "1d": "1h",
            "7d": "4h",
            "30d": "1d"
        }
        
        interval = interval_map.get(period, "1h")
        limit = 100 if period in ["1h", "4h"] else 200
        
        return self.binance.get_klines(symbol, interval, limit)
    
    def get_top_crypto_news(self, currencies: List[str] = None, limit: int = 10) -> Optional[List[Dict]]:
        """
        Get top cryptocurrency news
        
        Args:
            currencies: List of currency codes
            limit: Number of news items
            
        Returns:
            List of news items
        """
        if not currencies:
            currencies = ["BTC", "ETH", "SOL", "XRP"]
            
        return self.cryptopanic.get_news(currencies, limit)
    
    def get_market_overview(self) -> Optional[Dict]:
        """
        Get overall market overview
        
        Returns:
            Dict with market statistics
        """
        try:
            # Get top 10 cryptocurrencies by volume
            tickers = self.binance.get_24hr_ticker()
            
            if not tickers:
                return None
            
            # Calculate market metrics
            total_volume = sum(float(ticker['volume']) for ticker in tickers)
            gainers = sum(1 for ticker in tickers if float(ticker['priceChangePercent']) > 0)
            losers = sum(1 for ticker in tickers if float(ticker['priceChangePercent']) < 0)
            
            return {
                "total_volume": total_volume,
                "gainers": gainers,
                "losers": losers,
                "total_pairs": len(tickers),
                "top_performers": sorted(tickers, key=lambda x: float(x['priceChangePercent']), reverse=True)[:5],
                "worst_performers": sorted(tickers, key=lambda x: float(x['priceChangePercent']))[:5]
            }
            
        except Exception as e:
            logger.error(f"Error getting market overview: {e}")
            return None

# Global instances
_binance_service = None
_cryptopanic_service = None
_crypto_data_manager = None

def get_binance_service() -> BinanceDataService:
    """Get Binance service instance"""
    global _binance_service
    if _binance_service is None:
        _binance_service = BinanceDataService()
    return _binance_service

def get_cryptopanic_service() -> CryptoPanicService:
    """Get CryptoPanic service instance"""
    global _cryptopanic_service
    if _cryptopanic_service is None:
        _cryptopanic_service = CryptoPanicService()
    return _cryptopanic_service

def get_crypto_data_manager() -> CryptoDataManager:
    """Get crypto data manager instance"""
    global _crypto_data_manager
    if _crypto_data_manager is None:
        _crypto_data_manager = CryptoDataManager()
    return _crypto_data_manager

if __name__ == "__main__":
    # Test the services
    manager = get_crypto_data_manager()
    
    # Test Binance data
    print("Testing Binance data...")
    btc_data = manager.get_crypto_market_data("BTCUSDT", "1d")
    if btc_data is not None:
        print(f"BTC data shape: {btc_data.shape}")
        print(f"Latest BTC price: ${btc_data['close'].iloc[-1]:.2f}")
    
    # Test CryptoPanic news
    print("\nTesting CryptoPanic news...")
    news = manager.get_top_crypto_news(["BTC", "ETH"], 5)
    if news:
        print(f"Fetched {len(news)} news items")
        for item in news[:2]:
            print(f"- {item['title']} ({item['source']})")
    
    # Test market overview
    print("\nTesting market overview...")
    overview = manager.get_market_overview()
    if overview:
        print(f"Total volume: ${overview['total_volume']:,.0f}")
        print(f"Gainers: {overview['gainers']}, Losers: {overview['losers']}")
