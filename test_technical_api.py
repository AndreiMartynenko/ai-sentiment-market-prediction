#!/usr/bin/env python3
"""
Test script for Technical Indicators API
Tests the /technical endpoint with various trading symbols
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


def test_technical_indicator(symbol: str, period: str = "3mo"):
    """
    Test technical indicators endpoint
    
    Args:
        symbol: Trading symbol
        period: Time period for data
    """
    print(f"\nSymbol: {symbol} (Period: {period})")
    
    try:
        payload = {
            "symbol": symbol,
            "period": period
        }
        
        response = requests.post(
            f"{API_URL}/technical",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"  EMA 20: {result['ema20']}")
            print(f"  EMA 50: {result['ema50']}")
            print(f"  RSI: {result['rsi']}")
            print(f"  MACD: {result['macd']}")
            print(f"  Technical Score: {result['technical_score']:.4f}")
            
            # Interpret score
            if result['technical_score'] > 0.3:
                print(f"  ➡️  Signal: BULLISH (strong positive)")
            elif result['technical_score'] > 0:
                print(f"  ➡️  Signal: Slightly Bullish")
            elif result['technical_score'] < -0.3:
                print(f"  ➡️  Signal: BEARISH (strong negative)")
            elif result['technical_score'] < 0:
                print(f"  ➡️  Signal: Slightly Bearish")
            else:
                print(f"  ➡️  Signal: NEUTRAL")
            
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
    print("Technical Indicators API Test Suite")
    print("="*70)
    
    # Test health endpoint
    if not test_health():
        print("\n❌ Health check failed. Make sure the API is running on port 8000")
        print("   Start with: uvicorn ml_service.main:app --reload")
        return
    
    # Test cases for different asset types
    test_cases = [
        ("AAPL", "3mo", "Stock - Apple"),
        ("BTC-USD", "3mo", "Cryptocurrency - Bitcoin"),
        ("ETH-USD", "1mo", "Cryptocurrency - Ethereum"),
        ("TSLA", "3mo", "Stock - Tesla"),
        ("GOOGL", "6mo", "Stock - Google"),
    ]
    
    print("\n" + "="*70)
    print("Testing Technical Indicators")
    print("="*70)
    
    results = []
    for symbol, period, description in test_cases:
        print(f"\n{description}")
        print("-"*70)
        result = test_technical_indicator(symbol, period)
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
        print("\nResults Summary:")
        for i, result in enumerate(results, 1):
            score = result['technical_score']
            signal = "BULLISH" if score > 0.3 else "BEARISH" if score < -0.3 else "NEUTRAL"
            print(f"{i}. {result['symbol']}: {signal} (score: {score:.4f})")


if __name__ == "__main__":
    # Example curl command
    print("\nExample cURL command:")
    print("-"*70)
    print('curl -X POST http://localhost:8000/technical \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"symbol": "BTC-USD"}\'')
    print("-"*70)
    
    main()
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)

