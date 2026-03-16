import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Guard ──────────────────────────────────────────────────────────────────────
if not st.session_state.get("authentication_status"):
    st.switch_page("app.py")

st.set_page_config(
    page_title="QC Analytics · Modelos",
    page_icon="⬛",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;600&display=swap');
  :root {
    --bg:#0a0c10; --surface:#111419; --border:#1e2530;
    --accent:#00d4aa; --red:#ff3b5c; --text:#c9d1d9; --muted:#4a5568;
    --mono:'JetBrains Mono',monospace; --sans:'Inter',sans-serif;
  }
  html,body,[data-testid="stAppViewContainer"] {
    background:var(--bg) !important; color:var(--text) !important;
    font-family:var(--sans);
  }
  [data-testid="stSidebar"] {
    background:var(--surface) !important;
    border-right:1px solid var(--border) !important;
  }
  header[data-testid="stHeader"] { background:transparent !important; }
  .block-container { padding-top:1.5rem !important; }

  /* Cards de score */
  .score-card {
    background:var(--surface); border:1px solid var(--border);
    border-radius:8px; padding:20px 24px; text-align:center;
  }
  .score-label {
    font-family:var(--mono); font-size:10px; color:var(--muted);
    letter-spacing:1.5px; text-transform:uppercase; margin-bottom:8px;
  }
  .score-val {
    font-family:var(--mono); font-size:36px; font-weight:700;
  }
  .score-desc { font-size:12px; margin-top:6px; color:var(--muted); }

  /* Semáforo señal */
  .signal-box {
    border-radius:8px; padding:14px 18px;
    font-family:var(--mono); font-size:13px;
    display:flex; align-items:center; gap:10px;
    margin-bottom:8px;
  }
  .sig-buy  { background:rgba(0,212,170,.08); border:1px solid rgba(0,212,170,.25); }
  .sig-sell { background:rgba(255,59,92,.08);  border:1px solid rgba(255,59,92,.25); }
  .sig-neu  { background:rgba(74,85,104,.12);  border:1px solid rgba(74,85,104,.3); }

  h1,h2,h3 { font-family:var(--mono) !important; color:var(--text) !important; }
  .stButton > button {
    background:transparent !important; border:1px solid var(--accent) !important;
    color:var(--accent) !important; font-family:var(--mono) !important;
    font-size:12px !important; letter-spacing:1px !important;
    border-radius:4px !important;
  }
  .stButton > button:hover {
    background:var(--accent) !important; color:var(--bg) !important;
  }
  div[data-baseweb="tab-list"] { border-bottom:1px solid var(--border) !important; }
  div[data-baseweb="tab"] { font-family:var(--mono) !important; font-size:12px !important; }
</style>
""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#060810",
    font=dict(family="JetBrains Mono, monospace", color="#c9d1d9", size=11),
    xaxis=dict(gridcolor="#1e2530", showgrid=True, zeroline=False),
    yaxis=dict(gridcolor="#1e2530", showgrid=True, zeroline=False),
    margin=dict(l=10, r=10, t=36, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2530", borderwidth=1),
)

# ── Cache ──────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_data(ticker, period="1y", interval="1d"):
    df = yf.download(ticker, period=period, interval=interval,
                     auto_adjust=True, progress=False)
    df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    return df

@st.cache_data(ttl=600)
def get_info(ticker):
    try:
        return yf.Ticker(ticker).info
    except Exception:
        return {}

def fmt_large(n):
    if n is None: return "N/A"
    if abs(n) >= 1e12: return f"${n/1e12:.2f}T"
    if abs(n) >= 1e9:  return f"${n/1e9:.2f}B"
    if abs(n) >= 1e6:  return f"${n/1e6:.2f}M"
    return f"${n:,.0f}"

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:\'JetBrains Mono\',monospace;font-size:18px;font-weight:700;color:#00d4aa;letter-spacing:3px;padding-bottom:12px;border-bottom:1px solid #1e2530;margin-bottom:18px;">QC ANALYTICS</div>', unsafe_allow_html=True)
    # Ticker global compartido entre páginas
    if "ticker_global" not in st.session_state:
        st.session_state["ticker_global"] = "AAPL"
    ticker = st.text_input(
        "TICKER",
        value=st.session_state["ticker_global"],
        placeholder="ej. AAPL, GMEXICOB.MX",
        key="ticker_modelos",
    ).upper().strip()
    if ticker:
        st.session_state["ticker_global"] = ticker
    periodo = st.select_slider("PERIODO", options=["3M","6M","1A","2A","3A"], value="1A")
    periodo_map = {"3M":"3mo","6M":"6mo","1A":"1y","2A":"2y","3A":"3y"}
    st.markdown("---")
    user_name = st.session_state.get("name", "Usuario")
    st.markdown(f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#4a5568;margin-bottom:8px;">SESIÓN: {user_name.upper()}</div>', unsafe_allow_html=True)
    if st.button("CERRAR SESIÓN"):
        for k in ["authentication_status","name","username"]:
            st.session_state[k] = None
        st.switch_page("app.py")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;padding:6px 0 18px 0;
            border-bottom:1px solid #1e2530;margin-bottom:20px;">
  <span style="font-family:'JetBrains Mono',monospace;font-size:22px;font-weight:700;color:#00d4aa;letter-spacing:2px;">QC</span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:18px;color:#c9d1d9;">MODELOS FINANCIEROS</span>
  <span style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a5568;border:1px solid #1e2530;padding:2px 8px;border-radius:3px;letter-spacing:1px;">BETA</span>
</div>
""", unsafe_allow_html=True)

# ── Cargar datos ───────────────────────────────────────────────────────────────
with st.spinner("Cargando datos…"):
    df   = get_data(ticker, periodo_map[periodo])
    info = get_info(ticker)

if df.empty:
    st.error(f"No se encontraron datos para **{ticker}**.")
    st.stop()

close  = df["Close"].squeeze()
high   = df["High"].squeeze()
low    = df["Low"].squeeze()
volume = df["Volume"].squeeze() if "Volume" in df.columns else None

# ══════════════════════════════════════════════════════════════════════════════
# CÁLCULOS
# ══════════════════════════════════════════════════════════════════════════════

# ── RSI ───────────────────────────────────────────────────────────────────────
def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))

rsi = calc_rsi(close)
rsi_val = float(rsi.iloc[-1]) if not rsi.empty else 50

# ── MACD ──────────────────────────────────────────────────────────────────────
ema12    = close.ewm(span=12, adjust=False).mean()
ema26    = close.ewm(span=26, adjust=False).mean()
macd     = ema12 - ema26
signal   = macd.ewm(span=9, adjust=False).mean()
hist     = macd - signal
macd_val = float(macd.iloc[-1])
sig_val  = float(signal.iloc[-1])

# ── Soporte y Resistencia ─────────────────────────────────────────────────────
window = min(20, len(close) // 4)
soporte    = float(low.rolling(window).min().iloc[-1])
resistencia = float(high.rolling(window).max().iloc[-1])
precio_act  = float(close.iloc[-1])

# ── Score de salud financiera (0-100) ─────────────────────────────────────────
def health_score(info):
    score = 50  # base
    items = []

    pe = info.get("trailingPE")
    if pe:
        if pe < 15:   score += 10; items.append(("P/U bajo (<15)", +10))
        elif pe < 25: score += 5;  items.append(("P/U moderado",  +5))
        else:         score -= 5;  items.append(("P/U alto (>25)", -5))

    pm = info.get("profitMargins")
    if pm:
        if pm > 0.20:  score += 15; items.append(("Margen >20%",  +15))
        elif pm > 0.10: score += 8; items.append(("Margen >10%",   +8))
        elif pm > 0:    score += 2; items.append(("Margen positivo",+2))
        else:           score -= 15; items.append(("Margen negativo",-15))

    de = info.get("debtToEquity")
    if de is not None:
        if de < 50:    score += 10; items.append(("Deuda baja",   +10))
        elif de < 150: score += 3;  items.append(("Deuda moderada", +3))
        else:          score -= 10; items.append(("Deuda alta",   -10))

    roe = info.get("returnOnEquity")
    if roe:
        if roe > 0.20:  score += 10; items.append(("ROE >20%",   +10))
        elif roe > 0.10: score += 5; items.append(("ROE >10%",    +5))
        else:            score -= 3; items.append(("ROE bajo",    -3))

    rev_g = info.get("revenueGrowth")
    if rev_g:
        if rev_g > 0.15:  score += 5; items.append(("Crecimiento ingresos >15%", +5))
        elif rev_g > 0.05: score += 2; items.append(("Crecimiento ingresos >5%",  +2))
        else:              score -= 3; items.append(("Crecimiento lento",          -3))

    return max(0, min(100, score)), items

health, health_items = health_score(info)

# ── Señales ───────────────────────────────────────────────────────────────────
def rsi_signal(v):
    if v >= 70: return "SOBRECOMPRADA — considera esperar antes de comprar", "sell"
    if v <= 30: return "SOBREVENDIDA — posible oportunidad de compra", "buy"
    return "NEUTRAL — sin señal clara", "neu"

def macd_signal(m, s):
    if m > s: return "ALCISTA — MACD por encima de la señal", "buy"
    return "BAJISTA — MACD por debajo de la señal", "sell"

def sr_signal(p, sup, res):
    rango = res - sup
    if rango == 0: return "Sin rango definido", "neu"
    pos = (p - sup) / rango * 100
    if pos >= 85: return f"Cerca de resistencia (${res:,.2f}) — zona de presión vendedora", "sell"
    if pos <= 15: return f"Cerca de soporte (${sup:,.2f}) — zona de posible rebote", "buy"
    return f"En zona media del rango (${sup:,.2f} – ${res:,.2f})", "neu"

rsi_txt, rsi_sig = rsi_signal(rsi_val)
macd_txt, macd_sig = macd_signal(macd_val, sig_val)
sr_txt, sr_sig = sr_signal(precio_act, soporte, resistencia)

SIG_ICONS = {"buy": "🟢", "sell": "🔴", "neu": "🟡"}
SIG_CLASS = {"buy": "sig-buy", "sell": "sig-sell", "neu": "sig-neu"}

def health_color(s):
    if s >= 70: return "#00d4aa"
    if s >= 45: return "#f5c518"
    return "#ff3b5c"

def health_label(s):
    if s >= 70: return "SALUDABLE"
    if s >= 45: return "MODERADA"
    return "EN RIESGO"

# ══════════════════════════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════════════════════════
nombre = info.get("longName", ticker)
st.markdown(f"### {ticker} &nbsp;·&nbsp; {nombre}")
st.markdown("<br>", unsafe_allow_html=True)

tab_rsi, tab_macd, tab_sr, tab_health, tab_mc = st.tabs([
    "  RSI  ", "  MACD  ", "  SOPORTE / RESISTENCIA  ", "  SALUD FINANCIERA  ", "  MONTE CARLO  "
])

# ═══ RSI ══════════════════════════════════════════════════════════════════════
with tab_rsi:
    c1, c2 = st.columns([1, 3])
    with c1:
        col = "#00d4aa" if rsi_val <= 30 else "#ff3b5c" if rsi_val >= 70 else "#f5c518"
        st.markdown(f"""
        <div class="score-card">
          <div class="score-label">RSI (14)</div>
          <div class="score-val" style="color:{col}">{rsi_val:.1f}</div>
          <div class="score-desc">{'Sobrevendida' if rsi_val<=30 else 'Sobrecomprada' if rsi_val>=70 else 'Zona neutral'}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="signal-box {SIG_CLASS[rsi_sig]}">
          {SIG_ICONS[rsi_sig]} {rsi_txt}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a5568;margin-top:16px;line-height:1.8;">
        <b style="color:#c9d1d9;">¿Qué es el RSI?</b><br>
        Mide si una acción está cara o barata según su propio comportamiento reciente.<br><br>
        <b style="color:#ff3b5c;">RSI &gt; 70</b> → puede estar sobrecomprada<br>
        <b style="color:#00d4aa;">RSI &lt; 30</b> → puede estar sobrevendida<br>
        <b style="color:#f5c518;">RSI 30–70</b> → zona neutral
        </div>
        """, unsafe_allow_html=True)

    with c2:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.6, 0.4], vertical_spacing=0.04)
        fig.add_trace(go.Scatter(x=df.index, y=close, name="Precio",
                                  line=dict(color="#00d4aa", width=1.5)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=rsi, name="RSI",
                                  line=dict(color="#f5c518", width=1.5)), row=2, col=1)
        fig.add_hline(y=70, line_color="#ff3b5c", line_dash="dot", line_width=1,
                      opacity=0.6, row=2, col=1)
        fig.add_hline(y=30, line_color="#00d4aa", line_dash="dot", line_width=1,
                      opacity=0.6, row=2, col=1)
        fig.add_hrect(y0=70, y1=100, fillcolor="rgba(255,59,92,0.04)",
                      line_width=0, row=2, col=1)
        fig.add_hrect(y0=0, y1=30, fillcolor="rgba(0,212,170,0.04)",
                      line_width=0, row=2, col=1)
        layout = {**PLOTLY_LAYOUT, "height": 420, "showlegend": True}
        fig.update_layout(**layout)
        fig.update_yaxes(title_text="PRECIO", row=1, col=1)
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

# ═══ MACD ═════════════════════════════════════════════════════════════════════
with tab_macd:
    c1, c2 = st.columns([1, 3])
    with c1:
        macd_col = "#00d4aa" if macd_sig == "buy" else "#ff3b5c"
        st.markdown(f"""
        <div class="score-card">
          <div class="score-label">MACD</div>
          <div class="score-val" style="color:{macd_col};font-size:26px;">{macd_val:+.3f}</div>
          <div class="score-desc">Señal: {sig_val:.3f}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="signal-box {SIG_CLASS[macd_sig]}">
          {SIG_ICONS[macd_sig]} {macd_txt}
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a5568;margin-top:16px;line-height:1.8;">
        <b style="color:#c9d1d9;">¿Qué es el MACD?</b><br>
        Detecta cambios de tendencia comparando dos medias móviles.<br><br>
        <b style="color:#00d4aa;">MACD cruza hacia arriba</b> → señal de compra<br>
        <b style="color:#ff3b5c;">MACD cruza hacia abajo</b> → señal de venta<br>
        El histograma muestra la fuerza de la tendencia
        </div>
        """, unsafe_allow_html=True)

    with c2:
        fig2 = make_subplots(rows=2, cols=1, shared_xaxes=True,
                              row_heights=[0.55, 0.45], vertical_spacing=0.04)
        fig2.add_trace(go.Scatter(x=df.index, y=close, name="Precio",
                                   line=dict(color="#00d4aa", width=1.5)), row=1, col=1)
        fig2.add_trace(go.Scatter(x=df.index, y=macd, name="MACD",
                                   line=dict(color="#0090ff", width=1.5)), row=2, col=1)
        fig2.add_trace(go.Scatter(x=df.index, y=signal, name="Señal",
                                   line=dict(color="#f5c518", width=1.2, dash="dot")), row=2, col=1)
        hist_colors = ["#00d4aa" if v >= 0 else "#ff3b5c" for v in hist]
        fig2.add_trace(go.Bar(x=df.index, y=hist, name="Histograma",
                               marker_color=hist_colors, opacity=0.6), row=2, col=1)
        layout2 = {**PLOTLY_LAYOUT, "height": 420}
        fig2.update_layout(**layout2)
        fig2.update_yaxes(title_text="PRECIO", row=1, col=1)
        fig2.update_yaxes(title_text="MACD", row=2, col=1)
        st.plotly_chart(fig2, use_container_width=True)

# ═══ SOPORTE / RESISTENCIA ════════════════════════════════════════════════════
with tab_sr:
    c1, c2 = st.columns([1, 3])
    with c1:
        rango = resistencia - soporte
        pos_pct = (precio_act - soporte) / rango * 100 if rango > 0 else 50

        st.markdown(f"""
        <div class="score-card" style="margin-bottom:12px;">
          <div class="score-label">RESISTENCIA</div>
          <div class="score-val" style="color:#ff3b5c;font-size:24px;">${resistencia:,.2f}</div>
        </div>
        <div class="score-card" style="margin-bottom:12px;">
          <div class="score-label">PRECIO ACTUAL</div>
          <div class="score-val" style="font-size:24px;">${precio_act:,.2f}</div>
          <div class="score-desc">{pos_pct:.0f}% del rango</div>
        </div>
        <div class="score-card">
          <div class="score-label">SOPORTE</div>
          <div class="score-val" style="color:#00d4aa;font-size:24px;">${soporte:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="signal-box {SIG_CLASS[sr_sig]}">
          {SIG_ICONS[sr_sig]} {sr_txt}
        </div>
        """, unsafe_allow_html=True)

    with c2:
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=df.index, y=close, name="Precio",
                                   line=dict(color="#00d4aa", width=1.5),
                                   fill="tozeroy", fillcolor="rgba(0,212,170,0.04)"))
        fig3.add_hline(y=resistencia, line_color="#ff3b5c", line_dash="dash",
                       line_width=1.5, annotation_text=f"Resistencia ${resistencia:,.2f}",
                       annotation_font_color="#ff3b5c")
        fig3.add_hline(y=soporte, line_color="#00d4aa", line_dash="dash",
                       line_width=1.5, annotation_text=f"Soporte ${soporte:,.2f}",
                       annotation_font_color="#00d4aa")
        fig3.add_hrect(y0=soporte, y1=resistencia,
                       fillcolor="rgba(0,144,255,0.03)", line_width=0)
        fig3.update_layout(**PLOTLY_LAYOUT, height=420,
                            title=dict(text=f"Rango de precio · {window} períodos", font=dict(size=11)))
        st.plotly_chart(fig3, use_container_width=True)

# ═══ SALUD FINANCIERA ═════════════════════════════════════════════════════════
with tab_health:
    c1, c2 = st.columns([1, 2])
    with c1:
        hcol = health_color(health)
        hlbl = health_label(health)
        st.markdown(f"""
        <div class="score-card">
          <div class="score-label">SCORE DE SALUD</div>
          <div class="score-val" style="color:{hcol};font-size:56px;">{health}</div>
          <div class="score-desc" style="color:{hcol};font-size:13px;font-weight:600;">{hlbl}</div>
          <div class="score-desc">de 100 puntos posibles</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        # Gauge visual simple
        bar_w = health
        st.markdown(f"""
        <div style="margin-top:8px;">
          <div style="background:#1e2530;border-radius:4px;height:8px;overflow:hidden;">
            <div style="width:{bar_w}%;height:100%;background:{hcol};border-radius:4px;
                        transition:width .4s;"></div>
          </div>
          <div style="display:flex;justify-content:space-between;
                      font-family:'JetBrains Mono',monospace;font-size:9px;
                      color:#4a5568;margin-top:4px;">
            <span>0</span><span>50</span><span>100</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("#### Desglose del score")
        st.markdown("<br>", unsafe_allow_html=True)
        for item, pts in health_items:
            col_pts = "#00d4aa" if pts > 0 else "#ff3b5c"
            sign    = "+" if pts > 0 else ""
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                        padding:10px 14px;margin-bottom:6px;
                        background:#111419;border:1px solid #1e2530;border-radius:6px;">
              <span style="font-family:'JetBrains Mono',monospace;font-size:12px;">{item}</span>
              <span style="font-family:'JetBrains Mono',monospace;font-size:13px;
                           font-weight:700;color:{col_pts};">{sign}{pts} pts</span>
            </div>
            """, unsafe_allow_html=True)

        if not health_items:
            st.info("No hay suficientes datos fundamentales para este ticker.")

        st.markdown("<br>", unsafe_allow_html=True)
        # Métricas clave
        m1, m2, m3 = st.columns(3)
        metrics = [
            ("P/U", f"{info.get('trailingPE',0):.1f}x" if info.get('trailingPE') else "N/A"),
            ("Margen Neto", f"{info.get('profitMargins',0)*100:.1f}%" if info.get('profitMargins') else "N/A"),
            ("ROE", f"{info.get('returnOnEquity',0)*100:.1f}%" if info.get('returnOnEquity') else "N/A"),
        ]
        for col_m, (lbl, val) in zip([m1, m2, m3], metrics):
            col_m.markdown(f"""
            <div style="background:#111419;border:1px solid #1e2530;border-radius:6px;
                        padding:12px;text-align:center;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:9px;
                          color:#4a5568;letter-spacing:1px;margin-bottom:4px;">{lbl}</div>
              <div style="font-family:'JetBrains Mono',monospace;font-size:18px;
                          font-weight:700;">{val}</div>
            </div>
            """, unsafe_allow_html=True)

# ═══ MONTE CARLO ══════════════════════════════════════════════════════════════
with tab_mc:
    st.markdown("""
    <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#4a5568;
                margin-bottom:20px;line-height:1.7;">
    Simula miles de escenarios futuros posibles basados en la volatilidad histórica
    de la acción. No predice el futuro — muestra el <b style="color:#c9d1d9;">abanico de probabilidades</b>.
    </div>
    """, unsafe_allow_html=True)

    # Controles
    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1:
        if st.session_state.get("mc_sims") not in [1000, 2000, 5000, 10000]:
            st.session_state["mc_sims"] = 1000
        n_sims = st.select_slider(
            "SIMULACIONES", options=[1000, 2000, 5000, 10000], value=1000,
            key="mc_sims"
        )
    with ctrl2:
        horizonte = st.select_slider(
            "HORIZONTE (días)", options=[30, 60, 90, 180, 252, 504],
            value=252, key="mc_horizon",
            format_func=lambda x: {
                30:"1 mes", 60:"2 meses", 90:"3 meses",
                180:"6 meses", 252:"1 año", 504:"2 años"
            }[x]
        )
    with ctrl3:
        inversion = st.number_input(
            "INVERSIÓN INICIAL ($)", min_value=100,
            max_value=1_000_000, value=10_000, step=1000,
            key="mc_inv"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Cálculo Monte Carlo ────────────────────────────────────────────────────
    retornos = close.pct_change().dropna()
    mu       = float(retornos.mean())
    sigma    = float(retornos.std())
    S0       = precio_act
    dt       = 1  # 1 día

    np.random.seed(42)
    # Movimiento Browniano Geométrico: S(t) = S(t-1)*exp((μ-σ²/2)dt + σ√dt·Z)
    Z         = np.random.standard_normal((horizonte, n_sims))
    drift     = (mu - 0.5 * sigma**2) * dt
    diffusion = sigma * np.sqrt(dt) * Z
    precios   = np.zeros((horizonte + 1, n_sims))
    precios[0] = S0
    for t in range(1, horizonte + 1):
        precios[t] = precios[t - 1] * np.exp(drift + diffusion[t - 1])

    finales   = precios[-1]
    pct_5     = np.percentile(finales, 5)
    pct_25    = np.percentile(finales, 25)
    pct_50    = np.percentile(finales, 50)
    pct_75    = np.percentile(finales, 75)
    pct_95    = np.percentile(finales, 95)
    prob_gain = float((finales > S0).mean() * 100)

    # Percentiles en el tiempo
    p5_t  = np.percentile(precios, 5,  axis=1)
    p25_t = np.percentile(precios, 25, axis=1)
    p50_t = np.percentile(precios, 50, axis=1)
    p75_t = np.percentile(precios, 75, axis=1)
    p95_t = np.percentile(precios, 95, axis=1)
    dias  = list(range(horizonte + 1))

    # ── Gráfica ────────────────────────────────────────────────────────────────
    col_gr, col_stats = st.columns([2, 1])

    with col_gr:
        fig_mc = go.Figure()

        # Banda exterior 5-95%
        fig_mc.add_trace(go.Scatter(
            x=dias + dias[::-1], y=list(p95_t) + list(p5_t[::-1]),
            fill="toself", fillcolor="rgba(0,144,255,0.06)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Rango 5%–95%", hoverinfo="skip",
        ))
        # Banda interior 25-75%
        fig_mc.add_trace(go.Scatter(
            x=dias + dias[::-1], y=list(p75_t) + list(p25_t[::-1]),
            fill="toself", fillcolor="rgba(0,144,255,0.12)",
            line=dict(color="rgba(0,0,0,0)"),
            name="Rango 25%–75%", hoverinfo="skip",
        ))
        # Percentil 95
        fig_mc.add_trace(go.Scatter(
            x=dias, y=p95_t, name="Optimista (95%)",
            line=dict(color="#00d4aa", width=1.2, dash="dot"), opacity=0.7,
        ))
        # Percentil 50 (mediana)
        fig_mc.add_trace(go.Scatter(
            x=dias, y=p50_t, name="Mediana (50%)",
            line=dict(color="#f5c518", width=2),
        ))
        # Percentil 5
        fig_mc.add_trace(go.Scatter(
            x=dias, y=p5_t, name="Pesimista (5%)",
            line=dict(color="#ff3b5c", width=1.2, dash="dot"), opacity=0.7,
        ))
        # Precio actual (línea base)
        fig_mc.add_hline(
            y=S0, line_color="#4a5568", line_dash="dash", line_width=1,
            annotation_text=f"Hoy ${S0:,.2f}",
            annotation_font_color="#4a5568",
        )

        # Muestra 80 trayectorias aleatorias muy transparentes
        sample_idx = np.random.choice(n_sims, size=min(80, n_sims), replace=False)
        for i in sample_idx:
            fig_mc.add_trace(go.Scatter(
                x=dias, y=precios[:, i],
                mode="lines", line=dict(color="rgba(0,144,255,0.05)", width=0.5),
                showlegend=False, hoverinfo="skip",
            ))

        fig_mc.update_layout(
            **PLOTLY_LAYOUT, height=440,
            title=dict(
                text=f"Monte Carlo · {ticker} · {n_sims:,} simulaciones · {horizonte} días",
                font=dict(size=12)
            ),
            xaxis_title="Días",
            yaxis_title="Precio ($)",
        )
        st.plotly_chart(fig_mc, use_container_width=True)

    with col_stats:
        # KPIs de la simulación
        ret_med   = (pct_50 - S0) / S0 * 100
        ret_opt   = (pct_95 - S0) / S0 * 100
        ret_pes   = (pct_5  - S0) / S0 * 100
        val_med   = inversion * (1 + ret_med / 100)
        val_opt   = inversion * (1 + ret_opt / 100)
        val_pes   = inversion * (1 + ret_pes / 100)
        gain_col  = "#00d4aa" if prob_gain >= 50 else "#ff3b5c"

        st.markdown(f"""
        <div class="score-card" style="margin-bottom:10px;">
          <div class="score-label">PROBABILIDAD DE GANANCIA</div>
          <div class="score-val" style="color:{gain_col};font-size:40px;">{prob_gain:.0f}%</div>
          <div class="score-desc">de las {n_sims:,} simulaciones terminan en positivo</div>
        </div>
        """, unsafe_allow_html=True)

        escenarios = [
            ("🟢 OPTIMISTA (5% superior)",  pct_95, ret_opt, val_opt, "#00d4aa"),
            ("🟡 MEDIANA (escenario base)", pct_50, ret_med, val_med, "#f5c518"),
            ("🔴 PESIMISTA (5% inferior)",  pct_5,  ret_pes, val_pes, "#ff3b5c"),
        ]
        for label, precio_f, ret, val, color in escenarios:
            signo = "+" if ret >= 0 else ""
            st.markdown(f"""
            <div style="background:#111419;border:1px solid #1e2530;border-radius:8px;
                        padding:14px 16px;margin-bottom:8px;">
              <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                          color:#4a5568;margin-bottom:8px;">{label}</div>
              <div style="display:flex;justify-content:space-between;align-items:baseline;">
                <div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:18px;
                              font-weight:700;color:{color};">${precio_f:,.2f}</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                              color:{color};">{signo}{ret:.1f}%</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                              color:#4a5568;">inversión</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:16px;
                              font-weight:600;color:{color};">${val:,.0f}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Volatilidad y parámetros usados
        st.markdown(f"""
        <div style="background:#0a0c10;border:1px solid #1e2530;border-radius:8px;
                    padding:14px 16px;margin-top:4px;">
          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;
                      color:#4a5568;margin-bottom:10px;letter-spacing:1px;">PARÁMETROS DEL MODELO</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:11px;
                      color:#6b7a90;line-height:2;">
            Retorno diario μ: <b style="color:#c9d1d9;">{mu*100:+.4f}%</b><br>
            Volatilidad σ:    <b style="color:#c9d1d9;">{sigma*100:.4f}%</b><br>
            Vol. anual:       <b style="color:#c9d1d9;">{sigma*np.sqrt(252)*100:.1f}%</b><br>
            Precio hoy:       <b style="color:#c9d1d9;">${S0:,.2f}</b><br>
            Modelo:           <b style="color:#c9d1d9;">GBM</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#2d3748;
                    margin-top:12px;line-height:1.6;">
        ⚠ Simulación estadística basada en comportamiento histórico.<br>
        No constituye asesoría financiera profesional.<br>
        GBM = Movimiento Browniano Geométrico.
        </div>
        """, unsafe_allow_html=True)
