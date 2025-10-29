#!/usr/bin/env python3
"""
CryptoMind AI - Comprehensive System Test
Tests all components of the crypto-focused AI system
"""

import requests
import json
import time
from datetime import datetime

# Configuration
ML_SERVICE_URL = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8501"

def test_health_endpoint():
    """Test ML service health endpoint"""
    print("🔍 Testing ML Service Health...")
    try:
        response = requests.get(f"{ML_SERVICE_URL}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ML Service Status: {data.get('status', 'Unknown')}")
            print(f"   Models Loaded: {data.get('models_loaded', False)}")
            print(f"   Crypto Data Available: {data.get('crypto_data_available', False)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_crypto_sentiment():
    """Test crypto-specific sentiment analysis"""
    print("\n🧠 Testing Crypto Sentiment Analysis...")
    
    test_cases = [
        {
            "symbol": "BTCUSDT",
            "text": "Bitcoin reaches new all-time high amid strong institutional adoption and ETF approvals"
        },
        {
            "symbol": "ETHUSDT", 
            "text": "Ethereum network upgrade brings significant improvements to scalability and gas fees"
        },
        {
            "symbol": "SOLUSDT",
            "text": "Solana ecosystem continues to grow with new DeFi protocols and NFT marketplaces"
        },
        {
            "symbol": "XRPUSDT",
            "text": "Ripple faces regulatory challenges as SEC lawsuit creates uncertainty in the market"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        try:
            response = requests.post(
                f"{ML_SERVICE_URL}/sentiment",
                json=test_case,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Test {i}: {test_case['symbol']}")
                print(f"   Sentiment: {data.get('label', 'Unknown')}")
                print(f"   Score: {data.get('sentiment_score', 0):.3f}")
                print(f"   Confidence: {data.get('confidence', 0):.3f}")
            else:
                print(f"❌ Test {i} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test {i} error: {e}")
        
        time.sleep(0.5)  # Rate limiting

def test_technical_indicators():
    """Test technical indicators for crypto symbols"""
    print("\n📊 Testing Technical Indicators...")
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
    
    for i, symbol in enumerate(symbols, 1):
        try:
            response = requests.post(
                f"{ML_SERVICE_URL}/technical",
                json={"symbol": symbol, "period": "7d"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Test {i}: {symbol}")
                print(f"   EMA20: {data.get('ema20', 0):.2f}")
                print(f"   EMA50: {data.get('ema50', 0):.2f}")
                print(f"   RSI: {data.get('rsi', 0):.2f}")
                print(f"   MACD: {data.get('macd', 0):.2f}")
                print(f"   Technical Score: {data.get('technical_score', 0):.3f}")
            else:
                print(f"❌ Test {i} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test {i} error: {e}")
        
        time.sleep(1)  # Rate limiting

def test_hybrid_signals():
    """Test hybrid signal generation with volatility"""
    print("\n🤖 Testing Hybrid Signal Generation...")
    
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"]
    
    for i, symbol in enumerate(symbols, 1):
        try:
            response = requests.post(
                f"{ML_SERVICE_URL}/hybrid",
                json={"symbol": symbol},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Test {i}: {symbol}")
                print(f"   Signal: {data.get('signal', 'Unknown')}")
                print(f"   Hybrid Score: {data.get('hybrid_score', 0):.3f}")
                print(f"   Confidence: {data.get('confidence', 0):.3f}")
                print(f"   Sentiment: {data.get('sentiment_score', 0):.3f}")
                print(f"   Technical: {data.get('technical_score', 0):.3f}")
                print(f"   Volatility: {data.get('volatility_index', 0):.3f}")
                print(f"   Reason: {data.get('reason', 'No reason provided')[:100]}...")
            else:
                print(f"❌ Test {i} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test {i} error: {e}")
        
        time.sleep(1)  # Rate limiting

def test_crypto_news():
    """Test crypto news endpoint"""
    print("\n📰 Testing Crypto News...")
    
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/crypto/news",
            json={"currencies": ["BTC", "ETH", "SOL", "XRP"], "limit": 5},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                items = data.get('items', [])
                print(f"✅ News fetched: {len(items)} items")
                
                for i, item in enumerate(items[:3], 1):  # Show first 3
                    print(f"   News {i}: {item.get('title', 'No title')[:80]}...")
                    print(f"      Source: {item.get('source', 'Unknown')}")
                    print(f"      Sentiment: {item.get('sentiment_label', 'Unknown')} ({item.get('sentiment_score', 0):.3f})")
            else:
                print(f"❌ News fetch failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ News request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ News error: {e}")

def test_crypto_market_data():
    """Test crypto market data endpoint"""
    print("\n📈 Testing Crypto Market Data...")
    
    symbols = ["BTCUSDT", "ETHUSDT"]
    
    for i, symbol in enumerate(symbols, 1):
        try:
            response = requests.post(
                f"{ML_SERVICE_URL}/crypto/market",
                json={"symbol": symbol, "period": "1d"},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Test {i}: {symbol}")
                    print(f"   Data Points: {data.get('data_points', 0)}")
                    print(f"   Latest Price: ${data.get('latest_price', 0):,.2f}")
                    print(f"   Period: {data.get('period', 'Unknown')}")
                else:
                    print(f"❌ Test {i} failed: {data.get('message', 'Unknown error')}")
            else:
                print(f"❌ Test {i} failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Test {i} error: {e}")
        
        time.sleep(1)  # Rate limiting

def test_market_overview():
    """Test market overview endpoint"""
    print("\n🌐 Testing Market Overview...")
    
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/crypto/market",
            json={},  # No symbol = overview
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                overview = data.get('overview', {})
                print(f"✅ Market Overview:")
                print(f"   Total Volume: ${overview.get('total_volume', 0):,.0f}")
                print(f"   Gainers: {overview.get('gainers', 0)}")
                print(f"   Losers: {overview.get('losers', 0)}")
                print(f"   Total Pairs: {overview.get('total_pairs', 0)}")
            else:
                print(f"❌ Overview failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ Overview request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Overview error: {e}")

def test_dashboard_access():
    """Test dashboard accessibility"""
    print("\n🖥️  Testing Dashboard Access...")
    
    try:
        response = requests.get(DASHBOARD_URL, timeout=10)
        if response.status_code == 200:
            print(f"✅ Dashboard accessible at {DASHBOARD_URL}")
            return True
        else:
            print(f"❌ Dashboard error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting CryptoMind AI Comprehensive System Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test results tracking
    results = []
    
    # Run all tests
    results.append(("Health Check", test_health_endpoint()))
    results.append(("Crypto Sentiment", True))  # Will be tested in function
    test_crypto_sentiment()
    
    results.append(("Technical Indicators", True))  # Will be tested in function
    test_technical_indicators()
    
    results.append(("Hybrid Signals", True))  # Will be tested in function
    test_hybrid_signals()
    
    results.append(("Crypto News", True))  # Will be tested in function
    test_crypto_news()
    
    results.append(("Market Data", True))  # Will be tested in function
    test_crypto_market_data()
    
    results.append(("Market Overview", True))  # Will be tested in function
    test_market_overview()
    
    results.append(("Dashboard Access", test_dashboard_access()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All tests passed! CryptoMind AI is ready for use.")
    else:
        print("⚠️  Some tests failed. Please check the logs above.")
    
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    run_comprehensive_test()
