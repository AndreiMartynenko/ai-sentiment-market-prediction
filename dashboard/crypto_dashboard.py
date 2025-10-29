"""
CryptoMind AI - Cryptocurrency Market Dashboard
Enhanced Streamlit dashboard for cryptocurrency market analysis
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import os
import numpy as np

# Page configuration
st.set_page_config(
    page_title="CryptoMind AI - Cryptocurrency Market Dashboard",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #F7931A;
        text-align: center;
        margin-bottom: 1rem;
    }
    .crypto-card {
        background: linear-gradient(135deg, #F7931A 0%, #FF6B35 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .news-positive { color: #28a745; font-weight: bold; }
    .news-negative { color: #dc3545; font-weight: bold; }
    .news-neutral { color: #6c757d; font-weight: bold; }
    .signal-buy { color: #28a745; font-weight: bold; }
    .signal-sell { color: #dc3545; font-weight: bold; }
    .signal-hold { color: #ffc107; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# API Configuration
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000")

def get_crypto_news(limit=10):
    """Fetch crypto news from ML service"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/crypto/news",
            json={"currencies": ["BTC", "ETH", "SOL", "XRP"], "limit": limit},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return None

def get_crypto_market_data(symbol, period="1d"):
    """Fetch crypto market data from ML service"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/crypto/market",
            json={"symbol": symbol, "period": period},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return None

def get_hybrid_signal(symbol):
    """Get hybrid trading signal for symbol"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/hybrid",
            json={"symbol": symbol},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching hybrid signal: {e}")
        return None

def get_sentiment_analysis(symbol, text):
    """Get sentiment analysis for text"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/sentiment",
            json={"symbol": symbol, "text": text},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching sentiment analysis: {e}")
        return None

def plot_crypto_price_chart(data, symbol):
    """Create crypto price chart with candlesticks"""
    if not data or 'data' not in data:
        return None
    
    df = pd.DataFrame(data['data'])
    if df.empty:
        return None
    
    fig = go.Figure(data=go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name=symbol,
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    fig.update_layout(
        title=f"{symbol} Price Chart",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        height=500,
        template="plotly_white"
    )
    
    return fig

def display_news_with_sentiment(news_data):
    """Display news items with sentiment color coding"""
    if not news_data or 'items' not in news_data:
        st.info("No news available")
        return
    
    st.subheader("📰 Latest Crypto News")
    
    for i, item in enumerate(news_data['items'][:5]):  # Show top 5
        sentiment_score = item.get('sentiment_score', 0)
        sentiment_label = item.get('sentiment_label', 'neutral')
        
        # Color coding based on sentiment
        if sentiment_score > 0.1:
            sentiment_class = "news-positive"
            sentiment_icon = "📈"
        elif sentiment_score < -0.1:
            sentiment_class = "news-negative"
            sentiment_icon = "📉"
        else:
            sentiment_class = "news-neutral"
            sentiment_icon = "➡️"
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"**{item['title']}**")
                st.caption(f"Source: {item['source']} | {item['published_at']}")
            
            with col2:
                st.markdown(f'<span class="{sentiment_class}">{sentiment_icon} {sentiment_label.upper()}</span>', 
                           unsafe_allow_html=True)
                st.caption(f"Score: {sentiment_score:.2f}")
        
        st.divider()

def display_hybrid_signal(signal_data):
    """Display hybrid trading signal with confidence"""
    if not signal_data:
        st.info("No signal data available")
        return
    
    st.subheader("🤖 Hybrid AI Signal")
    
    # Signal display
    signal = signal_data.get('signal', 'HOLD')
    confidence = signal_data.get('confidence', 0)
    hybrid_score = signal_data.get('hybrid_score', 0)
    
    # Color coding
    if signal == 'BUY':
        signal_class = "signal-buy"
        signal_icon = "🚀"
    elif signal == 'SELL':
        signal_class = "signal-sell"
        signal_icon = "📉"
    else:
        signal_class = "signal-hold"
        signal_icon = "⏸️"
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Signal",
            f"{signal_icon} {signal}",
            delta=f"Score: {hybrid_score:.3f}"
        )
    
    with col2:
        st.metric(
            "Confidence",
            f"{confidence:.1%}",
            delta="AI Confidence"
        )
    
    with col3:
        sentiment_score = signal_data.get('sentiment_score', 0)
        technical_score = signal_data.get('technical_score', 0)
        volatility_index = signal_data.get('volatility_index', 0)
        
        st.metric(
            "Components",
            f"S:{sentiment_score:.2f} T:{technical_score:.2f} V:{volatility_index:.2f}",
            delta="Sentiment | Technical | Volatility"
        )
    
    # Detailed breakdown
    with st.expander("📊 Signal Breakdown"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Sentiment Analysis**")
            st.write(f"Score: {sentiment_score:.3f}")
            st.progress(abs(sentiment_score))
        
        with col2:
            st.write("**Technical Analysis**")
            st.write(f"Score: {technical_score:.3f}")
            st.progress(abs(technical_score))
        
        with col3:
            st.write("**Volatility Index**")
            st.write(f"Index: {volatility_index:.3f}")
            st.progress(abs(volatility_index))
        
        st.write("**Reasoning:**")
        st.write(signal_data.get('reason', 'No reasoning available'))

def main():
    """Main dashboard application"""
    st.markdown('<h1 class="main-header">₿ CryptoMind AI - Cryptocurrency Market Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Symbol selection
        symbol = st.selectbox(
            "Select Cryptocurrency",
            ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT", "DOTUSDT", "LINKUSDT"],
            index=0
        )
        
        # Time period selection
        period = st.selectbox(
            "Select Time Period",
            ["1h", "4h", "1d", "7d", "30d"],
            index=2
        )
        
        # Refresh button
        if st.button("🔄 Refresh Data", type="primary"):
            st.rerun()
        
        # API Status
        st.header("🔗 API Status")
        try:
            response = requests.get(f"{ML_SERVICE_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ ML Service Connected")
            else:
                st.error("❌ ML Service Error")
        except:
            st.error("❌ ML Service Offline")
    
    # Main content area
    tab1, tab2, tab3, tab4 = st.tabs(["₿ Crypto Overview", "📰 News & Sentiment", "📊 Market Analysis", "🤖 AI Signals"])
    
    with tab1:
        st.header("₿ Cryptocurrency Market Overview")
        
        # Get market data
        market_data = get_crypto_market_data(symbol, period)
        
        if market_data and market_data.get('success'):
            # Price chart
            fig = plot_crypto_price_chart(market_data, symbol)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Market metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Current Price",
                    f"${market_data.get('latest_price', 0):,.2f}",
                    delta="USDT"
                )
            
            with col2:
                st.metric(
                    "Data Points",
                    market_data.get('data_points', 0),
                    delta="Candles"
                )
            
            with col3:
                st.metric(
                    "Period",
                    period.upper(),
                    delta="Timeframe"
                )
            
            with col4:
                st.metric(
                    "Symbol",
                    symbol,
                    delta="Trading Pair"
                )
        else:
            st.error("Failed to load market data")
    
    with tab2:
        st.header("📰 News & Sentiment Analysis")
        
        # Get crypto news
        news_data = get_crypto_news(10)
        display_news_with_sentiment(news_data)
        
        # Sentiment analysis section
        st.subheader("🧠 Sentiment Analysis")
        
        # Text input for custom analysis
        custom_text = st.text_area(
            "Enter custom text for sentiment analysis:",
            placeholder="e.g., Bitcoin reaches new all-time high amid strong institutional adoption...",
            height=100
        )
        
        if st.button("Analyze Sentiment") and custom_text:
            sentiment_result = get_sentiment_analysis(symbol, custom_text)
            if sentiment_result:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Sentiment",
                        sentiment_result.get('label', 'Unknown').upper(),
                        delta=f"Score: {sentiment_result.get('sentiment_score', 0):.3f}"
                    )
                
                with col2:
                    st.metric(
                        "Confidence",
                        f"{sentiment_result.get('confidence', 0):.1%}",
                        delta="Model Confidence"
                    )
                
                with col3:
                    st.metric(
                        "Symbol",
                        sentiment_result.get('symbol', symbol),
                        delta="Analyzed For"
                    )
    
    with tab3:
        st.header("📊 Technical Analysis")
        
        # Get hybrid signal for technical analysis
        signal_data = get_hybrid_signal(symbol)
        
        if signal_data:
            # Technical indicators display
            st.subheader("📈 Technical Indicators")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                technical_score = signal_data.get('technical_score', 0)
                st.metric(
                    "Technical Score",
                    f"{technical_score:.3f}",
                    delta="EMA + RSI + MACD"
                )
            
            with col2:
                volatility_index = signal_data.get('volatility_index', 0)
                st.metric(
                    "Volatility Index",
                    f"{volatility_index:.3f}",
                    delta="Price Variance"
                )
            
            with col3:
                sentiment_score = signal_data.get('sentiment_score', 0)
                st.metric(
                    "Sentiment Score",
                    f"{sentiment_score:.3f}",
                    delta="News Analysis"
                )
            
            # Technical analysis explanation
            with st.expander("🔍 Technical Analysis Details"):
                st.write("**Technical Score Components:**")
                st.write("- EMA Trend: Exponential Moving Average analysis")
                st.write("- RSI Momentum: Relative Strength Index (0-100)")
                st.write("- MACD Signal: Moving Average Convergence Divergence")
                st.write(f"**Current Technical Score: {technical_score:.3f}**")
                
                if technical_score > 0.3:
                    st.success("📈 Bullish technical indicators detected")
                elif technical_score < -0.3:
                    st.error("📉 Bearish technical indicators detected")
                else:
                    st.info("➡️ Neutral technical indicators")
        else:
            st.error("Failed to load technical analysis data")
    
    with tab4:
        st.header("🤖 AI Trading Signals")
        
        # Get hybrid signal
        signal_data = get_hybrid_signal(symbol)
        display_hybrid_signal(signal_data)
        
        # Signal history (if available)
        st.subheader("📊 Signal History")
        st.info("Signal history will be displayed here when database integration is complete.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>₿ CryptoMind AI - Hybrid Cryptocurrency Market Analysis</strong></p>
        <p>Powered by FinBERT + Technical Analysis + Volatility Modeling + Hybrid AI Decision Engine</p>
        <p style="font-size: 0.8rem;">Last updated: {}</p>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
