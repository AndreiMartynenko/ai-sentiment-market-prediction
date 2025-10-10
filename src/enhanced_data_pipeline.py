#!/usr/bin/env python3
"""
Enhanced Data Pipeline for AI Sentiment Market Prediction
Comprehensive data collection, preprocessing, and feature engineering
"""

import logging
import os
import sys
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import tweepy
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from pathlib import Path
import json
import sqlite3
from dataclasses import dataclass
import schedule
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download('vader_lexicon', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
except:
    logger.warning("Failed to download NLTK data")

@dataclass
class NewsArticle:
    title: str
    content: str
    source: str
    url: str
    published_at: datetime
    sentiment_score: Optional[float] = None
    keywords: Optional[List[str]] = None

@dataclass
class MarketData:
    symbol: str
    price: float
    volume: int
    high: float
    low: float
    open_price: float
    close: float
    timestamp: datetime
    change_percent: Optional[float] = None

class DataCollector:
    """Enhanced data collector for multiple sources"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.db_path = "data/market_data.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for data storage"""
        os.makedirs("data", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                source TEXT NOT NULL,
                url TEXT UNIQUE,
                published_at TIMESTAMP,
                sentiment_score REAL,
                keywords TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume INTEGER,
                high REAL,
                low REAL,
                open_price REAL,
                close REAL,
                timestamp TIMESTAMP NOT NULL,
                change_percent REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                sentiment_label TEXT NOT NULL,
                confidence REAL NOT NULL,
                model_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized")
    
    async def collect_news_data(self, symbols: List[str], hours_back: int = 24) -> List[NewsArticle]:
        """Collect news data from multiple sources"""
        articles = []
        
        # NewsAPI
        if self.config.get('news_api_key'):
            articles.extend(await self._collect_from_newsapi(symbols, hours_back))
        
        # RSS Feeds
        articles.extend(await self._collect_from_rss_feeds(symbols, hours_back))
        
        # Web scraping
        articles.extend(await self._collect_from_web_scraping(symbols, hours_back))
        
        logger.info(f"Collected {len(articles)} news articles")
        return articles
    
    async def _collect_from_newsapi(self, symbols: List[str], hours_back: int) -> List[NewsArticle]:
        """Collect news from NewsAPI"""
        articles = []
        api_key = self.config['news_api_key']
        
        for symbol in symbols:
            try:
                url = "https://newsapi.org/v2/everything"
                params = {
                    'q': f"{symbol} stock market",
                    'apiKey': api_key,
                    'from': (datetime.now() - timedelta(hours=hours_back)).isoformat(),
                    'sortBy': 'publishedAt',
                    'pageSize': 50
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            for article in data.get('articles', []):
                                articles.append(NewsArticle(
                                    title=article['title'],
                                    content=article.get('description', ''),
                                    source=article['source']['name'],
                                    url=article['url'],
                                    published_at=datetime.fromisoformat(
                                        article['publishedAt'].replace('Z', '+00:00')
                                    )
                                ))
            except Exception as e:
                logger.error(f"Error collecting from NewsAPI for {symbol}: {e}")
        
        return articles
    
    async def _collect_from_rss_feeds(self, symbols: List[str], hours_back: int) -> List[NewsArticle]:
        """Collect news from RSS feeds"""
        articles = []
        rss_feeds = [
            'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'https://feeds.reuters.com/reuters/businessNews',
            'https://feeds.bloomberg.com/markets/news.rss'
        ]
        
        for feed_url in rss_feeds:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(feed_url) as response:
                        if response.status == 200:
                            content = await response.text()
                            # Parse RSS (simplified)
                            # In production, use feedparser library
                            pass
            except Exception as e:
                logger.error(f"Error collecting from RSS feed {feed_url}: {e}")
        
        return articles
    
    async def _collect_from_web_scraping(self, symbols: List[str], hours_back: int) -> List[NewsArticle]:
        """Collect news through web scraping"""
        articles = []
        
        # Example: Scrape financial news websites
        websites = [
            'https://www.reuters.com/business/',
            'https://www.bloomberg.com/markets',
            'https://finance.yahoo.com/news/'
        ]
        
        for website in websites:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(website) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract articles (implementation depends on website structure)
                            # This is a simplified example
                            pass
            except Exception as e:
                logger.error(f"Error scraping {website}: {e}")
        
        return articles
    
    async def collect_market_data(self, symbols: List[str], period: str = "1d") -> List[MarketData]:
        """Collect market data using yfinance"""
        market_data = []
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period=period)
                
                for timestamp, row in hist.iterrows():
                    market_data.append(MarketData(
                        symbol=symbol,
                        price=row['Close'],
                        volume=int(row['Volume']),
                        high=row['High'],
                        low=row['Low'],
                        open_price=row['Open'],
                        close=row['Close'],
                        timestamp=timestamp,
                        change_percent=((row['Close'] - row['Open']) / row['Open']) * 100
                    ))
                
                logger.info(f"Collected market data for {symbol}")
            except Exception as e:
                logger.error(f"Error collecting market data for {symbol}: {e}")
        
        return market_data
    
    async def collect_social_media_data(self, symbols: List[str], hours_back: int = 24) -> List[Dict]:
        """Collect social media sentiment data"""
        social_data = []
        
        # Twitter API (if configured)
        if self.config.get('twitter_api_key'):
            social_data.extend(await self._collect_twitter_data(symbols, hours_back))
        
        # Reddit API (if configured)
        if self.config.get('reddit_client_id'):
            social_data.extend(await self._collect_reddit_data(symbols, hours_back))
        
        return social_data
    
    async def _collect_twitter_data(self, symbols: List[str], hours_back: int) -> List[Dict]:
        """Collect Twitter data"""
        tweets = []
        
        # Twitter API v2 implementation
        # This is a placeholder - implement with actual Twitter API
        for symbol in symbols:
            query = f"${symbol} OR {symbol} stock"
            # Implement Twitter API calls here
        
        return tweets
    
    async def _collect_reddit_data(self, symbols: List[str], hours_back: int) -> List[Dict]:
        """Collect Reddit data"""
        reddit_posts = []
        
        # Reddit API implementation
        # This is a placeholder - implement with actual Reddit API
        for symbol in symbols:
            # Implement Reddit API calls here
            pass
        
        return reddit_posts

class DataPreprocessor:
    """Enhanced data preprocessing and feature engineering"""
    
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
        self.stop_words = set(stopwords.words('english'))
        self._setup_custom_patterns()
    
    def _setup_custom_patterns(self):
        """Setup custom patterns for financial text processing"""
        self.financial_keywords = {
            'positive': ['bullish', 'surge', 'rally', 'gain', 'profit', 'growth', 'strong', 'positive'],
            'negative': ['bearish', 'crash', 'decline', 'loss', 'weak', 'negative', 'fall', 'drop'],
            'neutral': ['stable', 'unchanged', 'flat', 'sideways', 'consolidation']
        }
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove special characters but keep financial symbols
        text = re.sub(r'[^a-zA-Z0-9\s$%]', ' ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract features from text"""
        features = {}
        
        # Basic text features
        features['word_count'] = len(text.split())
        features['char_count'] = len(text)
        features['sentence_count'] = len(text.split('.'))
        
        # Financial keyword counts
        for sentiment, keywords in self.financial_keywords.items():
            features[f'{sentiment}_keywords'] = sum(1 for keyword in keywords if keyword in text.lower())
        
        # VADER sentiment scores
        vader_scores = self.sia.polarity_scores(text)
        features.update({
            'vader_positive': vader_scores['pos'],
            'vader_negative': vader_scores['neg'],
            'vader_neutral': vader_scores['neu'],
            'vader_compound': vader_scores['compound']
        })
        
        # TextBlob sentiment
        blob = TextBlob(text)
        features['textblob_polarity'] = blob.sentiment.polarity
        features['textblob_subjectivity'] = blob.sentiment.subjectivity
        
        return features
    
    def calculate_sentiment_score(self, text: str) -> float:
        """Calculate comprehensive sentiment score"""
        if not text:
            return 0.0
        
        # Preprocess text
        processed_text = self.preprocess_text(text)
        
        # Get multiple sentiment scores
        vader_score = self.sia.polarity_scores(processed_text)['compound']
        textblob_score = TextBlob(processed_text).sentiment.polarity
        
        # Calculate weighted average
        sentiment_score = (vader_score * 0.6 + textblob_score * 0.4)
        
        # Normalize to 0-1 scale
        sentiment_score = (sentiment_score + 1) / 2
        
        return round(sentiment_score, 4)
    
    def create_sentiment_features(self, articles: List[NewsArticle]) -> pd.DataFrame:
        """Create feature matrix from articles"""
        features = []
        
        for article in articles:
            feature_dict = {
                'title': article.title,
                'content': article.content,
                'source': article.source,
                'published_at': article.published_at,
                'url': article.url
            }
            
            # Extract features from title and content
            title_features = self.extract_features(article.title)
            content_features = self.extract_features(article.content)
            
            # Combine features
            feature_dict.update({f'title_{k}': v for k, v in title_features.items()})
            feature_dict.update({f'content_{k}': v for k, v in content_features.items()})
            
            # Calculate overall sentiment
            combined_text = f"{article.title} {article.content}"
            feature_dict['sentiment_score'] = self.calculate_sentiment_score(combined_text)
            
            features.append(feature_dict)
        
        return pd.DataFrame(features)

class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.collector = DataCollector(config)
        self.preprocessor = DataPreprocessor()
        self.symbols = config.get('symbols', ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN'])
    
    async def run_full_pipeline(self):
        """Run the complete data pipeline"""
        logger.info("Starting full data pipeline")
        
        # Collect data
        news_articles = await self.collector.collect_news_data(self.symbols)
        market_data = await self.collector.collect_market_data(self.symbols)
        social_data = await self.collector.collect_social_media_data(self.symbols)
        
        # Preprocess data
        news_features = self.preprocessor.create_sentiment_features(news_articles)
        
        # Save data
        await self._save_data(news_articles, market_data, news_features)
        
        logger.info("Data pipeline completed")
    
    async def _save_data(self, articles: List[NewsArticle], market_data: List[MarketData], features: pd.DataFrame):
        """Save processed data to database"""
        conn = sqlite3.connect(self.collector.db_path)
        
        try:
            # Save news articles
            for article in articles:
                conn.execute('''
                    INSERT OR REPLACE INTO news_articles 
                    (title, content, source, url, published_at, sentiment_score)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    article.title,
                    article.content,
                    article.source,
                    article.url,
                    article.published_at,
                    article.sentiment_score
                ))
            
            # Save market data
            for data in market_data:
                conn.execute('''
                    INSERT OR REPLACE INTO market_data 
                    (symbol, price, volume, high, low, open_price, close, timestamp, change_percent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.symbol,
                    data.price,
                    data.volume,
                    data.high,
                    data.low,
                    data.open_price,
                    data.close,
                    data.timestamp,
                    data.change_percent
                ))
            
            conn.commit()
            logger.info("Data saved to database")
        
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            conn.rollback()
        finally:
            conn.close()

# Configuration
CONFIG = {
    'news_api_key': os.getenv('NEWS_API_KEY', ''),
    'twitter_api_key': os.getenv('TWITTER_API_KEY', ''),
    'reddit_client_id': os.getenv('REDDIT_CLIENT_ID', ''),
    'symbols': ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
}

async def main():
    """Main function to run the data pipeline"""
    pipeline = DataPipeline(CONFIG)
    await pipeline.run_full_pipeline()

if __name__ == "__main__":
    asyncio.run(main())
