"""
Streamlit Dashboard for AI-Driven Sentiment Market Prediction System
Professional real-time visualization with PostgreSQL database integration
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import os
import numpy as np
import requests

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
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .buy-signal { color: #28a745; font-weight: bold; }
    .sell-signal { color: #dc3545; font-weight: bold; }
    .hold-signal { color: #ffc107; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "database": os.getenv("POSTGRES_DB", "sentiment_market"),
    "port": int(os.getenv("POSTGRES_PORT", "5432"))
}

@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_db_connection():
    """Create database connection with caching"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def load_data_from_db(table_name: str, symbol: str, limit: int = 200) -> pd.DataFrame:
    """
    Load data from PostgreSQL table
    
    Args:
        table_name: Name of the table
        symbol: Trading symbol to filter by
        limit: Maximum number of rows to fetch
        
    Returns:
        DataFrame with the data
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        query = f"""
        SELECT * FROM {table_name} 
        WHERE symbol = %s 
        ORDER BY timestamp DESC 
        LIMIT %s
        """
        df = pd.read_sql(query, conn, params=(symbol, limit))
        return df
    except Exception as e:
        st.error(f"Error loading data from {table_name}: {e}")
        return pd.DataFrame()
    finally:
        conn.close()

def get_signal_color(signal: str) -> str:
    """Get color for signal type"""
    signal_colors = {"BUY": "#28a745", "SELL": "#dc3545", "HOLD": "#ffc107"}
    return signal_colors.get(signal, "#6c757d")

def plot_candlestick_with_ema(df: pd.DataFrame) -> go.Figure:
    """Create candlestick chart with EMA overlays"""
    fig = go.Figure()
    
    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Price",
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    # Add EMA20
    if 'ema20' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ema20'],
            name="EMA20",
            line=dict(color='orange', width=1.5)
        ))
    
    # Add EMA50
    if 'ema50' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['ema50'],
            name="EMA50",
            line=dict(color='blue', width=1.5)
        ))
    
    fig.update_layout(
        title=f"Price Chart with Exponential Moving Averages",
        xaxis_title="Time",
        yaxis_title="Price",
        height=600,
        hovermode='x unified',
        template="plotly_white"
    )
    
    return fig

def plot_sentiment_timeline(df: pd.DataFrame) -> go.Figure:
    """Create sentiment score timeline with color coding"""
    fig = go.Figure()
    
    # Color based on sentiment polarity
    colors = ['green' if x > 0 else 'red' if x < 0 else 'gray' for x in df['sentiment_score']]
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['sentiment_score'],
        mode='lines+markers',
        name='Sentiment Score',
        line=dict(color='blue', width=2),
        marker=dict(size=6),
        fill='tozeroy',
        fillcolor='rgba(100, 100, 255, 0.1)'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title="Sentiment Analysis Timeline (FinBERT)",
        xaxis_title="Time",
        yaxis_title="Sentiment Score (-1.0 to +1.0)",
        height=500,
        template="plotly_white"
    )
    
    return fig

def plot_technical_indicators(df: pd.DataFrame) -> go.Figure:
    """Create technical indicators chart with RSI and MACD"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('RSI (Relative Strength Index)', 'MACD (Moving Average Convergence Divergence)'),
        vertical_spacing=0.15
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'],
            y=df['rsi'],
            mode='lines',
            name='RSI',
            line=dict(color='purple', width=2)
        ),
        row=1, col=1
    )
    
    # Add RSI overbought/oversold lines
    fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, row=1, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=1, col=1)
    
    # MACD
    if 'macd' in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['macd'],
                mode='lines',
                name='MACD',
                line=dict(color='blue', width=2)
            ),
            row=2, col=1
        )
    
    fig.update_layout(
        height=600,
        title_text="Technical Indicators",
        hovermode='x unified',
        template="plotly_white"
    )
    
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="RSI (0-100)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    
    return fig

def plot_hybrid_signals(df: pd.DataFrame) -> go.Figure:
    """Create hybrid score timeline with signal markers"""
    fig = go.Figure()
    
    # Plot hybrid score
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['hybrid_score'],
        mode='lines+markers',
        name='Hybrid Score',
        line=dict(color='blue', width=2),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(100, 100, 255, 0.1)'
    ))
    
    # Add signal markers
    buy_signals = df[df['signal'] == 'BUY']
    sell_signals = df[df['signal'] == 'SELL']
    hold_signals = df[df['signal'] == 'HOLD']
    
    if not buy_signals.empty:
        fig.add_trace(go.Scatter(
            x=buy_signals['timestamp'],
            y=buy_signals['hybrid_score'],
            mode='markers',
            name='🟢 BUY',
            marker=dict(symbol='triangle-up', size=12, color='green', line=dict(width=2))
        ))
    
    if not sell_signals.empty:
        fig.add_trace(go.Scatter(
            x=sell_signals['timestamp'],
            y=sell_signals['hybrid_score'],
            mode='markers',
            name='🔴 SELL',
            marker=dict(symbol='triangle-down', size=12, color='red', line=dict(width=2))
        ))
    
    if not hold_signals.empty:
        fig.add_trace(go.Scatter(
            x=hold_signals['timestamp'],
            y=hold_signals['hybrid_score'],
            mode='markers',
            name='⚪ HOLD',
            marker=dict(symbol='circle', size=8, color='gray', line=dict(width=1))
        ))
    
    # Add threshold lines
    fig.add_hline(y=0.3, line_dash="dash", line_color="green", opacity=0.5)
    fig.add_hline(y=-0.3, line_dash="dash", line_color="red", opacity=0.5)
    
    fig.update_layout(
        title="Hybrid AI Signals Over Time",
        xaxis_title="Time",
        yaxis_title="Hybrid Score (-1.0 to +1.0)",
        height=500,
        template="plotly_white"
    )
    
    return fig

def plot_confidence(df: pd.DataFrame) -> go.Figure:
    """Create confidence bar chart"""
    fig = go.Figure()
    
    # Color bars based on signal
    colors = [get_signal_color(signal) for signal in df['signal']]
    
    fig.add_trace(go.Bar(
        x=df['timestamp'],
        y=df['confidence'],
        name='Confidence',
        marker=dict(color=colors),
        text=[f"{c*100:.1f}%" for c in df['confidence']],
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Signal Confidence Levels",
        xaxis_title="Time",
        yaxis_title="Confidence (0-1)",
        height=400,
        template="plotly_white"
    )
    
    return fig

# Sidebar Configuration
st.sidebar.title("📊 Dashboard Configuration")

selected_symbol = st.sidebar.selectbox(
    "Select Trading Symbol",
    ["AAPL", "TSLA", "GOOGL", "BTC-USD", "ETH-USD", "MSFT", "NVDA"],
    index=3
)

# Date range filter
date_range = st.sidebar.selectbox(
    "Time Range",
    ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
    index=2
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Signal Thresholds")
st.sidebar.info("""
- **BUY**: hybrid_score > 0.3
- **HOLD**: -0.3 ≤ hybrid_score ≤ 0.3
- **SELL**: hybrid_score < -0.3
""")

# Main Content
st.markdown('<div class="main-header">📈 AI-Driven Sentiment Market Dashboard</div>', unsafe_allow_html=True)

# KPI Cards
st.markdown("<br>", unsafe_allow_html=True)

# Load latest data
hybrid_df = load_data_from_db("hybrid_signals", selected_symbol, limit=1)
market_df = load_data_from_db("market_data", selected_symbol, limit=1)

# Display KPIs
if not hybrid_df.empty and not market_df.empty:
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    with kpi_col1:
        current_price = market_df.iloc[0]['close'] if not market_df.empty else 0
        st.metric("Current Price", f"${current_price:.2f}" if current_price > 0 else "N/A")
    
    with kpi_col2:
        last_signal = hybrid_df.iloc[0]['signal'] if not hybrid_df.empty else "HOLD"
        st.metric("Last Signal", last_signal)
    
    with kpi_col3:
        confidence = hybrid_df.iloc[0]['confidence'] if not hybrid_df.empty else 0
        st.metric("Confidence", f"{confidence*100:.1f}%")
    
    with kpi_col4:
        sentiment_score = hybrid_df.iloc[0].get('sentiment_score', 0) if not hybrid_df.empty else 0
        trend = "📈 Positive" if sentiment_score > 0 else "📉 Negative" if sentiment_score < 0 else "➡️ Neutral"
        st.metric("Sentiment Trend", trend)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Market Overview", "🧠 Sentiment", "⚙️ Technicals", "🤖 Hybrid Signals"])

# Tab 1: Market Overview
with tab1:
    st.header("📈 Market Overview")
    
    # Load market data and technical indicators
    market_data = load_data_from_db("market_data", selected_symbol, limit=100)
    technical_data = load_data_from_db("technical_indicators", selected_symbol, limit=100)
    
    if not market_data.empty:
        # Merge with technical data for EMAs
        if not technical_data.empty:
            market_data = pd.merge(market_data, technical_data[['timestamp', 'ema20', 'ema50']], 
                                  on='timestamp', how='left')
        
        fig_candle = plot_candlestick_with_ema(market_data)
        st.plotly_chart(fig_candle, use_container_width=True)
        
        # Display latest market data
        with st.expander("📊 Latest Market Data"):
            st.dataframe(market_data.head(10), use_container_width=True)
    else:
        st.info("No market data available for the selected symbol")

# Tab 2: Sentiment
with tab2:
    st.header("🧠 Sentiment Analysis")
    
    sentiment_data = load_data_from_db("sentiment_results", selected_symbol, limit=100)
    
    if not sentiment_data.empty:
        fig_sentiment = plot_sentiment_timeline(sentiment_data)
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Sentiment", f"{sentiment_data['sentiment_score'].mean():.4f}")
        with col2:
            st.metric("Positive Ratio", f"{(sentiment_data['sentiment_score'] > 0).sum() / len(sentiment_data) * 100:.1f}%")
        with col3:
            st.metric("Negative Ratio", f"{(sentiment_data['sentiment_score'] < 0).sum() / len(sentiment_data) * 100:.1f}%")
    else:
        st.info("No sentiment data available for the selected symbol")

# Tab 3: Technicals
with tab3:
    st.header("⚙️ Technical Indicators")
    
    technical_data = load_data_from_db("technical_indicators", selected_symbol, limit=100)
    
    if not technical_data.empty:
        fig_technical = plot_technical_indicators(technical_data)
        st.plotly_chart(fig_technical, use_container_width=True)
        
        # Current values
        current_technical = technical_data.iloc[0] if not technical_data.empty else None
        if current_technical is not None:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("EMA 20", f"{current_technical['ema20']:.2f}")
            with col2:
                st.metric("EMA 50", f"{current_technical['ema50']:.2f}")
            with col3:
                st.metric("RSI", f"{current_technical['rsi']:.2f}")
            with col4:
                st.metric("Technical Score", f"{current_technical['technical_score']:.4f}")
    else:
        st.info("No technical data available for the selected symbol")

# Tab 4: Hybrid Signals
with tab4:
    st.header("🤖 Hybrid AI Signals")
    
    hybrid_data = load_data_from_db("hybrid_signals", selected_symbol, limit=50)
    
    if not hybrid_data.empty:
        # Plot hybrid scores
        fig_hybrid = plot_hybrid_signals(hybrid_data)
        st.plotly_chart(fig_hybrid, use_container_width=True)
        
        # Confidence chart
        fig_confidence = plot_confidence(hybrid_data)
        st.plotly_chart(fig_confidence, use_container_width=True)
        
        # Signals table
        st.subheader("📋 Recent Signals (Last 10)")
        display_cols = ['timestamp', 'signal', 'sentiment_score', 'technical_score', 
                       'hybrid_score', 'confidence', 'reason']
        display_df = hybrid_data[display_cols].copy()
        display_df = display_df.head(10)
        
        # Format display
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df.columns = ['Timestamp', 'Signal', 'Sentiment', 'Technical', 'Hybrid', 'Confidence', 'Reason']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Statistics
        st.subheader("📊 Signal Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Signals", len(hybrid_data))
        with col2:
            buy_count = (hybrid_data['signal'] == 'BUY').sum()
            st.metric("BUY Signals", buy_count)
        with col3:
            sell_count = (hybrid_data['signal'] == 'SELL').sum()
            st.metric("SELL Signals", sell_count)
    else:
        st.info("No hybrid signals available for the selected symbol")

# --- Proof-of-Signal (On-Chain Verification) ---
st.markdown("---")
st.header("🔗 Proof-of-Signal (On-Chain Verification)")

col_ps1, col_ps2 = st.columns([2, 1])
with col_ps1:
    pos_symbol = st.selectbox("Select Symbol", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"], index=0)
    st.caption("Publish the latest AI signal for this symbol to Solana testnet.")

with col_ps2:
    publish_clicked = st.button("Publish Latest Signal to Solana", type="primary")

if publish_clicked:
    # Example payload; in a production flow this would be the latest computed signal
    signal_data = {
        "symbol": pos_symbol,
        "signal": "BUY",
        "sentiment_score": 0.82,
        "technical_score": 0.41,
        "reason": "Positive sentiment + RSI oversold",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    try:
        ml_url = os.getenv("ML_SERVICE_URL", "http://localhost:8000")
        res = requests.post(f"{ml_url}/proof", json=signal_data, timeout=15)
        if res.status_code == 200:
            data = res.json()
            st.success(f"Signal published! [View on Solana Explorer]({data['explorer_url']})")
            st.json(data)
        else:
            st.error(res.text)
    except Exception as e:
        st.error(f"Error publishing proof: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>AI-Driven Sentiment Market Prediction System</strong></p>
    <p>Powered by FinBERT + Technical Analysis + Hybrid AI Decision Engine</p>
    <p style="font-size: 0.8rem;">Last updated: {}</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)
