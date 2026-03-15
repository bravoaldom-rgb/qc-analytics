import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QC Analytics",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS — dark fintech terminal ─────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;600&display=swap');

  /* Base */
  :root {
    --bg:       #0a0c10;
    --surface:  #111419;
    --border:   #1e2530;
    --accent:   #00d4aa;
    --accent2:  #0090ff;
    --red:      #ff3b5c;
    --green:    #00d4aa;
    --yellow:   #f5c518;
    --text:     #c9d1d9;
    --muted:    #4a5568;
    --mono:     'JetBrains Mono', monospace;
    --sans:     'Inter', sans-serif;
  }

  html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans);
  }

  [data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
  }

  /* Header */
  .qc-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 0 18px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
  }
  .qc-logo {
    font-family: var(--mono);
    font-size: 22px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 2px;
  }
  .qc-tag {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    border: 1px solid var(--border);
    padding: 2px 8px;
    border-radius: 3px;
    letter-spacing: 1px;
  }

  /* Metric cards */
  .metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 16px 20px;
    font-family: var(--mono);
  }
  .metric-label {
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 6px;
  }
  .metric-value {
    font-size: 26px;
    font-weight: 700;
    color: var(--text);
  }
  .metric-delta-pos { color: var(--green); font-size: 12px; }
  .metric-delta-neg { color: var(--red);   font-size: 12px; }

  /* Terminal box */
  .terminal {
    background: #060810;
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 6px;
    padding: 14px 18px;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--accent);
    margin: 12px 0;
  }

  /* Streamlit tweaks */
  .stSelectbox > div > div,
  .stTextInput > div > div > input {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: var(--mono) !important;
    font-size: 13px !important;
  }
  .stButton > button {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: var(--mono) !important;
    font-size: 12px !important;
    letter-spacing: 1px !important;
    border-radius: 4px !important;
    padding: 6px 18px !important;
    transition: all 0.15s;
  }
  .stButton > button:hover {
    background: var(--accent) !important;
    color: var(--bg) !important;
  }
  h1, h2, h3 {
    font-family: var(--mono) !important;
    color: var(--text) !important;
    font-weight: 600 !important;
  }
  .stDataFrame { font-family: var(--mono) !important; font-size: 12px !important; }
  [data-testid="stMetricValue"] { font-family: var(--mono) !important; }
  .stSlider > div > div { background: var(--border) !important; }
  div[data-baseweb="tab-list"] { border-bottom: 1px solid var(--border) !important; }
  div[data-baseweb="tab"] { font-family: var(--mono) !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#060810",
    font=dict(family="JetBrains Mono, monospace", color="#c9d1d9", size=11),
    xaxis=dict(gridcolor="#1e2530", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e2530", showgrid=True, zeroline=False),
    margin=dict(l=10, r=10, t=30, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2530", borderwidth=1),
)

@st.cache_data(ttl=300)
def get_price_data(ticker: str, period: str, interval: str) -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=True, progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df

@st.cache_data(ttl=600)
def get_info(ticker: str) -> dict:
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}

def pct_color(v):
    return "metric-delta-pos" if v >= 0 else "metric-delta-neg"

def fmt_large(n):
    if n is None:
        return "N/A"
    if abs(n) >= 1e12:
        return f"${n/1e12:.2f}T"
    if abs(n) >= 1e9:
        return f"${n/1e9:.2f}B"
    if abs(n) >= 1e6:
        return f"${n/1e6:.2f}M"
    return f"${n:,.0f}"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:18px;font-weight:700;color:#00d4aa;letter-spacing:3px;padding-bottom:12px;border-bottom:1px solid #1e2530;margin-bottom:18px;">QC ANALYTICS</div>', unsafe_allow_html=True)

    ticker_input = st.text_input("TICKER", value="AAPL", placeholder="ej. MSFT, SPY, BTC-USD").upper().strip()

    period_map = {"1D": ("1d","5m"), "5D": ("5d","15m"), "1M": ("1mo","1h"),
                  "3M": ("3mo","1d"), "6M": ("6mo","1d"), "1A": ("1y","1d"),
                  "2A": ("2y","1wk"), "5A": ("5y","1wk")}
    period_sel = st.select_slider("PERIODO", options=list(period_map.keys()), value="1A")
    period, interval = period_map[period_sel]

    st.markdown("---")
    show_volume = st.checkbox("Volumen", value=True)
    show_ma     = st.checkbox("Medias Móviles", value=True)
    show_bb     = st.checkbox("Bandas de Bollinger", value=False)

    st.markdown("---")
    compare_raw = st.text_input("COMPARAR (separado por comas)", placeholder="SPY, QQQ")
    compare_list = [t.strip().upper() for t in compare_raw.split(",") if t.strip()] if compare_raw else []

    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:#4a5568;margin-top:24px;">QC ANALYTICS v0.1 · DATOS: YAHOO FINANCE</div>', unsafe_allow_html=True)

# ── Main area ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="qc-header">
  <span class="qc-logo">QC</span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:18px;color:#c9d1d9;">ANALYTICS</span>
  <span class="qc-tag">TERMINAL</span>
  <span style="flex:1"></span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#4a5568;">{datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}</span>
</div>
""", unsafe_allow_html=True)

# Load data
with st.spinner("Obteniendo datos de mercado…"):
    df   = get_price_data(ticker_input, period, interval)
    info = get_info(ticker_input)

if df.empty:
    st.error(f"No se encontraron datos para **{ticker_input}**. Verifica el símbolo.")
    st.stop()

close = df["Close"]
last  = float(close.iloc[-1])
prev  = float(close.iloc[-2]) if len(close) > 1 else last
chg   = last - prev
pct   = chg / prev * 100

# ── KPI row ────────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    ("ÚLTIMO PRECIO", f"${last:,.2f}",  f"{'▲' if chg>=0 else '▼'} {abs(chg):.2f}  ({pct:+.2f}%)", pct >= 0),
    ("CAP. MERCADO",  fmt_large(info.get("marketCap")), info.get("exchange","—"), True),
    ("MÁX. 52 SEM.",  f"${info.get('fiftyTwoWeekHigh', 0):,.2f}", "", True),
    ("MÍN. 52 SEM.",  f"${info.get('fiftyTwoWeekLow', 0):,.2f}",  "", True),
    ("VOL. PROMEDIO",  fmt_large(info.get("averageVolume")).replace("$",""), "", True),
]
for col, (label, val, delta, pos) in zip([c1,c2,c3,c4,c5], kpis):
    delta_class = "metric-delta-pos" if pos else "metric-delta-neg"
    col.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{val}</div>
      <div class="{delta_class}">{delta}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["  GRÁFICA  ", "  FUNDAMENTALES  ", "  COMPARAR  ", "  ANÁLISIS IA  "])

# ═══ TAB 1 · CHART ═══════════════════════════════════════════════════════════
with tab1:
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"],  close=df["Close"],
        name=ticker_input,
        increasing_line_color="#00d4aa", increasing_fillcolor="rgba(0,212,170,0.15)",
        decreasing_line_color="#ff3b5c", decreasing_fillcolor="rgba(255,59,92,0.15)",
    ))

    if show_ma:
        for n, color in [(20,"#0090ff"),(50,"#f5c518"),(200,"#a855f7")]:
            if len(df) >= n:
                fig.add_trace(go.Scatter(
                    x=df.index, y=close.rolling(n).mean(),
                    name=f"MA{n}", line=dict(color=color, width=1.2), opacity=0.85,
                ))

    if show_bb:
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        fig.add_trace(go.Scatter(x=df.index, y=ma20+2*std20, name="BB+2σ",
                                  line=dict(color="#4a5568", width=1, dash="dot")))
        fig.add_trace(go.Scatter(x=df.index, y=ma20-2*std20, name="BB-2σ",
                                  line=dict(color="#4a5568", width=1, dash="dot"),
                                  fill="tonexty", fillcolor="rgba(74,85,104,0.06)"))

    fig.update_layout(**PLOTLY_LAYOUT, height=420,
                       xaxis_rangeslider_visible=False,
                       title=dict(text=f"{ticker_input} · {period_sel}", font=dict(size=13)))
    st.plotly_chart(fig, use_container_width=True)

    if show_volume and "Volume" in df.columns:
        vol_colors = ["#00d4aa" if c >= o else "#ff3b5c"
                      for c, o in zip(df["Close"], df["Open"])]
        vfig = go.Figure(go.Bar(
            x=df.index, y=df["Volume"], marker_color=vol_colors,
            name="Volume", opacity=0.7,
        ))
        vfig.update_layout(**PLOTLY_LAYOUT, height=150,
                            yaxis_title="VOLUMEN", showlegend=False)
        st.plotly_chart(vfig, use_container_width=True)

# ═══ TAB 2 · FUNDAMENTALS ════════════════════════════════════════════════════
with tab2:
    st.markdown("### FUNDAMENTALES")
    if not info:
        st.warning("No hay datos fundamentales disponibles para este ticker.")
    else:
        left, right = st.columns(2)
        fund_left = {
            "Sector":          info.get("sector","—"),
            "Industria":       info.get("industry","—"),
            "País":            info.get("country","—"),
            "Empleados":       f"{info.get('fullTimeEmployees',0):,}",
            "P/U (TTM)":       f"{info.get('trailingPE',0):.2f}",
            "P/U Estimado":    f"{info.get('forwardPE',0):.2f}",
            "UPA (TTM)":       f"${info.get('trailingEps',0):.2f}",
        }
        fund_right = {
            "Ingresos":        fmt_large(info.get("totalRevenue")),
            "Margen Bruto":    f"{info.get('grossMargins',0)*100:.1f}%",
            "Margen Neto":     f"{info.get('profitMargins',0)*100:.1f}%",
            "ROE":             f"{info.get('returnOnEquity',0)*100:.1f}%",
            "Deuda/Capital":   f"{info.get('debtToEquity',0):.2f}",
            "Beta":            f"{info.get('beta',0):.2f}",
            "Rend. Dividendo": f"{info.get('dividendYield',0)*100:.2f}%" if info.get('dividendYield') else "—",
        }
        with left:
            rows = "".join(
                f'<tr><td style="color:#4a5568;padding:6px 12px 6px 0;font-size:11px;">{k}</td>'
                f'<td style="font-family:\'JetBrains Mono\',monospace;font-size:12px;">{v}</td></tr>'
                for k,v in fund_left.items()
            )
            st.markdown(f'<table style="width:100%;border-collapse:collapse;">{rows}</table>', unsafe_allow_html=True)
        with right:
            rows = "".join(
                f'<tr><td style="color:#4a5568;padding:6px 12px 6px 0;font-size:11px;">{k}</td>'
                f'<td style="font-family:\'JetBrains Mono\',monospace;font-size:12px;">{v}</td></tr>'
                for k,v in fund_right.items()
            )
            st.markdown(f'<table style="width:100%;border-collapse:collapse;">{rows}</table>', unsafe_allow_html=True)

        # Returns chart
        st.markdown("---")
        st.markdown("### DISTRIBUCIÓN DE RETORNOS")
        ret = close.pct_change().dropna() * 100
        rfig = go.Figure(go.Histogram(
            x=ret, nbinsx=60,
            marker_color="#0090ff", opacity=0.7, name="Retornos diarios",
        ))
        rfig.add_vline(x=float(ret.mean()), line_color="#00d4aa", line_dash="dash",
                       annotation_text=f"μ={ret.mean():.2f}%", annotation_font_color="#00d4aa")
        rfig.update_layout(**PLOTLY_LAYOUT, height=280, xaxis_title="Retorno (%)", yaxis_title="Frecuencia")
        st.plotly_chart(rfig, use_container_width=True)

# ═══ TAB 3 · COMPARE ═════════════════════════════════════════════════════════
with tab3:
    st.markdown("### RENDIMIENTO RELATIVO")
    if not compare_list:
        st.markdown('<div class="terminal">// Ingresa tickers en el panel → campo COMPARAR<br>// ej.  SPY, QQQ, NVDA</div>', unsafe_allow_html=True)
    else:
        all_tickers = [ticker_input] + compare_list
        colors      = ["#00d4aa","#0090ff","#f5c518","#a855f7","#ff3b5c"]
        cfig = go.Figure()
        for i, t in enumerate(all_tickers):
            try:
                cdf = get_price_data(t, period, interval)
                if cdf.empty:
                    continue
                norm = (cdf["Close"] / float(cdf["Close"].iloc[0]) - 1) * 100
                cfig.add_trace(go.Scatter(
                    x=cdf.index, y=norm,
                    name=t, line=dict(color=colors[i % len(colors)], width=1.8),
                ))
            except Exception:
                st.warning(f"No se pudo cargar {t}")
        cfig.update_layout(**PLOTLY_LAYOUT, height=440,
                            yaxis_title="Retorno vs inicio (%)",
                            title=dict(text=f"Retornos normalizados · {period_sel}", font=dict(size=13)))
        cfig.add_hline(y=0, line_color="#4a5568", line_dash="dot")
        st.plotly_chart(cfig, use_container_width=True)

# ═══ TAB 4 · AI ANALYSIS ═════════════════════════════════════════════════════
with tab4:
    st.markdown("### ANÁLISIS IA")
    api_key = os.getenv("ANTHROPIC_API_KEY", "")

    if not api_key:
        st.markdown("""
        <div class="terminal">
        // ANTHROPIC_API_KEY no configurada<br>
        // Agrégala a tu archivo .env para habilitar el análisis IA<br><br>
        // ANTHROPIC_API_KEY=sk-ant-...
        </div>
        """, unsafe_allow_html=True)
    else:
        prompt_type = st.selectbox("TIPO DE ANÁLISIS", [
            "Resumen rápido", "Análisis técnico", "Evaluación de riesgo",
            "Tesis de inversión", "Perspectiva de resultados",
        ])
        if st.button("EJECUTAR ANÁLISIS"):
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)

                context = f"""
Ticker: {ticker_input}
Precio: ${last:,.2f}  Cambio: {pct:+.2f}%
Cap. Mercado: {fmt_large(info.get('marketCap'))}
P/U: {info.get('trailingPE','N/A')}  Beta: {info.get('beta','N/A')}
Sector: {info.get('sector','N/A')}  Industria: {info.get('industry','N/A')}
Máx. 52 sem: ${info.get('fiftyTwoWeekHigh',0):,.2f}  Mín. 52 sem: ${info.get('fiftyTwoWeekLow',0):,.2f}
Ingresos: {fmt_large(info.get('totalRevenue'))}  Margen Neto: {info.get('profitMargins',0)*100:.1f}%
"""
                system_msg = (
                    "Eres un analista cuantitativo senior de una firma fintech. "
                    "Responde en español, sé conciso y orientado a datos, usa formato markdown. "
                    "Resalta números clave con **negrita**. Límite ~250 palabras."
                )
                with st.spinner("Analizando…"):
                    message = client.messages.create(
                        model="claude-opus-4-6",
                        max_tokens=600,
                        system=system_msg,
                        messages=[{"role":"user","content":f"Proporciona un {prompt_type} para:\n{context}"}],
                    )
                result = message.content[0].text
                st.markdown(f'<div style="background:#060810;border:1px solid #1e2530;border-left:3px solid #00d4aa;border-radius:6px;padding:18px;font-size:13px;line-height:1.7;">{result}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error IA: {e}")
