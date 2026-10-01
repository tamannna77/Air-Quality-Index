import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all_data
from Theme import get_theme, inject_theme_css, get_chart_layout, render_sidebar, MONTHS, bar_color_from_aqi

st.set_page_config(page_title="State & City — India AQI", page_icon="🗺️", layout="wide")
t = get_theme(); inject_theme_css(t); CL = get_chart_layout(t)
year_range = render_sidebar(t)

with st.spinner("Loading data..."):
    df, stations, pollutants = load_all_data()
df = df[(df['year']>=year_range[0])&(df['year']<=year_range[1])]

st.markdown(f"<div style='margin-bottom:24px;'><h1 style='font-family:Poppins;font-size:2.2rem;font-weight:700;color:{t['TEXT']};margin:0;'>🗺️ State & City Analysis</h1><p style='color:{t['SUBTEXT']};font-size:0.95rem;margin-top:8px;'>Comparing air quality across 20 Indian states and 240 cities.</p></div>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("<div class='section-title'>🏛️ State-wise AQI Comparison</div>", unsafe_allow_html=True)
c1,c2 = st.columns(2)
with c1:
    state_aqi = df.groupby('state')['AQI'].mean().sort_values(ascending=False).head(10).reset_index()
    fig1 = px.bar(state_aqi,x='AQI',y='state',orientation='h',color='AQI',color_continuous_scale=["#F9C74F","#F4A261","#E63946"],title="🔴 Top 10 Most Polluted States",text=state_aqi['AQI'].round(0).astype(int))
    fig1.update_traces(textposition='inside',textfont=dict(color='white',size=12,family='Orbitron'))
    fig1.update_layout(**CL,height=420,showlegend=False,coloraxis_showscale=False,xaxis_title="Average AQI",yaxis_title="")
    fig1.update_xaxes(range=[0,200],gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    fig1.update_yaxes(autorange='reversed',gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=11))
    st.plotly_chart(fig1,use_container_width=True)
with c2:
    all_states = df.groupby('state')['AQI'].mean().sort_values(ascending=False).reset_index()
    fig2 = px.bar(all_states,x='AQI',y='state',orientation='h',color='AQI',color_continuous_scale=[[0,"#2DC653"],[0.4,"#F9C74F"],[0.7,"#F4A261"],[1,"#E63946"]],title="🗺️ All States — AQI Ranking",text=all_states['AQI'].round(0).astype(int))
    fig2.update_traces(textposition='inside',textfont=dict(color='white',size=11,family='Orbitron'))
    fig2.update_layout(**CL,height=520,showlegend=False,coloraxis_showscale=False,xaxis_title="Average AQI",yaxis_title="")
    fig2.update_xaxes(range=[0,200],gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    fig2.update_yaxes(autorange='reversed',gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=10))
    st.plotly_chart(fig2,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> Delhi NCT leads at ~161 AQI. Bihar, Haryana and Punjab form the polluted North India belt. Southern states like Telangana and Karnataka are cleanest.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>📈 State AQI Trend Explorer</div>", unsafe_allow_html=True)
all_state_list = sorted(df['state'].dropna().unique().tolist())
sel_state = st.selectbox("🗺️ Select a State",all_state_list,index=all_state_list.index('Punjab') if 'Punjab' in all_state_list else 0)
state_trend = df[df['state']==sel_state].groupby('year')['AQI'].mean().reset_index()
nat_avg = df.groupby('year')['AQI'].mean().reset_index()
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=state_trend['year'],y=state_trend['AQI'],fill='tozeroy',fillcolor="rgba(0,212,255,0.08)" if t['is_dark'] else "rgba(0,119,182,0.08)",line=dict(color=t['ACCENT'],width=3),mode='lines+markers',marker=dict(size=8,color=t['ACCENT'],line=dict(color=t['CARD'],width=2)),name=sel_state,hovertemplate=f"<b>{sel_state}</b><br>Year: %{{x}}<br>AQI: %{{y:.1f}}<extra></extra>"))
fig3.add_trace(go.Scatter(x=nat_avg['year'],y=nat_avg['AQI'],line=dict(color="#F9C74F",width=2,dash='dot'),mode='lines',name="National Avg"))
fig3.update_layout(**CL,height=380,title=f"{sel_state} AQI Trend vs National Average",xaxis_title="Year",yaxis_title="Average AQI",showlegend=True)
fig3.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig3.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig3,use_container_width=True)
s_avg=state_trend['AQI'].mean(); diff=s_avg-df['AQI'].mean()
sc1,sc2,sc3,sc4 = st.columns(4)
for col,val,lbl,color in [(sc1,f"{s_avg:.0f}",f"{sel_state} Avg AQI",t['ACCENT']),(sc2,f"{state_trend['AQI'].max():.0f}","Worst Year AQI","#E63946"),(sc3,f"{state_trend['AQI'].min():.0f}","Best Year AQI","#2DC653"),(sc4,f"{'+' if diff>0 else ''}{diff:.0f}","vs National Avg","#E63946" if diff>0 else "#2DC653")]:
    with col:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-radius:12px;padding:16px;text-align:center;margin-top:8px;'><div style='font-family:Orbitron;font-size:1.6rem;font-weight:700;color:{color};'>{val}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};margin-top:4px;'>{lbl}</div></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>🏙️ City-Level Analysis</div>", unsafe_allow_html=True)
cc1,cc2 = st.columns(2)
with cc1:
    top10 = df.groupby('city')['AQI'].mean().sort_values(ascending=False).head(10).reset_index()
    fig4 = px.bar(top10,x='AQI',y='city',orientation='h',color='AQI',color_continuous_scale=["#F9C74F","#F4A261","#E63946"],title="🔴 Top 10 Most Polluted Cities",text=top10['AQI'].round(0).astype(int))
    fig4.update_traces(textposition='inside',textfont=dict(color='white',size=12,family='Orbitron'))
    fig4.update_layout(**CL,height=420,showlegend=False,coloraxis_showscale=False,xaxis_title="Average AQI",yaxis_title="")
    fig4.update_xaxes(range=[0,230],gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    fig4.update_yaxes(autorange='reversed',gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=11))
    st.plotly_chart(fig4,use_container_width=True)
with cc2:
    clean10 = df.groupby('city')['AQI'].mean().sort_values().head(10).reset_index()
    fig5 = px.bar(clean10,x='AQI',y='city',orientation='h',color='AQI',color_continuous_scale=["#2DC653","#A8E063","#F9C74F"],title="🟢 Top 10 Cleanest Cities",text=clean10['AQI'].round(0).astype(int))
    fig5.update_traces(textposition='inside',textfont=dict(color='white',size=12,family='Orbitron'))
    fig5.update_layout(**CL,height=420,showlegend=False,coloraxis_showscale=False,xaxis_title="Average AQI",yaxis_title="")
    fig5.update_xaxes(range=[0,90],gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    fig5.update_yaxes(autorange='reversed',gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=11))
    st.plotly_chart(fig5,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> PCBA tops polluted list at ~197 AQI. Aizawl in Mizoram leads cleanest cities at ~47 AQI — actually in the Good category. 4x difference between cleanest and most polluted.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>🔍 City AQI Explorer</div>", unsafe_allow_html=True)
all_cities = sorted(df['city'].dropna().unique().tolist())
sel_city = st.selectbox("🏙️ Select a City",all_cities,index=all_cities.index('Amritsar') if 'Amritsar' in all_cities else 0)
city_trend = df[df['city']==sel_city].groupby('year')['AQI'].mean().reset_index()
city_monthly = df[df['city']==sel_city].groupby('month')['AQI'].mean().reset_index()
city_monthly['month_name'] = city_monthly['month'].apply(lambda x: MONTHS[x-1])
cd1,cd2 = st.columns(2)
with cd1:
    fig6 = px.line(city_trend,x='year',y='AQI',markers=True,color_discrete_sequence=[t['ACCENT']],title=f"{sel_city} — Yearly AQI Trend")
    fig6.update_traces(line_width=2.5,marker_size=7)
    fig6.update_layout(**CL,height=320,xaxis_title="Year",yaxis_title="Average AQI")
    fig6.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    fig6.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig6,use_container_width=True)
with cd2:
    fig7 = px.bar(city_monthly,x='month_name',y='AQI',color='AQI',color_continuous_scale=["#2DC653","#F9C74F","#E63946"],title=f"{sel_city} — Month-wise AQI Pattern")
    fig7.update_layout(**CL,height=320,showlegend=False,coloraxis_showscale=False,xaxis_title="Month",yaxis_title="Average AQI")
    fig7.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=10))
    fig7.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig7,use_container_width=True)
city_avg = city_trend['AQI'].mean() if not city_trend.empty else 0
worst_m = city_monthly.loc[city_monthly['AQI'].idxmax(),'month_name'] if not city_monthly.empty else "N/A"
best_m = city_monthly.loc[city_monthly['AQI'].idxmin(),'month_name'] if not city_monthly.empty else "N/A"
vs_nat = city_avg - df['AQI'].mean()
cm1,cm2,cm3,cm4 = st.columns(4)
for col,val,lbl,color in [(cm1,f"{city_avg:.0f}",f"{sel_city} Avg AQI",t['ACCENT']),(cm2,worst_m,"Worst Month","#E63946"),(cm3,best_m,"Best Month","#2DC653"),(cm4,f"{'+' if vs_nat>0 else ''}{vs_nat:.0f}","vs National Avg","#E63946" if vs_nat>0 else "#2DC653")]:
    with col:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-radius:12px;padding:16px;text-align:center;margin-top:8px;'><div style='font-family:Orbitron;font-size:1.4rem;font-weight:700;color:{color};'>{val}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};margin-top:4px;'>{lbl}</div></div>", unsafe_allow_html=True)
