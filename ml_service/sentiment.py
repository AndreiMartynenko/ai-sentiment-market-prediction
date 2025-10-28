"""
Sentiment Analysis Module using FinBERT
Analyzes financial news and text for sentiment scoring
"""

import logging
import os
from typing import Dict, List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinBERTAnalyzer:
    """FinBERT-based sentiment analyzer for financial text"""
    
    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize FinBERT model for sentiment analysis
        
        Args:
            model_name: Hugging Face model name or path
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing FinBERT on device: {self.device}")
        
        try:
            # Load tokenizer and model
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Create pipeline for easier inference
            self.classifier = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1,
                return_all_scores=True
            )
            
            logger.info("FinBERT model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading FinBERT model: {e}")
            raise
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dict with sentiment label, score, and confidence
        """
        if not text or not text.strip():
            return {
                "label": "NEUTRAL",
                "score": 0.5,
                "confidence": 0.0
            }
        
        try:
            # Get predictions
            results = self.classifier(text)
            
            # Get the highest confidence prediction
            best_result = max(results[0], key=lambda x: x['score'])
            
            # Map FinBERT labels to our labels
            label_map = {
                "positive": "POSITIVE",
                "negative": "NEGATIVE",
                "neutral": "NEUTRAL"
            }
            
            label = label_map.get(best_result['label'].lower(), "NEUTRAL")
            confidence = best_result['score']
            
            # Calculate sentiment score (normalize to 0-1)
            sentiment_score = self._calculate_sentiment_score(results[0])
            
            return {
                "label": label,
                "score": sentiment_score,
                "confidence": confidence,
                "model": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {
                "label": "NEUTRAL",
                "score": 0.5,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment of multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        results = []
        for text in texts:
            result = self.analyze(text)
            results.append(result)
        
        return results
    
    def _calculate_sentiment_score(self, all_scores: List[Dict]) -> float:
        """
        Calculate normalized sentiment score from all predictions
        
        Args:
            all_scores: All sentiment scores from the model
            
        Returns:
            Normalized score between 0 and 1
        """
        try:
            # Create score mapping
            score_dict = {score['label'].lower(): score['score'] for score in all_scores}
            
            positive = score_dict.get('positive', 0.0)
            negative = score_dict.get('negative', 0.0)
            neutral = score_dict.get('neutral', 0.0)
            
            # Weighted score calculation
            # Higher weight on positive/negative, lower on neutral
            weighted_score = (positive * 1.0) + (negative * -1.0) + (neutral * 0.0)
            
            # Normalize to 0-1 range
            normalized_score = (weighted_score + 1) / 2
            
            return round(normalized_score, 4)
            
        except Exception as e:
            logger.error(f"Error calculating sentiment score: {e}")
            return 0.5


# Global analyzer instance
_analyzer: Optional[FinBERTAnalyzer] = None

def get_analyzer() -> FinBERTAnalyzer:
    """Get or create the global FinBERT analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = FinBERTAnalyzer()
    return _analyzer


# Example usage
if __name__ == "__main__":
    # Test the analyzer
    analyzer = get_analyzer()
    
    test_texts = [
        "Apple reported record-breaking quarterly earnings, surpassing all analyst expectations.",
        "Tesla stock plummets as production delays mount and quality concerns grow.",
        "The Federal Reserve announced no change to interest rates this month."
    ]
    
    print("\n" + "="*70)
    print("FinBERT Sentiment Analysis Test Results")
    print("="*70)
    
    for text in test_texts:
        result = analyzer.analyze(text)
        print(f"\nText: {text[:60]}...")
        print(f"Label: {result['label']}")
        print(f"Score: {result['score']}")
        print(f"Confidence: {result['confidence']:.4f}")

