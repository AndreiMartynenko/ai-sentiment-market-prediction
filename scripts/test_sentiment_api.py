#!/usr/bin/env python3
"""
Test script for FinBERT Sentiment Analysis API
Tests the /sentiment endpoint with various financial texts
"""

import requests
import json
from typing import Dict, List

# API Configuration
API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*70)
    print("Testing Health Endpoint")
    print("="*70)
    
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_sentiment(text: str, symbol: str = "AAPL"):
    """
    Test sentiment analysis endpoint
    
    Args:
        text: Text to analyze
        symbol: Trading symbol
    """
    print(f"\nSymbol: {symbol}")
    print(f"Text: {text[:80]}...")
    
    try:
        payload = {
            "symbol": symbol,
            "text": text
        }
        
        response = requests.post(
            f"{API_URL}/sentiment",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"  Label: {result['label']}")
            print(f"  Sentiment Score: {result['sentiment_score']}")
            print(f"  Confidence: {result['confidence']}")
            return result
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return None


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("FinBERT Sentiment Analysis API Test Suite")
    print("="*70)
    
    # Test health endpoint
    if not test_health():
        print("\n❌ Health check failed. Make sure the API is running on port 8000")
        print("   Start with: uvicorn ml_service.main:app --reload")
        return
    
    # Test cases
    test_cases = [
        ("AAPL", "Apple shares jump after record iPhone sales boost earnings"),
        ("TSLA", "Tesla stock plummets as production delays mount and quality concerns grow"),
        ("BTCUSDT", "Bitcoin reached new all-time highs as institutional adoption continues to grow"),
        ("ETHUSDT", "Ethereum price drops significantly amid market uncertainty"),
        ("AAPL", "The Federal Reserve announced no change to interest rates this month"),
    ]
    
    print("\n" + "="*70)
    print("Testing Sentiment Analysis")
    print("="*70)
    
    results = []
    for symbol, text in test_cases:
        result = test_sentiment(text, symbol)
        if result:
            results.append(result)
    
    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    print(f"Total tests: {len(test_cases)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(test_cases) - len(results)}")
    
    if results:
        print("\nResults:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['symbol']}: {result['label']} "
                  f"(score: {result['sentiment_score']:.4f}, "
                  f"conf: {result['confidence']:.4f})")


if __name__ == "__main__":
    # Example curl command
    print("\nExample cURL command:")
    print("-"*70)
    print('curl -X POST http://localhost:8000/sentiment \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"symbol": "AAPL", "text": "Apple shares jump after record iPhone sales"}\'')
    print("-"*70)
    
    main()
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)

