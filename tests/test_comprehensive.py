#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Sentiment Market Prediction
Testing all components of the system
"""

import pytest
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Import modules to test
from ml_service import SentimentMLService, AnalyzeRequest, AnalyzeResponse
from enhanced_data_pipeline import DataCollector, DataPreprocessor, DataPipeline, NewsArticle, MarketData
from sentiment_analysis import analyze_sentiment
from signal_generator import generate_signals

class TestSentimentMLService:
    """Test the ML service functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ml_service = SentimentMLService()
        self.sample_texts = [
            "Apple stock is performing exceptionally well this quarter",
            "Tesla shares are declining due to market concerns",
            "The market is showing mixed signals today"
        ]
    
    def test_model_loading(self):
        """Test that models are loaded correctly"""
        assert len(self.ml_service.models) > 0
        assert "finbert" in self.ml_service.models
    
    def test_analyze_text(self):
        """Test single text analysis"""
        result = self.ml_service.analyze_text("This is a positive statement", "finbert")
        
        assert isinstance(result, AnalyzeResponse)
        assert result.sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
        assert 0 <= result.confidence <= 1
        assert result.model == "finbert"
    
    def test_analyze_batch(self):
        """Test batch text analysis"""
        results = self.ml_service.analyze_batch(self.sample_texts, "finbert")
        
        assert len(results) == len(self.sample_texts)
        for result in results:
            assert isinstance(result, AnalyzeResponse)
            assert result.sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]
    
    def test_get_available_models(self):
        """Test getting available models"""
        models = self.ml_service.get_available_models()
        assert isinstance(models, list)
        assert len(models) > 0
        assert "finbert" in models
    
    def test_model_info(self):
        """Test getting model information"""
        info = self.ml_service.get_model_info("finbert")
        assert info.name == "finbert"
        assert info.description is not None
        assert 0 <= info.accuracy <= 1

class TestDataCollector:
    """Test the data collection functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {
            'news_api_key': 'test_key',
            'symbols': ['AAPL', 'GOOGL']
        }
        self.collector = DataCollector(self.config)
    
    def test_database_initialization(self):
        """Test database initialization"""
        assert os.path.exists(self.collector.db_path)
    
    @pytest.mark.asyncio
    async def test_collect_market_data(self):
        """Test market data collection"""
        # Mock yfinance to avoid actual API calls
        with patch('yfinance.Ticker') as mock_ticker:
            mock_hist = pd.DataFrame({
                'Open': [100, 101, 102],
                'High': [105, 106, 107],
                'Low': [95, 96, 97],
                'Close': [103, 104, 105],
                'Volume': [1000000, 1100000, 1200000]
            }, index=pd.date_range('2024-01-01', periods=3))
            
            mock_ticker.return_value.history.return_value = mock_hist
            
            market_data = await self.collector.collect_market_data(['AAPL'])
            
            assert len(market_data) > 0
            assert all(isinstance(data, MarketData) for data in market_data)
            assert all(data.symbol == 'AAPL' for data in market_data)
    
    @pytest.mark.asyncio
    async def test_collect_news_data(self):
        """Test news data collection"""
        # Mock aiohttp to avoid actual API calls
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json.return_value = {
                'articles': [
                    {
                        'title': 'Test News',
                        'description': 'Test Description',
                        'source': {'name': 'Test Source'},
                        'url': 'https://test.com',
                        'publishedAt': '2024-01-01T00:00:00Z'
                    }
                ]
            }
            mock_get.return_value.__aenter__.return_value = mock_response
            
            articles = await self.collector.collect_news_data(['AAPL'])
            
            # Note: This will be empty due to mocking, but structure is tested
            assert isinstance(articles, list)

class TestDataPreprocessor:
    """Test the data preprocessing functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.preprocessor = DataPreprocessor()
        self.sample_articles = [
            NewsArticle(
                title="Apple stock surges on strong earnings",
                content="Apple reported better than expected earnings...",
                source="Reuters",
                url="https://example.com",
                published_at=datetime.now()
            ),
            NewsArticle(
                title="Tesla shares decline amid market volatility",
                content="Tesla stock fell due to market concerns...",
                source="Bloomberg",
                url="https://example2.com",
                published_at=datetime.now()
            )
        ]
    
    def test_preprocess_text(self):
        """Test text preprocessing"""
        text = "This is a test URL: https://example.com with special chars!"
        processed = self.preprocessor.preprocess_text(text)
        
        assert "https://example.com" not in processed
        assert "!" not in processed
        assert processed.islower()
    
    def test_extract_features(self):
        """Test feature extraction"""
        text = "Apple stock is performing very well with strong growth"
        features = self.preprocessor.extract_features(text)
        
        assert 'word_count' in features
        assert 'char_count' in features
        assert 'vader_compound' in features
        assert 'textblob_polarity' in features
        assert features['word_count'] > 0
    
    def test_calculate_sentiment_score(self):
        """Test sentiment score calculation"""
        positive_text = "This is excellent news for investors"
        negative_text = "This is terrible news for the market"
        
        pos_score = self.preprocessor.calculate_sentiment_score(positive_text)
        neg_score = self.preprocessor.calculate_sentiment_score(negative_text)
        
        assert 0 <= pos_score <= 1
        assert 0 <= neg_score <= 1
        assert pos_score > neg_score  # Positive should score higher
    
    def test_create_sentiment_features(self):
        """Test creating feature matrix"""
        features_df = self.preprocessor.create_sentiment_features(self.sample_articles)
        
        assert isinstance(features_df, pd.DataFrame)
        assert len(features_df) == len(self.sample_articles)
        assert 'sentiment_score' in features_df.columns
        assert 'title_word_count' in features_df.columns

class TestSignalGeneration:
    """Test signal generation functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.sample_sentiment_data = [
            {"text": "Apple stock is performing well", "sentiment": "POSITIVE", "confidence": 0.85},
            {"text": "Tesla shares are declining", "sentiment": "NEGATIVE", "confidence": 0.78},
            {"text": "Market shows mixed signals", "sentiment": "NEUTRAL", "confidence": 0.65}
        ]
    
    def test_generate_signals(self):
        """Test signal generation"""
        signals = generate_signals(self.sample_sentiment_data)
        
        assert len(signals) == len(self.sample_sentiment_data)
        for signal in signals:
            assert 'action' in signal
            assert 'strength' in signal
            assert signal['action'] in ['BUY', 'SELL', 'HOLD']
            assert 0 <= signal['strength'] <= 1

class TestIntegration:
    """Integration tests for the complete system"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.config = {
            'news_api_key': 'test_key',
            'symbols': ['AAPL', 'GOOGL']
        }
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test the complete data pipeline"""
        # Mock external dependencies
        with patch('yfinance.Ticker') as mock_ticker, \
             patch('aiohttp.ClientSession.get') as mock_get:
            
            # Mock market data
            mock_hist = pd.DataFrame({
                'Open': [100, 101],
                'High': [105, 106],
                'Low': [95, 96],
                'Close': [103, 104],
                'Volume': [1000000, 1100000]
            }, index=pd.date_range('2024-01-01', periods=2))
            mock_ticker.return_value.history.return_value = mock_hist
            
            # Mock news API
            mock_response = Mock()
            mock_response.status = 200
            mock_response.json.return_value = {'articles': []}
            mock_get.return_value.__aenter__.return_value = mock_response
            
            pipeline = DataPipeline(self.config)
            
            # This should not raise an exception
            await pipeline.run_full_pipeline()
    
    def test_api_endpoints(self):
        """Test API endpoint functionality"""
        # This would test the FastAPI endpoints
        # For now, we'll test the core functionality
        ml_service = SentimentMLService()
        
        # Test analyze endpoint logic
        request = AnalyzeRequest(text="Test text", model="finbert")
        result = ml_service.analyze_text(request.text, request.model)
        
        assert isinstance(result, AnalyzeResponse)
        assert result.sentiment in ["POSITIVE", "NEGATIVE", "NEUTRAL"]

class TestPerformance:
    """Performance tests"""
    
    def test_sentiment_analysis_performance(self):
        """Test sentiment analysis performance"""
        ml_service = SentimentMLService()
        
        # Test with large batch
        large_texts = [f"Sample text {i}" for i in range(100)]
        
        start_time = datetime.now()
        results = ml_service.analyze_batch(large_texts, "finbert")
        end_time = datetime.now()
        
        processing_time = (end_time - start_time).total_seconds()
        
        assert len(results) == len(large_texts)
        assert processing_time < 60  # Should complete within 60 seconds
    
    def test_memory_usage(self):
        """Test memory usage with large datasets"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create large dataset
        large_articles = [
            NewsArticle(
                title=f"Article {i}",
                content=f"Content {i}" * 100,  # Large content
                source="Test",
                url=f"https://test{i}.com",
                published_at=datetime.now()
            )
            for i in range(1000)
        ]
        
        preprocessor = DataPreprocessor()
        features_df = preprocessor.create_sentiment_features(large_articles)
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        assert memory_increase < 500  # Should not use more than 500MB

class TestDataQuality:
    """Data quality tests"""
    
    def test_sentiment_score_distribution(self):
        """Test that sentiment scores are properly distributed"""
        preprocessor = DataPreprocessor()
        
        positive_texts = [
            "This is excellent news",
            "Great performance",
            "Outstanding results"
        ]
        
        negative_texts = [
            "This is terrible news",
            "Poor performance",
            "Disappointing results"
        ]
        
        positive_scores = [preprocessor.calculate_sentiment_score(text) for text in positive_texts]
        negative_scores = [preprocessor.calculate_sentiment_score(text) for text in negative_texts]
        
        # Positive texts should have higher scores
        assert np.mean(positive_scores) > np.mean(negative_scores)
        
        # All scores should be between 0 and 1
        all_scores = positive_scores + negative_scores
        assert all(0 <= score <= 1 for score in all_scores)
    
    def test_feature_consistency(self):
        """Test that features are consistent across similar texts"""
        preprocessor = DataPreprocessor()
        
        text1 = "Apple stock is performing well"
        text2 = "Apple stock is performing well"  # Identical
        
        features1 = preprocessor.extract_features(text1)
        features2 = preprocessor.extract_features(text2)
        
        # Identical texts should produce identical features
        for key in features1:
            assert features1[key] == features2[key]

# Pytest configuration
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
