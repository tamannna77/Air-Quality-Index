import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all_data
from Theme import get_theme, inject_theme_css, get_chart_layout, render_sidebar

st.set_page_config(page_title="Pollutant Analysis — India AQI", page_icon="🔬", layout="wide")
t = get_theme(); inject_theme_css(t); CL = get_chart_layout(t)
year_range = render_sidebar(t)

with st.spinner("Loading data..."):
    df, stations, pollutants = load_all_data()
df = df[(df['year']>=year_range[0])&(df['year']<=year_range[1])]

POLL_COLORS = {'pm2.5':'#E63946','pm10':'#F4A261','no2':'#F9C74F','so2':'#A8E063','ozone':'#4CC9F0','nh3':'#7C3AED','co':'#2DC653'}

st.markdown(f"<div style='margin-bottom:24px;'><p style='color:{t['ACCENT']};font-size:0.85rem;font-weight:700;letter-spacing:4px;'>PHASE 7 ANALYSIS</p><h1 style='font-family:Poppins;font-size:2.2rem;font-weight:700;color:{t['TEXT']};margin:0;'>🔬 Pollutant Analysis</h1><p style='color:{t['SUBTEXT']};font-size:0.95rem;margin-top:8px;'>Deep dive into 7 key pollutants — concentrations, health effects, sources and AQI relationship.</p></div>", unsafe_allow_html=True)
st.markdown("---")

# Pollutant info cards
st.markdown("<div class='section-title'>📋 Pollutant Reference Guide</div>", unsafe_allow_html=True)
poll_info = [
    ("PM2.5","Fine Particulate Matter","#E63946","🔴",f"{df['pm2.5'].mean():.1f}" if 'pm2.5' in df.columns else "N/A","5 µg/m³","11x","Crop burning, vehicles, coal plants","Enters bloodstream, causes heart attacks, lung cancer"),
    ("PM10","Coarse Particulate Matter","#F4A261","🟠",f"{df['pm10'].mean():.1f}" if 'pm10' in df.columns else "N/A","15 µg/m³","8x","Road dust, construction, mining","Respiratory tract irritation, asthma attacks, COPD"),
    ("NO2","Nitrogen Dioxide","#F9C74F","🟡",f"{df['no2'].mean():.1f}" if 'no2' in df.columns else "N/A","10 µg/m³","2.5x","Vehicle engines, power plants","Inflames airways, increases infection risk, acid rain"),
    ("SO2","Sulphur Dioxide","#A8E063","🟢",f"{df['so2'].mean():.1f}" if 'so2' in df.columns else "N/A","40 µg/m³","Under","Coal power plants, metal smelting","Airway constriction, acid rain, damages crops"),
    ("Ozone","Ground-Level Ozone","#4CC9F0","🔵",f"{df['ozone'].mean():.1f}" if 'ozone' in df.columns else "N/A","60 µg/m³","Under","NO2+VOCs react in sunlight, vehicles","Chest pain, lung scarring, reduces crop yields"),
    ("NH3","Ammonia","#7C3AED","🟣",f"{df['nh3'].mean():.1f}" if 'nh3' in df.columns else "N/A","—","—","Fertilizers, livestock, crop burning","Forms secondary PM2.5, water pollution"),
    ("CO","Carbon Monoxide","#2DC653","🟩",f"{df['co'].mean():.2f}" if 'co' in df.columns else "N/A","4 mg/m³","Under","Incomplete combustion, vehicles","Binds to haemoglobin, prevents oxygen delivery"),
]
for row in [poll_info[:4], poll_info[4:]]:
    cols = st.columns(len(row))
    for col,(name,full,color,icon,avg,who,times,source,effect) in zip(cols,row):
        with col:
            st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-top:4px solid {color};border-radius:14px;padding:16px;margin-bottom:12px;'><div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'><span style='font-size:1.5rem;'>{icon}</span><span style='font-family:Orbitron;font-size:1.1rem;font-weight:700;color:{color};white-space:nowrap;'>{avg}</span></div><div style='font-size:1rem;font-weight:700;color:{t['TEXT']};'>{name}</div><div style='font-size:0.75rem;color:{t['SUBTEXT']};margin-bottom:10px;'>{full}</div><div style='background:{'#0A0F1E' if t['is_dark'] else '#F1F5F9'};border-radius:8px;padding:8px;margin-bottom:8px;'><div style='font-size:0.7rem;color:{t['SUBTEXT']};'>WHO Limit</div><div style='font-size:0.85rem;color:{color};font-weight:700;'>{who} <span style='font-size:0.7rem;color:{t['SUBTEXT']};'>({times} limit)</span></div></div><div style='font-size:0.72rem;color:{t['SUBTEXT']};line-height:1.4;margin-bottom:6px;'><b style='color:{t['TEXT']};'>Source:</b> {source}</div><div style='font-size:0.72rem;color:{t['SUBTEXT']};line-height:1.4;'><b style='color:{t['TEXT']};'>Effect:</b> {effect}</div></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Avg pollutant levels
st.markdown("<div class='section-title'>📊 Average Pollutant Levels Across India</div>", unsafe_allow_html=True)
poll_avgs = {p:df[p].mean() for p in pollutants if p in df.columns}
poll_df = pd.DataFrame({'Pollutant':list(poll_avgs.keys()),'Average':list(poll_avgs.values())}).sort_values('Average',ascending=False)
fig1 = go.Figure(go.Bar(x=poll_df['Pollutant'].str.upper(),y=poll_df['Average'],
    marker_color=[POLL_COLORS.get(p,t['ACCENT']) for p in poll_df['Pollutant']],
    text=poll_df['Average'].round(1),textposition='outside',textfont=dict(color=t['TEXT'],size=12),
    hovertemplate="<b>%{x}</b><br>Avg: %{y:.2f} µg/m³<extra></extra>"))
fig1.update_layout(**CL,title="Average Concentration of Each Pollutant (µg/m³)",height=380,xaxis_title="Pollutant",yaxis_title="Average Concentration",showlegend=False)
fig1.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=12))
fig1.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],range=[0,poll_df['Average'].max()*1.2],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig1,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> PM10 (119.7 µg/m³) dominates — 8x above WHO safe limit. PM2.5 (57.3 µg/m³) is second at 11x above WHO limit. Both are particulate matter from dust, burning and vehicles confirming India's core pollution problem is physical particles not gases.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Correlation heatmap
st.markdown("<div class='section-title'>🔗 Pollutant Correlation with AQI</div>", unsafe_allow_html=True)
corr_cols = [p for p in pollutants if p in df.columns]+['AQI']
corr = df[corr_cols].corr().round(2)
fig2 = go.Figure(data=go.Heatmap(z=corr.values,x=[c.upper() for c in corr.columns],y=[c.upper() for c in corr.index],
    colorscale=[[0,"#2DC653"],[0.5,"#F9C74F"],[1,"#E63946"]],text=corr.values.round(2),texttemplate="%{text}",
    textfont=dict(size=11,color="white"),hoverongaps=False,
    hovertemplate="<b>%{y} vs %{x}</b><br>Correlation: %{z:.2f}<extra></extra>",
    colorbar=dict(title=dict(text="Corr",font=dict(color=t['TEXT'])),tickfont=dict(color=t['SUBTEXT']))))
fig2.update_layout(**CL,title="Pollutant Correlation Matrix",height=480)
fig2.update_xaxes(tickfont=dict(color=t['TEXT'],size=11))
fig2.update_yaxes(tickfont=dict(color=t['TEXT'],size=11))
st.plotly_chart(fig2,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> PM2.5 → AQI correlation is 0.95 — near perfect. This validates our AQI calculation from PM2.5. PM10 → AQI is 0.79 — also very strong. SO2, CO and Ozone show weak correlations (below 0.15) meaning gases barely affect India's AQI scores.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Pollutant trend
st.markdown("<div class='section-title'>📈 Pollutant Trends Over 15 Years</div>", unsafe_allow_html=True)
yearly_poll = df.groupby('year')[[p for p in ['pm2.5','pm10','no2'] if p in df.columns]].mean().reset_index()
colors_tr = {'pm2.5':'#E63946','pm10':'#F4A261','no2':'#F9C74F'}
fig3 = go.Figure()
for col_ in ['pm2.5','pm10','no2']:
    if col_ in yearly_poll.columns:
        fig3.add_trace(go.Scatter(x=yearly_poll['year'],y=yearly_poll[col_],name=col_.upper(),mode='lines+markers',line=dict(color=colors_tr[col_],width=2.5),marker=dict(size=7,color=colors_tr[col_],line=dict(color=t['CARD'],width=2)),hovertemplate=f"<b>{col_.upper()}</b><br>Year: %{{x}}<br>Avg: %{{y:.1f}} µg/m³<extra></extra>"))
fig3.add_vrect(x0=2019.8,x1=2020.8,fillcolor="rgba(45,198,83,0.1)",line_width=0,annotation_text="😷 COVID",annotation_font_color="#2DC653",annotation_font_size=10)
fig3.update_layout(**CL,title="PM2.5 vs PM10 vs NO2 — Yearly Trend (2009–2024)",height=400,xaxis_title="Year",yaxis_title="Average Concentration (µg/m³)",showlegend=True)
fig3.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig3.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig3,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> PM2.5 peaked in 2016–2018 then started declining — BS6 fuel norms and NCAP policies are working. NO2 has declined by 44% from 2012 to 2024. All three show a visible dip in 2020 confirming COVID lockdown effect.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Distribution explorer
st.markdown("<div class='section-title'>🔍 Pollutant Distribution Explorer</div>", unsafe_allow_html=True)
sel_poll = st.selectbox("🔬 Select Pollutant",[p.upper() for p in pollutants if p in df.columns],index=0)
poll_low = sel_poll.lower()
ch1,ch2 = st.columns([2,1])
with ch1:
    sample = df[poll_low].dropna().sample(min(50000,len(df)))
    fig4 = go.Figure(go.Histogram(x=sample,nbinsx=60,marker_color=POLL_COLORS.get(poll_low,t['ACCENT']),opacity=0.85,hovertemplate="Range: %{x}<br>Count: %{y}<extra></extra>"))
    fig4.update_layout(**CL,title=f"{sel_poll} — Concentration Distribution",height=360,xaxis_title=f"{sel_poll} Concentration",yaxis_title="Frequency",showlegend=False)
    fig4.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT']))
    fig4.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig4,use_container_width=True)
with ch2:
    p_data = df[poll_low].dropna()
    st.markdown("<br>", unsafe_allow_html=True)
    for label,val,color in [("Mean",f"{p_data.mean():.2f}",t['ACCENT']),("Median",f"{p_data.median():.2f}","#A8E063"),("Std Dev",f"{p_data.std():.2f}","#F9C74F"),("Min",f"{p_data.min():.2f}","#2DC653"),("Max",f"{p_data.max():.2f}","#E63946"),("95th %",f"{p_data.quantile(0.95):.2f}","#F4A261")]:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {t['BORDER']};border-left:4px solid {color};border-radius:8px;padding:10px 14px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;'><span style='color:{t['SUBTEXT']};font-size:0.85rem;'>{label}</span><span style='color:{color};font-family:Orbitron;font-size:0.95rem;font-weight:700;'>{val}</span></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Compare two pollutants
st.markdown("<div class='section-title'>⚡ Compare Any Two Pollutants</div>", unsafe_allow_html=True)
sc1,sc2 = st.columns(2)
with sc1:
    x_poll = st.selectbox("X-axis Pollutant",[p.upper() for p in pollutants if p in df.columns],index=0)
with sc2:
    y_poll = st.selectbox("Y-axis Pollutant",[p.upper() for p in pollutants if p in df.columns],index=1)
x_col=x_poll.lower(); y_col=y_poll.lower()
sample = df[[x_col,y_col,'AQI','city']].dropna().sample(min(3000,len(df)))
fig5 = px.scatter(sample,x=x_col,y=y_col,color='AQI',color_continuous_scale=[[0,"#2DC653"],[0.4,"#F9C74F"],[0.7,"#F4A261"],[1,"#E63946"]],hover_data=['city'],opacity=0.6,title=f"{x_poll} vs {y_poll} — colored by AQI")
fig5.update_layout(**CL,height=420,xaxis_title=f"{x_poll} (µg/m³)",yaxis_title=f"{y_poll} (µg/m³)",coloraxis_colorbar=dict(title=dict(text="AQI",font=dict(color=t['TEXT'])),tickfont=dict(color=t['SUBTEXT'])))
fig5.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig5.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig5,use_container_width=True)
