"""
Crypto-Focused FinBERT Sentiment Analysis Module
Analyzes cryptocurrency news and text using yiyanghkust/finbert-tone model

This module provides sentiment analysis using FinBERT, a domain-specific BERT model
fine-tuned on financial text. Enhanced for cryptocurrency market analysis with
crypto-specific keywords and sentiment patterns.

Model: yiyanghkust/finbert-tone (HuggingFace)
- 3-class classification: positive, negative, neutral
- Optimized for financial text sentiment analysis
- Enhanced for crypto news (BTC, ETH, SOL, XRP, DeFi, NFTs, etc.)
- Output: sentiment_score (-1.0 to +1.0), confidence (max probability)
"""

import logging
import os
import re
from typing import Dict, List, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FinBERTAnalyzer:
    """
    Crypto-focused FinBERT sentiment analyzer for cryptocurrency text
    
    Uses yiyanghkust/finbert-tone model for domain-specific financial sentiment analysis.
    Enhanced with crypto-specific keywords and sentiment patterns for better
    cryptocurrency market analysis.
    """
    
    def __init__(self, model_name: str = "yiyanghkust/finbert-tone"):
        """
        Initialize FinBERT model for sentiment analysis
        
        Args:
            model_name: Hugging Face model name (default: yiyanghkust/finbert-tone)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing FinBERT ({model_name}) on device: {self.device}")
        
        try:
            # Load tokenizer and model
            logger.info("Loading tokenizer and model...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # Label mapping for the finbert-tone model
            # The model outputs: 0=positive, 1=negative, 2=neutral
            self.id2label = {0: "positive", 1: "negative", 2: "neutral"}
            
            # Crypto-specific sentiment keywords
            self.crypto_positive_keywords = [
                "moon", "bullish", "pump", "surge", "rally", "breakout", "adoption",
                "institutional", "etf", "halving", "burn", "deflationary", "hodl",
                "diamond hands", "to the moon", "bull run", "green", "gains"
            ]
            
            self.crypto_negative_keywords = [
                "dump", "crash", "bearish", "fud", "panic", "sell-off", "correction",
                "bubble", "scam", "rug pull", "hack", "exploit", "bear market",
                "red", "losses", "fear", "uncertainty", "doubt"
            ]
            
            logger.info("Crypto-focused FinBERT model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading FinBERT model: {e}")
            raise
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text using FinBERT
        
        Args:
            text: Input financial text to analyze
            
        Returns:
            Dict with sentiment label, sentiment_score (-1 to +1), and confidence
            
        Example:
            >>> result = analyzer.analyze("Apple shares jump after record iPhone sales")
            >>> print(result)
            {'label': 'positive', 'sentiment_score': 0.82, 'confidence': 0.91}
        """
        if not text or not text.strip():
            return {
                "label": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.0
            }
        
        try:
            with torch.no_grad():
                # Tokenize input
                inputs = self.tokenizer(
                    text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Get model predictions
                outputs = self.model(**inputs)
                logits = outputs.logits
                
                # Apply softmax to get probabilities
                probabilities = torch.nn.functional.softmax(logits, dim=-1)
                
                # Get predicted class and confidence
                max_prob, predicted_class = torch.max(probabilities, dim=-1)
                max_prob = max_prob.item()
                predicted_class = predicted_class.item()
                
                # Map to label
                label = self.id2label.get(predicted_class, "neutral")
                
                # Calculate sentiment score in range -1.0 to +1.0
                if label.lower() == "positive":
                    sentiment_score = max_prob  # positive → +value
                elif label.lower() == "negative":
                    sentiment_score = -max_prob  # negative → -value
                else:  # neutral
                    sentiment_score = 0.0  # neutral → ≈0
                
                return {
                    "label": label,
                    "sentiment_score": round(sentiment_score, 4),
                    "confidence": round(max_prob, 4),
                    "model": self.model_name
                }
                
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {
                "label": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def preprocess_crypto_text(self, text: str) -> str:
        """
        Preprocess crypto text for better sentiment analysis
        
        Args:
            text: Raw crypto text
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Replace common crypto abbreviations
        crypto_replacements = {
            "btc": "bitcoin",
            "eth": "ethereum", 
            "sol": "solana",
            "xrp": "ripple",
            "ada": "cardano",
            "dot": "polkadot",
            "link": "chainlink",
            "defi": "decentralized finance",
            "nft": "non-fungible token",
            "dao": "decentralized autonomous organization"
        }
        
        for abbr, full in crypto_replacements.items():
            text = re.sub(rf'\b{abbr}\b', full, text)
        
        return text
    
    def get_crypto_sentiment_boost(self, text: str) -> float:
        """
        Calculate crypto-specific sentiment boost based on keywords
        
        Args:
            text: Input text
            
        Returns:
            Boost factor (-0.2 to +0.2)
        """
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in self.crypto_positive_keywords 
                           if keyword in text_lower)
        negative_count = sum(1 for keyword in self.crypto_negative_keywords 
                           if keyword in text_lower)
        
        # Calculate boost (max ±0.2)
        boost = min(0.2, (positive_count - negative_count) * 0.05)
        return boost

    def analyze_crypto(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of crypto text with enhanced preprocessing
        
        Args:
            text: Input crypto text to analyze
            
        Returns:
            Dict with enhanced sentiment analysis results
        """
        if not text or not text.strip():
            return {
                "label": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.0
            }
        
        try:
            # Preprocess crypto text
            processed_text = self.preprocess_crypto_text(text)
            
            # Get base sentiment analysis
            result = self.analyze(processed_text)
            
            # Apply crypto-specific boost
            crypto_boost = self.get_crypto_sentiment_boost(text)
            result["sentiment_score"] += crypto_boost
            
            # Clamp to valid range
            result["sentiment_score"] = max(-1.0, min(1.0, result["sentiment_score"]))
            result["sentiment_score"] = round(result["sentiment_score"], 4)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing crypto text: {e}")
            return {
                "label": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.0
            }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment of multiple texts efficiently using batching
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of sentiment analysis results
        """
        if not texts:
            return []
        
        try:
            results = []
            # Process texts in batches for efficiency
            batch_size = 16
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                batch_results = self._analyze_batch_internal(batch_texts)
                results.extend(batch_results)
            
            return results
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return [{"error": str(e)} for _ in texts]
    
    def _analyze_batch_internal(self, texts: List[str]) -> List[Dict]:
        """Internal method to process a batch of texts"""
        results = []
        
        for text in texts:
            result = self.analyze(text)
            results.append(result)
        
        return results


class DatabaseManager:
    """
    Manages PostgreSQL connection and operations for sentiment results
    """
    
    def __init__(self, 
                 host: str = "postgres",
                 user: str = "postgres",
                 password: str = "postgres",
                 dbname: str = "sentiment_market",
                 port: int = 5432):
        """
        Initialize database connection
        
        Args:
            host: Database host
            user: Database user
            password: Database password
            dbname: Database name
            port: Database port
        """
        self.connection_string = {
            "host": host,
            "user": user,
            "password": password,
            "dbname": dbname,
            "port": port
        }
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.connection_string)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def save_sentiment_result(self, symbol: str, sentiment_score: float, 
                             label: str, confidence: float) -> int:
        """
        Save sentiment analysis result to database
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTCUSDT')
            sentiment_score: Sentiment score (-1.0 to +1.0)
            label: Sentiment label (positive/negative/neutral)
            confidence: Confidence score (0.0 to 1.0)
            
        Returns:
            Inserted record ID
        """
        try:
            cur = self.conn.cursor()
            cur.execute(
                """
                INSERT INTO sentiment_results (symbol, sentiment_score, label, confidence, timestamp)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING id
                """,
                (symbol, sentiment_score, label.lower(), confidence)
            )
            result = cur.fetchone()
            self.conn.commit()
            cur.close()
            
            record_id = result[0] if result else None
            logger.debug(f"Saved sentiment result for {symbol} with ID: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"Error saving sentiment result: {e}")
            self.conn.rollback()
            return None
    
    def save_sentiment_batch(self, results: List[Dict]) -> int:
        """
        Save multiple sentiment results efficiently using batch insert
        
        Args:
            results: List of result dictionaries with keys: symbol, sentiment_score, label, confidence
            
        Returns:
            Number of records inserted
        """
        try:
            cur = self.conn.cursor()
            
            # Prepare data for bulk insert
            values = [
                (
                    r.get("symbol", "UNKNOWN"),
                    r.get("sentiment_score", 0.0),
                    r.get("label", "neutral").lower(),
                    r.get("confidence", 0.0)
                )
                for r in results
            ]
            
            execute_values(
                cur,
                """
                INSERT INTO sentiment_results (symbol, sentiment_score, label, confidence, timestamp)
                VALUES %s
                """,
                values,
                page_size=100
            )
            
            count = cur.rowcount
            self.conn.commit()
            cur.close()
            
            logger.info(f"Saved {count} sentiment results in batch")
            return count
            
        except Exception as e:
            logger.error(f"Error saving batch sentiment results: {e}")
            self.conn.rollback()
            return 0
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Global instances
_analyzer: Optional[FinBERTAnalyzer] = None
_db_manager: Optional[DatabaseManager] = None


def get_analyzer() -> FinBERTAnalyzer:
    """Get or create the global FinBERT analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = FinBERTAnalyzer()
    return _analyzer


def get_db_manager() -> Optional[DatabaseManager]:
    """Get or create the global database manager instance"""
    global _db_manager
    if _db_manager is None:
        try:
            _db_manager = DatabaseManager(
                host=os.getenv("DB_HOST", "postgres"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                dbname=os.getenv("POSTGRES_DB", "sentiment_market"),
                port=int(os.getenv("POSTGRES_PORT", "5432"))
            )
        except Exception as e:
            logger.warning(f"Could not initialize database manager: {e}")
            logger.warning("Running without database persistence")
    return _db_manager


if __name__ == "__main__":
    """
    Example usage and testing
    Run with: python ml_service/sentiment.py
    """
    import sys
    from pathlib import Path
    
    # Add parent directory to path for imports
    sys.path.insert(0, str(Path(__file__).parent))
    
    print("\n" + "="*70)
    print("FinBERT Sentiment Analysis Module Test")
    print("="*70)
    
    # Initialize analyzer
    analyzer = get_analyzer()
    
    # Test texts
    test_texts = [
        "Apple reported record-breaking quarterly earnings, surpassing all analyst expectations.",
        "Tesla stock plummets as production delays mount and quality concerns grow.",
        "The Federal Reserve announced no change to interest rates this month.",
        "Bitcoin reached new all-time highs as institutional adoption continues to grow.",
        "Market volatility spikes amid geopolitical tensions."
    ]
    
    print("\nAnalyzing test texts...")
    print("-"*70)
    
    for i, text in enumerate(test_texts, 1):
        result = analyzer.analyze(text)
        print(f"\n{i}. Text: {text[:60]}...")
        print(f"   Label: {result['label']}")
        print(f"   Sentiment Score: {result['sentiment_score']:.4f}")
        print(f"   Confidence: {result['confidence']:.4f}")
    
    # Test batch processing
    print("\n" + "="*70)
    print("Batch Processing Test")
    print("="*70)
    
    batch_results = analyzer.analyze_batch(test_texts)
    print(f"\nProcessed {len(batch_results)} texts in batch")
    
    # Database test (if available)
    try:
        db = get_db_manager()
        if db:
            print("\n" + "="*70)
            print("Database Integration Test")
            print("="*70)
            
            test_result = analyzer.analyze("Test sentiment analysis for database storage.")
            record_id = db.save_sentiment_result(
                symbol="TEST",
                sentiment_score=test_result['sentiment_score'],
                label=test_result['label'],
                confidence=test_result['confidence']
            )
            print(f"Saved test result with ID: {record_id}")
            db.close()
    except Exception as e:
        print(f"Database test failed: {e}")
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)
