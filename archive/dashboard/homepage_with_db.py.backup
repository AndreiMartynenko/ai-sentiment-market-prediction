"""
ProofOfSignal - Homepage Dashboard
Main landing page displaying list of generated trading signals with Solana blockchain verification
"""

import streamlit as st
import requests
import os
from datetime import datetime
from typing import Optional, Dict, List

# Page configuration
st.set_page_config(
    page_title="ProofOfSignal - AI Trading Signals",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Configuration
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000")

# Crypto logo mapping (using emoji for now, can be replaced with image URLs)
CRYPTO_LOGOS = {
    "BTCUSDT": "₿",
    "BTC-USD": "₿",
    "ETHUSDT": "Ξ",
    "ETH-USD": "Ξ",
    "SOLUSDT": "◎",
    "SOL-USD": "◎",
    "ADAUSDT": "₳",
    "ADA-USD": "₳",
    "XRPUSDT": "✕",
    "XRP-USD": "✕",
    "DOTUSDT": "●",
    "DOT-USD": "●",
    "LINKUSDT": "⬡",
    "LINK-USD": "⬡",
}

def get_crypto_logo(symbol: str) -> str:
    """Get crypto logo/emoji for symbol"""
    # Try exact match first
    if symbol in CRYPTO_LOGOS:
        return CRYPTO_LOGOS[symbol]
    # Try without USDT suffix
    base_symbol = symbol.replace("USDT", "").replace("-USD", "")
    for key in CRYPTO_LOGOS:
        if base_symbol in key:
            return CRYPTO_LOGOS[key]
    return "💎"  # Default logo

# Custom CSS for header and styling
st.markdown("""
    <style>
    /* Hide default Streamlit header */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Header Styling */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        margin-bottom: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-text {
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
        margin: 0;
    }
    
    .nav-section {
        display: flex;
        gap: 2rem;
        align-items: center;
    }
    
    .nav-link {
        color: white;
        text-decoration: none;
        font-weight: 500;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: background 0.3s;
    }
    
    .nav-link:hover {
        background: rgba(255, 255, 255, 0.2);
    }
    
    .auth-section {
        display: flex;
        gap: 1rem;
        align-items: center;
    }
    
    .auth-button {
        padding: 0.5rem 1.5rem;
        border-radius: 5px;
        border: 2px solid white;
        background: transparent;
        color: white;
        font-weight: 500;
        cursor: pointer;
        text-decoration: none;
    }
    
    .auth-button:hover {
        background: white;
        color: #667eea;
    }
    
    /* Signal Card Styling */
    .signal-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .signal-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .signal-buy {
        border-left-color: #28a745;
    }
    
    .signal-sell {
        border-left-color: #dc3545;
    }
    
    .signal-hold {
        border-left-color: #ffc107;
    }
    
    .signal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .signal-logo {
        font-size: 2.5rem;
        margin-right: 1rem;
    }
    
    .signal-info {
        flex: 1;
    }
    
    .signal-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
    }
    
    .badge-buy {
        background: #d4edda;
        color: #155724;
    }
    
    .badge-sell {
        background: #f8d7da;
        color: #721c24;
    }
    
    .badge-hold {
        background: #fff3cd;
        color: #856404;
    }
    
    .solana-link {
        color: #14f195;
        text-decoration: none;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .solana-link:hover {
        text-decoration: underline;
    }
    
    .accuracy-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        background: #e7f3ff;
        color: #004085;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

def render_header():
    """Render the header with navigation"""
    st.markdown("""
        <div class="header-container">
            <div class="header-content">
                <div class="logo-section">
                    <h1 class="logo-text">🔐 ProofOfSignal</h1>
                </div>
                <div class="nav-section">
                    <a href="#" class="nav-link">Home</a>
                    <a href="#about" class="nav-link">About</a>
                    <a href="#prices" class="nav-link">Prices</a>
                    <a href="#contact" class="nav-link">Contact Us</a>
                </div>
                <div class="auth-section">
                    <a href="#login" class="auth-button">Log In</a>
                    <a href="#signup" class="auth-button">Sign Up</a>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def get_signals_list(limit: int = 50) -> Optional[Dict]:
    """Fetch signals list from ML service"""
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/signals/list",
            params={"limit": limit, "offset": 0},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching signals: {e}")
        return None

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        return timestamp_str

def get_solana_explorer_url(tx_signature: Optional[str]) -> Optional[str]:
    """Get Solana explorer URL for transaction"""
    if not tx_signature:
        return None
    return f"https://explorer.solana.com/tx/{tx_signature}?cluster=testnet"

def render_signal_card(signal: Dict):
    """Render a single signal card"""
    symbol = signal.get('symbol', 'UNKNOWN')
    signal_type = signal.get('signal', 'HOLD')
    confidence = signal.get('confidence', 0.0)
    if confidence and confidence <= 1.0:
        confidence = confidence * 100  # Convert to percentage if in 0-1 range
    timestamp = signal.get('timestamp') or signal.get('created_at', '')
    tx_signature = signal.get('tx_signature')
    proof_hash = signal.get('proof_hash')
    
    # Determine signal class
    signal_class = f"signal-{signal_type.lower()}"
    badge_class = f"badge-{signal_type.lower()}"
    
    # Get logo
    logo = get_crypto_logo(symbol)
    
    # Format timestamp
    time_display = format_timestamp(timestamp) if timestamp else "N/A"
    
    # Solana link
    solana_url = get_solana_explorer_url(tx_signature)
    
    # Build proof hash display
    proof_display = ""
    if proof_hash:
        hash_display = proof_hash[:16] + "..." if len(proof_hash) > 16 else proof_hash
        proof_display = f'<p style="margin-top: 0.5rem; color: #666; font-size: 0.85rem;">Proof Hash: <code style="background: #f5f5f5; padding: 0.2rem 0.4rem; border-radius: 3px;">{hash_display}</code></p>'
    
    st.markdown(f"""
        <div class="signal-card {signal_class}">
            <div class="signal-header">
                <div style="display: flex; align-items: center;">
                    <span class="signal-logo">{logo}</span>
                    <div class="signal-info">
                        <h3 style="margin: 0; font-size: 1.3rem;">{symbol}</h3>
                        <p style="margin: 0.25rem 0; color: #666; font-size: 0.9rem;">{time_display}</p>
                    </div>
                </div>
                <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
                    <span class="signal-badge {badge_class}">{signal_type}</span>
                    <span class="accuracy-badge">{confidence:.1f}% Accuracy</span>
                </div>
            </div>
            <div style="margin-top: 1rem;">
                {f'<a href="{solana_url}" target="_blank" class="solana-link">🔗 View on Solana Explorer</a>' if solana_url else '<span style="color: #999;">⛓️ Not published to blockchain</span>'}
                {proof_display}
            </div>
        </div>
    """, unsafe_allow_html=True)

def main():
    """Main homepage application"""
    # Render header
    render_header()
    
    # Page title
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h2 style="font-size: 2rem; color: #333; margin-bottom: 0.5rem;">AI Trading Signals</h2>
            <p style="color: #666; font-size: 1.1rem;">Verified on Solana Blockchain</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Refresh Signals", type="primary", use_container_width=True):
            st.rerun()
    
    # Fetch signals
    with st.spinner("Loading signals..."):
        signals_data = get_signals_list(limit=50)
    
    if signals_data and signals_data.get('success'):
        signals = signals_data.get('signals', [])
        
        if signals:
            st.markdown(f"### 📊 Found {len(signals)} Signals")
            st.markdown("---")
            
            # Display signals
            for signal in signals:
                render_signal_card(signal)
        else:
            st.info("""
                ### No signals found
                
                No trading signals have been generated yet. 
                
                To generate signals:
                1. Use the ML service API endpoint: `POST /hybrid`
                2. Or use the dashboard to analyze a cryptocurrency
            """)
    else:
        st.error("""
            ### Error loading signals
            
            Could not connect to the ML service. Please ensure:
            - The ML service is running on `{}`
            - The database is properly configured
            - There are signals in the database
        """.format(ML_SERVICE_URL))
        
        # Show connection status
        try:
            response = requests.get(f"{ML_SERVICE_URL}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ ML Service is running")
            else:
                st.warning("⚠️ ML Service returned an error")
        except:
            st.error("❌ Cannot reach ML Service")

if __name__ == "__main__":
    main()

