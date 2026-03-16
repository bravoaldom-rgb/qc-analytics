import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import random

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QC Analytics",
    page_icon="⬛",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Redirect si ya hay sesión ──────────────────────────────────────────────────
if st.session_state.get("authentication_status") is True:
    st.switch_page("pages/dashboard.py")

# ── Generar velas aleatorias ───────────────────────────────────────────────────
random.seed(42)
candles_html = ""
for i in range(32):
    left   = (i / 32) * 100 + random.uniform(-1.2, 1.2)
    left   = max(0.3, min(99, left))
    body_h = random.randint(18, 190)
    wick_t = random.randint(6, 38)
    wick_b = random.randint(3, 18)
    green  = random.random() > 0.42
    col    = "#00d4aa" if green else "#ff3b5c"
    spd    = random.uniform(2.5, 8.0)
    dly    = random.uniform(0, 8)
    op     = random.uniform(0.10, 0.28)
    candles_html += (
        f'<div class="qc-c" style="left:{left:.1f}%;'
        f'animation-duration:{spd:.1f}s;animation-delay:-{dly:.2f}s;opacity:{op:.2f};">'
        f'<div style="width:1.5px;height:{wick_t}px;background:{col};margin:0 auto;"></div>'
        f'<div style="width:9px;height:{body_h}px;background:{col};border-radius:1px;"></div>'
        f'<div style="width:1.5px;height:{wick_b}px;background:{col};margin:0 auto;"></div>'
        f'</div>'
    )

# ── Ticker tape ────────────────────────────────────────────────────────────────
TICKERS = [
    ("AAPL","$182.63","+2.34%",True), ("MSFT","$415.21","+1.12%",True),
    ("TSLA","$234.15","-0.87%",False),("NVDA","$875.42","+4.21%",True),
    ("AMZN","$192.87","+0.94%",True), ("META","$521.33","+1.67%",True),
    ("GOOG","$172.54","-0.31%",False),("SPY", "$524.11","+0.72%",True),
    ("BTC", "$67,421","+3.15%",True), ("ETH", "$3,842", "+2.08%",True),
    ("AMX", "$14.23", "-1.24%",False),("BIMBO","$88.12","+0.88%",True),
    ("QQQ", "$447.23","+1.45%",True), ("GLD", "$212.45","-0.19%",False),
    ("JPM", "$213.67","+0.63%",True), ("CEMEX","$7.84","-2.11%",False),
    ("WALMEX","$68.40","+1.33%",True),("IPC","$55,242","+0.61%",True),
]
tape_inner = ""
for sym, price, pct, up in TICKERS * 5:
    col = "#00d4aa" if up else "#ff3b5c"
    arr = "▲" if up else "▼"
    tape_inner += (
        f'<span style="margin:0 28px;white-space:nowrap;">'
        f'<span style="color:#8892a4;font-size:11px;letter-spacing:1px;">{sym} </span>'
        f'<span style="color:#c9d1d9;font-size:11px;">{price} </span>'
        f'<span style="color:{col};font-size:11px;">{arr} {pct}</span>'
        f'</span>'
    )

# ── CSS + fondo animado ────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');

  :root {{
    --bg:      #0a0c10;
    --surface: #111419;
    --border:  #1e2530;
    --accent:  #00d4aa;
    --red:     #ff3b5c;
    --text:    #c9d1d9;
    --muted:   #4a5568;
  }}

  /* ── Reset Streamlit ── */
  html, body {{
    background-color: var(--bg) !important;
    margin: 0; padding: 0;
  }}
  [data-testid="stAppViewContainer"] {{
    background: transparent !important;
  }}
  [data-testid="stMain"] {{
    background: transparent !important;
  }}
  [data-testid="stSidebar"],
  [data-testid="collapsedControl"],
  [data-testid="stDecoration"],
  header[data-testid="stHeader"] {{
    display: none !important;
  }}
  .block-container {{
    padding-top: 0 !important;
    max-width: 500px !important;
  }}

  /* ── Fondo fijo ── */
  .qc-bg {{
    position: fixed;
    inset: 0;
    z-index: 0;
    background: #0a0c10;
    overflow: hidden;
  }}

  /* Grid */
  .qc-grid {{
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(0,212,170,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0,212,170,0.04) 1px, transparent 1px);
    background-size: 60px 60px;
  }}

  /* Gradiente central para legibilidad */
  .qc-vignette {{
    position: absolute;
    inset: 0;
    background: radial-gradient(
      ellipse 70% 80% at 50% 50%,
      rgba(10,12,16,0.88) 0%,
      rgba(10,12,16,0.55) 60%,
      transparent 100%
    );
  }}

  /* ── Velas ── */
  .qc-c {{
    position: absolute;
    bottom: 56px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: center;
    transform-origin: bottom center;
    animation: qcPulse linear infinite alternate;
  }}
  @keyframes qcPulse {{
    0%   {{ transform: scaleY(0.45); }}
    100% {{ transform: scaleY(1.05); }}
  }}

  /* ── Ticker tape ── */
  .qc-tape-wrap {{
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 36px;
    background: rgba(17,20,25,0.85);
    border-top: 1px solid var(--border);
    display: flex;
    align-items: center;
    overflow: hidden;
    z-index: 2;
  }}
  .qc-tape {{
    display: flex;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
    animation: tickerScroll 80s linear infinite;
  }}
  @keyframes tickerScroll {{
    0%   {{ transform: translateX(0); }}
    100% {{ transform: translateX(-50%); }}
  }}

  /* ── Líneas de precio flotantes ── */
  .qc-line {{
    position: absolute;
    left: 0;
    right: 0;
    height: 1px;
    opacity: 0.18;
    animation: linePulse ease-in-out infinite alternate;
  }}
  .qc-line-1 {{
    top: 22%;
    background: linear-gradient(90deg, transparent 0%, #00d4aa 30%, #00d4aa 70%, transparent 100%);
    animation-duration: 4.2s;
    animation-delay: 0s;
  }}
  .qc-line-2 {{
    top: 38%;
    background: linear-gradient(90deg, transparent 0%, #0090ff 30%, #0090ff 70%, transparent 100%);
    animation-duration: 5.8s;
    animation-delay: -2s;
  }}
  .qc-line-3 {{
    top: 60%;
    background: linear-gradient(90deg, transparent 0%, #a855f7 20%, #a855f7 80%, transparent 100%);
    animation-duration: 3.5s;
    animation-delay: -1s;
  }}
  @keyframes linePulse {{
    0%   {{ opacity: 0.06; transform: scaleX(0.7); }}
    100% {{ opacity: 0.22; transform: scaleX(1); }}
  }}

  /* ── Puntos flotantes ── */
  .qc-dot {{
    position: absolute;
    width: 3px;
    height: 3px;
    border-radius: 50%;
    background: #00d4aa;
    opacity: 0.25;
    animation: floatUp linear infinite;
  }}
  @keyframes floatUp {{
    0%   {{ transform: translateY(0);     opacity: 0.25; }}
    100% {{ transform: translateY(-100vh); opacity: 0; }}
  }}

  /* ── Content layer ── */
  .qc-content {{
    position: relative;
    z-index: 10;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px 80px 20px;
  }}

  /* ── Logo ── */
  .qc-logo-wrap {{
    text-align: center;
    margin-bottom: 32px;
  }}
  .qc-logo-main {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 56px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 8px;
    line-height: 1;
    text-shadow: 0 0 40px rgba(0,212,170,0.3);
  }}
  .qc-logo-sub {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 5px;
    margin-top: 4px;
  }}
  .qc-logo-desc {{
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    color: #5a6478;
    margin-top: 12px;
    letter-spacing: 0.3px;
  }}

  /* ── Card ── */
  .auth-card {{
    background: rgba(17, 20, 25, 0.90);
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid rgba(0,212,170,0.12);
    border-radius: 16px;
    padding: 36px 40px 32px 40px;
    width: 100%;
    max-width: 460px;
    box-shadow:
      0 0 0 1px rgba(0,212,170,0.04),
      0 8px 60px rgba(0,0,0,0.7),
      0 0 80px rgba(0,212,170,0.03);
  }}

  /* ── Tabs ── */
  div[data-baseweb="tab-list"] {{
    background: rgba(6,8,16,0.8) !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: 1px solid var(--border) !important;
    margin-bottom: 28px !important;
    gap: 0 !important;
  }}
  div[data-baseweb="tab"] {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    color: var(--muted) !important;
    border-radius: 7px !important;
    padding: 10px 0 !important;
    flex: 1 !important;
    justify-content: center !important;
    transition: color 0.2s !important;
  }}
  div[data-baseweb="tab"][aria-selected="true"] {{
    background: rgba(0,212,170,0.08) !important;
    color: var(--accent) !important;
    border-bottom: none !important;
  }}
  div[data-baseweb="tab-highlight"],
  div[data-baseweb="tab-border"] {{ display: none !important; }}

  /* ── Inputs ── */
  .stTextInput > div > div > input {{
    background: rgba(6,8,16,0.9) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
  }}
  .stTextInput > div > div > input:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0,212,170,0.10) !important;
    outline: none !important;
  }}
  label[data-testid="stWidgetLabel"] p {{
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    color: var(--muted) !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
  }}

  /* ── Botón ── */
  .stButton > button {{
    background: var(--accent) !important;
    border: none !important;
    color: #0a0c10 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    border-radius: 8px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    margin-top: 6px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 20px rgba(0,212,170,0.15) !important;
  }}
  .stButton > button:hover {{
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(0,212,170,0.28) !important;
  }}
  .stButton > button:active {{
    transform: translateY(0) !important;
  }}

  /* ── Alerts ── */
  .stAlert {{
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    border: none !important;
    background: rgba(6,8,16,0.8) !important;
  }}
</style>

<!-- ── FONDO ANIMADO ─────────────────────────────────── -->
<div class="qc-bg">

  <!-- Grid -->
  <div class="qc-grid"></div>

  <!-- Líneas de precio -->
  <div class="qc-line qc-line-1"></div>
  <div class="qc-line qc-line-2"></div>
  <div class="qc-line qc-line-3"></div>

  <!-- Velas -->
  {candles_html}

  <!-- Puntos flotantes -->
  <div class="qc-dot" style="left:12%;animation-duration:12s;animation-delay:-3s;"></div>
  <div class="qc-dot" style="left:27%;animation-duration:18s;animation-delay:-7s;"></div>
  <div class="qc-dot" style="left:45%;animation-duration:15s;animation-delay:-1s;"></div>
  <div class="qc-dot" style="left:63%;animation-duration:20s;animation-delay:-9s;"></div>
  <div class="qc-dot" style="left:78%;animation-duration:13s;animation-delay:-5s;"></div>
  <div class="qc-dot" style="left:91%;animation-duration:16s;animation-delay:-11s;"></div>

  <!-- Viñeta central -->
  <div class="qc-vignette"></div>

  <!-- Ticker tape -->
  <div class="qc-tape-wrap">
    <div class="qc-tape">
      {tape_inner}
      {tape_inner}
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

# ── Credentials ────────────────────────────────────────────────────────────────
CREDS_FILE = Path(__file__).parent / "credentials.yaml"

def load_config():
    if CREDS_FILE.exists():
        with open(CREDS_FILE) as f:
            return yaml.load(f, Loader=SafeLoader)
    return {
        "credentials": {"usernames": {}},
        "cookie": {
            "expiry_days": 30,
            "key": "qc_analytics_secret_key_2025",
            "name": "qc_auth",
        },
        "preauthorized": {"emails": []},
    }

def save_config(cfg):
    with open(CREDS_FILE, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)

config      = load_config()
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ── Logo ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="qc-logo-wrap">
  <div class="qc-logo-main">QC</div>
  <div class="qc-logo-sub">ANALYTICS · TERMINAL</div>
  <div class="qc-logo-desc">Analiza cualquier acción en segundos, en español.</div>
</div>
""", unsafe_allow_html=True)

# ── Card ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="auth-card">', unsafe_allow_html=True)

tab_login, tab_register = st.tabs(["  INICIAR SESIÓN  ", "  CREAR CUENTA  "])

# ══ LOGIN ══════════════════════════════════════════════════════════════════════
with tab_login:
    try:
        authenticator.login(location="main", key="login_form")
    except Exception as e:
        st.error(f"Error: {e}")

    status = st.session_state.get("authentication_status")
    if status is True:
        st.switch_page("pages/dashboard.py")
    elif status is False:
        st.error("⚠ Usuario o contraseña incorrectos.")

# ══ REGISTRO ═══════════════════════════════════════════════════════════════════
with tab_register:
    try:
        result = authenticator.register_user(
            location="main",
            key="register_form",
            fields={
                "Form name":       "",
                "Name":            "Nombre completo",
                "Email":           "Correo electrónico",
                "Username":        "Usuario",
                "Password":        "Contraseña",
                "Repeat password": "Confirmar contraseña",
                "Register":        "CREAR CUENTA →",
            },
        )
        if result and result[1]:
            save_config(config)
            st.success("✅ Cuenta creada. Inicia sesión arriba.")
    except Exception as e:
        err = str(e).lower()
        if "already" in err or "registered" in err or "existe" in err:
            st.warning("⚠ Ese usuario o correo ya existe.")
        else:
            st.error(f"Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)
