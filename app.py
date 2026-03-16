import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from pathlib import Path
import base64

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QC Analytics",
    page_icon="⬛",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Guards ─────────────────────────────────────────────────────────────────────
if st.session_state.get("authentication_status") is True:
    st.switch_page("pages/dashboard.py")

if "show_register" not in st.session_state:
    st.session_state.show_register = False

# ── Logo ───────────────────────────────────────────────────────────────────────
def get_logo_html():
    p = Path(__file__).parent / "assets" / "logo.png"
    if p.exists():
        b64 = base64.b64encode(p.read_bytes()).decode()
        return f'<img src="data:image/png;base64,{b64}" class="logo-img"/>'
    return (
        '<svg class="logo-svg" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<rect width="48" height="48" rx="12" fill="rgba(34,211,165,0.08)"/>'
        '<rect width="48" height="48" rx="12" stroke="rgba(34,211,165,0.18)" stroke-width="1"/>'
        '<text x="50%" y="54%" dominant-baseline="middle" text-anchor="middle" '
        'font-family="Inter,sans-serif" font-size="15" font-weight="700" fill="#22d3a5"'
        ' letter-spacing="1">QC</text>'
        '</svg>'
    )

# ── Ticker tape ────────────────────────────────────────────────────────────────
TICKERS = [
    ("S&P 500","5,248","+0.72%",True),  ("NASDAQ","18,421","+1.14%",True),
    ("DOW JONES","39,170","-0.18%",False),("IPC MX","55,242","+0.61%",True),
    ("AAPL","182.63","+2.34%",True),    ("MSFT","415.21","+1.12%",True),
    ("TSLA","234.15","-0.87%",False),   ("NVDA","875.42","+4.21%",True),
    ("BTC","67,421","+3.15%",True),     ("ETH","3,842","+2.08%",True),
    ("GOLD","2,341","+0.52%",True),     ("WTI","82.41","-0.67%",False),
    ("EUR/USD","1.0821","+0.11%",True), ("AMX","14.23","-1.24%",False),
    ("WALMEX","68.40","+1.33%",True),   ("CEMEX","7.84","-2.11%",False),
    ("META","521.33","+1.67%",True),    ("AMZN","192.87","+0.94%",True),
]
tape = "".join(
    f'<span class="ti"><span class="ti-s">{s}</span>'
    f'<span class="ti-p">{p}</span>'
    f'<span class="{"ti-u" if u else "ti-d"}">'
    f'{"▲" if u else "▼"} {c}</span></span>'
    f'<span class="ti-dot"></span>'
    for s, p, c, u in TICKERS * 5
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {{
  --bg:       #060810;
  --card:     #0c0f18;
  --border:   rgba(255,255,255,0.07);
  --border2:  rgba(255,255,255,0.11);
  --accent:   #22d3a5;
  --accent-d: #1ab88f;
  --text:     #eef0f3;
  --sub:      #60697a;
  --muted:    #3a4150;
  --red:      #f87171;
  --green:    #22d3a5;
}}

*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
  background: var(--bg) !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--text) !important;
}}

/* Ocultar chrome Streamlit */
[data-testid="stSidebar"], [data-testid="collapsedControl"],
[data-testid="stDecoration"], header[data-testid="stHeader"],
[data-testid="stToolbar"], #MainMenu, footer {{ display:none !important; }}

.block-container {{
  max-width: 440px !important;
  padding: 0 24px 80px !important;
  margin: 0 auto !important;
}}

/* Fondo: dot grid + glow */
[data-testid="stAppViewContainer"]::before {{
  content: '';
  position: fixed; inset: 0; z-index: 0;
  background-image: radial-gradient(rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 28px 28px;
  pointer-events: none;
}}
[data-testid="stAppViewContainer"]::after {{
  content: '';
  position: fixed; z-index: 0;
  top: -15%; left: 50%; transform: translateX(-50%);
  width: 800px; height: 600px;
  background: radial-gradient(ellipse, rgba(34,211,165,0.06) 0%, transparent 60%);
  pointer-events: none;
}}

/* ── Ticker ── */
.qc-ticker {{
  position: fixed; top:0; left:0; right:0; z-index:999;
  height: 32px;
  background: rgba(6,8,16,0.96);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center;
  overflow: hidden;
}}
.qc-ticker-track {{
  display: flex; align-items: center;
  white-space: nowrap;
  animation: ticker 100s linear infinite;
}}
@keyframes ticker {{
  from {{ transform: translateX(0); }}
  to   {{ transform: translateX(-50%); }}
}}
.ti {{ display:inline-flex; align-items:center; gap:5px; padding: 0 16px; }}
.ti-s {{ font-size:10.5px; font-weight:600; color:#4b5563; letter-spacing:.4px; }}
.ti-p {{ font-size:10.5px; font-weight:500; color:#9ca3af; }}
.ti-u {{ font-size:10.5px; color:var(--green); }}
.ti-d {{ font-size:10.5px; color:var(--red); }}
.ti-dot {{ width:2px; height:2px; border-radius:50%; background:rgba(255,255,255,0.08); }}

/* ── Logo área ── */
.logo-area {{
  position: relative; z-index: 1;
  text-align: center;
  padding: 68px 0 32px;
}}
.logo-img {{
  width: 72px; height: 72px;
  object-fit: contain;
  mix-blend-mode: lighten;
  filter: drop-shadow(0 0 16px rgba(34,211,165,0.25));
  margin-bottom: 14px;
}}
.logo-svg {{
  width: 48px; height: 48px;
  margin-bottom: 14px;
}}
.logo-name {{
  font-size: 13px; font-weight: 600;
  letter-spacing: 4px; color: var(--accent);
  text-transform: uppercase; margin-bottom: 20px;
}}
.logo-headline {{
  font-size: 24px; font-weight: 600;
  letter-spacing: -0.5px; color: var(--text);
  margin-bottom: 6px; line-height: 1.2;
}}
.logo-tagline {{
  font-size: 14px; font-weight: 400;
  color: var(--sub); line-height: 1.5;
}}

/* ── Card ── */
.auth-card {{
  position: relative; z-index: 1;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 32px 32px 28px;
  box-shadow:
    0 0 0 1px rgba(34,211,165,0.03),
    0 1px 0 0 rgba(255,255,255,0.04) inset,
    0 24px 64px rgba(0,0,0,0.5);
}}

/* ── Inputs Streamlit ── */
.stTextInput {{ margin-bottom: 4px !important; }}
.stTextInput > label {{ margin-bottom: 6px !important; }}

.stTextInput > div > div > input {{
  background: #080b13 !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important; font-weight: 400 !important;
  border-radius: 9px !important;
  padding: 11px 13px !important;
  transition: border-color .15s, box-shadow .15s !important;
  -webkit-font-smoothing: antialiased !important;
}}
.stTextInput > div > div > input:hover {{
  border-color: var(--border2) !important;
}}
.stTextInput > div > div > input:focus {{
  border-color: rgba(34,211,165,0.4) !important;
  box-shadow: 0 0 0 3px rgba(34,211,165,0.07) !important;
  outline: none !important;
  background: #070a11 !important;
}}
.stTextInput > div > div > input::placeholder {{
  color: var(--muted) !important;
}}
label[data-testid="stWidgetLabel"] p {{
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important; font-weight: 500 !important;
  color: #6b7280 !important;
  letter-spacing: 0 !important; text-transform: none !important;
}}

/* ── Botón login (sólido) ── */
.stButton > button {{
  width: 100% !important;
  background: var(--accent) !important;
  border: none !important;
  color: #03100b !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important; font-weight: 600 !important;
  letter-spacing: -0.1px !important;
  border-radius: 9px !important;
  padding: 12px 20px !important;
  margin-top: 12px !important;
  cursor: pointer !important;
  transition: background .15s, box-shadow .15s, transform .1s !important;
  -webkit-font-smoothing: antialiased !important;
}}
.stButton > button:hover {{
  background: var(--accent-d) !important;
  box-shadow: 0 4px 20px rgba(34,211,165,0.2) !important;
  transform: translateY(-1px) !important;
}}
.stButton > button:active {{ transform: translateY(0) !important; }}

/* ── Botón registro (ghost) ── */
.stFormSubmitButton > button {{
  width: 100% !important;
  background: transparent !important;
  border: 1px solid var(--border2) !important;
  color: var(--text) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important; font-weight: 500 !important;
  border-radius: 9px !important;
  padding: 12px 20px !important;
  margin-top: 12px !important;
  cursor: pointer !important;
  transition: border-color .15s, background .15s !important;
}}
.stFormSubmitButton > button:hover {{
  border-color: rgba(255,255,255,0.18) !important;
  background: rgba(255,255,255,0.02) !important;
}}

/* ── Alerts ── */
[data-testid="stAlert"] {{
  background: rgba(248,113,113,0.06) !important;
  border: 1px solid rgba(248,113,113,0.15) !important;
  border-radius: 9px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important;
  padding: 10px 14px !important;
}}
.success-msg {{
  background: rgba(34,211,165,0.06);
  border: 1px solid rgba(34,211,165,0.15);
  border-radius: 9px;
  padding: 11px 14px;
  font-size: 13px; color: var(--accent);
  margin-top: 10px; text-align: center;
  font-family: 'Inter', sans-serif;
}}

/* ── Divisor ── */
.form-divider {{
  display: flex; align-items: center; gap: 12px;
  margin: 20px 0 16px;
}}
.form-divider-line {{ flex:1; height:1px; background: var(--border); }}
.form-divider-text {{
  font-size: 12px; color: var(--muted);
  font-family: 'Inter', sans-serif;
  white-space: nowrap;
}}

/* ── Switch link ── */
.switch-row {{
  position: relative; z-index: 1;
  text-align: center;
  margin-top: 20px;
  font-size: 13px; color: var(--sub);
  font-family: 'Inter', sans-serif;
}}

/* Footer */
.qc-footer {{
  position: relative; z-index: 1;
  text-align: center;
  margin-top: 40px;
  font-size: 11px; color: var(--muted);
  font-family: 'Inter', sans-serif;
  letter-spacing: .3px;
}}
</style>

<!-- TICKER -->
<div class="qc-ticker">
  <div class="qc-ticker-track">{tape}{tape}</div>
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

show_reg = st.session_state.show_register

# ── Logo + headline ────────────────────────────────────────────────────────────
headline = "Crea tu cuenta" if show_reg else "Bienvenido de vuelta"
tagline  = "Comienza a invertir con inteligencia." if show_reg else "Accede a tu terminal financiera."

st.markdown(f"""
<div class="logo-area">
  {get_logo_html()}
  <div class="logo-name">QC Analytics</div>
  <div class="logo-headline">{headline}</div>
  <div class="logo-tagline">{tagline}</div>
</div>
""", unsafe_allow_html=True)

# ── Card ───────────────────────────────────────────────────────────────────────
st.markdown('<div class="auth-card">', unsafe_allow_html=True)

# ══ INICIAR SESIÓN ════════════════════════════════════════════════════════════
if not show_reg:
    try:
        authenticator.login(location="main", key="login_form")
    except Exception as e:
        st.error(f"Error: {e}")

    status = st.session_state.get("authentication_status")
    if status is True:
        st.switch_page("pages/dashboard.py")
    elif status is False:
        st.error("Usuario o contraseña incorrectos.")

    st.markdown("""
    <div class="form-divider">
      <div class="form-divider-line"></div>
      <div class="form-divider-text">¿no tienes cuenta?</div>
      <div class="form-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Registrarse", key="go_reg"):
        st.session_state.show_register = True
        st.rerun()

# ══ REGISTRARSE ═══════════════════════════════════════════════════════════════
else:
    with st.form("reg_form", clear_on_submit=True):
        nombre  = st.text_input("Nombre completo",      placeholder="Aldo Bravo")
        usuario = st.text_input("Usuario",              placeholder="aldob")
        correo  = st.text_input("Correo electrónico",   placeholder="correo@ejemplo.com")
        pwd     = st.text_input("Contraseña",           type="password", placeholder="Mínimo 6 caracteres")
        pwd2    = st.text_input("Confirmar contraseña", type="password", placeholder="Repite tu contraseña")
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
            st.markdown('<div class="success-msg">✓ Cuenta creada. Ya puedes iniciar sesión.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="form-divider">
      <div class="form-divider-line"></div>
      <div class="form-divider-text">¿ya tienes cuenta?</div>
      <div class="form-divider-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Iniciar sesión", key="go_login"):
        st.session_state.show_register = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="qc-footer">QC Analytics &nbsp;·&nbsp; '
    'Datos: Yahoo Finance &nbsp;·&nbsp; IA: Claude</div>',
    unsafe_allow_html=True,
)
