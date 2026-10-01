import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all_data
from Theme import get_theme, inject_theme_css, get_chart_layout, render_sidebar, MONTHS, bar_color_from_aqi

st.set_page_config(page_title="Station Analysis — India AQI", page_icon="📡", layout="wide")
t = get_theme(); inject_theme_css(t); CL = get_chart_layout(t)
year_range = render_sidebar(t)

with st.spinner("Loading data..."):
    df, stations, pollutants = load_all_data()
df = df[(df['year']>=year_range[0])&(df['year']<=year_range[1])]

st.markdown(f"<div style='margin-bottom:24px;'><p style='color:{t['ACCENT']};font-size:0.85rem;font-weight:700;letter-spacing:4px;'>PHASE 5 ANALYSIS</p><h1 style='font-family:Poppins;font-size:2.2rem;font-weight:700;color:{t['TEXT']};margin:0;'>📡 Station Analysis</h1><p style='color:{t['SUBTEXT']};font-size:0.95rem;margin-top:8px;'>Deep dive into India's 483 individual monitoring stations.</p></div>", unsafe_allow_html=True)
st.markdown("---")

worst_stn = df.groupby('station_code')['AQI'].mean().idxmax()
worst_aqi = df.groupby('station_code')['AQI'].mean().max()
k1,k2,k3,k4 = st.columns(4)
for col,val,lbl,color in [(k1,str(df['station_code'].nunique()),"Monitoring Stations",t['ACCENT']),(k2,str(df['city'].nunique()),"Cities Covered","#A8E063"),(k3,str(df['state'].nunique()),"States Covered","#F9C74F"),(k4,f"{worst_aqi:.0f}","Worst Station AQI","#E63946")]:
    with col:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-radius:14px;padding:18px 10px;text-align:center;box-shadow:0 0 16px {color}22;'><div style='font-family:Orbitron;font-size:1.5rem;font-weight:700;color:{color};white-space:nowrap;'>{val}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};margin-top:6px;line-height:1.3;'>{lbl}</div></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>🔴 Top 15 Most Polluted Stations</div>", unsafe_allow_html=True)
stn_aqi = df.groupby('station_code')['AQI'].mean().sort_values(ascending=False).head(15).reset_index()
stn_aqi = stn_aqi.merge(df[['station_code','city','state']].drop_duplicates(),on='station_code',how='left')
stn_aqi['label'] = stn_aqi['station_code']+" — "+stn_aqi['city'].fillna("Unknown")+" ("+stn_aqi['state'].fillna("")+")"
fig1 = go.Figure(go.Bar(x=stn_aqi['AQI'].round(0).astype(int),y=stn_aqi['label'],orientation='h',
    marker_color=stn_aqi['AQI'].apply(lambda x:'#E63946' if x>170 else '#F4A261' if x>150 else '#F9C74F'),
    text=stn_aqi['AQI'].round(0).astype(int),textposition='inside',textfont=dict(color='white',size=11,family='Orbitron'),
    hovertemplate="<b>%{y}</b><br>Avg AQI: %{x}<extra></extra>"))
fig1.update_layout(**CL,title="Top 15 Most Polluted Monitoring Stations in India",height=520,xaxis_title="Average AQI",yaxis_title="",showlegend=False)
fig1.update_xaxes(range=[0,230],gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig1.update_yaxes(autorange='reversed',gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=11))
st.plotly_chart(fig1,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> UN82 (PCBA) is the most polluted station at ~197 AQI — an industrial monitoring zone not a residential area. 7 out of top 15 stations are in Delhi NCT. UP15 (Ghaziabad) and WB19 (Howrah) are the only non-Delhi entries.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>🟢 Top 10 Cleanest Stations</div>", unsafe_allow_html=True)
clean_stn = df.groupby('station_code')['AQI'].mean().sort_values().head(10).reset_index()
clean_stn = clean_stn.merge(df[['station_code','city','state']].drop_duplicates(),on='station_code',how='left')
clean_stn['label'] = clean_stn['station_code']+" — "+clean_stn['city'].fillna("Unknown")+" ("+clean_stn['state'].fillna("")+")"
fig2 = go.Figure(go.Bar(x=clean_stn['AQI'].round(0).astype(int),y=clean_stn['label'],orientation='h',
    marker_color=clean_stn['AQI'].apply(lambda x:'#2DC653' if x<=50 else '#A8E063' if x<=75 else '#F9C74F'),
    text=clean_stn['AQI'].round(0).astype(int),textposition='inside',textfont=dict(color='white',size=11,family='Orbitron'),
    hovertemplate="<b>%{y}</b><br>Avg AQI: %{x}<extra></extra>"))
fig2.update_layout(**CL,title="Top 10 Cleanest Monitoring Stations in India",height=420,xaxis_title="Average AQI",yaxis_title="",showlegend=False)
fig2.update_xaxes(range=[0,100],gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig2.update_yaxes(autorange='reversed',gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=11))
st.plotly_chart(fig2,use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>🏙️ AQI Variation Within a City</div>", unsafe_allow_html=True)
city_stn_counts = df.groupby('city')['station_code'].nunique()
multi_stn_cities = sorted(city_stn_counts[city_stn_counts>1].index.tolist())
sel_city = st.selectbox("🏙️ Select City with Multiple Stations",multi_stn_cities,index=multi_stn_cities.index('Delhi') if 'Delhi' in multi_stn_cities else 0)
city_stns = df[df['city']==sel_city].groupby('station_code')['AQI'].mean().sort_values(ascending=False).reset_index()
fig3 = go.Figure(go.Bar(x=city_stns['AQI'].round(0).astype(int),y=city_stns['station_code'],orientation='h',
    marker_color=[bar_color_from_aqi(a) for a in city_stns['AQI']],
    text=city_stns['AQI'].round(0).astype(int),textposition='inside',textfont=dict(color='white',size=11,family='Orbitron'),
    hovertemplate="<b>Station: %{y}</b><br>Avg AQI: %{x}<extra></extra>"))
fig3.update_layout(**CL,title=f"AQI Variation Across All Stations in {sel_city}",height=max(300,len(city_stns)*40),xaxis_title="Average AQI",yaxis_title="",showlegend=False)
fig3.update_xaxes(range=[0,city_stns['AQI'].max()+30],gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig3.update_yaxes(autorange='reversed',gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=11))
st.plotly_chart(fig3,use_container_width=True)
mx=city_stns['AQI'].max(); mn=city_stns['AQI'].min(); gap=mx-mn
sv1,sv2,sv3 = st.columns(3)
for col,val,lbl,color in [(sv1,f"{mx:.0f}",f"Most Polluted Station in {sel_city}","#E63946"),(sv2,f"{mn:.0f}",f"Cleanest Station in {sel_city}","#2DC653"),(sv3,f"{gap:.0f}","AQI Gap Within Same City",t['ACCENT'])]:
    with col:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-radius:12px;padding:16px;text-align:center;margin-top:8px;'><div style='font-family:Orbitron;font-size:1.5rem;font-weight:700;color:{color};'>{val}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};margin-top:4px;line-height:1.3;'>{lbl}</div></div>", unsafe_allow_html=True)
st.markdown(f"<div class='insight-box' style='margin-top:12px;'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> Even within {sel_city}, AQI varies by <b style='color:{t['TEXT']}'>{gap:.0f} points</b> between the most and least polluted station. Where you live within a city matters enormously for daily air quality.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>📈 Station AQI Trend Explorer</div>", unsafe_allow_html=True)
all_stns = sorted(df['station_code'].dropna().unique().tolist())
sel_stn = st.selectbox("📡 Select Station Code",all_stns,index=all_stns.index('PB03') if 'PB03' in all_stns else 0)
stn_df = df[df['station_code']==sel_stn]
stn_city = stn_df['city'].mode()[0] if not stn_df.empty else "Unknown"
stn_state = stn_df['state'].mode()[0] if not stn_df.empty else "Unknown"
stn_trend = stn_df.groupby('year')['AQI'].mean().reset_index()
stn_monthly = stn_df.groupby('month')['AQI'].mean().reset_index()
stn_monthly['month_name'] = stn_monthly['month'].apply(lambda x: MONTHS[x-1])
st.markdown(f"<div style='background:{t['CARD']};border:1px solid {t['ACCENT']};border-radius:12px;padding:14px 20px;margin-bottom:16px;'><span style='color:{t['SUBTEXT']};font-size:0.88rem;'>📡 <b style='color:{t['TEXT']}'>Station:</b> {sel_stn} &nbsp;|&nbsp; 🏙️ <b style='color:{t['TEXT']}'>City:</b> {stn_city} &nbsp;|&nbsp; 🗺️ <b style='color:{t['TEXT']}'>State:</b> {stn_state} &nbsp;|&nbsp; 📊 <b style='color:{t['TEXT']}'>Avg AQI:</b> <span style='color:{t['ACCENT']};font-family:Orbitron;'>{stn_df['AQI'].mean():.0f}</span></span></div>", unsafe_allow_html=True)
tc1,tc2 = st.columns(2)
with tc1:
    nat_avg = df.groupby('year')['AQI'].mean().reset_index()
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=stn_trend['year'],y=stn_trend['AQI'],name=sel_stn,mode='lines+markers',line=dict(color=t['ACCENT'],width=3),marker=dict(size=8,color=t['ACCENT'],line=dict(color=t['CARD'],width=2)),fill='tozeroy',fillcolor="rgba(0,212,255,0.06)" if t['is_dark'] else "rgba(0,119,182,0.06)"))
    fig4.add_trace(go.Scatter(x=nat_avg['year'],y=nat_avg['AQI'],name="National Avg",mode='lines',line=dict(color="#F9C74F",width=2,dash='dot')))
    fig4.update_layout(**CL,title=f"{sel_stn} ({stn_city}) — Yearly AQI Trend",height=340,xaxis_title="Year",yaxis_title="Average AQI",showlegend=True)
    fig4.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    fig4.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig4,use_container_width=True)
with tc2:
    fig5 = go.Figure(go.Bar(x=stn_monthly['month_name'],y=stn_monthly['AQI'],marker_color=[bar_color_from_aqi(a) for a in stn_monthly['AQI']],text=stn_monthly['AQI'].round(0).astype(int),textposition='outside',textfont=dict(color=t['TEXT'],size=10)))
    fig5.update_layout(**CL,title=f"{sel_stn} — Month-wise AQI Pattern",height=340,xaxis_title="Month",yaxis_title="Average AQI",showlegend=False)
    fig5.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=10))
    fig5.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],range=[0,stn_monthly['AQI'].max()+25],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig5,use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>🗺️ All Stations in a State</div>", unsafe_allow_html=True)
all_states_list = sorted(df['state'].dropna().unique().tolist())
sel_st = st.selectbox("🗺️ Select State",all_states_list,index=all_states_list.index('Punjab') if 'Punjab' in all_states_list else 0)
state_stns = df[df['state']==sel_st].groupby('station_code')['AQI'].mean().sort_values(ascending=False).reset_index()
state_stns = state_stns.merge(df[['station_code','city']].drop_duplicates(),on='station_code',how='left')
state_stns['label'] = state_stns['station_code']+" — "+state_stns['city'].fillna("Unknown")
fig6 = go.Figure(go.Bar(x=state_stns['AQI'].round(0).astype(int),y=state_stns['label'],orientation='h',marker_color=[bar_color_from_aqi(a) for a in state_stns['AQI']],text=state_stns['AQI'].round(0).astype(int),textposition='inside',textfont=dict(color='white',size=11,family='Orbitron'),hovertemplate="<b>%{y}</b><br>Avg AQI: %{x}<extra></extra>"))
fig6.update_layout(**CL,title=f"All Stations in {sel_st} — Ranked by AQI",height=max(300,len(state_stns)*50),xaxis_title="Average AQI",yaxis_title="",showlegend=False)
fig6.update_xaxes(range=[0,state_stns['AQI'].max()+30],gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig6.update_yaxes(autorange='reversed',gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=11))
st.plotly_chart(fig6,use_container_width=True)
