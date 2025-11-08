"""
Crypto News Fetcher with Sentiment Analysis
Fetches cryptocurrency news from CryptoPanic (or other sources) and applies FinBERT sentiment analysis.
"""

import logging
import os
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests

from ml_service.sentiment import FinBERTAnalyzer


# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CryptoNewsManager:
    """Fetches crypto news from external APIs and enriches with sentiment."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        analyzer: Optional[FinBERTAnalyzer] = None,
        cache_ttl: int = 300,
    ) -> None:
        """Initialize the news manager.

        Args:
            api_key: CryptoPanic API key.
            analyzer: FinBERT analyzer instance.
            cache_ttl: Cache time-to-live in seconds (default 5 minutes).
        """
        self.api_key = api_key or os.getenv("CRYPTOPANIC_API_KEY")
        self.analyzer = analyzer
        self.cache_ttl = cache_ttl
        self.base_url = "https://cryptopanic.com/api/developer/v2/posts/"
        self._cache: Dict[str, Dict] = {}

        if not self.api_key:
            logger.warning("CRYPTOPANIC_API_KEY not set. News fetching will be disabled.")

        if self.analyzer is None:
            # Lazily import to avoid circular dependencies
            try:
                self.analyzer = FinBERTAnalyzer()
            except Exception as exc:
                logger.error(f"Failed to initialize FinBERT analyzer: {exc}")
                self.analyzer = None

    def _cache_key(self, symbol: str, limit: int) -> str:
        return f"{symbol.upper()}_{limit}"

    def _is_cached(self, key: str) -> bool:
        cached = self._cache.get(key)
        if not cached:
            return False
        return time.time() - cached["timestamp"] < self.cache_ttl

    def _get_cached(self, key: str):
        return self._cache.get(key, {}).get("data")

    def _set_cache(self, key: str, data):
        self._cache[key] = {"timestamp": time.time(), "data": data}

    def fetch_symbol_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """Fetch news for a single symbol from CryptoPanic."""
        symbol = symbol.upper()
        cache_key = self._cache_key(symbol, limit)

        if self._is_cached(cache_key):
            return self._get_cached(cache_key)

        if not self.api_key:
            logger.debug("No API key available; returning empty news list.")
            return []

        params = {
            "auth_token": self.api_key,
            "currencies": symbol,
            "kind": "news",
            "limit": limit,
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            logger.debug(f"CryptoPanic request params: {params}")
            logger.debug(f"CryptoPanic response status: {response.status_code}")
            logger.debug(f"CryptoPanic raw response: {response.text[:500]}")
            response.raise_for_status()
            data = response.json()
            results = data.get("results") or data.get("data") or []
            if isinstance(results, dict) and "results" in results:
                results = results["results"]
            if not isinstance(results, list):
                results = []
            results = results[:limit]

            enriched_items: List[Dict] = []
            for item in results:
                title = item.get("title", "")
                sentiment = {
                    "label": "neutral",
                    "sentiment_score": 0.0,
                    "confidence": 0.0,
                }

                if self.analyzer:
                    try:
                        sentiment = self.analyzer.analyze_crypto(title)
                    except Exception as analyze_error:
                        logger.warning(f"Sentiment analysis failed for '{title}': {analyze_error}")

                metadata = item.get("metadata", {}) or {}
                source_value = item.get("source")
                if isinstance(source_value, dict):
                    source_name = source_value.get("title") or source_value.get("name")
                else:
                    source_name = source_value
                if not source_name:
                    source_name = metadata.get("source") or metadata.get("source_title") or "Unknown"

                published_at = item.get("published_at") or metadata.get("published_at") or metadata.get("created_at")
                url = (
                    item.get("original_url")
                    or metadata.get("original_url")
                    or metadata.get("url")
                    or item.get("url")
                    or item.get("link")
                )
                domain = item.get("domain") or metadata.get("domain")
                if (not domain) and url:
                    try:
                        domain = urlparse(url).netloc
                    except Exception:
                        domain = None

                enriched_items.append(
                    {
                        "title": title,
                        "url": url,
                        "published_at": published_at,
                        "source": source_name,
                        "domain": domain,
                        "sentiment": sentiment,
                        "sentiment_label": sentiment.get("label", "neutral"),
                        "sentiment_score": float(sentiment.get("sentiment_score", 0.0)),
                        "sentiment_confidence": float(sentiment.get("confidence", 0.0)),
                    }
                )

            self._set_cache(cache_key, enriched_items)
            return enriched_items

        except requests.RequestException as req_err:
            logger.error(f"Error fetching news for {symbol}: {req_err}")
            return []
        except ValueError as json_err:
            logger.error(f"Invalid JSON from CryptoPanic: {json_err}")
            return []

    def fetch_news_for_symbols(self, symbols: List[str], limit: int = 10) -> Dict[str, List[Dict]]:
        """Fetch news for multiple symbols."""
        news_data: Dict[str, List[Dict]] = {}
        for symbol in symbols:
            news_data[symbol.upper()] = self.fetch_symbol_news(symbol, limit)
        return news_data


def get_crypto_news_manager(analyzer: Optional[FinBERTAnalyzer] = None) -> CryptoNewsManager:
    """Factory function to get a CryptoNewsManager instance."""
    return CryptoNewsManager(analyzer=analyzer)

