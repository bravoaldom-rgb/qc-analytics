import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import base64
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

# ── Toggle ────────────────────────────────────────────────────────────────────
if "show_register" not in st.session_state:
    st.session_state.show_register = False

# ── Logo: carga desde assets/logo.png si existe ───────────────────────────────
def get_logo_html():
    logo_path = Path(__file__).parent / "assets" / "logo.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f'<img src="data:image/png;base64,{b64}" class="logo-img" />'
    # Fallback: marca de texto
    return '<div class="logo-mark">QC</div>'

# ── Ticker tape (mercado de valores en la parte superior) ──────────────────────
TICKERS = [
    ("S&P 500","5,248","▲ +0.72%","up"), ("NASDAQ","18,421","▲ +1.14%","up"),
    ("DOW JONES","39,170","▼ -0.18%","dn"), ("IPC MX","55,242","▲ +0.61%","up"),
    ("AAPL","$182.63","▲ +2.34%","up"), ("MSFT","$415.21","▲ +1.12%","up"),
    ("TSLA","$234.15","▼ -0.87%","dn"), ("NVDA","$875.42","▲ +4.21%","up"),
    ("AMZN","$192.87","▲ +0.94%","up"), ("META","$521.33","▲ +1.67%","up"),
    ("GOOG","$172.54","▼ -0.31%","dn"), ("BTC","$67,421","▲ +3.15%","up"),
    ("ETH","$3,842","▲ +2.08%","up"),   ("AMX","$14.23","▼ -1.24%","dn"),
    ("BIMBO","$88.12","▲ +0.88%","up"), ("CEMEX","$7.84","▼ -2.11%","dn"),
    ("WALMEX","$68.40","▲ +1.33%","up"),("GOLD","$2,341","▲ +0.52%","up"),
    ("WTI","$82.41","▼ -0.67%","dn"),   ("EUR/USD","1.0821","▲ +0.11%","up"),
]
tape_items = ""
for sym, price, chg, direction in TICKERS * 4:
    col = "#22d3a5" if direction == "up" else "#f87171"
    tape_items += (
        f'<span class="ti">'
        f'<span class="ti-sym">{sym}</span>'
        f'<span class="ti-price">{price}</span>'
        f'<span style="color:{col};font-size:11px;">{chg}</span>'
        f'</span>'
        f'<span class="ti-sep">·</span>'
    )

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  :root {{
    --bg:      #07090e;
    --surface: #0d1017;
    --border:  rgba(255,255,255,0.07);
    --accent:  #22d3a5;
    --text:    #f1f3f5;
    --sub:     #6b7280;
    --red:     #f87171;
  }}

  *, *::before, *::after {{ box-sizing: border-box; }}

  html, body,
  [data-testid="stAppViewContainer"],
  [data-testid="stMain"] {{
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
    margin: 0; padding: 0;
  }}

  [data-testid="stSidebar"], [data-testid="collapsedControl"],
  [data-testid="stDecoration"], header[data-testid="stHeader"],
  [data-testid="stToolbar"], #MainMenu {{ display: none !important; }}

  .block-container {{
    max-width: 420px !important;
    padding: 0 20px 60px 20px !important;
    margin: 0 auto !important;
  }}

  /* Glow sutil de fondo */
  [data-testid="stAppViewContainer"]::before {{
    content: '';
    position: fixed;
    top: -20%;
    left: 50%;
    transform: translateX(-50%);
    width: 700px; height: 700px;
    background: radial-gradient(circle, rgba(34,211,165,0.05) 0%, transparent 65%);
    pointer-events: none;
    z-index: 0;
  }}

  /* ── TICKER TAPE (parte superior) ── */
  .ticker-bar {{
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 34px;
    background: rgba(13,16,23,0.97);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    display: flex;
    align-items: center;
    overflow: hidden;
    z-index: 1000;
  }}
  .ticker-track {{
    display: flex;
    align-items: center;
    white-space: nowrap;
    animation: tickRoll 90s linear infinite;
    font-family: 'Inter', sans-serif;
  }}
  @keyframes tickRoll {{
    0%   {{ transform: translateX(0); }}
    100% {{ transform: translateX(-50%); }}
  }}
  .ti {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0 18px;
  }}
  .ti-sym {{
    font-size: 11px;
    font-weight: 600;
    color: #9ca3af;
    letter-spacing: 0.5px;
  }}
  .ti-price {{
    font-size: 11px;
    font-weight: 500;
    color: var(--text);
  }}
  .ti-sep {{
    color: rgba(255,255,255,0.1);
    font-size: 14px;
  }}

  /* ── LOGO ── */
  .logo-block {{
    text-align: center;
    padding: 72px 0 36px 0;
    position: relative; z-index: 1;
  }}
  .logo-img {{
    width: 90px;
    height: 90px;
    object-fit: contain;
    margin-bottom: 16px;
    /* quita el fondo blanco del PNG */
    mix-blend-mode: lighten;
    filter: drop-shadow(0 0 20px rgba(34,211,165,0.2));
  }}
  .logo-mark {{
    display: inline-flex;
    align-items: center; justify-content: center;
    width: 52px; height: 52px;
    background: rgba(34,211,165,0.08);
    border: 1px solid rgba(34,211,165,0.20);
    border-radius: 14px;
    font-size: 18px; font-weight: 700;
    color: var(--accent);
    margin-bottom: 16px;
  }}
  .logo-title {{
    font-size: 22px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.4px;
    margin-bottom: 5px;
  }}
  .logo-sub {{
    font-size: 14px;
    font-weight: 400;
    color: var(--sub);
  }}

  /* ── INPUTS ── */
  .stTextInput > div > div > input {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 400 !important;
    border-radius: 10px !important;
    padding: 12px 14px !important;
    transition: border-color .15s, box-shadow .15s !important;
  }}
  .stTextInput > div > div > input:focus {{
    border-color: rgba(34,211,165,0.45) !important;
    box-shadow: 0 0 0 3px rgba(34,211,165,0.08) !important;
    outline: none !important;
    background: #0a0d13 !important;
  }}
  label[data-testid="stWidgetLabel"] p {{
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #9ca3af !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    margin-bottom: 5px !important;
  }}

  /* ── BOTÓN LOGIN (sólido) ── */
  .stButton > button {{
    background: var(--accent) !important;
    border: none !important;
    color: #04120d !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: -0.1px !important;
    border-radius: 10px !important;
    padding: 13px 20px !important;
    width: 100% !important;
    margin-top: 10px !important;
    transition: all .15s ease !important;
  }}
  .stButton > button:hover {{
    background: #1fc799 !important;
    box-shadow: 0 4px 24px rgba(34,211,165,0.22) !important;
    transform: translateY(-1px) !important;
  }}
  .stButton > button:active {{ transform: translateY(0) !important; }}

  /* ── BOTÓN REGISTRO (outline) ── */
  .stFormSubmitButton > button {{
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    border-radius: 10px !important;
    padding: 13px 20px !important;
    width: 100% !important;
    margin-top: 10px !important;
    transition: all .15s ease !important;
  }}
  .stFormSubmitButton > button:hover {{
    border-color: rgba(255,255,255,0.18) !important;
    background: rgba(255,255,255,0.03) !important;
  }}

  /* ── ALERTS ── */
  [data-testid="stAlert"] {{
    background: rgba(248,113,113,0.07) !important;
    border: 1px solid rgba(248,113,113,0.18) !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
  }}
  .success-box {{
    background: rgba(34,211,165,0.07);
    border: 1px solid rgba(34,211,165,0.18);
    border-radius: 10px;
    padding: 12px 14px;
    font-size: 13px;
    color: var(--accent);
    margin-top: 12px;
    text-align: center;
  }}

  /* ── SWITCH LINK ── */
  .switch-row {{
    text-align: center;
    margin-top: 22px;
    font-size: 13px;
    color: var(--sub);
    position: relative; z-index: 1;
  }}

  /* Footer */
  .auth-footer {{
    text-align: center;
    font-size: 11px;
    color: #1f2937;
    margin-top: 44px;
    position: relative; z-index: 1;
  }}
</style>

<!-- TICKER TAPE SUPERIOR -->
<div class="ticker-bar">
  <div class="ticker-track">
    {tape_items}
    {tape_items}
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

# ── Logo + headline ────────────────────────────────────────────────────────────
headline = "Crea tu cuenta" if st.session_state.show_register else "Bienvenido de vuelta"
subline  = "Empieza a invertir con inteligencia." if st.session_state.show_register else "Ingresa a tu terminal financiera."

st.markdown(f"""
<div class="logo-block">
  {get_logo_html()}
  <div class="logo-title">{headline}</div>
  <div class="logo-sub">{subline}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INICIAR SESIÓN
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

    st.markdown('<div class="switch-row">¿No tienes cuenta?</div>', unsafe_allow_html=True)
    if st.button("Registrarse →", key="go_register"):
        st.session_state.show_register = True
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# REGISTRARSE
# ══════════════════════════════════════════════════════════════════════════════
else:
    with st.form("register_form", clear_on_submit=True):
        nombre  = st.text_input("Nombre completo")
        usuario = st.text_input("Usuario")
        correo  = st.text_input("Correo electrónico")
        pwd     = st.text_input("Contraseña",           type="password")
        pwd2    = st.text_input("Confirmar contraseña", type="password")
        submit  = st.form_submit_button("Registrarse")

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

    st.markdown('<div class="switch-row">¿Ya tienes cuenta?</div>', unsafe_allow_html=True)
    if st.button("← Iniciar sesión", key="go_login"):
        st.session_state.show_register = False
        st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="auth-footer">QC Analytics · Datos: Yahoo Finance · IA: Claude</div>', unsafe_allow_html=True)
