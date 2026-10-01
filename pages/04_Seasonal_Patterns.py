import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all_data
from Theme import get_theme, inject_theme_css, get_chart_layout, render_sidebar,MONTHS, bar_color_from_aqi

st.set_page_config(page_title="Seasonal Patterns — India AQI", page_icon="📅", layout="wide")
t = get_theme(); inject_theme_css(t); CL = get_chart_layout(t)
year_range = render_sidebar(t)

with st.spinner("Loading data..."):
    df, stations, pollutants = load_all_data()
df = df[(df['year']>=year_range[0])&(df['year']<=year_range[1])]

st.markdown(f"<div style='margin-bottom:24px;'><p style='color:{t['ACCENT']};font-size:0.85rem;font-weight:700;letter-spacing:4px;'>PHASE 6 ANALYSIS</p><h1 style='font-family:Poppins;font-size:2.2rem;font-weight:700;color:{t['TEXT']};margin:0;'>📅 Seasonal AQI Patterns</h1><p style='color:{t['SUBTEXT']};font-size:0.95rem;margin-top:8px;'>Understanding how India's air quality changes across months, seasons and years.</p></div>", unsafe_allow_html=True)
st.markdown("---")

# Monthly India
st.markdown("<div class='section-title'>📆 Month-wise Average AQI — India</div>", unsafe_allow_html=True)
monthly_india = df.groupby('month')['AQI'].mean().reset_index()
monthly_india['month_name'] = monthly_india['month'].apply(lambda x: MONTHS[x-1])
fig1 = go.Figure(go.Bar(x=monthly_india['month_name'],y=monthly_india['AQI'],
    marker_color=[bar_color_from_aqi(a) for a in monthly_india['AQI']],
    text=monthly_india['AQI'].round(0).astype(int),textposition='outside',
    textfont=dict(color=t['TEXT'],size=12,family='Orbitron'),
    hovertemplate="<b>%{x}</b><br>Avg AQI: %{y:.1f}<extra></extra>"))
fig1.update_layout(**CL,title="Month-wise Average AQI — All India (2009–2024)",height=420,xaxis_title="Month",yaxis_title="Average AQI")
fig1.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=12))
fig1.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],range=[0,monthly_india['AQI'].max()+25],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig1,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> November (163) and January (161) are the worst months. July and August (AQI 84) are the cleanest — monsoon rains physically wash particulate matter out of the atmosphere. The pattern forms a clear U-shape — high in winter, bottoming out in monsoon.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Season-wise
st.markdown("<div class='section-title'>🌦️ Season-wise AQI Comparison</div>", unsafe_allow_html=True)
col1,col2 = st.columns([1,1])
with col1:
    season_order = ['Winter','Spring','Summer','Autumn']
    season_colors = ['#74B9FF','#55EFC4','#FDCB6E','#E17055']
    season_aqi = df.groupby('season',observed=True)['AQI'].mean().reindex(season_order).reset_index()
    fig2 = go.Figure()
    for i,row in season_aqi.iterrows():
        fig2.add_trace(go.Bar(x=[row['season']],y=[row['AQI']],name=row['season'],marker_color=season_colors[i],
            text=[f"{row['AQI']:.0f}"],textposition='outside',textfont=dict(color=t['TEXT'],size=14,family='Orbitron'),
            hovertemplate=f"<b>{row['season']}</b><br>Avg AQI: {row['AQI']:.1f}<extra></extra>"))
    fig2.update_layout(**CL,title="Season-wise Average AQI",height=380,showlegend=False,xaxis_title="Season",yaxis_title="Average AQI",bargap=0.3)
    fig2.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=13))
    fig2.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],range=[0,season_aqi['AQI'].max()+25],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig2,use_container_width=True)
with col2:
    for icon,name,months_,aqi,color,desc in [
        ("❄️","Winter","Dec–Feb","155","#74B9FF","Worst season. Cold air traps pollutants near ground. Crop burning residue lingers."),
        ("🌸","Spring","Mar–May","121","#55EFC4","Moderate. Temperatures rise, winds improve dispersion of pollutants."),
        ("☀️","Summer","Jun–Sep","90","#FDCB6E","Best season. Monsoon rains wash away PM2.5 and PM10 from the atmosphere."),
        ("🍂","Autumn","Oct–Nov","127","#E17055","Gets worse. Crop burning season begins. Cold air starts to return."),
    ]:
        st.markdown(f"<div style='background:{t['CARD']};border-left:4px solid {color};border:1px solid {t['BORDER']};border-radius:10px;padding:14px 16px;margin-bottom:10px;'><div style='display:flex;justify-content:space-between;align-items:center;'><span style='font-size:1rem;font-weight:700;color:{t['TEXT']};'>{icon} {name} <span style='color:{t['SUBTEXT']};font-size:0.8rem;'>({months_})</span></span><span style='font-family:Orbitron;font-size:1.1rem;font-weight:700;color:{color};'>AQI {aqi}</span></div><p style='color:{t['SUBTEXT']};font-size:0.82rem;margin:8px 0 0 0;line-height:1.4;'>{desc}</p></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Heatmap
st.markdown("<div class='section-title'>🔥 Year × Month Heatmap</div>", unsafe_allow_html=True)
pivot = df.pivot_table(values='AQI',index='year',columns='month',aggfunc='mean').round(0)
pivot.columns = MONTHS
fig3 = go.Figure(data=go.Heatmap(z=pivot.values,x=MONTHS,y=pivot.index.tolist(),
    colorscale=[[0,"#2DC653"],[0.3,"#F9C74F"],[0.6,"#F4A261"],[0.8,"#E63946"],[1,"#6C1515"]],
    hoverongaps=False,hovertemplate="<b>Year:</b> %{y}<br><b>Month:</b> %{x}<br><b>AQI:</b> %{z:.0f}<extra></extra>",
    text=pivot.values.astype(int),texttemplate="%{text}",textfont=dict(size=10,color="white"),
    colorbar=dict(title=dict(text="AQI",font=dict(color=t['TEXT'])),tickfont=dict(color=t['SUBTEXT']))))
fig3.update_layout(**CL,height=520,title="AQI Heatmap — Every Year × Every Month",xaxis_title="Month",yaxis_title="Year")
fig3.update_xaxes(tickfont=dict(color=t['TEXT'],size=11))
fig3.update_yaxes(tickmode='linear',tickfont=dict(color=t['TEXT'],size=11))
st.plotly_chart(fig3,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> December 2018 (AQI 202) is the single worst month-year combination in 15 years. Jul–Aug columns are consistently light green across ALL years. The 2020 row is visibly lighter due to COVID lockdown. The 2024 row is the lightest overall.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# State comparison
st.markdown("<div class='section-title'>🗺️ State-wise Seasonal Comparison</div>", unsafe_allow_html=True)
all_states = sorted(df['state'].dropna().unique().tolist())
sel_state = st.selectbox("🗺️ Select State to Compare",all_states,index=all_states.index('Punjab') if 'Punjab' in all_states else 0)
state_monthly = df[df['state']==sel_state].groupby('month')['AQI'].mean().reset_index()
india_monthly = df.groupby('month')['AQI'].mean().reset_index()
state_monthly['month_name'] = state_monthly['month'].apply(lambda x: MONTHS[x-1])
india_monthly['month_name'] = india_monthly['month'].apply(lambda x: MONTHS[x-1])
fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=state_monthly['month_name'],y=state_monthly['AQI'],name=sel_state,mode='lines+markers',line=dict(color="#E63946",width=3),marker=dict(size=8,color="#E63946",line=dict(color=t['CARD'],width=2)),hovertemplate=f"<b>{sel_state}</b><br>%{{x}}: %{{y:.1f}}<extra></extra>"))
fig4.add_trace(go.Scatter(x=india_monthly['month_name'],y=india_monthly['AQI'],name="India Average",mode='lines+markers',line=dict(color=t['ACCENT'],width=2,dash='dot'),marker=dict(size=6,color=t['ACCENT']),hovertemplate="<b>India Avg</b><br>%{x}: %{y:.1f}<extra></extra>"))
fig4.update_layout(**CL,title=f"{sel_state} vs India — Monthly AQI Pattern",height=400,xaxis_title="Month",yaxis_title="Average AQI",showlegend=True)
fig4.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=12))
fig4.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig4,use_container_width=True)
if not state_monthly.empty:
    worst=state_monthly.loc[state_monthly['AQI'].idxmax()]; best=state_monthly.loc[state_monthly['AQI'].idxmin()]
    diff=state_monthly['AQI'].mean()-india_monthly['AQI'].mean()
    sm1,sm2,sm3,sm4 = st.columns(4)
    for col,val,lbl,color in [(sm1,worst['month_name'],f"Worst Month in {sel_state}","#E63946"),(sm2,f"{worst['AQI']:.0f}","Worst Month AQI","#E63946"),(sm3,best['month_name'],f"Best Month in {sel_state}","#2DC653"),(sm4,f"{'+' if diff>0 else ''}{diff:.0f}","vs India Avg","#E63946" if diff>0 else "#2DC653")]:
        with col:
            st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-radius:12px;padding:16px;text-align:center;margin-top:8px;'><div style='font-family:Orbitron;font-size:1.4rem;font-weight:700;color:{color};'>{val}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};margin-top:4px;'>{lbl}</div></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Crop burning explainer
st.markdown("<div class='section-title' style='border-color:#F4A261;'>🌾 Why November is Always Worst</div>", unsafe_allow_html=True)
ce1,ce2,ce3 = st.columns(3)
for col,(icon,title_,desc) in zip([ce1,ce2,ce3],[
    ("🌾","Paddy Stubble Burning","After rice harvest in Oct–Nov, farmers in Punjab and Haryana burn crop residue to clear fields. This releases massive amounts of PM2.5, PM10, CO and NH3 simultaneously."),
    ("❄️","Temperature Inversion","In winter, cold air near the ground gets trapped under warmer air above — like a lid on a pot. This prevents pollutants from rising and dispersing."),
    ("💨","Combined Effect","When crop burning smoke meets temperature inversion, AQI spikes dramatically. Punjab's November AQI of 179 is the result of both factors hitting simultaneously every year."),
]):
    with col:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid #F4A261;border-top:4px solid #F4A261;border-radius:14px;padding:18px;'><div style='font-size:1.6rem;margin-bottom:8px;'>{icon}</div><div style='font-size:0.92rem;font-weight:700;color:{t['TEXT']};margin-bottom:6px;'>{title_}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};line-height:1.5;'>{desc}</div></div>", unsafe_allow_html=True)
