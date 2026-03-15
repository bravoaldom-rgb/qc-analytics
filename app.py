import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
from pathlib import Path

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QC Analytics",
    page_icon="⬛",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap');

  :root {
    --bg:      #0a0c10;
    --surface: #111419;
    --border:  #1e2530;
    --accent:  #00d4aa;
    --red:     #ff3b5c;
    --text:    #c9d1d9;
    --muted:   #4a5568;
  }

  html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif;
  }
  [data-testid="stSidebar"] { display: none !important; }
  [data-testid="collapsedControl"] { display: none !important; }
  header[data-testid="stHeader"] { background: transparent !important; }

  /* Card centrada */
  .auth-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 40px 44px;
    max-width: 440px;
    margin: 60px auto 0 auto;
  }
  .auth-logo {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 3px;
    text-align: center;
    margin-bottom: 4px;
  }
  .auth-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    text-align: center;
    letter-spacing: 2px;
    margin-bottom: 32px;
  }
  .auth-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0;
  }
  .badge-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 32px;
    flex-wrap: wrap;
  }
  .badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    border: 1px solid var(--border);
    padding: 4px 10px;
    border-radius: 3px;
    letter-spacing: 1px;
  }

  /* Inputs */
  .stTextInput > div > div > input,
  .stTextInput > div > div > input:focus {
    background: #060810 !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 13px !important;
    border-radius: 6px !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
  }
  label[data-testid="stWidgetLabel"] p {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 10px !important;
    color: var(--muted) !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
  }

  /* Botón principal */
  .stButton > button {
    background: var(--accent) !important;
    border: none !important;
    color: #0a0c10 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    border-radius: 6px !important;
    padding: 10px 24px !important;
    width: 100% !important;
    transition: opacity 0.15s !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }

  /* Tabs */
  div[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
  }
  div[data-baseweb="tab"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 1px !important;
    color: var(--muted) !important;
    padding: 10px 20px !important;
  }
  div[data-baseweb="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
  }
  .stAlert { border-radius: 6px !important; font-family: 'JetBrains Mono', monospace !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

# ── Archivo de credenciales ────────────────────────────────────────────────────
CREDS_FILE = Path(__file__).parent / "credentials.yaml"

def load_config():
    if CREDS_FILE.exists():
        with open(CREDS_FILE) as f:
            return yaml.load(f, Loader=SafeLoader)
    # Config vacía inicial
    return {
        "credentials": {"usernames": {}},
        "cookie": {"expiry_days": 30, "key": "qc_analytics_secret_key_2024", "name": "qc_auth"},
        "preauthorized": {"emails": []}
    }

def save_config(config):
    with open(CREDS_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

config = load_config()

# ── Autenticador ───────────────────────────────────────────────────────────────
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ── Si ya hay sesión activa, ir directo al dashboard ──────────────────────────
if st.session_state.get("authentication_status") is True:
    st.switch_page("pages/dashboard.py")

# ── Layout principal ───────────────────────────────────────────────────────────
st.markdown('<div class="auth-card">', unsafe_allow_html=True)
st.markdown('<div class="auth-logo">QC</div>', unsafe_allow_html=True)
st.markdown('<div class="auth-sub">ANALYTICS · TERMINAL</div>', unsafe_allow_html=True)

tab_login, tab_register = st.tabs(["  INICIAR SESIÓN  ", "  REGISTRARSE  "])

# ══ TAB LOGIN ══════════════════════════════════════════════════════════════════
with tab_login:
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        authenticator.login(location="main", key="login_form")
    except Exception as e:
        st.error(f"Error: {e}")

    auth_status = st.session_state.get("authentication_status")

    if auth_status is True:
        # Redirigir automáticamente sin necesitar botón
        st.switch_page("pages/dashboard.py")

    elif auth_status is False:
        st.error("Usuario o contraseña incorrectos")

    else:
        st.markdown("""
        <div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#4a5568;margin-top:8px;">
        Ingresa tus credenciales para acceder
        </div>
        """, unsafe_allow_html=True)

# ══ TAB REGISTRO ═══════════════════════════════════════════════════════════════
with tab_register:
    st.markdown("<br>", unsafe_allow_html=True)
    try:
        reg_result = authenticator.register_user(
            location="main",
            key="register_form",
            fields={
                "Form name":        "Crear cuenta",
                "Email":            "Correo electrónico",
                "Username":         "Usuario",
                "Password":         "Contraseña",
                "Repeat password":  "Confirmar contraseña",
                "Register":         "CREAR CUENTA",
            }
        )
        # streamlit-authenticator ≥0.3 devuelve (email, username, name)
        if reg_result and reg_result[1]:
            save_config(config)
            st.success("Cuenta creada. Ya puedes iniciar sesión.")
    except Exception as e:
        err = str(e)
        if "already" in err.lower() or "existe" in err.lower():
            st.warning("Ese usuario o correo ya está registrado.")
        else:
            st.error(f"Error al registrar: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# Badges
st.markdown("""
<div class="badge-row">
  <span class="badge">DATOS: YAHOO FINANCE</span>
  <span class="badge">IA: CLAUDE</span>
  <span class="badge">v0.1</span>
</div>
""", unsafe_allow_html=True)
