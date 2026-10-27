import requests
import streamlit as st

# ─────────────────────────────────────────────────────────────
# 1. Page setup
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Diabetes Risk Predictor", page_icon="🩺", layout="wide")


def html(markup: str):
    """Render raw HTML (whitespace stripped so Markdown never treats it as a code block)."""
    st.markdown(" ".join(l.strip() for l in markup.splitlines() if l.strip()), unsafe_allow_html=True)


def stretch_button(label: str) -> bool:
    try:
        return st.button(label, width="stretch")
    except TypeError:  # older Streamlit versions
        return st.button(label, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# 2. Custom CSS (theme inspired by the reference UI kit)
# ─────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

:root{
  --primary:#4A63F5; --primary-dark:#3A4FE0; --cyan:#00C2FF;
  --ink:#1F2A44; --muted:#8A93B2; --soft:#F4F6FF; --line:#E3E8FF;
}

/* ---------- Base ---------- */
html, body, .stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp li,
.stApp h1, .stApp h2, .stApp h3, [data-testid="stMarkdownContainer"]{font-family:'Poppins',sans-serif;}
.stApp{
  background:linear-gradient(160deg,#8093FB 0%,#6B80F7 45%,#5A6FF0 100%);
  background-attachment:fixed; color:var(--ink);
}
header[data-testid="stHeader"]{background:transparent;}
#MainMenu, footer{visibility:hidden;}
.block-container{max-width:1080px; padding-top:2.2rem; padding-bottom:3rem;}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"]{background:#fff !important; box-shadow:8px 0 40px rgba(25,35,120,.18);}
section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3{color:var(--ink) !important; font-weight:600;}
[data-testid="stCaptionContainer"]{color:var(--muted) !important;}

/* ---------- Hero ---------- */
.hero{
  position:relative; z-index:0; overflow:hidden; border-radius:30px; padding:2.4rem 2.6rem; color:#fff;
  background:linear-gradient(135deg,#4F68FF 0%,#3A4FE0 100%);
  box-shadow:0 24px 60px rgba(25,35,120,.35);
}
.hero::before{content:""; position:absolute; right:-70px; top:-70px; width:300px; height:300px;
  border-radius:50%; border:34px solid rgba(255,255,255,.10); z-index:0;}
.hero::after{content:""; position:absolute; right:70px; bottom:-110px; width:220px; height:220px;
  border-radius:50%; background:rgba(0,194,255,.28); z-index:0;}
.hero > *{position:relative; z-index:1;}
.hero-badge{display:inline-block; padding:.35rem .9rem; border-radius:999px; background:rgba(255,255,255,.18);
  font-size:.75rem; font-weight:500; letter-spacing:.08em; text-transform:uppercase;}
.hero-title{font-size:2.5rem; font-weight:700; line-height:1.15; margin:1rem 0 .5rem; color:#fff;}
.hero-sub{max-width:560px; font-size:1rem; line-height:1.6; color:rgba(255,255,255,.85);}
.hero-chips{display:flex; flex-wrap:wrap; gap:.6rem; margin-top:1.4rem;}
.hero-chips span{padding:.45rem 1rem; border-radius:14px; background:rgba(255,255,255,.14);
  font-size:.82rem; font-weight:500; color:#fff;}

/* ---------- Input card ---------- */
.st-key-input_card{
  position:relative; z-index:1;
  background:#fff; border-radius:28px; padding:1.9rem 2rem 2rem; margin-top:1.4rem;
  box-shadow:0 24px 60px rgba(25,35,120,.22);
}
.card-title{display:flex; align-items:center; gap:.6rem; font-size:1.15rem; font-weight:600; color:var(--ink);}
.card-title .dot{width:10px; height:10px; border-radius:50%; background:linear-gradient(135deg,var(--cyan),var(--primary));}
.card-sub{color:var(--muted); font-size:.85rem; margin:.2rem 0 .4rem;}

/* ---------- Inputs ---------- */
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label{
  color:#5A6485 !important; font-weight:500; font-size:.85rem;}
div[data-baseweb="input"], div[data-baseweb="base-input"]{background:var(--soft) !important; border-radius:14px !important;}
div[data-baseweb="input"]{border:1px solid var(--line) !important;}
div[data-baseweb="input"]:focus-within{border-color:var(--primary) !important; box-shadow:0 0 0 3px rgba(74,99,245,.15);}
div[data-baseweb="input"] input{color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; font-weight:500;}
[data-testid="stNumberInput"] button{background:transparent !important; color:var(--primary) !important; border:none !important;}

/* ---------- Sliders ----------
   Streamlit's default slider accent is red (#FF4B4B). Hue-rotating the whole slider widget
   turns it into the theme blue; the label is rotated back so its colour stays unchanged. */
[data-testid="stSlider"]{filter:hue-rotate(240deg); padding-bottom:1.5rem;}
[data-testid="stSlider"] [data-testid="stWidgetLabel"]{filter:hue-rotate(-240deg);}
[data-testid="stSlider"] [role="slider"]{
  box-shadow:0 0 0 5px rgba(255,75,75,.18), 0 4px 10px rgba(255,75,75,.35) !important;}
[data-testid*="TickBar"], [data-testid*="TickBar"] *{
  color:#8E8E93 !important; opacity:1 !important; font-size:.72rem !important;}
[data-testid*="ThumbValue"]{font-weight:600 !important; font-size:.82rem !important;}

/* ---------- Live snapshot tiles ---------- */
.soft-divider{height:1px; background:var(--line); margin:1.4rem 0 1rem;}
.snap-title{font-size:.78rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:.1em; margin-bottom:.7rem;}
.snap-grid{display:grid; grid-template-columns:repeat(4,1fr); gap:.8rem; margin-bottom:1.2rem;}
.snap-tile{background:var(--soft); border:1px solid var(--line); border-radius:18px; padding:.9rem 1.1rem;}
.snap-label{font-size:.68rem; font-weight:500; letter-spacing:.08em; text-transform:uppercase; color:var(--muted);}
.snap-value{font-size:1.55rem; font-weight:700; color:var(--ink); line-height:1.3;}
.snap-unit{font-size:.72rem; font-weight:500; color:var(--primary); margin-left:.3rem;}
@media (max-width:700px){.snap-grid{grid-template-columns:repeat(2,1fr);}}

/* ---------- Predict button ---------- */
.stButton{width:100%;}
.stButton > button{
  width:100%; border:none !important; border-radius:999px; padding:.95rem 1.5rem;
  background:linear-gradient(135deg,#5B73FF 0%,#3F54E8 100%) !important;
  box-shadow:0 12px 24px rgba(63,84,232,.35); transition:all .2s ease;
}
.stButton > button p{color:#fff !important; font-weight:600; font-size:.95rem; letter-spacing:.1em; text-transform:uppercase;}
.stButton > button:hover{transform:translateY(-2px); box-shadow:0 16px 30px rgba(63,84,232,.45);}
.stButton > button:active{transform:translateY(0);}
.stButton > button:focus{outline:none; box-shadow:0 0 0 4px rgba(74,99,245,.3);}

/* ---------- Result card ---------- */
.result-card{
  position:relative; z-index:1;
  display:flex; align-items:center; gap:2.2rem; background:#fff; border-radius:28px;
  padding:2rem 2.4rem; margin-top:1.4rem; box-shadow:0 24px 60px rgba(25,35,120,.25);
}
.ring{position:relative; flex:0 0 auto; width:170px; height:170px; border-radius:50%;
  display:flex; align-items:center; justify-content:center;}
.ring::before{content:""; position:absolute; inset:15px; border-radius:50%; background:#fff;
  box-shadow:0 6px 22px rgba(74,99,245,.18);}
.ring-inner{position:relative; text-align:center;}
.ring-value{display:block; font-size:1.9rem; font-weight:700; color:var(--ink); line-height:1.1;}
.ring-label{display:block; font-size:.65rem; font-weight:500; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin-top:.2rem;}
.pill{display:inline-block; padding:.35rem .95rem; border-radius:999px; font-size:.75rem; font-weight:600; letter-spacing:.08em; text-transform:uppercase;}
.pill-bad{background:#FFE9EE; color:#E63958;}
.pill-good{background:#DFF8F0; color:#0E9F78;}
.result-title{font-size:1.55rem; font-weight:700; color:var(--ink); margin:.7rem 0 .3rem;}
.result-text{color:#5A6485; font-size:.92rem; line-height:1.65;}
@media (max-width:700px){.result-card{flex-direction:column; text-align:center;}}

/* ---------- Alerts / footer ---------- */
.alert{position:relative; z-index:1; display:flex; gap:.8rem; align-items:flex-start; background:#fff; border-left:6px solid #FFB020;
  border-radius:18px; padding:1.1rem 1.4rem; margin-top:1.4rem; color:var(--ink); font-size:.92rem;
  line-height:1.55; box-shadow:0 16px 40px rgba(25,35,120,.2);}
.alert code{background:var(--soft); color:var(--primary); padding:.1rem .45rem; border-radius:8px; font-size:.85rem;}
.disclaimer{text-align:center; color:rgba(255,255,255,.8); font-size:.78rem; margin-top:2rem; line-height:1.6;}
.stSpinner p{color:#fff !important;}
</style>
"""
html(CUSTOM_CSS)

# ─────────────────────────────────────────────────────────────
# 3. Hero header
# ─────────────────────────────────────────────────────────────
html("""
<div class="hero">
  <div class="hero-badge">AI-Powered Health Screening</div>
  <div class="hero-title">Diabetes Risk Predictor</div>
  <div class="hero-sub">Enter the patient's medical details below to check the diabetes risk.</div>
  <div class="hero-chips"><span>8 Health Metrics</span><span>Instant Prediction</span><span>Confidence Score</span></div>
</div>
""")

# ─────────────────────────────────────────────────────────────
# 4. Sidebar – API configuration
# ─────────────────────────────────────────────────────────────
st.sidebar.header("API Configuration")
API_URL = st.sidebar.text_input("FastAPI URL:", value="https://affidavit-whiny-carwash.ngrok-free.dev").rstrip("/")
st.sidebar.caption("Public URL of your running FastAPI server (e.g. your ngrok link).")

# ─────────────────────────────────────────────────────────────
# 5. Input card
# ─────────────────────────────────────────────────────────────
with st.container(key="input_card"):
    html("""
    <div class="card-title"><span class="dot"></span>Patient Details</div>
    <div class="card-sub">Adjust the values below. The snapshot updates live.</div>
    """)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        pregnancies = st.number_input("Pregnancies", min_value=0, max_value=17, value=2, step=1)
        glucose = st.slider("Glucose (mg/dL)", min_value=0.0, max_value=200.0, value=120.0, step=1.0, format="%.0f")
        blood_pressure = st.slider("Blood Pressure (mm Hg)", min_value=0.0, max_value=130.0, value=70.0, step=1.0, format="%.0f")
        skin_thickness = st.slider("Skin Thickness (mm)", min_value=0.0, max_value=100.0, value=20.0, step=1.0, format="%.0f")

    with col2:
        dpf = st.number_input("Diabetes Pedigree Function", min_value=0.0, max_value=2.5, value=0.5, step=0.01)
        insulin = st.slider("Insulin (µU/mL)", min_value=0.0, max_value=850.0, value=80.0, step=1.0, format="%.0f")
        bmi = st.slider("BMI (kg/m²)", min_value=0.0, max_value=70.0, value=25.0, step=0.1, format="%.1f")
        age = st.slider("Age (years)", min_value=18, max_value=90, value=30, step=1)

    html('<div class="soft-divider"></div>')

    tiles = [
        ("Glucose", f"{glucose:.0f}", "mg/dL"),
        ("Blood Pressure", f"{blood_pressure:.0f}", "mm Hg"),
        ("BMI", f"{bmi:.1f}", "kg/m²"),
        ("Age", f"{age}", "yrs"),
    ]
    tiles_html = "".join(
        f'<div class="snap-tile"><div class="snap-label">{n}</div>'
        f'<div class="snap-value">{v}<span class="snap-unit">{u}</span></div></div>'
        for n, v, u in tiles
    )
    html(f'<div class="snap-title">Live Snapshot</div><div class="snap-grid">{tiles_html}</div>')

    clicked = stretch_button("Predict Diabetes Risk")


# ─────────────────────────────────────────────────────────────
# 6. Result + alert helpers
# ─────────────────────────────────────────────────────────────
def show_result(label: str, confidence: float):
    confidence = max(0.0, min(1.0, confidence))
    deg = confidence * 360

    if label == "Diabetic":
        c1, c2 = "#FF8FA3", "#F43F5E"
        pill, title = "pill-bad", "Higher diabetes risk detected"
        text = (f"Based on the entered values, the model predicts <b>{label}</b>. "
                "Please consult a healthcare professional for proper testing and diagnosis.")
    else:
        c1, c2 = "#00C2FF", "#19D3A2"
        pill, title = "pill-good", "Lower diabetes risk detected"
        text = (f"Based on the entered values, the model predicts <b>{label}</b>. "
                "Keep up regular check-ups and a healthy lifestyle.")

    html(f"""
    <div class="result-card">
      <div class="ring" style="background:conic-gradient({c1} 0deg, {c2} {deg:.1f}deg, #EEF1FF {deg:.1f}deg 360deg);">
        <div class="ring-inner">
          <span class="ring-value">{confidence * 100:.1f}%</span>
          <span class="ring-label">Confidence</span>
        </div>
      </div>
      <div>
        <span class="pill {pill}">{label}</span>
        <div class="result-title">{title}</div>
        <div class="result-text">{text}</div>
      </div>
    </div>
    """)


def show_alert(message: str):
    html(f'<div class="alert"><div>⚠️</div><div>{message}</div></div>')


# ─────────────────────────────────────────────────────────────
# 7. Predict → API call
# ─────────────────────────────────────────────────────────────
if clicked:
    # Exact field names from PatientFeatures model in main.py
    payload = {
        "Pregnancies": int(pregnancies),
        "Glucose": float(glucose),
        "BloodPressure": float(blood_pressure),
        "SkinThickness": float(skin_thickness),
        "Insulin": float(insulin),
        "BMI": float(bmi),
        "DiabetesPedigreeFunction": float(dpf),
        "Age": int(age),
    }

    try:
        with st.spinner("Analysing patient data..."):
            response = requests.post(
                f"{API_URL}/predict",
                json=payload,
                headers={"ngrok-skip-browser-warning": "true"},
                timeout=30,
            )

        if response.status_code == 200:
            data = response.json()
            show_result(data["result_label"], float(data["confidence"]))
        else:
            show_alert(f"Server returned status code <b>{response.status_code}</b>. "
                       "Make sure the FastAPI server is running properly.")

    except requests.exceptions.RequestException:
        show_alert("Could not connect to the API. Please start the FastAPI server first "
                   "(<code>uvicorn main:app --reload</code>).")

# ─────────────────────────────────────────────────────────────
# 8. Footer
# ─────────────────────────────────────────────────────────────
html("""
<div class="disclaimer">
  This tool provides a screening estimate only and is not a medical diagnosis.<br>
  Please consult a qualified healthcare professional for medical advice.
</div>
""")