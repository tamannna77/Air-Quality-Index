import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all_data
from Theme import get_theme, inject_theme_css, get_chart_layout, render_sidebar, render_footer, MONTHS, BUCKET_ORDER, aqi_bucket_color

st.set_page_config(page_title="India AQI Dashboard", page_icon="🌿", layout="wide")
t = get_theme(); inject_theme_css(t); CL = get_chart_layout(t)
year_range = render_sidebar(t)

with st.spinner("🌿 Loading data..."):
    df, stations, pollutants = load_all_data()
df = df[(df['year']>=year_range[0])&(df['year']<=year_range[1])]

st.markdown(f"""
<div style='background:linear-gradient(135deg,{t['CARD']} 0%,{t['BG']} 100%);border-radius:20px;padding:40px;margin-bottom:24px;border:1px solid {t['BORDER']};'>
    <h1 style='font-family:Poppins;font-size:2.8rem;font-weight:700;color:{t['TEXT']};margin:0;line-height:1.2;'>🌿 India Air Quality</h1>
    <h1 style='font-family:Poppins;font-size:2.8rem;font-weight:700;color:{t['ACCENT']};margin:0 0 16px 0;'>Index Dashboard</h1>
    <p style='color:{t['SUBTEXT']};font-size:1rem;max-width:600px;line-height:1.7;'>A comprehensive analysis of air pollution across <b style='color:{t['TEXT']}'>483 monitoring stations</b>, <b style='color:{t['TEXT']}'>240 cities</b> and <b style='color:{t['TEXT']}'>20 Indian states</b> from 2009 to 2024. Data sourced from CPCB of India.</p>
</div>""", unsafe_allow_html=True)

k1,k2,k3,k4,k5 = st.columns(5)
for col,val,lbl in [(k1,"483","Monitoring Stations"),(k2,"240","Cities Covered"),(k3,"20","Indian States"),(k4,"7,38,097","Daily Readings"),(k5,"15 Yrs","Data Coverage")]:
    with col:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {t['BORDER']};border-radius:14px;padding:18px 10px;text-align:center;'><div style='font-family:Orbitron;font-size:1.5rem;font-weight:700;color:{t['ACCENT']};white-space:nowrap;'>{val}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};margin-top:6px;'>{lbl}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>📊 AQI Scale Reference</div>", unsafe_allow_html=True)
aqi_scale = [("0–50","🟢 Good","#2DC653","Safe for everyone."),("51–100","🟡 Satisfactory","#A8E063","Minor discomfort for sensitive groups."),("101–200","🟡 Moderate","#F9C74F","Breathing discomfort on exertion."),("201–300","🟠 Poor","#F4A261","Breathing discomfort for most."),("301–400","🔴 Very Poor","#E63946","Respiratory illness on exposure."),("401–500","🟤 Severe","#6C1515","Dangerous even on light activity.")]
cols = st.columns(6)
for col,(rng,cat,color,desc) in zip(cols,aqi_scale):
    with col:
        st.markdown(f"<div style='background:{color}22;border:1px solid {color};border-radius:12px;padding:12px 8px;text-align:center;min-height:150px;'><div style='font-size:0.78rem;font-weight:700;color:{color};margin-bottom:6px;'>{cat}</div><div style='font-size:1rem;font-weight:800;color:{t['TEXT']};font-family:Orbitron;margin:4px 0;'>{rng}</div><div style='font-size:0.7rem;color:{t['SUBTEXT']};line-height:1.3;margin-top:6px;'>{desc}</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>🗺️ India AQI Heat Map</div>", unsafe_allow_html=True)
st.markdown(f"<p style='color:{t['SUBTEXT']};font-size:0.9rem'>Hover over any point to see city name and AQI value.</p>", unsafe_allow_html=True)
map_df = df.dropna(subset=['latitude','longitude','AQI'])
map_df = map_df.groupby(['station_code','city','state','latitude','longitude'])['AQI'].mean().reset_index()
fig_map = px.scatter_map(
    map_df,
    lat='latitude',
    lon='longitude',
    color='AQI',
    size='AQI',
    size_max=18,
    hover_name='city',
    hover_data={'state':True,'AQI':':.0f','latitude':False,'longitude':False},
    color_continuous_scale=[
        [0,"#2DC653"],
        [0.2,"#A8E063"],
        [0.4,"#F9C74F"],
        [0.6,"#F4A261"],
        [0.8,"#E63946"],
        [1,"#6C1515"]
    ],
    range_color=[50,200],
    zoom=4,
    center={"lat":22.5,"lon":82.0},
    height=520,
    map_style="carto-darkmatter"
)
fig_map.update_layout(paper_bgcolor=t['CARD'],margin=dict(l=0,r=0,t=0,b=0),coloraxis_colorbar=dict(title=dict(text="AQI",font=dict(color=t['TEXT'])),tickfont=dict(color=t['SUBTEXT'])))
st.plotly_chart(fig_map,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> The map clearly shows India's North-South pollution divide. The entire Indo-Gangetic Plain (Delhi, Punjab, Bihar, UP) shows red and orange while Northeast India and coastal South India remain green.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

c1,c2 = st.columns(2)
with c1:
    st.markdown("<div class='section-title'>📈 National AQI Trend</div>", unsafe_allow_html=True)
    yearly = df.groupby('year')['AQI'].mean().reset_index()
    fig1 = px.line(yearly,x='year',y='AQI',markers=True,color_discrete_sequence=[t['ACCENT']],title="India Average AQI — 2009 to 2024")
    fig1.add_vrect(x0=2019.8,x1=2020.8,fillcolor="rgba(45,198,83,0.12)",line_width=0,annotation_text="COVID 2020",annotation_font_color="#2DC653")
    fig1.update_traces(line_width=2.5,marker_size=7)
    fig1.update_layout(**CL)
    fig1.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    fig1.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig1,use_container_width=True)

with c2:
    st.markdown("<div class='section-title'>🥧 AQI Category Share</div>", unsafe_allow_html=True)
    bucket_counts = df['AQI_Bucket'].value_counts().reindex(BUCKET_ORDER).dropna()
    fig2 = go.Figure(go.Pie(labels=bucket_counts.index,values=bucket_counts.values,marker=dict(colors=[aqi_bucket_color(b) for b in bucket_counts.index],line=dict(color=t['CARD'],width=2)),hole=0.45,textinfo='label+percent',textfont=dict(size=11,color=t['TEXT'])))
    fig2.update_layout(**CL,showlegend=False,title="AQI Category Distribution")
    st.plotly_chart(fig2,use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
ca,cb = st.columns(2)
with ca:
    st.markdown("<div class='section-title' style='border-color:#E63946'>🔴 Top 5 Most Polluted Cities</div>", unsafe_allow_html=True)
    for _,row in df.groupby('city')['AQI'].mean().sort_values(ascending=False).head(5).reset_index().iterrows():
        st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;background:{t['CARD']};border:1px solid #E63946;border-radius:10px;padding:12px 18px;margin-bottom:8px;'><span style='color:{t['TEXT']};font-weight:600'>🏙️ {row['city']}</span><span style='color:#E63946;font-family:Orbitron;font-weight:700'>AQI {int(row['AQI'])}</span></div>", unsafe_allow_html=True)

with cb:
    st.markdown("<div class='section-title' style='border-color:#2DC653'>🟢 Top 5 Cleanest Cities</div>", unsafe_allow_html=True)
    for _,row in df.groupby('city')['AQI'].mean().sort_values().head(5).reset_index().iterrows():
        st.markdown(f"<div style='display:flex;justify-content:space-between;align-items:center;background:{t['CARD']};border:1px solid #2DC653;border-radius:10px;padding:12px 18px;margin-bottom:8px;'><span style='color:{t['TEXT']};font-weight:600'>🌿 {row['city']}</span><span style='color:#2DC653;font-family:Orbitron;font-weight:700'>AQI {int(row['AQI'])}</span></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>💡 Did You Know?</div>", unsafe_allow_html=True)
facts = [("🗓️","Only 6.3% of days in India have Good air quality over the last 15 years"),("🏙️","Delhi NCT's AQI of 161 is 4x worse than Aizawl — India's cleanest city at AQI 47"),("🌧️","Monsoon months (Jul–Aug) reduce AQI by nearly 50% compared to winter months"),("😷","COVID-19 lockdown in 2020 reduced India's average AQI by 15% in just 2 months"),("🌾","Punjab's November AQI spikes to 179 due to paddy stubble burning every harvest season"),("📉","NO2 levels have declined by 44% over 15 years thanks to cleaner fuel norms")]
fc = st.columns(3)
for i,(icon,fact) in enumerate(facts):
    with fc[i%3]:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {t['BORDER']};border-radius:12px;padding:16px;margin-bottom:12px;'><span style='font-size:1.4rem'>{icon}</span><p style='margin:8px 0 0 0;font-size:0.88rem;color:{t['SUBTEXT']};line-height:1.5'>{fact}</p></div>", unsafe_allow_html=True)
