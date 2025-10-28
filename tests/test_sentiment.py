"""
Test suite for sentiment analysis module
"""

import pytest
from ml_service.sentiment import FinBERTAnalyzer


class TestSentiment:
    """Test cases for sentiment analysis"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        return FinBERTAnalyzer()
    
    def test_analyze_positive_text(self, analyzer):
        """Test sentiment analysis of positive text"""
        text = "Bitcoin reached new all-time highs as institutional adoption continues to grow."
        result = analyzer.analyze(text)
        
        assert result is not None
        assert "label" in result
        assert "score" in result
        assert "confidence" in result
        assert result["confidence"] > 0
    
    def test_analyze_negative_text(self, analyzer):
        """Test sentiment analysis of negative text"""
        text = "Stock market crashes amid inflation concerns and rising interest rates."
        result = analyzer.analyze(text)
        
        assert result is not None
        assert "label" in result
        assert result["score"] is not None
        assert 0 <= result["score"] <= 1
    
    def test_analyze_neutral_text(self, analyzer):
        """Test sentiment analysis of neutral text"""
        text = "The Federal Reserve announced no change to interest rates this month."
        result = analyzer.analyze(text)
        
        assert result is not None
        assert "label" in result
        assert "score" in result
    
    def test_analyze_empty_text(self, analyzer):
        """Test handling of empty text"""
        result = analyzer.analyze("")
        
        assert result is not None
        assert result["label"] == "NEUTRAL"
        assert result["score"] == 0.5
    
    def test_analyze_batch(self, analyzer):
        """Test batch sentiment analysis"""
        texts = [
            "Stock prices are rising.",
            "Market is declining.",
            "No significant changes."
        ]
        
        results = analyzer.analyze_batch(texts)
        
        assert len(results) == 3
        assert all("label" in r for r in results)
        assert all("score" in r for r in results)
    
    def test_calculate_sentiment_score(self, analyzer):
        """Test sentiment score calculation"""
        scores = [
            {"label": "positive", "score": 0.8},
            {"label": "negative", "score": 0.1},
            {"label": "neutral", "score": 0.1}
        ]
        
        score = analyzer._calculate_sentiment_score(scores)
        
        assert 0 <= score <= 1
        assert score > 0.5  # Should be positive


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

