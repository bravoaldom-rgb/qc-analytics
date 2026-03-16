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
    page_title="QC Analytics · Dashboard",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Guard: requiere sesión activa ──────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;text-align:center;margin-top:80px;">
      <div style="font-size:24px;color:#00d4aa;font-weight:700;letter-spacing:3px;">QC</div>
      <div style="font-size:12px;color:#4a5568;margin:8px 0 24px 0;letter-spacing:2px;">ACCESO RESTRINGIDO</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("← Ir al login"):
        st.switch_page("app.py")
    st.stop()

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

  /* ── Selector de periodo de volumen ── */
  div[data-testid="stRadio"] > div {
    flex-direction: row !important;
    flex-wrap: wrap !important;
    gap: 4px !important;
    margin-top: 6px !important;
  }
  div[data-testid="stRadio"] label {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    padding: 3px 10px !important;
    cursor: pointer !important;
    font-family: var(--mono) !important;
    font-size: 11px !important;
    color: var(--muted) !important;
    letter-spacing: .8px !important;
    transition: all .15s !important;
  }
  div[data-testid="stRadio"] label:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
  }
  div[data-testid="stRadio"] label:has(input:checked) {
    background: rgba(0,212,170,0.08) !important;
    border-color: var(--accent) !important;
    color: var(--accent) !important;
  }
  div[data-testid="stRadio"] input[type="radio"] { display: none !important; }
  div[data-testid="stRadio"] > label { display: none !important; }
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

    # Ticker global compartido entre páginas
    if "ticker_global" not in st.session_state:
        st.session_state["ticker_global"] = "AAPL"
    ticker_input = st.text_input(
        "TICKER",
        value=st.session_state["ticker_global"],
        placeholder="ej. MSFT, SPY, BTC-USD",
        key="ticker_dashboard",
    ).upper().strip()
    if ticker_input:
        st.session_state["ticker_global"] = ticker_input

    period_map = {
        "1D": ("1d",  "5m"),
        "5D": ("5d",  "15m"),
        "1M": ("1mo", "1h"),
        "3M": ("3mo", "1d"),
        "6M": ("6mo", "1d"),
        "1A": ("1y",  "1d"),
        "2A": ("2y",  "1wk"),
        "3A": ("3y",  "1wk"),
        "4A": ("4y",  "1wk"),
        "5A": ("5y",  "1wk"),
    }
    period_sel = st.select_slider("PERIODO", options=list(period_map.keys()), value="1A")
    period, interval = period_map[period_sel]

    st.markdown("---")
    show_volume = st.checkbox("Volumen", value=True)
    show_ma     = st.checkbox("Medias Móviles", value=True)
    show_bb     = st.checkbox("Bandas de Bollinger", value=False)

    st.markdown("---")
    compare_raw = st.text_input("COMPARAR (separado por comas)", placeholder="SPY, QQQ")
    compare_list = [t.strip().upper() for t in compare_raw.split(",") if t.strip()] if compare_raw else []

    st.markdown("---")
    user_name = st.session_state.get("name", "Usuario")
    st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#4a5568;margin-bottom:8px;">SESIÓN: {user_name.upper()}</div>', unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN"):
        st.session_state["authentication_status"] = None
        st.session_state["name"] = None
        st.session_state["username"] = None
        st.switch_page("app.py")

    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:#4a5568;margin-top:16px;">QC ANALYTICS v0.1 · DATOS: YAHOO FINANCE</div>', unsafe_allow_html=True)

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

close = df["Close"].squeeze()          # garantiza Serie 1D aunque yfinance devuelva DataFrame
last  = float(close.iloc[-1].item() if hasattr(close.iloc[-1], "item") else close.iloc[-1])
prev  = float(close.iloc[-2].item() if hasattr(close.iloc[-2], "item") else close.iloc[-2]) if len(close) > 1 else last
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

    # ── Selector de tipo de gráfica ───────────────────────────────────────────
    chart_col1, chart_col2 = st.columns([3, 1])
    with chart_col2:
        chart_type = st.radio(
            "Tipo",
            ["🕯 Velas", "⛰ Montaña"],
            horizontal=True,
            key="chart_type",
            label_visibility="collapsed",
        )

    fig = go.Figure()

    if chart_type == "⛰ Montaña":
        # ── Estilo Yahoo Finance: línea + área rellena ────────────────────────
        line_color  = "#00d4aa" if pct >= 0 else "#ff3b5c"
        fill_color  = "rgba(0,212,170,0.12)" if pct >= 0 else "rgba(255,59,92,0.10)"

        fig.add_trace(go.Scatter(
            x=df.index,
            y=close,
            mode="lines",
            name=ticker_input,
            line=dict(color=line_color, width=1.8),
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate=(
                "<b>%{x|%d %b %Y  %H:%M}</b><br>"
                "Precio: <b>$%{y:,.2f}</b><extra></extra>"
            ),
        ))

        # Punto final (precio actual)
        fig.add_trace(go.Scatter(
            x=[df.index[-1]],
            y=[last],
            mode="markers",
            marker=dict(color=line_color, size=8, line=dict(color="#0a0c10", width=2)),
            name="Actual",
            hovertemplate=f"<b>Precio actual</b><br>${last:,.2f}<extra></extra>",
        ))

        # Línea horizontal del cierre anterior (guía)
        fig.add_hline(
            y=prev,
            line_color=line_color,
            line_dash="dot",
            line_width=0.8,
            opacity=0.4,
        )

    else:
        # ── Candlestick ───────────────────────────────────────────────────────
        fig.add_trace(go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            name=ticker_input,
            increasing_line_color="#00d4aa", increasing_fillcolor="rgba(0,212,170,0.15)",
            decreasing_line_color="#ff3b5c", decreasing_fillcolor="rgba(255,59,92,0.15)",
        ))

    # ── Indicadores (aplican en ambos modos) ──────────────────────────────────
    if show_ma:
        for n, color in [(20,"#0090ff"),(50,"#f5c518"),(200,"#a855f7")]:
            if len(df) >= n:
                fig.add_trace(go.Scatter(
                    x=df.index, y=close.rolling(n).mean(),
                    name=f"MA{n}", line=dict(color=color, width=1.2), opacity=0.85,
                ))

    if show_bb:
        ma20  = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        fig.add_trace(go.Scatter(x=df.index, y=ma20+2*std20, name="BB+2σ",
                                  line=dict(color="#4a5568", width=1, dash="dot")))
        fig.add_trace(go.Scatter(x=df.index, y=ma20-2*std20, name="BB-2σ",
                                  line=dict(color="#4a5568", width=1, dash="dot"),
                                  fill="tonexty", fillcolor="rgba(74,85,104,0.06)"))

    fig.update_layout(
        **PLOTLY_LAYOUT, height=440,
        xaxis_rangeslider_visible=False,
        title=dict(text=f"{ticker_input} · {period_sel}", font=dict(size=13)),
    )
    st.plotly_chart(fig, use_container_width=True)

    if show_volume and "Volume" in df.columns:
        vol_colors = ["#00d4aa" if c >= o else "#ff3b5c"
                      for c, o in zip(df["Close"], df["Open"])]
        vfig = go.Figure(go.Bar(
            x=df.index, y=df["Volume"],
            marker_color=vol_colors,
            name="Volumen", opacity=0.75,
        ))
        vfig.update_layout(
            **PLOTLY_LAYOUT, height=160,
            yaxis_title="VOLUMEN", showlegend=False,
            title=dict(text=f"VOLUMEN · {ticker_input} · {period_sel}", font=dict(size=11)),
        )
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
        prompt_type = st.selectbox("¿QUÉ QUIERES SABER?", [
            "¿Vale la pena invertir aquí?",
            "¿Qué hace esta empresa y cómo gana dinero?",
            "¿Qué tan arriesgada es esta inversión?",
            "¿Es cara o barata esta acción ahora mismo?",
            "¿Qué podría salir mal si invierto aquí?",
        ])
        st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#4a5568;margin-bottom:12px;">Explicación en lenguaje simple, sin tecnicismos</div>', unsafe_allow_html=True)

        if st.button("ANALIZAR CON IA"):
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)

                context = f"""
Empresa / Ticker: {ticker_input}
Nombre: {info.get('longName', ticker_input)}
Precio actual: ${last:,.2f}  Cambio hoy: {pct:+.2f}%
Capitalización de mercado: {fmt_large(info.get('marketCap'))}
Sector: {info.get('sector','N/A')}  Industria: {info.get('industry','N/A')}
País: {info.get('country','N/A')}
Precio más alto en 52 semanas: ${info.get('fiftyTwoWeekHigh',0):,.2f}
Precio más bajo en 52 semanas: ${info.get('fiftyTwoWeekLow',0):,.2f}
P/U (veces que pagas por cada peso de ganancia): {info.get('trailingPE','N/A')}
Beta (volatilidad vs mercado): {info.get('beta','N/A')}
Ingresos totales: {fmt_large(info.get('totalRevenue'))}
Margen de ganancia neta: {info.get('profitMargins',0)*100:.1f}%
Rendimiento por dividendo: {info.get('dividendYield',0)*100:.2f}% si info.get('dividendYield') else 'No paga dividendos'
"""
                system_msg = (
                    "Eres un asesor financiero amigable que ayuda a personas que NUNCA han invertido en bolsa. "
                    "Tu misión es explicar todo en lenguaje cotidiano, como si le hablaras a un amigo de 25 años. "
                    "NUNCA uses jerga financiera sin explicarla. "
                    "Siempre empieza con una conclusión clara: 🟢 INTERESANTE, 🟡 CON CAUTELA, o 🔴 CON CUIDADO. "
                    "Usa analogías simples para explicar conceptos (ej. 'el P/U es como cuántos años tardarías en recuperar tu dinero'). "
                    "Termina siempre con 2-3 puntos concretos en bullets. "
                    "Responde en español mexicano, cálido y directo. Máximo 280 palabras."
                )
                with st.spinner("Analizando en lenguaje simple…"):
                    message = client.messages.create(
                        model="claude-opus-4-6",
                        max_tokens=700,
                        system=system_msg,
                        messages=[{"role":"user","content":f"Pregunta del usuario: {prompt_type}\n\nDatos de la acción:\n{context}"}],
                    )
                result = message.content[0].text
                st.markdown(f'<div style="background:#060810;border:1px solid #1e2530;border-left:3px solid #00d4aa;border-radius:6px;padding:20px;font-size:14px;line-height:1.8;">{result}</div>', unsafe_allow_html=True)
                st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:9px;color:#4a5568;margin-top:8px;">⚠ Esto es información educativa, no asesoría financiera profesional.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error IA: {e}")
