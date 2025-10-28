"""
Streamlit Dashboard for AI-Driven Sentiment Market Prediction System
Real-time visualization of signals, sentiment, and technical indicators
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="AI Sentiment Market Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1E88E5;
    }
    .buy-signal {
        color: #28a745;
        font-weight: bold;
    }
    .sell-signal {
        color: #dc3545;
        font-weight: bold;
    }
    .hold-signal {
        color: #ffc107;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8080/api/v1")
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000")

# Sidebar
st.sidebar.title("📊 Configuration")
selected_symbol = st.sidebar.selectbox(
    "Select Symbol",
    ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "XRPUSDT"],
    index=0
)

time_range = st.sidebar.selectbox(
    "Time Range",
    ["1 Day", "7 Days", "30 Days", "90 Days"],
    index=1
)

auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 10, 300, 30)

# Helper functions
def fetch_signals(symbol: str):
    """Fetch trading signals from API"""
    try:
        response = requests.get(f"{API_URL}/signals/{symbol}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except Exception as e:
        st.error(f"Error fetching signals: {e}")
        return []

def fetch_sentiment(symbol: str):
    """Fetch sentiment data from API"""
    try:
        response = requests.get(f"{API_URL}/sentiment/{symbol}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except Exception as e:
        st.error(f"Error fetching sentiment: {e}")
        return []

def fetch_technical(symbol: str):
    """Fetch technical indicators from API"""
    try:
        response = requests.get(f"{API_URL}/technical/{symbol}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except Exception as e:
        st.error(f"Error fetching technical data: {e}")
        return []

def fetch_market_data(symbol: str):
    """Fetch market data from API"""
    try:
        response = requests.get(f"{API_URL}/market/{symbol}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        return []
    except Exception as e:
        st.error(f"Error fetching market data: {e}")
        return []

def get_signal_color(signal: str):
    """Get color for signal type"""
    if signal == "BUY":
        return "#28a745"
    elif signal == "SELL":
        return "#dc3545"
    else:
        return "#ffc107"

def plot_price_and_signals(market_data, signals):
    """Create price chart with signals"""
    if not market_data:
        return None
    
    df_market = pd.DataFrame(market_data)
    df_market['timestamp'] = pd.to_datetime(df_market['timestamp'])
    df_market = df_market.sort_values('timestamp')
    
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df_market['timestamp'],
        open=df_market['open'],
        high=df_market['high'],
        low=df_market['low'],
        close=df_market['close'],
        name="Price"
    ))
    
    # Add signals as markers
    if signals:
        df_signals = pd.DataFrame(signals)
        df_signals['timestamp'] = pd.to_datetime(df_signals['timestamp'])
        df_signals = df_signals.sort_values('timestamp')
        
        # Buy signals
        buy_signals = df_signals[df_signals['signal'] == 'BUY']
        if not buy_signals.empty:
            fig.add_trace(go.Scatter(
                x=buy_signals['timestamp'],
                y=df_market.merge(buy_signals, on='timestamp', how='inner')['close'],
                mode='markers',
                marker=dict(symbol='triangle-up', size=15, color='green'),
                name='Buy Signal',
                showlegend=True
            ))
        
        # Sell signals
        sell_signals = df_signals[df_signals['signal'] == 'SELL']
        if not sell_signals.empty:
            fig.add_trace(go.Scatter(
                x=sell_signals['timestamp'],
                y=df_market.merge(sell_signals, on='timestamp', how='inner')['close'],
                mode='markers',
                marker=dict(symbol='triangle-down', size=15, color='red'),
                name='Sell Signal',
                showlegend=True
            ))
    
    fig.update_layout(
        title=f"{selected_symbol} Price Chart with Trading Signals",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        height=500,
        hovermode='x unified'
    )
    
    return fig

def plot_sentiment_and_technical(sentiment_data, technical_data):
    """Create sentiment and technical indicators chart"""
    if not sentiment_data or not technical_data:
        return None
    
    df_sentiment = pd.DataFrame(sentiment_data)
    df_technical = pd.DataFrame(technical_data)
    
    df_sentiment['timestamp'] = pd.to_datetime(df_sentiment['timestamp'])
    df_technical['timestamp'] = pd.to_datetime(df_technical['timestamp'])
    
    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Sentiment Score', 'Technical Indicators', 'Hybrid Score'),
        vertical_spacing=0.12
    )
    
    # Sentiment score
    fig.add_trace(
        go.Scatter(
            x=df_sentiment['timestamp'],
            y=df_sentiment['sentiment_score'],
            mode='lines+markers',
            name='Sentiment',
            line=dict(color='blue'),
            fill='tozeroy'
        ),
        row=1, col=1
    )
    
    # Technical indicators (RSI)
    fig.add_trace(
        go.Scatter(
            x=df_technical['timestamp'],
            y=df_technical['rsi'],
            mode='lines',
            name='RSI',
            line=dict(color='orange')
        ),
        row=2, col=1
    )
    
    # Technical score
    fig.add_trace(
        go.Scatter(
            x=df_technical['timestamp'],
            y=df_technical['technical_score'],
            mode='lines+markers',
            name='Technical Score',
            line=dict(color='purple'),
            fill='tozeroy'
        ),
        row=3, col=1
    )
    
    fig.update_layout(
        height=700,
        title_text="Sentiment & Technical Analysis",
        hovermode='x unified'
    )
    
    fig.update_xaxes(title_text="Time", row=3, col=1)
    fig.update_yaxes(title_text="Score (0-1)", row=1, col=1)
    fig.update_yaxes(title_text="RSI", row=2, col=1)
    fig.update_yaxes(title_text="Score (0-1)", row=3, col=1)
    
    return fig

# Main content
st.markdown('<div class="main-header">📈 AI Sentiment Market Prediction System</div>', unsafe_allow_html=True)

# Fetch data
signals = fetch_signals(selected_symbol)
sentiment = fetch_sentiment(selected_symbol)
technical = fetch_technical(selected_symbol)
market_data = fetch_market_data(selected_symbol)

# Latest signal metrics
if signals:
    latest_signal = signals[0] if signals else None
    if latest_signal:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            signal_class = f"{latest_signal['signal'].lower()}-signal"
            st.metric("Current Signal", latest_signal['signal'], delta=None)
        
        with col2:
            st.metric("Hybrid Score", f"{latest_signal['hybrid_score']:.4f}", delta=None)
        
        with col3:
            st.metric("Confidence", f"{latest_signal['confidence']*100:.2f}%", delta=None)
        
        with col4:
            timestamp = pd.to_datetime(latest_signal['timestamp'])
            st.metric("Last Updated", timestamp.strftime("%H:%M:%S"), delta=None)
        
        # Display reason
        st.info(f"💡 **Reason**: {latest_signal['reason']}")
else:
    st.warning("No signals available for the selected symbol")

# Charts section
st.markdown("---")
st.subheader("📊 Price Chart with Trading Signals")

if market_data:
    fig_price = plot_price_and_signals(market_data, signals)
    if fig_price:
        st.plotly_chart(fig_price, use_container_width=True)
else:
    st.info("No market data available")

if sentiment and technical:
    st.subheader("🔍 Sentiment & Technical Analysis")
    fig_analysis = plot_sentiment_and_technical(sentiment, technical)
    if fig_analysis:
        st.plotly_chart(fig_analysis, use_container_width=True)

# Signals table
st.markdown("---")
st.subheader("📋 Recent Trading Signals")

if signals:
    df_signals = pd.DataFrame(signals)
    df_signals['timestamp'] = pd.to_datetime(df_signals['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    # Format display
    df_display = df_signals[['timestamp', 'symbol', 'signal', 'hybrid_score', 'confidence', 'reason']].copy()
    df_display.columns = ['Timestamp', 'Symbol', 'Signal', 'Hybrid Score', 'Confidence', 'Reason']
    
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("No signals data available")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>AI-Driven Sentiment Market Prediction System</p>
    <p>Powered by FinBERT + Technical Analysis + Hybrid AI Engine</p>
</div>
""", unsafe_allow_html=True)

# Auto refresh
if auto_refresh:
    st.rerun()

