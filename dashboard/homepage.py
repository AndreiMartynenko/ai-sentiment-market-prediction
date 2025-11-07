"""
ProofOfSignal - Modern Dashboard
Beautiful, modern UI for AI trading signals with blockchain verification
"""

import streamlit as st
import streamlit.components.v1 as components
import requests
import os
from datetime import datetime
from typing import Optional, Dict

# Page configuration
st.set_page_config(
    page_title="ProofOfSignal - AI Trading Signals",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000")

# Crypto logo mapping
CRYPTO_LOGOS = {
    "BTCUSDT": "₿", "BTC-USD": "₿",
    "ETHUSDT": "Ξ", "ETH-USD": "Ξ",
    "SOLUSDT": "◎", "SOL-USD": "◎",
    "ADAUSDT": "₳", "XRPUSDT": "✕",
    "DOTUSDT": "●", "LINKUSDT": "⬡",
    "BNBUSDT": "🔶", "MATICUSDT": "🟣",
}

def get_crypto_logo(symbol: str) -> str:
    """Get crypto logo/emoji for symbol"""
    if symbol in CRYPTO_LOGOS:
        return CRYPTO_LOGOS[symbol]
    base_symbol = symbol.replace("USDT", "").replace("-USD", "")
    for key in CRYPTO_LOGOS:
        if base_symbol in key:
            return CRYPTO_LOGOS[key]
    return "💎"

def convert_to_tradingview_symbol(symbol: str) -> str:
    """Convert symbol to TradingView format (BINANCE:BTCUSDT)"""
    # Remove common suffixes/prefixes
    symbol = symbol.upper().strip()
    
    # If already in TradingView format, return as is
    if ":" in symbol:
        return symbol
    
    # Convert to TradingView format (BINANCE:SYMBOL)
    if symbol.endswith("USDT"):
        return f"BINANCE:{symbol}"
    elif "-" in symbol:
        # Convert BTC-USD to BINANCE:BTCUSDT
        base = symbol.split("-")[0]
        return f"BINANCE:{base}USDT"
    else:
        # Assume it's a base symbol, add USDT
        return f"BINANCE:{symbol}USDT"

# Modern CSS with glass morphism, gradients, and animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Modern Header */
    .header-modern {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 1.5rem 3rem;
        margin: -2rem -1rem 3rem -1rem;
        border-radius: 0 0 30px 30px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .header-modern::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grid" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M 100 0 L 0 0 0 100" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        z-index: 1;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-icon {
        font-size: 2.5rem;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
        animation: float 3s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .logo-text {
        font-size: 2rem;
        font-weight: 800;
        color: white;
        margin: 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
        letter-spacing: -0.5px;
    }
    
    .nav-modern {
        display: flex;
        gap: 2.5rem;
        align-items: center;
    }
    
    .nav-link-modern {
        color: white;
        text-decoration: none;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
    }
    
    .nav-link-modern:hover {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        transform: translateY(-2px);
    }
    
    .auth-modern {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .btn-primary-modern {
        padding: 0.7rem 1.8rem;
        border-radius: 12px;
        border: 2px solid white;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        color: white;
        font-weight: 600;
        cursor: pointer;
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: inline-block;
    }
    
    .btn-primary-modern:hover {
        background: white;
        color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }
    
    /* Hero Section */
    .hero-modern {
        text-align: center;
        padding: 4rem 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 30px;
        margin-bottom: 3rem;
        position: relative;
        overflow: hidden;
    }
    
    .hero-modern::before {
        content: '';
        position: absolute;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
        top: -200px;
        right: -200px;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        line-height: 1.2;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #64748b;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    /* Input Modern */
    .stTextInput > div > div > input {
        border-radius: 15px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.8rem 1.2rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Button Modern */
    .stButton > button {
        border-radius: 15px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Signal Card Modern */
    .signal-card-modern {
        background: white;
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(226, 232, 240, 0.8);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .signal-card-modern::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 6px;
        height: 100%;
        transition: width 0.3s ease;
    }
    
    .signal-card-modern:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .signal-card-modern:hover::before {
        width: 100%;
        opacity: 0.05;
    }
    
    .signal-buy-modern::before {
        background: linear-gradient(180deg, #10b981 0%, #059669 100%);
    }
    
    .signal-sell-modern::before {
        background: linear-gradient(180deg, #ef4444 0%, #dc2626 100%);
    }
    
    .signal-hold-modern::before {
        background: linear-gradient(180deg, #f59e0b 0%, #d97706 100%);
    }
    
    .signal-header-modern {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    .signal-logo-modern {
        font-size: 3.5rem;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .signal-info-modern h3 {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0 0 0.5rem 0;
    }
    
    .signal-info-modern p {
        color: #64748b;
        font-size: 0.95rem;
        margin: 0;
        font-weight: 500;
    }
    
    .badge-modern {
        display: inline-flex;
        align-items: center;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .badge-buy-modern {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .badge-sell-modern {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        color: white;
    }
    
    .badge-hold-modern {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .accuracy-badge-modern {
        display: inline-flex;
        align-items: center;
        padding: 0.6rem 1.2rem;
        border-radius: 12px;
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 700;
        font-size: 0.9rem;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .solana-link-modern {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: #14f195;
        text-decoration: none;
        font-weight: 600;
        padding: 0.8rem 1.5rem;
        background: rgba(20, 241, 149, 0.1);
        border-radius: 12px;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    
    .solana-link-modern:hover {
        background: rgba(20, 241, 149, 0.2);
        transform: translateX(5px);
    }
    
    .proof-hash-modern {
        margin-top: 1rem;
        padding: 1rem;
        background: #f8fafc;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        font-family: 'Monaco', 'Courier New', monospace;
        font-size: 0.85rem;
        color: #475569;
        word-break: break-all;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1.5rem;
        margin-bottom: 3rem;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stat-label {
        color: #64748b;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    
    /* Loading animation */
    .spinner {
        border: 3px solid #f3f4f6;
        border-top: 3px solid #667eea;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    /* TradingView Widget Container */
    .tradingview-widget-container {
        border-radius: 24px;
        overflow: hidden;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
        margin: 2rem 0;
        background: white;
        border: 1px solid rgba(226, 232, 240, 0.8);
    }
    
    .tradingview-widget-container__widget {
        border-radius: 24px;
    }
    
    .chart-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-bottom: 2px solid #e2e8f0;
    }
    
    .chart-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .chart-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 500;
    }
    
    /* Streamlit components container */
    iframe {
        border-radius: 24px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12) !important;
    }
    </style>
""", unsafe_allow_html=True)

def render_modern_header():
    """Render modern header with glassmorphism"""
    st.markdown("""
        <div class="header-modern">
            <div class="header-content">
                <div class="logo-section">
                    <span class="logo-icon">🔐</span>
                    <h1 class="logo-text">ProofOfSignal</h1>
                </div>
                <nav class="nav-modern">
                    <a href="#" class="nav-link-modern">Home</a>
                    <a href="#about" class="nav-link-modern">About</a>
                    <a href="#prices" class="nav-link-modern">Prices</a>
                    <a href="#contact" class="nav-link-modern">Contact</a>
                </nav>
                <div class="auth-modern">
                    <a href="#login" class="btn-primary-modern">Log In</a>
                    <a href="#signup" class="btn-primary-modern">Sign Up</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_hero_section():
    """Render modern hero section"""
    st.markdown("""
        <div class="hero-modern">
            <h1 class="hero-title">AI-Powered Trading Signals</h1>
            <p class="hero-subtitle">Blockchain-verified cryptocurrency trading signals powered by advanced AI</p>
        </div>
    """, unsafe_allow_html=True)

def generate_signal(symbol: str):
    """Generate a signal on demand"""
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/hybrid",
            json={"symbol": symbol},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error generating signal: {e}")
        return None

def render_signal_card(signal_data: Dict, symbol: str):
    """Render modern signal card"""
    signal_type = signal_data.get('signal', 'HOLD')
    confidence = signal_data.get('confidence', 0.0)
    if confidence and confidence <= 1.0:
        confidence = confidence * 100
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    tx_signature = signal_data.get('tx_signature')
    proof_hash = signal_data.get('proof_hash')
    logo = get_crypto_logo(symbol.upper())
    
    signal_class = f"signal-{signal_type.lower()}-modern"
    badge_class = f"badge-{signal_type.lower()}-modern"
    
    solana_url = f"https://explorer.solana.com/tx/{tx_signature}?cluster=testnet" if tx_signature else None
    
    solana_html = f'''
        <a href="{solana_url}" target="_blank" class="solana-link-modern">
            <span>🔗</span>
            <span>View on Solana Explorer</span>
        </a>
    ''' if solana_url else '<span style="color: #94a3b8; padding: 0.8rem 1.5rem; background: #f8fafc; border-radius: 12px; display: inline-block; margin-top: 1rem;">⛓️ Not published to blockchain</span>'
    
    proof_html = f'''
        <div class="proof-hash-modern">
            <strong>Proof Hash:</strong> {proof_hash[:32]}...
        </div>
    ''' if proof_hash else ''
    
    st.markdown(f"""
        <div class="signal-card-modern {signal_class}">
            <div class="signal-header-modern">
                <div style="display: flex; align-items: center; gap: 1.5rem;">
                    <span class="signal-logo-modern">{logo}</span>
                    <div class="signal-info-modern">
                        <h3>{symbol.upper()}</h3>
                        <p>{timestamp}</p>
                    </div>
                </div>
                <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                    <span class="badge-modern {badge_class}">{signal_type}</span>
                    <span class="accuracy-badge-modern">{confidence:.1f}% Accuracy</span>
                </div>
            </div>
            <div>
                {solana_html}
                {proof_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_tradingview_chart(symbol: str):
    """Render TradingView chart widget"""
    tv_symbol = convert_to_tradingview_symbol(symbol)
    logo = get_crypto_logo(symbol)
    chart_id = f"tradingview_{symbol.replace('-', '_').replace(':', '_').replace('/', '_')}"
    
    # Chart header
    st.markdown(f"""
        <div class="chart-header">
            <div>
                <div class="chart-title">
                    <span>{logo}</span>
                    <span>{symbol.upper()}</span>
                </div>
                <div class="chart-subtitle">Live Price Chart - TradingView</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # TradingView widget HTML with script
    tradingview_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
            #{chart_id} {{
                height: 600px;
                width: 100%;
            }}
        </style>
    </head>
    <body>
        <div class="tradingview-widget-container">
            <div id="{chart_id}"></div>
            <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
            <script type="text/javascript">
                new TradingView.widget({{
                    "autosize": true,
                    "symbol": "{tv_symbol}",
                    "interval": "D",
                    "timezone": "Etc/UTC",
                    "theme": "light",
                    "style": "1",
                    "locale": "en",
                    "toolbar_bg": "#f1f3f6",
                    "enable_publishing": false,
                    "allow_symbol_change": true,
                    "container_id": "{chart_id}",
                    "hide_side_toolbar": false,
                    "details": true,
                    "studies": [
                        "Volume@tv-basicstudies",
                        "RSI@tv-basicstudies"
                    ],
                    "show_popup_button": true,
                    "popup_width": "1000",
                    "popup_height": "650"
                }});
            </script>
        </div>
    </body>
    </html>
    """
    
    # Render using components.html for proper JavaScript execution
    components.html(tradingview_html, height=620, scrolling=False)

def main():
    """Main homepage application"""
    render_modern_header()
    render_hero_section()
    
    # Input section
    col1, col2, col3 = st.columns([2, 1, 0.5])
    with col1:
        symbol = st.text_input(
            "Enter Cryptocurrency Symbol",
            value="BTCUSDT",
            placeholder="BTCUSDT, ETHUSDT, SOLUSDT...",
            label_visibility="collapsed"
        )
    with col2:
        st.write("")  # Spacing
        generate_btn = st.button("🚀 Generate Signal", type="primary", use_container_width=True)
    with col3:
        st.write("")  # Spacing
    
    # TradingView Chart Section
    if symbol:
        st.markdown("### 📈 Live Market Chart")
        render_tradingview_chart(symbol)
        st.markdown("---")
    
    # Generate signal
    if generate_btn and symbol:
        with st.spinner(""):
            st.markdown("""
                <div style="text-align: center; padding: 2rem;">
                    <div class="spinner"></div>
                    <p style="margin-top: 1rem; color: #64748b; font-weight: 500;">Analyzing market data...</p>
                </div>
            """, unsafe_allow_html=True)
            
            signal_data = generate_signal(symbol.upper())
            
            if signal_data:
                st.empty()  # Clear spinner
                render_signal_card(signal_data, symbol.upper())
            else:
                st.error("❌ Failed to generate signal. Make sure the ML service is running.")
    
    # Stats section (if signals exist)
    st.markdown("---")
    
    # Service status
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        try:
            response = requests.get(f"{ML_SERVICE_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ ML Service: Online")
            else:
                st.warning("⚠️ ML Service: Error")
        except:
            st.error(f"❌ ML Service: Offline")
    
    with col2:
        st.info("💡 Tip: Use the chart above to analyze price action, then generate AI signals below")

if __name__ == "__main__":
    main()
