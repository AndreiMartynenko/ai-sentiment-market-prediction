"""
ProofOfSignal - Modern Neon Dashboard with TradingView Charts and Crypto News Sentiment
"""
from datetime import datetime
from typing import Dict, List, Optional
import requests
import streamlit as st
import os
import streamlit.components.v1 as components
# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="ProofOfSignal - AI Trading Signals",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed",
)
try:
    _secret_ml_service_url = st.secrets["ML_SERVICE_URL"]
except Exception:
    _secret_ml_service_url = None
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", _secret_ml_service_url or "http://localhost:8000")
NEWS_DEFAULT_SYMBOLS = [
    "BTC",
    "ETH",
    "SOL",
    "BNB",
    "ADA",
    "XRP",
    "DOGE",
    "AVAX",
    "DOT",
    "MATIC",
    "TON",
    "FET",
    "RNDR",
    "NEAR",
    "UNI",
    "AAVE",
    "COMP",
    "ARB",
    "OP",
    "USDT",
    "USDC",
]
CRYPTO_LOGOS = {
    "BTC": "₿",
    "ETH": "Ξ",
    "SOL": "◎",
    "BNB": "🟡",
    "ADA": "₳",
    "XRP": "✕",
    "DOGE": "🐕",
    "AVAX": "🅐",
    "DOT": "●",
    "MATIC": "🟣",
    "TON": "⚡",
    "FET": "🤖",
    "RNDR": "🎨",
    "NEAR": "ⓝ",
    "UNI": "🦄",
    "AAVE": "🏦",
    "COMP": "📈",
    "ARB": "🧠",
    "OP": "🟥",
    "USDT": "🟢",
    "USDC": "🔵",
}
# ------------------------------------------------------------------------------
# Styling (Dark + Neon Accents)
# ------------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    html, body {
        background: radial-gradient(circle at 18% -12%, rgba(34, 211, 238, 0.35), transparent 58%),
                    radial-gradient(circle at 85% -10%, rgba(236, 72, 153, 0.3), transparent 60%),
                    linear-gradient(135deg, #040819 0%, #020614 35%, #01040e 65%, #000208 100%) !important;
        color: #e2e8f0 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    .stApp {
        background: transparent;
    }
    .main .block-container {
        padding: 2.4rem 2.6rem;
        max-width: 1400px;
        background: rgba(8, 12, 26, 0.55);
        border: 1px solid rgba(59, 130, 246, 0.14);
        border-radius: 34px;
        box-shadow: 0 60px 120px rgba(1, 4, 12, 0.75);
        backdrop-filter: blur(20px);
    }
    .neon-glass {
        backdrop-filter: blur(16px);
        background: linear-gradient(135deg, rgba(30, 58, 138, 0.45), rgba(91, 33, 182, 0.35));
        border: 1px solid rgba(46, 58, 89, 0.6);
        box-shadow: 0 20px 45px rgba(23, 23, 43, 0.45);
        border-radius: 24px;
    }
    /* Header */
    .header-modern {
        position: relative;
        margin: -2rem -1rem 2.5rem -1rem;
        padding: 2.4rem 3rem;
        border-radius: 32px;
        overflow: hidden;
        background: radial-gradient(circle at 15% -20%, rgba(56, 189, 248, 0.35), transparent 55%),
                    radial-gradient(circle at 85% 0%, rgba(236, 72, 153, 0.32), transparent 50%),
                    linear-gradient(135deg, rgba(10, 12, 29, 0.95), rgba(15, 23, 42, 0.92) 55%, rgba(17, 24, 39, 0.88));
        border: 1px solid rgba(59, 130, 246, 0.35);
        box-shadow: 0 45px 90px rgba(4, 7, 15, 0.7);
    }

    .header-modern::before {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(99, 102, 241, 0.05));
        mix-blend-mode: screen;
        opacity: 0.6;
    }

    .header-orb {
        position: absolute;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.55;
    }

    .header-orb.orb-left {
        width: 320px;
        height: 320px;
        top: -140px;
        left: -110px;
        background: radial-gradient(circle, rgba(34, 211, 238, 0.75), transparent 60%);
    }

    .header-orb.orb-right {
        width: 280px;
        height: 280px;
        top: -160px;
        right: -90px;
        background: radial-gradient(circle, rgba(236, 72, 153, 0.65), transparent 60%);
    }

    .header-top {
        position: relative;
        z-index: 2;
        display: grid;
        grid-template-columns: auto 1fr auto;
        align-items: center;
        gap: 2rem;
    }

    .brand-block {
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    .brand-icon {
        font-size: 2.8rem;
        filter: drop-shadow(0 15px 35px rgba(34, 211, 238, 0.55));
    }

    .brand-block h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        color: #f8fafc;
    }

    .brand-block p {
        margin: 0.25rem 0 0 0;
        color: #cbd5f5;
        font-weight: 500;
    }

    .header-nav {
        display: flex;
        justify-content: center;
        gap: 1.6rem;
        flex-wrap: wrap;
    }

    .header-nav a {
        position: relative;
        padding: 0.55rem 1.2rem;
        border-radius: 999px;
        color: #cbd5f5;
        text-decoration: none;
        font-weight: 600;
        letter-spacing: 0.03em;
        transition: color 0.3s ease, transform 0.3s ease;
    }

    .header-nav a::after {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: inherit;
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.7), rgba(236, 72, 153, 0.7));
        opacity: 0;
        transition: opacity 0.3s ease;
        filter: blur(0.5px);
    }

    .header-nav a span {
        position: relative;
        z-index: 1;
    }

    .header-nav a:hover {
        color: #0f172a;
        transform: translateY(-2px);
    }

    .header-nav a:hover::after {
        opacity: 1;
    }

    .action-block {
        display: flex;
        gap: 0.9rem;
        align-items: center;
        flex-wrap: wrap;
        justify-content: flex-end;
    }

    .action-button {
        position: relative;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.7rem 1.6rem;
        border-radius: 14px;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-decoration: none;
        transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
    }

    .action-button.primary {
        background: linear-gradient(135deg, #22d3ee, #6366f1);
        color: #020617;
        box-shadow: 0 18px 40px rgba(79, 70, 229, 0.45);
    }

    .action-button.ghost {
        border: 1px solid rgba(148, 163, 184, 0.5);
        color: #e0f2fe;
        background: rgba(15, 23, 42, 0.4);
    }

    .action-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 24px 45px rgba(59, 130, 246, 0.35);
    }

    .header-bottom {
        position: relative;
        z-index: 2;
        margin-top: 2.4rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1.2rem;
        flex-wrap: wrap;
    }

    .tagline {
        font-size: 1.1rem;
        color: #dbeafe;
        max-width: 620px;
        line-height: 1.55;
    }

    .metric-row {
        display: flex;
        gap: 0.75rem;
        flex-wrap: wrap;
        justify-content: flex-end;
    }

    .metric-chip {
        padding: 0.45rem 1.1rem;
        border-radius: 999px;
        border: 1px solid rgba(59, 130, 246, 0.4);
        background: rgba(15, 23, 42, 0.6);
        color: #cbd5f5;
        font-weight: 600;
        font-size: 0.8rem;
        letter-spacing: 0.04em;
        box-shadow: 0 12px 30px rgba(15, 23, 42, 0.45);
    }

    .hero-modern {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 64, 175, 0.45));
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 28px;
        padding: 3.5rem 2.5rem;
        text-align: center;
        margin-bottom: 2.5rem;
        box-shadow: 0 30px 60px rgba(2, 6, 23, 0.65);
        position: relative;
        overflow: hidden;
    }
    .hero-modern::after {
        content: '';
        position: absolute;
        inset: -50% -10% auto -10%;
        height: 120%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.35), transparent 60%);
        opacity: 0.6;
    }
    .hero-title {
        font-size: clamp(2.8rem, 4vw, 3.6rem);
        font-weight: 900;
        margin-bottom: 1rem;
        background: linear-gradient(135deg, #22d3ee, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #cbd5f5;
        font-weight: 500;
        max-width: 620px;
        margin: 0 auto;
    }
    /* Inputs / Buttons */
    .stTextInput > div > div > input {
        background: rgba(15, 23, 42, 0.75) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(148, 163, 184, 0.45) !important;
        padding: 0.8rem 1.1rem !important;
        color: #f8fafc !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: rgba(59, 130, 246, 0.85) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.35) !important;
    }
    .stButton > button {
        border-radius: 14px !important;
        padding: 0.85rem 2rem !important;
        font-weight: 600 !important;
        background: linear-gradient(135deg, #22d3ee, #6366f1) !important;
        color: #0f172a !important;
        border: none !important;
        box-shadow: 0 18px 45px rgba(79, 70, 229, 0.45) !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.01) !important;
    }
    /* TradingView container */
    .chart-header {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85), rgba(30, 64, 175, 0.28));
        border: 1px solid rgba(59, 130, 246, 0.35);
        border-radius: 22px 22px 0 0;
        padding: 1.2rem 1.6rem;
        color: #e2e8f0;
        box-shadow: 0 15px 30px rgba(15, 23, 42, 0.5);
    }
    .chart-title {
        font-size: 1.4rem;
        font-weight: 700;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    iframe {
        border-radius: 0 0 22px 22px !important;
        border: 1px solid rgba(59, 130, 246, 0.25) !important;
        box-shadow: 0 30px 60px rgba(15, 23, 42, 0.55) !important;
        background: #020617 !important;
    }
    /* Signal card */
    .signal-card-modern {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(30, 64, 175, 0.35));
        border: 1px solid rgba(79, 70, 229, 0.35);
        color: #f8fafc;
    }
    .badge-modern {
        box-shadow: 0 12px 30px rgba(34, 211, 238, 0.3);
    }
    .accuracy-badge-modern {
        background: linear-gradient(135deg, #22d3ee, #0ea5e9);
        box-shadow: 0 12px 30px rgba(34, 211, 238, 0.4);
    }
    .proof-hash-modern {
        background: rgba(15, 23, 42, 0.75);
        border: 1px dashed rgba(148, 163, 184, 0.3);
        color: #94a3b8;
    }
    /* News section */
    .news-wrapper {
        display: flex;
        flex-direction: column;
        gap: 1.2rem;
        margin-bottom: 2rem;
    }
    details.news-card {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.92), rgba(59, 130, 246, 0.18));
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-left: 4px solid rgba(236, 72, 153, 0.65);
        border-radius: 18px;
        padding: 1rem 1.4rem;
        transition: transform 0.35s ease, box-shadow 0.35s ease;
        color: #e2e8f0;
    }
    details.news-card[open] {
        transform: translateY(-2px);
        box-shadow: 0 28px 55px rgba(15, 23, 42, 0.65);
    }
    details.news-card summary {
        list-style: none;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 700;
        color: #f8fafc;
        font-size: 1.1rem;
    }
    details.news-card summary::-webkit-details-marker {
        display: none;
    }
    .news-summary-left {
        display: flex;
        gap: 0.8rem;
        align-items: center;
    }
    .news-chip {
        background: rgba(59, 130, 246, 0.2);
        color: #93c5fd;
        padding: 0.3rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .news-items {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 1rem;
        margin-top: 1.2rem;
    }
    .news-item {
        background: rgba(15, 23, 42, 0.85);
        border-radius: 16px;
        padding: 1rem 1.1rem;
        border: 1px solid rgba(59, 130, 246, 0.2);
        display: flex;
        flex-direction: column;
        gap: 0.65rem;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .news-item:hover {
        transform: translateY(-4px);
        border-color: rgba(236, 72, 153, 0.45);
    }
    .news-item.empty {
        justify-content: center;
        align-items: center;
        color: #94a3b8;
        font-style: italic;
    }
    .news-headline-text {
        font-weight: 600;
        color: #f8fafc;
    }
    .news-headline a {
        color: #f8fafc;
        font-weight: 600;
        text-decoration: none;
    }
    .news-headline a:hover {
        color: #22d3ee;
    }
    .news-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        font-size: 0.8rem;
        color: #93c5fd;
    }
    .sentiment-tag {
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.75rem;
        letter-spacing: 0.02em;
    }
    .sentiment-positive { background: rgba(34, 197, 94, 0.22); color: #4ade80; }
    .sentiment-negative { background: rgba(248, 113, 113, 0.22); color: #f87171; }
    .sentiment-neutral { background: rgba(148, 163, 184, 0.22); color: #cbd5f5; }
    .spinner {
        border: 3px solid rgba(51, 65, 85, 0.5);
        border-top: 3px solid #22d3ee;
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
    </style>
    """,
    unsafe_allow_html=True,
)
# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_news_data(symbols: List[str], limit: int = 10) -> Optional[Dict]:
    try:
        response = requests.get(
            f"{ML_SERVICE_URL}/news/crypto",
            params={"symbols": ",".join(symbols), "limit": limit},
            timeout=15,
        )
        if response.status_code == 200:
            return response.json()
        st.warning("Unable to fetch news (status code: %s)" % response.status_code)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Error fetching news data: {exc}")
    return None
def get_crypto_logo(symbol: str) -> str:
    return CRYPTO_LOGOS.get(symbol.upper(), "💎")
def convert_to_tradingview_symbol(symbol: str) -> str:
    symbol = symbol.upper().strip()
    if ":" in symbol:
        return symbol
    if symbol.endswith("USDT"):
        return f"BINANCE:{symbol}"
    if "-" in symbol:
        base = symbol.split("-")[0]
        return f"BINANCE:{base}USDT"
    return f"BINANCE:{symbol}USDT"
def format_timestamp(timestamp: Optional[str]) -> str:
    if not timestamp:
        return "Unknown"
    try:
        if timestamp.endswith("Z"):
            dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
        else:
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%d %b %Y • %H:%M UTC")
    except Exception:  # noqa: BLE001
        return timestamp



def get_sentiment_tag(score: float) -> str:
    if score >= 0.2:
        return "positive"
    if score <= -0.2:
        return "negative"
    return "neutral"
def render_news_section(news_response: Optional[Dict]):
    st.markdown("## 📰 Neon Pulse Market Intelligence")
    if not news_response or not news_response.get("success"):
        st.info("Real-time news feed unavailable. Please try again shortly.")
        return
    data = news_response.get("data", [])
    if not data:
        st.info("No headlines available right now.")
        return
    html_parts: List[str] = ['<div class="news-wrapper">']
    for entry in data:
        symbol = entry.get("symbol", "NA").upper()
        items = entry.get("items", []) or []
        logo = get_crypto_logo(symbol)
        headline_count = len(items)
        html_parts.append(
            f"<details class='news-card'><summary>"
            f"<div class='news-summary-left'><span>{logo}</span><span>{symbol}</span></div>"
            f"<span class='news-chip'>{headline_count} Headlines</span>"
            "</summary>"
        )
        if items:
            html_parts.append("<div class='news-items'>")
        else:
            html_parts.append("<div class='news-items'><div class='news-item empty'>No headlines available.</div>")
        for item in items:
            title = item.get("title") or "Untitled"
            url = item.get("url") or ""
            domain = item.get("domain") or ""
            published_at = item.get("published_at")
            source = item.get("source") or domain or "CryptoPanic"
            score = float(item.get("sentiment_score", 0.0))
            label = (item.get("sentiment_label") or "neutral").lower()
            confidence = float(item.get("sentiment_confidence", 0.0))
            confidence_pct = confidence * 100 if confidence <= 1 else confidence
            sentiment_class = get_sentiment_tag(score)
            sentiment_display = f"{score:+.2f} | {label.upper()}"
            timestamp = format_timestamp(published_at)

            if not url and domain:
                url = domain if domain.startswith("http") else f"https://{domain}"

            if url:
                headline_html = f"<a href='{url}' target='_blank' rel='noopener noreferrer'>{title}</a>"
            else:
                headline_html = f"<span class='news-headline-text'>{title}</span>"

            html_parts.append(
                "<div class='news-item'>"
                f"<div class='news-headline'>{headline_html}</div>"
                "<div class='news-meta'>"
                f"<span class='sentiment-tag sentiment-{sentiment_class}'>{sentiment_display}</span>"
                f"<span>{confidence_pct:.0f}%</span>"
                f"<span>{source}</span>"
                f"<span>{timestamp}</span>"
                "</div>"
                "</div>"
            )
        html_parts.append("</div></details>")
    html_parts.append("</div>")
    st.markdown("\n".join(html_parts), unsafe_allow_html=True)
def generate_signal(symbol: str) -> Optional[Dict]:
    try:
        response = requests.post(
            f"{ML_SERVICE_URL}/hybrid",
            json={"symbol": symbol},
            timeout=20,
        )
        if response.status_code == 200:
            return response.json()
        st.error(f"Failed to generate signal (status {response.status_code})")
    except Exception as exc:  # noqa: BLE001
        st.error(f"Error generating signal: {exc}")
    return None
def render_signal_card(signal_data: Dict, symbol: str):
    signal_type = signal_data.get("signal", "HOLD")
    confidence = signal_data.get("confidence", 0.0)
    if confidence <= 1:
        confidence *= 100
    timestamp = datetime.now().strftime("%d %b %Y • %H:%M UTC")
    tx_signature = signal_data.get("tx_signature")
    proof_hash = signal_data.get("proof_hash")
    logo = get_crypto_logo(symbol)
    signal_class = f"signal-{signal_type.lower()}-modern"
    solana_html = (
        f"<a href='https://explorer.solana.com/tx/{tx_signature}?cluster=testnet' target='_blank' class='solana-link-modern'>"
        "<span>🔗</span><span>Solana Explorer</span></a>"
        if tx_signature
        else "<span style='color:#94a3b8;padding:0.8rem 1.5rem;background:#111827;border-radius:12px;display:inline-block;margin-top:1rem;'>⛓️ Not published to blockchain</span>"
    )
    proof_html = (
        f"<div class='proof-hash-modern'><strong>Proof Hash:</strong> {proof_hash[:32]}...</div>"
        if proof_hash
        else ""
    )
    st.markdown(
        f"""
        <div class="signal-card-modern {signal_class}">
            <div class="signal-header-modern">
                <div style="display:flex;align-items:center;gap:1.5rem;">
                    <span class="signal-logo-modern">{logo}</span>
                    <div class="signal-info-modern">
                        <h3>{symbol}</h3>
                        <p>{timestamp}</p>
                    </div>
                </div>
                <div style="display:flex;gap:1rem;align-items:center;flex-wrap:wrap;">
                    <span class="badge-modern badge-{signal_type.lower()}-modern">{signal_type}</span>
                    <span class="accuracy-badge-modern">{confidence:.1f}% Confidence</span>
                </div>
            </div>
            <div>
                {solana_html}
                {proof_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
def render_tradingview_chart(symbol: str):
    tv_symbol = convert_to_tradingview_symbol(symbol)
    logo = get_crypto_logo(symbol)
    chart_id = f"tradingview_{symbol.replace('-', '_').replace(':', '_').replace('/', '_')}"
    st.markdown(
        f"""
        <div class="chart-header">
            <div class="chart-title">
                <span>{logo}</span>
                <span>{symbol.upper()}</span>
            </div>
            <div class="chart-subtitle">Live Price Chart powered by TradingView</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    tradingview_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                background: #020617;
            }}
            #{chart_id} {{
                height: 600px;
                width: 100%;
            }}
        </style>
    </head>
    <body>
        <div class=\"tradingview-widget-container\">
            <div id=\"{chart_id}\"></div>
        </div>
        <script type=\"text/javascript\" src=\"https://s3.tradingview.com/tv.js\"></script>
        <script type=\"text/javascript\">
            new TradingView.widget({{
                "autosize": true,
                "symbol": "{tv_symbol}",
                "interval": "D",
                "timezone": "Etc/UTC",
                "theme": "dark",
                "style": "1",
                "locale": "en",
                "toolbar_bg": "#0f172a",
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
    </body>
    </html>
    """
    components.html(tradingview_html, height=620, scrolling=False)
def render_modern_header():
    st.markdown(
        """
        <div class="header-modern">
            <div class="header-orb orb-left"></div>
            <div class="header-orb orb-right"></div>
            <div class="header-top">
                <div class="brand-block">
                    <div class="brand-icon">🔐</div>
                    <div>
                        <h1>ProofOfSignal</h1>
                        <p>On-chain verified market intelligence for crypto-native teams.</p>
                    </div>
                </div>
                <nav class="header-nav">
                    <a href="#overview"><span>Overview</span></a>
                    <a href="#signals"><span>Signals</span></a>
                    <a href="#news"><span>News</span></a>
                    <a href="#docs"><span>Docs</span></a>
                </nav>
                <div class="action-block">
                    <a class="action-button ghost" href="#docs">Docs</a>
                    <a class="action-button primary" href="#dashboard">Launch Console</a>
                </div>
            </div>
            <div class="header-bottom">
                <div class="tagline">
                    Hybrid AI, sentiment analytics, and on-chain proofs powering next-generation trading experiences.
                </div>
                <div class="metric-row">
                    <div class="metric-chip">⚡ Real-time Signals</div>
                    <div class="metric-chip">🧠 FinBERT Sentiment</div>
                    <div class="metric-chip">⛓️ Proof-of-Signal</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
def render_hero_section():
    st.markdown(
        """
        <div class="hero-modern neon-glass">
            <h1 class="hero-title">Neon-Powered Crypto Intelligence</h1>
            <p class="hero-subtitle">
                Fuse institutional-grade AI signals with live blockchain-verified insights, TradingView charts,
                and real-time sentiment across the top digital assets.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
def check_service_health() -> str:
    try:
        response = requests.get(f"{ML_SERVICE_URL}/health", timeout=5)
        if response.status_code == 200:
            return "online"
        return "degraded"
    except Exception:  # noqa: BLE001
        return "offline"
# ------------------------------------------------------------------------------
# Main App
# ------------------------------------------------------------------------------
def main():
    render_modern_header()
    render_hero_section()
    selected_symbol = st.session_state.get("selected_symbol", "BTCUSDT")
    signal_result: Optional[Dict] = None
    # Fetch news (cached)
    news_response = fetch_news_data(NEWS_DEFAULT_SYMBOLS, limit=10)
    # Layout: Sidebar / TradingView / News
    col_sidebar, col_chart, col_news = st.columns([0.85, 2.2, 1.4], gap="large")
    with col_sidebar:
        st.markdown("### 🎯 Controls")
        symbol = st.text_input(
            "Symbol",
            value=selected_symbol,
            placeholder="BTCUSDT, ETHUSDT, SOLUSDT...",
            help="Enter a Binance-style trading pair",
        )
        generate_btn = st.button("🚀 Generate Signal", use_container_width=True)
        st.markdown("---")
        status = check_service_health()
        if status == "online":
            st.success("ML Service: Online")
        elif status == "degraded":
            st.warning("ML Service: Degraded")
        else:
            st.error("ML Service: Offline")
        st.markdown("---")
        st.markdown("#### 💡 Tips")
        st.write("- Explore top headlines per asset")
        st.write("- Overlay AI signals with live charts")
        st.write("- Blockchain proofs ensure authenticity")
    if generate_btn and symbol:
        with st.spinner("Synthesizing AI signal..."):
            signal_result = generate_signal(symbol.upper())
        if signal_result:
            st.session_state["selected_symbol"] = symbol.upper()
            selected_symbol = symbol.upper()
    with col_chart:
        st.markdown("### 📈 TradingView")
        render_tradingview_chart(selected_symbol)
        st.markdown("---")
        st.markdown("### 🤖 Hybrid Signal")
        if signal_result:
            render_signal_card(signal_result, selected_symbol)
        else:
            st.info("Generate a signal to view AI insights alongside the chart.")
    with col_news:
        render_news_section(news_response)
if __name__ == "__main__":
    main()