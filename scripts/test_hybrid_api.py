#!/usr/bin/env python3
"""
Test script for Hybrid AI Decision Engine API
Tests the /hybrid endpoint with various trading symbols
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


def test_hybrid_signal(symbol: str):
    """
    Test hybrid signal generation endpoint
    
    Args:
        symbol: Trading symbol
    """
    print(f"\nSymbol: {symbol}")
    
    try:
        payload = {"symbol": symbol}
        
        response = requests.post(
            f"{API_URL}/hybrid",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"  Sentiment Score: {result['sentiment_score']:.4f if result['sentiment_score'] else 'N/A'}")
            print(f"  Technical Score: {result['technical_score']:.4f if result['technical_score'] else 'N/A'}")
            print(f"  Hybrid Score: {result['hybrid_score']:.4f}")
            print(f"  Signal: {result['signal']}")
            print(f"  Confidence: {result['confidence']:.4f}")
            print(f"  Reason: {result['reason']}")
            
            # Visual indicator
            score = result['hybrid_score']
            if result['signal'] == "BUY":
                print(f"  🟢 BUY Signal (Bullish momentum)")
            elif result['signal'] == "SELL":
                print(f"  🔴 SELL Signal (Bearish momentum)")
            else:
                print(f"  🟡 HOLD Signal (Neutral)")
            
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
    print("Hybrid AI Decision Engine API Test Suite")
    print("="*70)
    
    # Test health endpoint
    if not test_health():
        print("\n❌ Health check failed. Make sure:")
        print("   1. The API is running on port 8000")
        print("   2. PostgreSQL database is accessible")
        print("   3. Sentiment and technical data exist in database")
        print("\nStart with: uvicorn ml_service.main:app --reload")
        return
    
    # Test cases for different asset types
    test_cases = [
        ("AAPL", "Stock - Apple"),
        ("BTC-USD", "Cryptocurrency - Bitcoin"),
        ("ETH-USD", "Cryptocurrency - Ethereum"),
        ("TSLA", "Stock - Tesla"),
    ]
    
    print("\n" + "="*70)
    print("Testing Hybrid Signal Generation")
    print("="*70)
    print("\nNote: Requires sentiment and technical data in database")
    print("If data is missing, the endpoint will return HOLD signal")
    
    results = []
    for symbol, description in test_cases:
        print(f"\n{description}")
        print("-"*70)
        result = test_hybrid_signal(symbol)
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
        print("\nSignal Distribution:")
        buy_count = sum(1 for r in results if r['signal'] == 'BUY')
        sell_count = sum(1 for r in results if r['signal'] == 'SELL')
        hold_count = sum(1 for r in results if r['signal'] == 'HOLD')
        print(f"  BUY: {buy_count}")
        print(f"  SELL: {sell_count}")
        print(f"  HOLD: {hold_count}")
        
        print("\nResults Summary:")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['symbol']}: {result['signal']} "
                  f"(hybrid_score: {result['hybrid_score']:.4f}, "
                  f"confidence: {result['confidence']:.4f})")


if __name__ == "__main__":
    # Example curl command
    print("\nExample cURL command:")
    print("-"*70)
    print('curl -X POST http://localhost:8000/hybrid \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"symbol": "BTC-USD"}\'')
    print("-"*70)
    
    print("\n📝 Preparation Steps:")
    print("1. Ensure PostgreSQL is running with schema.sql loaded")
    print("2. Run sentiment analysis first: POST /sentiment")
    print("3. Run technical analysis first: POST /technical")
    print("4. Then run hybrid analysis: POST /hybrid")
    print("-"*70)
    
    main()
    
    print("\n" + "="*70)
    print("Test Complete")
    print("="*70)

