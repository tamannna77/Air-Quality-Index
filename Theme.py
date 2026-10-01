import streamlit as st

def get_theme():
    if 'theme' not in st.session_state:
        st.session_state.theme = 'dark'
    is_dark = st.session_state.theme == 'dark'
    if is_dark:
        return dict(is_dark=True, BG="#0A0F1E", CARD="#111827", TEXT="#E2E8F0",
                    SUBTEXT="#94A3B8", ACCENT="#00D4FF", GRID="#1F2937",
                    BORDER="#1F2937", SIDEBAR="#0D1117", MAP_STYLE="carto-darkmatter")
    else:
        return dict(is_dark=False, BG="#F0F4F8", CARD="#FFFFFF", TEXT="#0F172A",
                    SUBTEXT="#475569", ACCENT="#0077B6", GRID="#CBD5E1",
                    BORDER="#CBD5E1", SIDEBAR="#E2E8F0", MAP_STYLE="carto-positron")

def inject_theme_css(t):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&family=Inter:wght@400;500&family=Orbitron:wght@700&display=swap');
    html,body,[class*="css"]{{font-family:'Inter',sans-serif !important;}}
    .stApp{{background-color:{t['BG']} !important;}}
    [data-testid="stSidebar"]{{background-color:{t['SIDEBAR']} !important;}}
    [data-testid="stSidebar"] *{{color:{t['TEXT']} !important;}}
    .stButton>button{{background:{t['CARD']} !important;color:{t['TEXT']} !important;border:1px solid {t['BORDER']} !important;border-radius:8px !important;}}
    .stButton>button:hover{{border-color:{t['ACCENT']} !important;color:{t['ACCENT']} !important;}}
    [data-testid="stExpander"]{{background:{t['CARD']} !important;border:1px solid {t['BORDER']} !important;border-radius:10px !important;}}
    [data-testid="stExpander"] summary{{color:{t['TEXT']} !important;}}
    .stSelectbox label,.stSlider label{{color:{t['TEXT']} !important;}}
    div[data-baseweb="select"]>div{{background:{t['CARD']} !important;border-color:{t['BORDER']} !important;color:{t['TEXT']} !important;}}
    .section-title{{font-family:'Poppins',sans-serif;font-size:1.4rem;font-weight:700;color:{t['TEXT']};border-left:4px solid {t['ACCENT']};padding-left:12px;margin-bottom:16px;}}
    .insight-box{{background:{t['CARD']};border-left:4px solid {t['ACCENT']};border-radius:8px;padding:16px 20px;margin-top:12px;font-size:0.92rem;color:{t['SUBTEXT']};line-height:1.6;}}
    .footer{{text-align:center;font-size:0.8rem;color:{t['SUBTEXT']};padding:24px 0 8px 0;margin-top:40px;border-top:1px solid {t['BORDER']};}}
    *{{transition:background-color 0.3s ease,color 0.3s ease !important;}}
    </style>""", unsafe_allow_html=True)

def get_chart_layout(t):
    return dict(paper_bgcolor=t['CARD'], plot_bgcolor=t['CARD'],
                font=dict(family='Inter',color=t['SUBTEXT']),
                title_font=dict(family='Poppins',color=t['TEXT'],size=16),
                margin=dict(l=20,r=20,t=50,b=20),
                legend=dict(bgcolor=t['CARD'],bordercolor=t['BORDER'],font=dict(color=t['TEXT'])))

def render_sidebar(t):
    with st.sidebar:
        st.markdown(f"<h2 style='color:{t['TEXT']};margin:0'>🌿 India AQI</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:{t['SUBTEXT']};margin:0 0 12px 0'>Dashboard</p>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("☀️ Switch to Light Mode" if t['is_dark'] else "🌙 Switch to Dark Mode", use_container_width=True):
            st.session_state.theme = 'light' if t['is_dark'] else 'dark'
            st.rerun()
        st.markdown("---")
        st.markdown(f"<p style='color:{t['TEXT']};font-weight:700'>🔽 Filters</p>", unsafe_allow_html=True)
        year_range = st.slider("📅 Year Range", 2009, 2024, (2009, 2024))
        st.markdown("---")
        st.markdown(f"<div style='font-size:0.75rem;color:{t['SUBTEXT']};text-align:center'>Made by <b>Ayush Sharma</b><br>DAVIET • Roll: 2513533<br>CSE AI/ML</div>", unsafe_allow_html=True)
    return year_range

def aqi_bucket_color(bucket):
    return {'Good':'#2DC653','Satisfactory':'#A8E063','Moderate':'#F9C74F','Poor':'#F4A261','Very Poor':'#E63946','Severe':'#6C1515'}.get(bucket,'#94A3B8')

def bar_color_from_aqi(aqi):
    if aqi<=50: return '#2DC653'
    elif aqi<=100: return '#A8E063'
    elif aqi<=200: return '#F9C74F'
    elif aqi<=300: return '#F4A261'
    elif aqi<=400: return '#E63946'
    else: return '#6C1515'

MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
BUCKET_ORDER = ['Good','Satisfactory','Moderate','Poor','Very Poor','Severe']
