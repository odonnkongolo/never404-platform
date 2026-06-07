import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Volatility Engine | Odon Nkongolo",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Global Page CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #0B0F1A !important;
}

/* Remove Streamlit chrome */
header[data-testid="stHeader"]  { display: none !important; }
footer                           { display: none !important; }
#MainMenu                        { display: none !important; }

.block-container {
    padding: 2rem 2.5rem 2rem 2.5rem !important;
    max-width: 100% !important;
}

/* ── Page title ── */
.page-header {
    display: flex;
    align-items: baseline;
    gap: 14px;
    margin-bottom: 0.25rem;
}
.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: #F9FAFB;
    letter-spacing: -0.5px;
    line-height: 1.2;
}
.page-badge {
    font-size: 0.7rem;
    font-weight: 600;
    color: #10B981;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.3);
    padding: 3px 10px;
    border-radius: 99px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.page-subtitle {
    font-size: 0.78rem;
    color: #4B5563;
    font-weight: 400;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    margin-bottom: 2.25rem;
}

/* ── iframe wrapper spacing ── */
iframe {
    border-radius: 0 0 14px 14px !important;
    display: block;
}
</style>
""", unsafe_allow_html=True)

# ── Page Header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <span class="page-title">⚡ Tech &amp; Energy Volatility Engine</span>
    <span class="page-badge">● Live</span>
</div>
<div class="page-subtitle">Odon Nkongolo &nbsp;·&nbsp; TradingView Powered &nbsp;·&nbsp; 1-Min Candles</div>
""", unsafe_allow_html=True)

# ── Ticker Config ────────────────────────────────────────────────────────────
TICKERS = [
    {"symbol": "BITSTAMP:BTCUSD", "label": "BTC / USD",  "name": "Bitcoin",    "accent": "#F59E0B"},
    {"symbol": "NASDAQ:TSLA",     "label": "TSLA",        "name": "Tesla Inc.", "accent": "#EF4444"},
    {"symbol": "NASDAQ:AAPL",     "label": "AAPL",        "name": "Apple Inc.", "accent": "#3B82F6"},
]

# ── Render each ticker as a full-width stacked card ──────────────────────────
for i, ticker in enumerate(TICKERS):
    accent = ticker["accent"]

    card_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

      * {{ margin: 0; padding: 0; box-sizing: border-box; }}

      body {{
        background: #0F1622;
        font-family: 'Inter', sans-serif;
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid #1E2A3A;
        box-shadow: 0 4px 32px rgba(0,0,0,0.4);
      }}

      /* Top accent bar */
      .accent-bar {{
        height: 3px;
        background: linear-gradient(90deg, {accent}, transparent);
        width: 100%;
      }}

      /* Card header */
      .card-header {{
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px 20px;
        background: #0F1622;
        border-bottom: 1px solid #1E2A3A;
      }}

      /* Live pulse dot */
      .live-dot {{
        width: 9px; height: 9px;
        border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 0 0 rgba(16,185,129,0.5);
        animation: pulse 2.2s ease-out infinite;
        flex-shrink: 0;
      }}
      @keyframes pulse {{
        0%   {{ box-shadow: 0 0 0 0 rgba(16,185,129,0.5); }}
        70%  {{ box-shadow: 0 0 0 8px rgba(16,185,129,0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(16,185,129,0); }}
      }}

      .ticker-symbol {{
        font-size: 1.15rem;
        font-weight: 800;
        color: #F9FAFB;
        letter-spacing: -0.2px;
      }}

      .ticker-name {{
        font-size: 0.72rem;
        color: #6B7280;
        font-weight: 500;
        background: #1A2333;
        padding: 3px 10px;
        border-radius: 99px;
        border: 1px solid #1E2A3A;
        letter-spacing: 0.3px;
      }}

      .accent-chip {{
        font-size: 0.68rem;
        font-weight: 700;
        color: {accent};
        background: transparent;
        border: 1px solid {accent}55;
        padding: 2px 9px;
        border-radius: 99px;
        letter-spacing: 0.5px;
        margin-left: auto;
      }}

      /* Chart container */
      #chart_{i} {{
        height: 490px;
        width: 100%;
        background: #0F1622;
      }}
    </style>
    </head>
    <body>
      <div class="accent-bar"></div>
      <div class="card-header">
        <div class="live-dot"></div>
        <span class="ticker-symbol">{ticker['label']}</span>
        <span class="ticker-name">{ticker['name']}</span>
        <span class="accent-chip">1M · LIVE</span>
      </div>
      <div id="chart_{i}"></div>

      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>
        new TradingView.widget({{
          "container_id":       "chart_{i}",
          "autosize":           true,
          "symbol":             "{ticker['symbol']}",
          "interval":           "1",
          "timezone":           "Etc/UTC",
          "theme":              "dark",
          "style":              "1",
          "locale":             "en",
          "backgroundColor":    "#0F1622",
          "gridColor":          "#1A2333",
          "hide_top_toolbar":   false,
          "hide_legend":        false,
          "hide_side_toolbar":  false,
          "withdateranges":     true,
          "allow_symbol_change": false,
          "save_image":         false,
          "enable_publishing":  false
        }});
      </script>
    </body>
    </html>
    """

    components.html(card_html, height=548, scrolling=False)

    # Gap between cards
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)