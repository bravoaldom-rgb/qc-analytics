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

# ── Redirect si ya hay sesión ──────────────────────────────────────────────────
if st.session_state.get("authentication_status") is True:
    st.switch_page("pages/dashboard.py")

# ── Toggle entre login / registro ─────────────────────────────────────────────
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  :root {
    --bg:       #080a0f;
    --surface:  #0f1117;
    --border:   rgba(255,255,255,0.07);
    --accent:   #00d4aa;
    --text:     #f1f3f5;
    --sub:      #6b7280;
    --error:    #f87171;
  }

  *, *::before, *::after { box-sizing: border-box; }

  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"] {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
    margin: 0; padding: 0;
  }

  /* Ocultar chrome de Streamlit */
  [data-testid="stSidebar"],
  [data-testid="collapsedControl"],
  [data-testid="stDecoration"],
  header[data-testid="stHeader"],
  [data-testid="stToolbar"],
  #MainMenu { display: none !important; }

  .block-container {
    max-width: 420px !important;
    padding: 0 24px 60px 24px !important;
    margin: 0 auto !important;
  }

  /* Glow de fondo muy sutil */
  [data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    top: -30%;
    left: 50%;
    transform: translateX(-50%);
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(0,212,170,0.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
  }

  /* ── Logo ── */
  .logo-block {
    text-align: center;
    padding: 64px 0 44px 0;
  }
  .logo-mark {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px; height: 44px;
    background: rgba(0,212,170,0.10);
    border: 1px solid rgba(0,212,170,0.20);
    border-radius: 12px;
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 1px;
    margin-bottom: 20px;
  }
  .logo-title {
    font-size: 22px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.4px;
    margin-bottom: 6px;
  }
  .logo-sub {
    font-size: 14px;
    font-weight: 400;
    color: var(--sub);
    letter-spacing: 0;
  }

  /* ── Inputs ── */
  .stTextInput { margin-bottom: 2px !important; }

  .stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    width: 100% !important;
  }
  .stTextInput > div > div > input::placeholder {
    color: #374151 !important;
  }
  .stTextInput > div > div > input:focus {
    border-color: rgba(0,212,170,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,212,170,0.08) !important;
    outline: none !important;
    background: #0d1018 !important;
  }

  /* Labels */
  label[data-testid="stWidgetLabel"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #9ca3af !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    margin-bottom: 6px !important;
  }

  /* ── Botón primario (login) ── */
  .stButton > button {
    background: var(--accent) !important;
    border: none !important;
    color: #050810 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: -0.1px !important;
    border-radius: 10px !important;
    padding: 13px 20px !important;
    width: 100% !important;
    margin-top: 10px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
  }
  .stButton > button:hover {
    background: #00bfa0 !important;
    box-shadow: 0 4px 24px rgba(0,212,170,0.22) !important;
    transform: translateY(-1px) !important;
  }
  .stButton > button:active { transform: translateY(0) !important; }

  /* ── Botón registro (outline) ── */
  .stFormSubmitButton > button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    letter-spacing: -0.1px !important;
    border-radius: 10px !important;
    padding: 13px 20px !important;
    width: 100% !important;
    margin-top: 10px !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
  }
  .stFormSubmitButton > button:hover {
    border-color: rgba(255,255,255,0.16) !important;
    background: rgba(255,255,255,0.03) !important;
  }

  /* ── Switch link ── */
  .switch-link {
    text-align: center;
    margin-top: 24px;
    font-size: 13px;
    color: var(--sub);
  }
  .switch-link a, .switch-link strong {
    color: var(--accent) !important;
    font-weight: 500;
    text-decoration: none;
    cursor: pointer;
  }

  /* ── Divider ── */
  .soft-divider {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 20px 0;
  }
  .soft-divider span {
    flex: 1;
    height: 1px;
    background: var(--border);
  }
  .soft-divider p {
    font-size: 12px;
    color: #374151;
    white-space: nowrap;
  }

  /* ── Alerts ── */
  [data-testid="stAlert"] {
    background: rgba(248,113,113,0.07) !important;
    border: 1px solid rgba(248,113,113,0.18) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    color: #fca5a5 !important;
  }
  [data-testid="stAlert"][data-baseweb="notification"] {
    padding: 12px 14px !important;
  }

  /* Éxito */
  .success-box {
    background: rgba(0,212,170,0.07);
    border: 1px solid rgba(0,212,170,0.18);
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 13px;
    color: var(--accent);
    margin-top: 12px;
    text-align: center;
  }

  /* Footer */
  .auth-footer {
    text-align: center;
    font-size: 11px;
    color: #1f2937;
    margin-top: 48px;
    letter-spacing: 0.3px;
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
        "cookie": {"expiry_days": 30, "key": "qc_secret_2025", "name": "qc_auth"},
        "preauthorized": {"emails": []},
    }

def save_config(cfg):
    with open(CREDS_FILE, "w") as f:
        yaml.dump(cfg, f, default_flow_style=False)

config        = load_config()
authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
)

# ── Logo ───────────────────────────────────────────────────────────────────────
if st.session_state.show_register:
    headline = "Crea tu cuenta"
    subline  = "Empieza a invertir con inteligencia."
else:
    headline = "Bienvenido de vuelta"
    subline  = "Ingresa a tu terminal financiera."

st.markdown(f"""
<div class="logo-block">
  <div class="logo-mark">QC</div>
  <div class="logo-title">{headline}</div>
  <div class="logo-sub">{subline}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FORMULARIO LOGIN
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.show_register:
    try:
        authenticator.login(location="main", key="login_form")
    except Exception as e:
        st.error(f"Error: {e}")

    status = st.session_state.get("authentication_status")
    if status is True:
        st.switch_page("pages/dashboard.py")
    elif status is False:
        st.error("Usuario o contraseña incorrectos.")

    st.markdown('<div class="switch-link">¿No tienes cuenta?</div>', unsafe_allow_html=True)
    if st.button("Crear cuenta gratis →", key="go_register"):
        st.session_state.show_register = True
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# FORMULARIO REGISTRO
# ══════════════════════════════════════════════════════════════════════════════
else:
    with st.form("register_form", clear_on_submit=True):
        nombre  = st.text_input("Nombre completo")
        usuario = st.text_input("Usuario")
        correo  = st.text_input("Correo electrónico")
        pwd     = st.text_input("Contraseña",          type="password")
        pwd2    = st.text_input("Confirmar contraseña", type="password")
        submit  = st.form_submit_button("Crear cuenta")

    if submit:
        if not all([nombre, usuario, correo, pwd, pwd2]):
            st.error("Completa todos los campos.")
        elif pwd != pwd2:
            st.error("Las contraseñas no coinciden.")
        elif len(pwd) < 6:
            st.error("La contraseña debe tener al menos 6 caracteres.")
        elif usuario in config["credentials"]["usernames"]:
            st.error("Ese nombre de usuario ya existe.")
        elif any(u["email"] == correo for u in config["credentials"]["usernames"].values()):
            st.error("Ese correo ya está registrado.")
        else:
            hashed = stauth.Hasher([pwd]).generate()[0]
            config["credentials"]["usernames"][usuario] = {
                "name": nombre, "email": correo, "password": hashed,
            }
            save_config(config)
            st.markdown('<div class="success-box">✓ Cuenta creada. Ya puedes iniciar sesión.</div>', unsafe_allow_html=True)

    st.markdown('<div class="switch-link">¿Ya tienes cuenta?</div>', unsafe_allow_html=True)
    if st.button("← Iniciar sesión", key="go_login"):
        st.session_state.show_register = False
        st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="auth-footer">QC Analytics · Datos: Yahoo Finance · IA: Claude</div>', unsafe_allow_html=True)
