"""
Hybrid Decision Engine
Combines sentiment analysis and technical indicators to generate trading signals
"""

import logging
from typing import Dict, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Signal(Enum):
    """Trading signal types"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"

class HybridEngine:
    """Hybrid AI Decision Engine combining sentiment and technical analysis"""
    
    def __init__(self, sentiment_weight: float = 0.4, technical_weight: float = 0.6):
        """
        Initialize hybrid decision engine
        
        Args:
            sentiment_weight: Weight for sentiment analysis (0-1)
            technical_weight: Weight for technical indicators (0-1)
        """
        self.sentiment_weight = sentiment_weight
        self.technical_weight = technical_weight
        
        # Normalize weights to sum to 1
        total_weight = sentiment_weight + technical_weight
        if total_weight > 0:
            self.sentiment_weight = sentiment_weight / total_weight
            self.technical_weight = technical_weight / total_weight
        else:
            self.sentiment_weight = 0.5
            self.technical_weight = 0.5
        
        logger.info(f"Hybrid Engine initialized with weights - "
                   f"Sentiment: {self.sentiment_weight:.2f}, "
                   f"Technical: {self.technical_weight:.2f}")
    
    def generate_signal(self, 
                       sentiment_score: float,
                       technical_score: float,
                       sentiment_confidence: float = 1.0,
                       technical_confidence: float = 1.0) -> Dict:
        """
        Generate trading signal based on hybrid analysis
        
        Args:
            sentiment_score: Sentiment score (0-1, 0.5=neutral)
            technical_score: Technical score (0-1, 0.5=neutral)
            sentiment_confidence: Confidence in sentiment (0-1)
            technical_confidence: Confidence in technical (0-1)
            
        Returns:
            Dict with signal, hybrid score, reason, and confidence
        """
        try:
            # Adjust weights based on confidence
            adjusted_sentiment_weight = self.sentiment_weight * sentiment_confidence
            adjusted_technical_weight = self.technical_weight * technical_confidence
            
            total_adjusted = adjusted_sentiment_weight + adjusted_technical_weight
            if total_adjusted > 0:
                final_sentiment_weight = adjusted_sentiment_weight / total_adjusted
                final_technical_weight = adjusted_technical_weight / total_adjusted
            else:
                final_sentiment_weight = 0.5
                final_technical_weight = 0.5
            
            # Calculate hybrid score
            hybrid_score = (
                sentiment_score * final_sentiment_weight +
                technical_score * final_technical_weight
            )
            
            # Generate signal based on hybrid score
            if hybrid_score >= 0.65:
                signal = Signal.BUY
                signal_str = "BUY"
                reason = self._generate_reason(sentiment_score, technical_score, "bullish")
                confidence = min(hybrid_score, 0.95)
            elif hybrid_score <= 0.35:
                signal = Signal.SELL
                signal_str = "SELL"
                reason = self._generate_reason(sentiment_score, technical_score, "bearish")
                confidence = min(1 - hybrid_score, 0.95)
            else:
                signal = Signal.HOLD
                signal_str = "HOLD"
                reason = self._generate_reason(sentiment_score, technical_score, "neutral")
                confidence = 0.5
            
            return {
                "signal": signal_str,
                "hybrid_score": round(hybrid_score, 4),
                "confidence": round(confidence, 4),
                "reason": reason,
                "sentiment_score": round(sentiment_score, 4),
                "technical_score": round(technical_score, 4),
                "weight_used": {
                    "sentiment": round(final_sentiment_weight, 4),
                    "technical": round(final_technical_weight, 4)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return {
                "signal": "HOLD",
                "hybrid_score": 0.5,
                "confidence": 0.0,
                "reason": "Error in signal generation",
                "error": str(e)
            }
    
    def _generate_reason(self, 
                        sentiment_score: float, 
                        technical_score: float,
                        overall_trend: str) -> str:
        """
        Generate human-readable reason for the signal
        
        Args:
            sentiment_score: Sentiment score (0-1)
            technical_score: Technical score (0-1)
            overall_trend: Overall market trend (bullish/bearish/neutral)
            
        Returns:
            Human-readable reason string
        """
        reasons = []
        
        # Sentiment reason
        if sentiment_score >= 0.7:
            reasons.append("Strong positive sentiment")
        elif sentiment_score >= 0.6:
            reasons.append("Moderately positive sentiment")
        elif sentiment_score <= 0.3:
            reasons.append("Strong negative sentiment")
        elif sentiment_score <= 0.4:
            reasons.append("Moderately negative sentiment")
        else:
            reasons.append("Neutral sentiment")
        
        # Technical reason
        if technical_score >= 0.7:
            reasons.append("strong technical indicators")
        elif technical_score >= 0.6:
            reasons.append("favorable technical setup")
        elif technical_score <= 0.3:
            reasons.append("weak technical indicators")
        elif technical_score <= 0.4:
            reasons.append("unfavorable technical setup")
        else:
            reasons.append("mixed technical signals")
        
        reason = f"{reasons[0]} with {reasons[1]} suggesting {overall_trend} momentum"
        
        return reason
    
    def adjust_weights(self, sentiment_weight: float, technical_weight: float):
        """
        Dynamically adjust weights based on market conditions
        
        Args:
            sentiment_weight: New sentiment weight
            technical_weight: New technical weight
        """
        self.sentiment_weight = sentiment_weight
        self.technical_weight = technical_weight
        
        # Normalize
        total_weight = sentiment_weight + technical_weight
        if total_weight > 0:
            self.sentiment_weight = sentiment_weight / total_weight
            self.technical_weight = technical_weight / total_weight
        
        logger.info(f"Weights adjusted - Sentiment: {self.sentiment_weight:.2f}, "
                   f"Technical: {self.technical_weight:.2f}")


# Global instance
_engine: Optional[HybridEngine] = None

def get_engine(sentiment_weight: float = 0.4, technical_weight: float = 0.6) -> HybridEngine:
    """Get or create the global hybrid engine instance"""
    global _engine
    if _engine is None:
        _engine = HybridEngine(sentiment_weight, technical_weight)
    return _engine


# Example usage
if __name__ == "__main__":
    # Initialize engine
    engine = get_engine(sentiment_weight=0.4, technical_weight=0.6)
    
    # Test scenarios
    test_cases = [
        {"sentiment": 0.85, "technical": 0.75, "name": "Strong Buy"},
        {"sentiment": 0.25, "technical": 0.20, "name": "Strong Sell"},
        {"sentiment": 0.55, "technical": 0.52, "name": "Hold"},
        {"sentiment": 0.90, "technical": 0.30, "name": "Mixed Signals"},
        {"sentiment": 0.30, "technical": 0.90, "name": "Technical Override"},
    ]
    
    print("\n" + "="*70)
    print("Hybrid Decision Engine Test Results")
    print("="*70)
    
    for case in test_cases:
        result = engine.generate_signal(
            sentiment_score=case['sentiment'],
            technical_score=case['technical']
        )
        
        print(f"\n{case['name']}")
        print(f"  Sentiment: {case['sentiment']:.2f}, Technical: {case['technical']:.2f}")
        print(f"  Signal: {result['signal']} (Hybrid Score: {result['hybrid_score']:.4f})")
        print(f"  Confidence: {result['confidence']:.4f}")
        print(f"  Reason: {result['reason']}")

