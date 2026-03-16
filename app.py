import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QC Analytics",
    page_icon="⬛",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Redirect inmediato si ya hay sesión ────────────────────────────────────────
if st.session_state.get("authentication_status") is True:
    st.switch_page("pages/dashboard.py")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');

  :root {
    --bg:      #0a0c10;
    --surface: #111419;
    --surface2:#161b23;
    --border:  #1e2530;
    --accent:  #00d4aa;
    --red:     #ff3b5c;
    --text:    #c9d1d9;
    --muted:   #4a5568;
  }

  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
  }
  [data-testid="stSidebar"],
  [data-testid="collapsedControl"] { display: none !important; }
  header[data-testid="stHeader"]   { background: transparent !important; }
  [data-testid="stDecoration"]     { display: none !important; }
  .block-container { padding-top: 2rem !important; }

  /* ── Hero ── */
  .hero {
    text-align: center;
    padding: 48px 0 36px 0;
  }
  .hero-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 52px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 6px;
    line-height: 1;
  }
  .hero-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 4px;
    margin-top: 6px;
  }
  .hero-desc {
    font-family: 'Inter', sans-serif;
    font-size: 15px;
    color: #6b7a90;
    margin-top: 14px;
    line-height: 1.6;
  }

  /* ── Card ── */
  .auth-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 36px 40px 32px 40px;
    max-width: 460px;
    margin: 0 auto 32px auto;
    box-shadow: 0 4px 32px rgba(0,0,0,0.4);
  }

  /* ── Tabs ── */
  div[data-baseweb="tab-list"] {
    background: var(--surface2) !important;
    border-radius: 8px !important;
    padding: 4px !important;
    border: none !important;
    margin-bottom: 24px !important;
    gap: 0 !important;
  }
  div[data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    color: var(--muted) !important;
    border-radius: 6px !important;
    padding: 10px 20px !important;
    flex: 1 !important;
    justify-content: center !important;
  }
  div[data-baseweb="tab"][aria-selected="true"] {
    background: var(--surface) !important;
    color: var(--accent) !important;
    border-bottom: none !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.3) !important;
  }
  div[data-baseweb="tab-highlight"] { display: none !important; }
  div[data-baseweb="tab-border"]    { display: none !important; }

  /* ── Inputs ── */
  .stTextInput > div > div > input {
    background: #060810 !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    padding: 10px 14px !important;
    transition: border-color 0.2s !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(0,212,170,0.12) !important;
    outline: none !important;
  }
  label[data-testid="stWidgetLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    color: var(--muted) !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
  }

  /* ── Botón principal ── */
  .stButton > button {
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
    transition: all 0.2s !important;
    margin-top: 8px !important;
  }
  .stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(0,212,170,0.25) !important;
  }
  .stButton > button:active { transform: translateY(0) !important; }

  /* ── Alerts ── */
  .stAlert {
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    border: none !important;
  }

  /* ── Features row ── */
  .features {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin: 28px 0 0 0;
    flex-wrap: wrap;
  }
  .feature-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 6px 14px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1px;
  }
  .feature-dot {
    width: 6px; height: 6px;
    background: var(--accent);
    border-radius: 50%;
    flex-shrink: 0;
  }

  /* ── Footer ── */
  .auth-footer {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 1px;
    margin-top: 20px;
    opacity: 0.6;
  }
</style>
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

config = load_config()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-logo">QC</div>
  <div class="hero-tag">ANALYTICS · TERMINAL</div>
  <div class="hero-desc">
    Analiza cualquier acción en segundos.<br>
    Datos reales + inteligencia artificial, en español.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Auth card ──────────────────────────────────────────────────────────────────
st.markdown('<div class="auth-card">', unsafe_allow_html=True)

tab_login, tab_register = st.tabs(["  INICIAR SESIÓN  ", "  CREAR CUENTA  "])

# ══ LOGIN ══════════════════════════════════════════════════════════════════════
with tab_login:
    try:
        authenticator.login(location="main", key="login_form")
    except Exception as e:
        st.error(f"Error: {e}")

    auth_status = st.session_state.get("authentication_status")

    if auth_status is True:
        st.switch_page("pages/dashboard.py")
    elif auth_status is False:
        st.error("⚠ Usuario o contraseña incorrectos. Intenta de nuevo.")
    else:
        st.markdown("""
        <div style="
          font-family:'JetBrains Mono',monospace;
          font-size:11px;color:#4a5568;
          margin-top:6px;text-align:center;
        ">
          ¿Aún no tienes cuenta? Usa la pestaña <strong style="color:#00d4aa;">CREAR CUENTA</strong>
        </div>
        """, unsafe_allow_html=True)

# ══ REGISTRO ═══════════════════════════════════════════════════════════════════
with tab_register:
    st.markdown("""
    <div style="
      font-family:'JetBrains Mono',monospace;
      font-size:10px;color:#4a5568;
      letter-spacing:1px;margin-bottom:16px;
    ">
      GRATIS · SIN TARJETA · ACCESO INMEDIATO
    </div>
    """, unsafe_allow_html=True)
    try:
        reg_result = authenticator.register_user(
            location="main",
            key="register_form",
            fields={
                "Form name":       "Nueva cuenta",
                "Email":           "Correo electrónico",
                "Username":        "Nombre de usuario",
                "Password":        "Contraseña",
                "Repeat password": "Confirmar contraseña",
                "Register":        "CREAR MI CUENTA →",
            },
        )
        if reg_result and reg_result[1]:
            save_config(config)
            st.success("✅ Cuenta creada. Ya puedes iniciar sesión en la pestaña anterior.")
    except Exception as e:
        err = str(e).lower()
        if "already" in err or "existe" in err or "registered" in err:
            st.warning("⚠ Ese usuario o correo ya está registrado.")
        else:
            st.error(f"Error al registrar: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# ── Features ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="features">
  <div class="feature-pill"><div class="feature-dot"></div>GRÁFICAS EN TIEMPO REAL</div>
  <div class="feature-pill"><div class="feature-dot"></div>ANÁLISIS CON IA</div>
  <div class="feature-pill"><div class="feature-dot"></div>FUNDAMENTALES</div>
  <div class="feature-pill"><div class="feature-dot"></div>COMPARAR ACTIVOS</div>
</div>
""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="auth-footer">
  QC ANALYTICS v0.1 · DATOS: YAHOO FINANCE · IA: CLAUDE
</div>
""", unsafe_allow_html=True)
