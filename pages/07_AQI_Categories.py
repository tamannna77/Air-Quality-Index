import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all_data
from Theme import get_theme, inject_theme_css, get_chart_layout, render_sidebar, BUCKET_ORDER, aqi_bucket_color

st.set_page_config(page_title="AQI Categories — India AQI", page_icon="📊", layout="wide")
t = get_theme(); inject_theme_css(t); CL = get_chart_layout(t)
year_range = render_sidebar(t)

with st.spinner("Loading data..."):
    df, stations, pollutants = load_all_data()
df = df[(df['year']>=year_range[0])&(df['year']<=year_range[1])]

st.markdown(f"<div style='margin-bottom:24px;'><h1 style='font-family:Poppins;font-size:2.2rem;font-weight:700;color:{t['TEXT']};margin:0;'>📊 AQI Categories</h1><p style='color:{t['SUBTEXT']};font-size:0.95rem;margin-top:8px;'>How often is India's air actually safe to breathe? Explore distribution across 15 years.</p></div>", unsafe_allow_html=True)
st.markdown("---")

# Health advisory
st.markdown("<div class='section-title'>🛡️ Health Advisory — What Each AQI Level Means</div>", unsafe_allow_html=True)
health_info = [
    ("Good","0–50","#2DC653","😊","Safe for everyone","✅ All outdoor activities safe\n✅ Open windows for ventilation\n✅ No precautions needed"),
    ("Satisfactory","51–100","#A8E063","🙂","Minor discomfort for sensitive groups","⚠️ Sensitive people limit outdoor time\n⚠️ Keep windows open moderately\n⚠️ Light exercise is fine"),
    ("Moderate","101–200","#F9C74F","😐","Breathing discomfort on exertion","⚠️ Avoid prolonged outdoor exertion\n⚠️ Wear mask during outdoor exercise\n⚠️ Use air purifier indoors"),
    ("Poor","201–300","#F4A261","😷","Breathing discomfort for most","❌ Avoid outdoor exercise\n❌ Wear N95 mask if going out\n❌ Keep elderly & children indoors"),
    ("Very Poor","301–400","#E63946","🤧","Respiratory illness on exposure","🚨 Stay indoors, seal windows\n🚨 N95 mask mandatory outside\n🚨 Consult doctor if issues"),
    ("Severe","401–500","#6C1515","💀","Dangerous even on light activity","🚨 Do NOT go outside\n🚨 Schools & events cancel\n🚨 Seek medical help immediately"),
]
cols = st.columns(3)
for i,(cat,rng,color,emoji,summary,tips) in enumerate(health_info):
    with cols[i%3]:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-top:4px solid {color};border-radius:14px;padding:16px;margin-bottom:14px;'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'><span style='font-size:1.8rem;'>{emoji}</span><span style='font-family:Orbitron;font-size:0.95rem;font-weight:700;color:{color};'>AQI {rng}</span></div><div style='font-size:1rem;font-weight:700;color:{color};margin-bottom:4px;'>{cat}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};margin-bottom:10px;'>{summary}</div><div style='background:{'#0A0F1E' if t['is_dark'] else '#F1F5F9'};border-radius:8px;padding:10px;font-size:0.74rem;color:{t['SUBTEXT']};line-height:1.7;'>{tips.replace(chr(10),'<br>')}</div></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Distribution charts
st.markdown("<div class='section-title'>📊 AQI Category Distribution — India (2009–2024)</div>", unsafe_allow_html=True)
bucket_counts = df['AQI_Bucket'].value_counts().reindex(BUCKET_ORDER).dropna()
bucket_pcts   = (bucket_counts/bucket_counts.sum()*100).round(1)
ch1,ch2 = st.columns(2)
with ch1:
    fig1 = go.Figure(go.Bar(x=bucket_counts.index,y=bucket_counts.values,marker_color=[aqi_bucket_color(b) for b in bucket_counts.index],text=[f"{v:,}\n({bucket_pcts[k]:.1f}%)" for k,v in bucket_counts.items()],textposition='outside',textfont=dict(color=t['TEXT'],size=10),hovertemplate="<b>%{x}</b><br>Days: %{y:,}<extra></extra>"))
    fig1.update_layout(**CL,title="Number of Days per AQI Category",height=400,xaxis_title="AQI Category",yaxis_title="Number of Days",showlegend=False)
    fig1.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=11))
    fig1.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],range=[0,bucket_counts.max()*1.25],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig1,use_container_width=True)
with ch2:
    fig2 = go.Figure(go.Pie(labels=bucket_counts.index,values=bucket_counts.values,marker=dict(colors=[aqi_bucket_color(b) for b in bucket_counts.index],line=dict(color=t['CARD'],width=2)),hole=0.45,textinfo='label+percent',textfont=dict(size=11,color=t['TEXT']),hovertemplate="<b>%{label}</b><br>Days: %{value:,}<br>%{percent}<extra></extra>"))
    fig2.update_layout(**CL,title="AQI Category Share — Proportional View",height=400,showlegend=False)
    st.plotly_chart(fig2,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> 57.5% of all days in India fall in the Moderate category. Only 6.3% of days have Good air quality. Combined Poor + Very Poor + Severe = 5.8% which represents thousands of genuinely dangerous days across 483 stations over 15 years.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Category trend
st.markdown("<div class='section-title'>📈 How AQI Categories Changed Over Years</div>", unsafe_allow_html=True)
bucket_year = df.groupby(['year','AQI_Bucket'],observed=True).size().reset_index(name='count')
bucket_year['pct'] = bucket_year.groupby('year')['count'].transform(lambda x: x/x.sum()*100)
fig3 = go.Figure()
for bucket in BUCKET_ORDER:
    data = bucket_year[bucket_year['AQI_Bucket']==bucket]
    fig3.add_trace(go.Scatter(x=data['year'],y=data['pct'],name=bucket,mode='lines+markers',line=dict(color=aqi_bucket_color(bucket),width=2.5),marker=dict(size=6,color=aqi_bucket_color(bucket)),hovertemplate=f"<b>{bucket}</b><br>Year: %{{x}}<br>%{{y:.1f}}%<extra></extra>"))
fig3.update_layout(**CL,title="AQI Category % Share Per Year — Is India Getting Better?",height=450,xaxis_title="Year",yaxis_title="% of Days",showlegend=True)
fig3.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig3.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig3,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> Satisfactory (light green) rising from near 0% in 2014 to 38% by 2024 shows genuine improvement. Moderate (yellow) declining from 99% to 51% is a near halving over 10 years. Good (dark green) rising from 0% to 8% by 2024 shows real progress.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# State category breakdown
st.markdown("<div class='section-title'>🗺️ AQI Category Breakdown by State</div>", unsafe_allow_html=True)
all_states = sorted(df['state'].dropna().unique().tolist())
sel_state  = st.selectbox("🗺️ Select State",all_states,index=all_states.index('Punjab') if 'Punjab' in all_states else 0)
state_df      = df[df['state']==sel_state]
state_buckets = state_df['AQI_Bucket'].value_counts().reindex(BUCKET_ORDER).dropna()
state_pcts    = (state_buckets/state_buckets.sum()*100).round(1)
sb1,sb2 = st.columns([1,1])
with sb1:
    fig4 = go.Figure(go.Bar(x=state_buckets.index,y=state_pcts.values,marker_color=[aqi_bucket_color(b) for b in state_buckets.index],text=[f"{v:.1f}%" for v in state_pcts.values],textposition='outside',textfont=dict(color=t['TEXT'],size=11),hovertemplate="<b>%{x}</b><br>%{y:.1f}% of days<extra></extra>"))
    fig4.update_layout(**CL,title=f"{sel_state} — AQI Category Distribution",height=380,xaxis_title="AQI Category",yaxis_title="% of Days",showlegend=False)
    fig4.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=10))
    fig4.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],range=[0,state_pcts.max()*1.25],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig4,use_container_width=True)
with sb2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:{t['CARD']};border:1px solid {t['BORDER']};border-radius:14px;padding:20px;'><div style='font-size:1rem;font-weight:700;color:{t['TEXT']};margin-bottom:16px;'>📋 {sel_state} — Category Summary</div>", unsafe_allow_html=True)
    for bucket in BUCKET_ORDER:
        if bucket in state_pcts.index:
            pct=state_pcts[bucket]; color=aqi_bucket_color(bucket)
            st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'><span style='color:{t['TEXT']};font-size:0.88rem;font-weight:600;'>{bucket}</span><div style='flex:1;margin:0 12px;background:{t['GRID']};border-radius:4px;height:8px;overflow:hidden;'><div style='width:{min(pct*1.5,100):.0f}%;background:{color};height:100%;border-radius:4px;'></div></div><span style='font-family:Orbitron;font-size:0.85rem;font-weight:700;color:{color};min-width:50px;text-align:right;'>{pct:.1f}%</span></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Protect yourself
st.markdown("<div class='section-title'>💪 How to Protect Yourself</div>", unsafe_allow_html=True)
tips_data = [
    ("🪟","Check AQI Daily","Check the AQI every morning before planning outdoor activities. Apps like AQI India, Sameer (CPCB) give real-time readings for your city."),
    ("😷","Wear the Right Mask","N95 masks filter 95% of PM2.5 particles. Regular surgical masks only filter large particles. N95 is essential when AQI is above 200."),
    ("🏠","Stay Indoors on Bad Days","When AQI exceeds 300, keep windows and doors closed. Use wet cloth or tape to seal gaps. Run air purifier with HEPA filter continuously."),
    ("🌱","Indoor Plants Help","Spider plants, peace lilies and snake plants absorb indoor pollutants. While they don't replace air purifiers, they improve indoor air quality."),
    ("⏰","Time Your Outdoor Activity","AQI is typically lowest in the afternoon (2–4 PM) and highest in early morning and evening. Exercise during low-AQI windows."),
    ("🏥","Consult a Doctor","If you experience persistent cough, shortness of breath or chest tightness on high-AQI days, consult a pulmonologist immediately."),
]
tp_cols = st.columns(3)
for i,(icon,title_,desc) in enumerate(tips_data):
    with tp_cols[i%3]:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {t['BORDER']};border-left:4px solid {t['ACCENT']};border-radius:12px;padding:18px;margin-bottom:12px;'><div style='font-size:1.8rem;margin-bottom:8px;'>{icon}</div><div style='font-size:0.95rem;font-weight:700;color:{t['TEXT']};margin-bottom:6px;'>{title_}</div><div style='font-size:0.8rem;color:{t['SUBTEXT']};line-height:1.5;'>{desc}</div></div>", unsafe_allow_html=True)
