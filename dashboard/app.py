"""
AI-Driven Cryptocurrency Market Prediction Dashboard
Complete Streamlit dashboard with PostgreSQL integration and Solana Proof-of-Signal
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
from streamlit_autorefresh import st_autorefresh
import hashlib

# Page configuration
st.set_page_config(
    page_title="AI-Blockchain Hybrid Market Predictor",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh every 60 seconds
st_autorefresh(interval=60 * 1000, limit=None, key="dataautorefresh")

# Custom CSS for modern design
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #F7931A;
        text-align: center;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .kpi-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .buy-signal { color: #28a745; font-weight: bold; }
    .sell-signal { color: #dc3545; font-weight: bold; }
    .hold-signal { color: #ffc107; font-weight: bold; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
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

def load_data_from_db(table_name: str, symbol: str, time_range: str = "1M", limit: int = 500) -> pd.DataFrame:
    """
    Load data from PostgreSQL table with time range filtering
    
    Args:
        table_name: Name of the table
        symbol: Trading symbol to filter by
        time_range: Time range filter (1D, 1W, 1M, 3M)
        limit: Maximum number of rows to fetch
        
    Returns:
        DataFrame with the data
    """
    conn = get_db_connection()
    if not conn:
        return pd.DataFrame()
    
    try:
        # Calculate time delta based on range
        now = datetime.now()
        if time_range == "1D":
            delta = timedelta(days=1)
        elif time_range == "1W":
            delta = timedelta(days=7)
        elif time_range == "1M":
            delta = timedelta(days=30)
        elif time_range == "3M":
            delta = timedelta(days=90)
        else:
            delta = timedelta(days=30)  # default
        
        start_time = now - delta
        
        query = f"""
        SELECT * FROM {table_name} 
        WHERE symbol = %s AND timestamp >= %s
        ORDER BY timestamp DESC 
        LIMIT %s
        """
        df = pd.read_sql(query, conn, params=(symbol, start_time, limit))
        
        # Convert timestamp to datetime if present
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
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

def plot_candlestick_with_ema(market_df: pd.DataFrame, technical_df: pd.DataFrame) -> go.Figure:
    """Create candlestick chart with EMA overlays"""
    fig = go.Figure()
    
    # Add candlestick
    fig.add_trace(go.Candlestick(
        x=market_df['timestamp'],
        open=market_df['open'],
        high=market_df['high'],
        low=market_df['low'],
        close=market_df['close'],
        name="Price",
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    # Merge with technical data for EMAs
    if not technical_df.empty:
        merged_df = pd.merge(market_df[['timestamp']], technical_df[['timestamp', 'ema20', 'ema50']], 
                           on='timestamp', how='left')
        
        # Add EMA20
        if 'ema20' in merged_df.columns and not merged_df['ema20'].isna().all():
            fig.add_trace(go.Scatter(
                x=merged_df['timestamp'],
                y=merged_df['ema20'],
                name="EMA20",
                line=dict(color='orange', width=2),
                connectgaps=True
            ))
        
        # Add EMA50
        if 'ema50' in merged_df.columns and not merged_df['ema50'].isna().all():
            fig.add_trace(go.Scatter(
                x=merged_df['timestamp'],
                y=merged_df['ema50'],
                name="EMA50",
                line=dict(color='blue', width=2),
                connectgaps=True
            ))
    
    fig.update_layout(
        title="📊 Market Overview: OHLC with Exponential Moving Averages",
        xaxis_title="Time",
        yaxis_title="Price (USDT)",
        height=600,
        hovermode='x unified',
        template="plotly_white",
        showlegend=True
    )
    
    return fig

def plot_sentiment_timeline(df: pd.DataFrame) -> go.Figure:
    """Create sentiment score timeline with color coding"""
    fig = go.Figure()
    
    # Map sentiment scores to range -1 to 1 if needed
    if df['sentiment_score'].max() <= 1.0:
        # Assuming 0-1 scale, convert to -1 to 1
        sentiment_mapped = (df['sentiment_score'] - 0.5) * 2
    else:
        sentiment_mapped = df['sentiment_score']
    
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=sentiment_mapped,
        mode='lines+markers',
        name='Sentiment Score',
        line=dict(color='#667eea', width=2),
        marker=dict(size=6, color='#764ba2'),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add sentiment bands
    fig.add_hrect(y0=0, y1=1, fillcolor="green", opacity=0.05, layer="below", line_width=0)
    fig.add_hrect(y0=-1, y1=0, fillcolor="red", opacity=0.05, layer="below", line_width=0)
    
    fig.update_layout(
        title="🧠 AI Sentiment Analysis Timeline (FinBERT)",
        xaxis_title="Time",
        yaxis_title="Sentiment Score (-1.0 to +1.0)",
        height=500,
        template="plotly_white",
        hovermode='x unified'
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
    if 'rsi' in df.columns:
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
        fig.add_hline(y=70, line_dash="dash", line_color="red", opacity=0.5, 
                     annotation_text="Overbought (70)", row=1, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5,
                     annotation_text="Oversold (30)", row=1, col=1)
    
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
        
        # Add zero line for MACD
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=2, col=1)
    
    fig.update_layout(
        height=600,
        title_text="⚙️ Technical Indicators",
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
        line=dict(color='#667eea', width=2),
        marker=dict(size=8, color='#764ba2'),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
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
            marker=dict(symbol='triangle-up', size=15, color='green', 
                       line=dict(width=2, color='darkgreen'))
        ))
    
    if not sell_signals.empty:
        fig.add_trace(go.Scatter(
            x=sell_signals['timestamp'],
            y=sell_signals['hybrid_score'],
            mode='markers',
            name='🔴 SELL',
            marker=dict(symbol='triangle-down', size=15, color='red',
                       line=dict(width=2, color='darkred'))
        ))
    
    if not hold_signals.empty:
        fig.add_trace(go.Scatter(
            x=hold_signals['timestamp'],
            y=hold_signals['hybrid_score'],
            mode='markers',
            name='⚪ HOLD',
            marker=dict(symbol='circle', size=10, color='gray',
                       line=dict(width=1, color='darkgray'))
        ))
    
    # Add threshold lines
    fig.add_hline(y=0.3, line_dash="dash", line_color="green", opacity=0.5,
                 annotation_text="BUY Threshold")
    fig.add_hline(y=-0.3, line_dash="dash", line_color="red", opacity=0.5,
                 annotation_text="SELL Threshold")
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.3)
    
    fig.update_layout(
        title="🔗 Hybrid AI Signals Over Time",
        xaxis_title="Time",
        yaxis_title="Hybrid Score (-1.0 to +1.0)",
        height=500,
        template="plotly_white",
        hovermode='x unified'
    )
    
    return fig

def generate_proof_hash(symbol: str, signal: str, timestamp: str, hybrid_score: float) -> str:
    """Generate a proof hash for the signal (placeholder implementation)"""
    data_string = f"{symbol}{signal}{timestamp}{hybrid_score}"
    proof_hash = hashlib.sha256(data_string.encode()).hexdigest()
    return proof_hash

# Sidebar Configuration
st.sidebar.title("🎛️ Dashboard Controls")

selected_symbol = st.sidebar.selectbox(
    "📊 Select Trading Symbol",
    ["BTC-USDT", "ETH-USDT", "SOL-USDT"],
    index=0
)

# Map display symbols to database symbols
symbol_mapping = {
    "BTC-USDT": "BTCUSDT",
    "ETH-USDT": "ETHUSDT",
    "SOL-USDT": "SOLUSDT"
}
db_symbol = symbol_mapping.get(selected_symbol, "BTCUSDT")

# Date range filter
date_range = st.sidebar.selectbox(
    "⏱️ Time Range",
    ["1D", "1W", "1M", "3M"],
    index=2
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Signal Thresholds")
st.sidebar.info("""
**BUY**: hybrid_score > 0.3  
**HOLD**: -0.3 ≤ hybrid_score ≤ 0.3  
**SELL**: hybrid_score < -0.3
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Database Status")
if get_db_connection():
    st.sidebar.success("✅ Connected")
else:
    st.sidebar.error("❌ Disconnected")

# Main Content
st.markdown('<div class="main-header">🧠 AI-Blockchain Hybrid Market Predictor</div>', unsafe_allow_html=True)

# Load latest data for KPIs
hybrid_df = load_data_from_db("hybrid_signals", db_symbol, date_range, limit=1)
market_df = load_data_from_db("market_data", db_symbol, date_range, limit=1)

# Display KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    if not market_df.empty:
        current_price = market_df.iloc[0]['close']
        st.metric("💰 Current Price", f"${current_price:,.2f}")
    else:
        st.metric("💰 Current Price", "N/A")

with col2:
    if not hybrid_df.empty:
        last_signal = hybrid_df.iloc[0]['signal']
        signal_color = get_signal_color(last_signal)
        st.markdown(f'<div style="color: {signal_color}; font-weight: bold; font-size: 1.5rem;">📊 Last Signal: {last_signal}</div>', 
                   unsafe_allow_html=True)
    else:
        st.metric("📊 Last Signal", "HOLD")

with col3:
    if not hybrid_df.empty:
        confidence = hybrid_df.iloc[0]['confidence']
        st.metric("🎯 Confidence Level", f"{confidence*100:.1f}%")
    else:
        st.metric("🎯 Confidence Level", "0%")

with col4:
    if not hybrid_df.empty:
        hybrid_score = hybrid_df.iloc[0]['hybrid_score']
        if hybrid_score > 0.3:
            trend = "📈 Strong Bullish"
        elif hybrid_score > 0:
            trend = "📈 Bullish"
        elif hybrid_score < -0.3:
            trend = "📉 Strong Bearish"
        else:
            trend = "➡️ Neutral"
        st.metric("📊 Sentiment Trend", trend)
    else:
        st.metric("📊 Sentiment Trend", "➡️ Neutral")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Market Overview", 
    "🧠 AI Sentiment", 
    "⚙️ Technical Indicators", 
    "🔗 Hybrid Signals",
    "🔒 Proof-of-Signal"
])

# Tab 1: Market Overview
with tab1:
    st.header("📊 Market Overview")
    
    market_data = load_data_from_db("market_data", db_symbol, date_range, limit=200)
    technical_data = load_data_from_db("technical_indicators", db_symbol, date_range, limit=200)
    
    if not market_data.empty:
        # Sort by timestamp for proper display
        market_data = market_data.sort_values('timestamp')
        if not technical_data.empty:
            technical_data = technical_data.sort_values('timestamp')
        
        fig_candle = plot_candlestick_with_ema(market_data, technical_data)
        st.plotly_chart(fig_candle, use_container_width=True)
        
        # Display latest market data
        with st.expander("📊 Latest Market Data"):
            display_df = market_data.copy()
            display_df = display_df.sort_values('timestamp', ascending=False).head(10)
            st.dataframe(display_df[['timestamp', 'open', 'high', 'low', 'close', 'volume']], 
                        use_container_width=True, hide_index=True)
    else:
        st.info("No market data available for the selected symbol and time range")

# Tab 2: AI Sentiment
with tab2:
    st.header("🧠 AI Sentiment Analysis")
    
    sentiment_data = load_data_from_db("sentiment_results", db_symbol, date_range, limit=200)
    
    if not sentiment_data.empty:
        sentiment_data = sentiment_data.sort_values('timestamp')
        fig_sentiment = plot_sentiment_timeline(sentiment_data)
        st.plotly_chart(fig_sentiment, use_container_width=True)
        
        # Statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_sentiment = sentiment_data['sentiment_score'].mean()
            st.metric("📊 Avg Sentiment", f"{avg_sentiment:.4f}")
        with col2:
            positive_ratio = (sentiment_data['sentiment_score'] > 0.5).sum() / len(sentiment_data) * 100 if len(sentiment_data) > 0 else 0
            st.metric("📈 Positive Ratio", f"{positive_ratio:.1f}%")
        with col3:
            negative_ratio = (sentiment_data['sentiment_score'] < 0.5).sum() / len(sentiment_data) * 100 if len(sentiment_data) > 0 else 0
            st.metric("📉 Negative Ratio", f"{negative_ratio:.1f}%")
        
        # Show latest sentiment results
        with st.expander("📋 Latest Sentiment Results"):
            display_sentiment = sentiment_data.copy()
            display_sentiment = display_sentiment.sort_values('timestamp', ascending=False).head(10)
            st.dataframe(display_sentiment[['timestamp', 'sentiment_score', 'label', 'confidence']], 
                        use_container_width=True, hide_index=True)
    else:
        st.info("No sentiment data available for the selected symbol and time range")

# Tab 3: Technical Indicators
with tab3:
    st.header("⚙️ Technical Indicators")
    
    technical_data = load_data_from_db("technical_indicators", db_symbol, date_range, limit=200)
    
    if not technical_data.empty:
        technical_data = technical_data.sort_values('timestamp')
        fig_technical = plot_technical_indicators(technical_data)
        st.plotly_chart(fig_technical, use_container_width=True)
        
        # Current values
        current_technical = technical_data.iloc[-1] if not technical_data.empty else None
        if current_technical is not None:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                ema20 = current_technical['ema20'] if pd.notna(current_technical.get('ema20')) else 0
                st.metric("📈 EMA 20", f"${ema20:,.2f}" if ema20 > 0 else "N/A")
            with col2:
                ema50 = current_technical['ema50'] if pd.notna(current_technical.get('ema50')) else 0
                st.metric("📈 EMA 50", f"${ema50:,.2f}" if ema50 > 0 else "N/A")
            with col3:
                rsi = current_technical['rsi'] if pd.notna(current_technical.get('rsi')) else 0
                st.metric("📊 RSI", f"{rsi:.2f}" if rsi > 0 else "N/A")
            with col4:
                tech_score = current_technical['technical_score'] if pd.notna(current_technical.get('technical_score')) else 0
                st.metric("⚙️ Technical Score", f"{tech_score:.4f}" if tech_score > 0 else "N/A")
        
        # Show latest technical data
        with st.expander("📋 Latest Technical Indicators"):
            display_technical = technical_data.copy()
            display_technical = display_technical.sort_values('timestamp', ascending=False).head(10)
            st.dataframe(display_technical, use_container_width=True, hide_index=True)
    else:
        st.info("No technical data available for the selected symbol and time range")

# Tab 4: Hybrid Signals
with tab4:
    st.header("🔗 Hybrid AI Signals")
    
    hybrid_data = load_data_from_db("hybrid_signals", db_symbol, date_range, limit=100)
    
    if not hybrid_data.empty:
        hybrid_data = hybrid_data.sort_values('timestamp')
        
        # Plot hybrid scores
        fig_hybrid = plot_hybrid_signals(hybrid_data)
        st.plotly_chart(fig_hybrid, use_container_width=True)
        
        # Signals table
        st.subheader("📋 Recent Signals")
        display_cols = ['timestamp', 'signal', 'hybrid_score', 'confidence', 'reason']
        display_df = hybrid_data.copy()
        display_df = display_df.sort_values('timestamp', ascending=False)
        
        # Filter columns
        display_df = display_df[display_cols].head(15)
        
        # Format display
        display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_df.columns = ['Timestamp', 'Signal', 'Hybrid Score', 'Confidence', 'Reasoning']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Statistics
        st.subheader("📊 Signal Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Signals", len(hybrid_data))
        with col2:
            buy_count = (hybrid_data['signal'] == 'BUY').sum()
            st.metric("🟢 BUY Signals", buy_count)
        with col3:
            sell_count = (hybrid_data['signal'] == 'SELL').sum()
            st.metric("🔴 SELL Signals", sell_count)
        with col4:
            hold_count = (hybrid_data['signal'] == 'HOLD').sum()
            st.metric("⚪ HOLD Signals", hold_count)
        
        # Explainability panel
        if not hybrid_data.empty:
            latest_signal = hybrid_data.iloc[-1]
            with st.expander("🔍 Signal Explainability"):
                st.markdown(f"**Current Signal:** {latest_signal['signal']}")
                st.markdown(f"**Hybrid Score:** {latest_signal['hybrid_score']:.4f}")
                st.markdown(f"**Confidence:** {latest_signal['confidence']:.4f} ({latest_signal['confidence']*100:.1f}%)")
                st.markdown(f"**Reasoning:**")
                st.info(latest_signal.get('reason', 'No reasoning provided'))
    else:
        st.info("No hybrid signals available for the selected symbol and time range")

# Tab 5: Proof-of-Signal
with tab5:
    st.header("🔒 Proof-of-Signal (Solana Blockchain Verification)")
    
    st.markdown("""
    ### What is Proof-of-Signal?
    **Proof-of-Signal** is our innovative blockchain-based verification system that publishes AI trading signals to the Solana blockchain. 
    Each signal is cryptographically hashed and stored on-chain, creating an immutable, timestamped record of AI predictions.
    
    This provides:
    - ✅ **Transparency**: Anyone can verify the authenticity of signals
    - ✅ **Immutable History**: Tamper-proof record of all predictions  
    - ✅ **Accountability**: Permanent on-chain proof of AI performance
    - ✅ **Auditability**: Independent verification of trading signals
    """)
    
    # Load recent signals with proof hashes
    signals_with_proof = load_data_from_db("hybrid_signals", db_symbol, date_range, limit=50)
    
    if not signals_with_proof.empty:
        st.subheader("📋 Recent Signals with Proof Hashes")
        
        # Generate proof hashes for signals that don't have them
        if 'proof_hash' not in signals_with_proof.columns or signals_with_proof['proof_hash'].isna().all():
            st.info("🔧 Generating proof hashes for signals...")
            proof_hashes = []
            for idx, row in signals_with_proof.iterrows():
                timestamp_str = row['timestamp'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(row['timestamp']) else str(row['timestamp'])
                proof_hash = generate_proof_hash(row['symbol'], row['signal'], timestamp_str, float(row['hybrid_score']))
                proof_hashes.append(proof_hash)
            signals_with_proof['proof_hash'] = proof_hashes
        else:
            proof_hashes = signals_with_proof['proof_hash'].tolist()
        
        # Display table
        display_proof = signals_with_proof.copy()
        display_proof = display_proof.sort_values('timestamp', ascending=False).head(20)
        
        # Format for display
        display_proof['timestamp'] = pd.to_datetime(display_proof['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        display_proof['proof_hash_display'] = display_proof['proof_hash'].apply(
            lambda x: x[:8] + '...' + x[-8:] if len(str(x)) > 16 else str(x) if pd.notna(x) else 'N/A'
        )
        
        # Create display dataframe
        proof_display_df = pd.DataFrame({
            'Timestamp': display_proof['timestamp'],
            'Signal': display_proof['signal'],
            'Hybrid Score': display_proof['hybrid_score'],
            'Confidence': (display_proof['confidence'] * 100).round(1).astype(str) + '%',
            'Proof Hash': display_proof['proof_hash_display']
        })
        
        st.dataframe(proof_display_df, use_container_width=True, hide_index=True)
        
        # Show full hash for selected signal
        st.subheader("🔍 View Full Proof Hash")
        if len(signals_with_proof) > 0:
            signal_options = [f"{idx}: {row['signal']} @ {row['timestamp']}" 
                             for idx, row in signals_with_proof.iterrows()]
            selected = st.selectbox("Select a signal to view full hash", range(len(signals_with_proof)), 
                                   format_func=lambda x: f"{signals_with_proof.iloc[x]['signal']} @ {signals_with_proof.iloc[x]['timestamp']}")
            
            selected_row = signals_with_proof.iloc[selected]
            full_hash = selected_row['proof_hash']
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.code(full_hash, language=None)
            with col2:
                # Placeholder Solscan link
                solscan_link = f"https://solscan.io/tx/PLACEHOLDER_{full_hash[:8]}"
                st.markdown(f"[🔗 View on Solscan]({solscan_link})")
        
        # Publish button (placeholder)
        st.divider()
        st.subheader("🚀 Publish Latest Signal to Solana")
        
        if st.button("⛓️ Publish Latest Signal to Solana", type="primary"):
            if not signals_with_proof.empty:
                latest = signals_with_proof.iloc[-1]
                proof_hash = latest.get('proof_hash', generate_proof_hash(
                    str(latest['symbol']), 
                    str(latest['signal']), 
                    latest['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                    float(latest['hybrid_score'])
                ))
                
                st.success(f"""
                ✅ **Signal Published!**
                
                - **Symbol:** {latest['symbol']}
                - **Signal:** {latest['signal']}
                - **Proof Hash:** `{proof_hash}`
                
                🔗 **Transaction Link:** [View on Solscan](https://solscan.io/tx/PLACEHOLDER_{proof_hash[:8]})
                """)
                
                st.info("💡 **Note:** This is a placeholder implementation. Full Solana integration coming soon!")
            else:
                st.error("No signals available to publish")
    else:
        st.info("No signals available for the selected symbol and time range")
    
    # Additional info
    with st.expander("📖 How Proof-of-Signal Works"):
        st.markdown("""
        ### Technical Implementation
        
        1. **Hash Generation**: Each AI signal is cryptographically hashed using SHA-256
        2. **On-Chain Storage**: Hash is stored on Solana blockchain as a transaction
        3. **Verification**: Anyone can verify a signal by:
           - Retrieving the hash from Solana
           - Recomputing the hash from the signal data
           - Comparing the two hashes
        
        ### Security Benefits
        
        - **Tamper-Proof**: Cryptographic hashing ensures data integrity
        - **Public Verification**: Transparent, publicly auditable records
        - **Timestamped**: Blockchain provides proof of when prediction was made
        - **Immutable**: Cannot be altered after being written to blockchain
        
        ### Future Enhancements
        
        - Real Solana transaction integration
        - IPFS storage for full signal metadata
        - Smart contract verification
        - Multi-signature wallets
        - Gasless transactions via sponsored accounts
        """)

# Footer
st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>🧠 AI-Blockchain Hybrid Market Prediction System</strong></p>
    <p>Powered by FinBERT + Technical Analysis + Hybrid AI Decision Engine + Solana Blockchain</p>
    <p style="font-size: 0.8rem;">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p style="font-size: 0.7rem;">⚡ Auto-refresh every 60 seconds</p>
</div>
""", unsafe_allow_html=True)
