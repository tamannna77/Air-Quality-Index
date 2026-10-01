import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all_data
from Theme import get_theme, inject_theme_css, get_chart_layout, render_sidebar, MONTHS, bar_color_from_aqi

st.set_page_config(page_title="Punjab Spotlight — India AQI", page_icon="🌾", layout="wide")
t = get_theme(); inject_theme_css(t); CL = get_chart_layout(t)
year_range = render_sidebar(t)

with st.spinner("Loading data..."):
    df, stations, pollutants = load_all_data()
df = df[(df['year']>=year_range[0])&(df['year']<=year_range[1])]
punjab = df[df['state']=='Punjab']
ORANGE = "#F4A261"

st.markdown(f"<div style='background:linear-gradient(135deg,{t['CARD']} 0%,{t['BG']} 100%);border-radius:20px;padding:32px 40px;margin-bottom:24px;border:1px solid {t['BORDER']};border-left:6px solid {ORANGE};'><p style='color:{ORANGE};font-size:0.85rem;font-weight:700;letter-spacing:4px;margin-bottom:4px;'>PUNJAB SPOTLIGHT</p><h1 style='font-family:Poppins;font-size:2.2rem;font-weight:700;color:{t['TEXT']};margin:0;'>🌾 Punjab Air Quality Analysis</h1><p style='color:{t['SUBTEXT']};font-size:0.95rem;margin-top:10px;max-width:700px;line-height:1.7;'>A deep dive into Punjab's unique air quality challenges — from paddy stubble burning to industrial pollution in Bathinda and Ludhiana, and what it means for cities like <b style='color:{t['TEXT']}'>Amritsar.</b></p></div>", unsafe_allow_html=True)
st.markdown("---")

punjab_avg=punjab['AQI'].mean(); india_avg=df['AQI'].mean(); diff=punjab_avg-india_avg
nov_aqi=punjab[punjab['month']==11]['AQI'].mean(); aug_aqi=punjab[punjab['month']==8]['AQI'].mean()
k1,k2,k3,k4,k5 = st.columns(5)
for col,val,lbl,color in [(k1,f"{punjab_avg:.0f}","Punjab Avg AQI",ORANGE),(k2,f"{india_avg:.0f}","India Avg AQI",t['ACCENT']),(k3,f"+{diff:.0f}","Above National Avg","#E63946"),(k4,f"{nov_aqi:.0f}","November AQI (Worst)","#E63946"),(k5,f"{aug_aqi:.0f}","August AQI (Best)","#2DC653")]:
    with col:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-radius:14px;padding:18px 10px;text-align:center;box-shadow:0 0 16px {color}22;'><div style='font-family:Orbitron;font-size:1.5rem;font-weight:700;color:{color};white-space:nowrap;'>{val}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};margin-top:6px;line-height:1.3;'>{lbl}</div></div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Punjab vs India yearly
st.markdown(f"<div class='section-title' style='border-color:{ORANGE}'>📈 Punjab vs India — AQI Trend</div>", unsafe_allow_html=True)
punjab_yearly = punjab.groupby('year')['AQI'].mean().reset_index()
india_yearly  = df.groupby('year')['AQI'].mean().reset_index()
common_yrs    = set(punjab_yearly['year']) & set(india_yearly['year'])
punjab_yearly = punjab_yearly[punjab_yearly['year'].isin(common_yrs)]
india_yearly  = india_yearly[india_yearly['year'].isin(common_yrs)]
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=punjab_yearly['year'].tolist()+india_yearly['year'].tolist()[::-1],y=punjab_yearly['AQI'].tolist()+india_yearly['AQI'].tolist()[::-1],fill='toself',fillcolor="rgba(244,162,97,0.1)",line=dict(color='rgba(0,0,0,0)'),showlegend=False,hoverinfo='skip'))
fig1.add_trace(go.Scatter(x=punjab_yearly['year'],y=punjab_yearly['AQI'],name="Punjab",mode='lines+markers',line=dict(color=ORANGE,width=3),marker=dict(size=8,color=ORANGE,line=dict(color=t['CARD'],width=2)),hovertemplate="<b>Punjab</b><br>Year: %{x}<br>AQI: %{y:.1f}<extra></extra>"))
fig1.add_trace(go.Scatter(x=india_yearly['year'],y=india_yearly['AQI'],name="India Average",mode='lines+markers',line=dict(color=t['ACCENT'],width=2,dash='dot'),marker=dict(size=6,color=t['ACCENT']),hovertemplate="<b>India Avg</b><br>Year: %{x}<br>AQI: %{y:.1f}<extra></extra>"))
fig1.update_layout(**CL,title="Punjab AQI vs India National Average — Year by Year",height=400,xaxis_title="Year",yaxis_title="Average AQI",showlegend=True)
fig1.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig1.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig1,use_container_width=True)
st.markdown(f"<div class='insight-box' style='border-color:{ORANGE};'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> Punjab consistently stays above India's national average every single year. Both show a dip in 2020 due to COVID lockdown but Punjab recovered to higher levels faster. The widening gap in 2023–2024 suggests India is improving faster than Punjab.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Monthly pattern
st.markdown(f"<div class='section-title' style='border-color:{ORANGE}'>📅 Monthly AQI — Punjab vs India</div>", unsafe_allow_html=True)
punjab_monthly = punjab.groupby('month')['AQI'].mean().reset_index()
india_monthly  = df.groupby('month')['AQI'].mean().reset_index()
punjab_monthly['month_name'] = punjab_monthly['month'].apply(lambda x: MONTHS[x-1])
india_monthly['month_name']  = india_monthly['month'].apply(lambda x: MONTHS[x-1])
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=punjab_monthly['month_name'],y=punjab_monthly['AQI'],name="Punjab",mode='lines+markers',line=dict(color=ORANGE,width=3),marker=dict(size=9,color=ORANGE,line=dict(color=t['CARD'],width=2)),fill='tozeroy',fillcolor="rgba(244,162,97,0.08)",hovertemplate="<b>Punjab</b><br>%{x}: %{y:.1f}<extra></extra>"))
fig2.add_trace(go.Scatter(x=india_monthly['month_name'],y=india_monthly['AQI'],name="India Average",mode='lines+markers',line=dict(color=t['ACCENT'],width=2,dash='dot'),marker=dict(size=6,color=t['ACCENT']),hovertemplate="<b>India Avg</b><br>%{x}: %{y:.1f}<extra></extra>"))
nov_val = punjab_monthly[punjab_monthly['month']==11]['AQI'].values
if len(nov_val)>0:
    fig2.add_annotation(x="Nov",y=nov_val[0],text="🌾 Stubble Burning Peak",showarrow=True,arrowhead=2,arrowcolor=ORANGE,font=dict(color=ORANGE,size=11),bgcolor=t['CARD'],bordercolor=ORANGE,ax=-80,ay=-40)
fig2.update_layout(**CL,title="Month-wise AQI — Punjab vs India National Average",height=420,xaxis_title="Month",yaxis_title="Average AQI",showlegend=True)
fig2.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=12))
fig2.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig2,use_container_width=True)
st.markdown(f"<div class='insight-box' style='border-color:{ORANGE};'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> Punjab's November AQI of 179 is dramatically higher than any other month — directly caused by paddy stubble burning. May (135) is unusually high due to wheat harvesting dust. Punjab's best month (August ~95) is still higher than India's national best (84).</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Station ranking
st.markdown(f"<div class='section-title' style='border-color:{ORANGE}'>📡 Punjab Stations — AQI Ranking</div>", unsafe_allow_html=True)
if 'station_code' in punjab.columns:
    pjb_stns = punjab.groupby('station_code')['AQI'].mean().sort_values(ascending=False).reset_index()
    pjb_stns = pjb_stns.merge(df[['station_code','city']].drop_duplicates(),on='station_code',how='left')
    pjb_stns['label'] = pjb_stns['station_code']+" — "+pjb_stns['city'].fillna("Unknown")
    fig3 = go.Figure(go.Bar(x=pjb_stns['AQI'].round(0).astype(int),y=pjb_stns['label'],orientation='h',marker_color=[bar_color_from_aqi(a) for a in pjb_stns['AQI']],text=pjb_stns['AQI'].round(0).astype(int),textposition='inside',textfont=dict(color='white',size=12,family='Orbitron'),hovertemplate="<b>%{y}</b><br>Avg AQI: %{x}<extra></extra>"))
    fig3.update_layout(**CL,title="Punjab Monitoring Stations — Ranked by Average AQI",height=max(300,len(pjb_stns)*55),xaxis_title="Average AQI",yaxis_title="",showlegend=False)
    fig3.update_xaxes(range=[0,180],gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    fig3.update_yaxes(autorange='reversed',gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=12))
    st.plotly_chart(fig3,use_container_width=True)
st.markdown(f"<div class='insight-box' style='border-color:{ORANGE};'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> Bathinda is Punjab's most polluted station — home to India's largest thermal power plant. Ludhiana follows — Punjab's industrial capital. Amritsar sits at ~128 AQI — densely populated with heavy traffic but less heavy industry. Kalal Majra is the cleanest rural location.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Amritsar spotlight
st.markdown(f"<div class='section-title' style='border-color:{ORANGE}'>🕌 Amritsar — Your City</div>", unsafe_allow_html=True)
amritsar = df[df['city']=='Amritsar']
if not amritsar.empty:
    amritsar_yearly  = amritsar.groupby('year')['AQI'].mean().reset_index()
    amritsar_monthly = amritsar.groupby('month')['AQI'].mean().reset_index()
    amritsar_monthly['month_name'] = amritsar_monthly['month'].apply(lambda x: MONTHS[x-1])
    ac1,ac2 = st.columns(2)
    with ac1:
        fig4 = px.line(amritsar_yearly,x='year',y='AQI',markers=True,color_discrete_sequence=[ORANGE],title="Amritsar — Yearly AQI Trend")
        fig4.update_traces(line_width=2.5,marker_size=8)
        fig4.update_layout(**CL,height=320,xaxis_title="Year",yaxis_title="AQI")
        fig4.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
        fig4.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
        st.plotly_chart(fig4,use_container_width=True)
    with ac2:
        fig5 = go.Figure(go.Bar(x=amritsar_monthly['month_name'],y=amritsar_monthly['AQI'],marker_color=[bar_color_from_aqi(a) for a in amritsar_monthly['AQI']],text=amritsar_monthly['AQI'].round(0).astype(int),textposition='outside',textfont=dict(color=t['TEXT'],size=10)))
        fig5.update_layout(**CL,title="Amritsar — Month-wise AQI",height=320,xaxis_title="Month",yaxis_title="AQI",showlegend=False)
        fig5.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT'],size=10))
        fig5.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],range=[0,amritsar_monthly['AQI'].max()+25],tickfont=dict(color=t['SUBTEXT']))
        st.plotly_chart(fig5,use_container_width=True)
    am_avg=amritsar['AQI'].mean(); am_worst=amritsar_monthly.loc[amritsar_monthly['AQI'].idxmax(),'month_name']; am_best=amritsar_monthly.loc[amritsar_monthly['AQI'].idxmin(),'month_name']; am_vs=am_avg-df['AQI'].mean()
    am1,am2,am3,am4 = st.columns(4)
    for col,val,lbl,color in [(am1,f"{am_avg:.0f}","Amritsar Avg AQI",ORANGE),(am2,am_worst,"Worst Month","#E63946"),(am3,am_best,"Best Month","#2DC653"),(am4,f"+{am_vs:.0f}","Above National Avg","#E63946")]:
        with col:
            st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-radius:12px;padding:16px;text-align:center;margin-top:8px;'><div style='font-family:Orbitron;font-size:1.4rem;font-weight:700;color:{color};white-space:nowrap;'>{val}</div><div style='font-size:0.78rem;color:{t['SUBTEXT']};margin-top:4px;'>{lbl}</div></div>", unsafe_allow_html=True)
else:
    st.info("Amritsar data not found in dataset.")
st.markdown("<br>", unsafe_allow_html=True)

# Stubble burning timeline
st.markdown(f"<div class='section-title' style='border-color:{ORANGE}'>🔥 Stubble Burning — Impact Timeline</div>", unsafe_allow_html=True)
punjab_nov = punjab[punjab['month'].isin([10,11,12])]
if not punjab_nov.empty:
    nov_yearly = punjab_nov.groupby(['year','month'])['AQI'].mean().reset_index()
    nov_yearly['month_name'] = nov_yearly['month'].apply(lambda x: MONTHS[x-1])
    fig6 = px.line(nov_yearly,x='year',y='AQI',color='month_name',markers=True,color_discrete_map={'Oct':'#F9C74F','Nov':'#E63946','Dec':ORANGE},title="Punjab Oct–Nov–Dec AQI Over Years — Stubble Burning Season")
    fig6.update_traces(line_width=2.5,marker_size=7)
    fig6.update_layout(**CL,height=380,xaxis_title="Year",yaxis_title="Average AQI",showlegend=True)
    fig6.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    fig6.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
    st.plotly_chart(fig6,use_container_width=True)
st.markdown(f"<div class='insight-box' style='border-color:{ORANGE};'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> The November line (red) is consistently the highest across all years — confirming stubble burning is a persistent, annual, predictable pollution event. Despite government bans since 2015, the November AQI spike continues unabated every year.</div>", unsafe_allow_html=True)
