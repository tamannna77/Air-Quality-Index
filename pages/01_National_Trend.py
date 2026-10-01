import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import load_all_data
from Theme import get_theme, inject_theme_css, get_chart_layout, render_sidebar, MONTHS

st.set_page_config(page_title="National Trend — India AQI", page_icon="📈", layout="wide")
t = get_theme(); inject_theme_css(t); CL = get_chart_layout(t)
year_range = render_sidebar(t)

with st.spinner("Loading data..."):
    df, stations, pollutants = load_all_data()
df = df[(df['year']>=year_range[0])&(df['year']<=year_range[1])]

st.markdown(f"<div style='margin-bottom:24px;'><p style='color:{t['ACCENT']};font-size:0.85rem;font-weight:700;letter-spacing:4px;margin-bottom:4px;'>PHASE 3 ANALYSIS</p><h1 style='font-family:Poppins;font-size:2.2rem;font-weight:700;color:{t['TEXT']};margin:0;'>📈 National AQI Trend</h1><p style='color:{t['SUBTEXT']};font-size:0.95rem;margin-top:8px;'>Tracking India's air quality journey from 2009 to 2024 across 483 monitoring stations.</p></div>", unsafe_allow_html=True)
st.markdown("---")

# Chart 1 — Yearly line
st.markdown("<div class='section-title'>📉 India Average AQI — Year by Year</div>", unsafe_allow_html=True)
yearly = df.groupby('year')['AQI'].mean().reset_index()
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=yearly['year'],y=yearly['AQI'],fill='tozeroy',
    fillcolor="rgba(0,212,255,0.08)" if t['is_dark'] else "rgba(0,119,182,0.08)",
    line=dict(color=t['ACCENT'],width=3),mode='lines+markers',
    marker=dict(size=8,color=t['ACCENT'],line=dict(color=t['CARD'],width=2)),
    hovertemplate="<b>Year:</b> %{x}<br><b>Avg AQI:</b> %{y:.1f}<extra></extra>"))
fig1.add_vrect(x0=2019.8,x1=2020.8,fillcolor="rgba(45,198,83,0.12)",line_width=0,
    annotation_text="😷 COVID Lockdown",annotation_position="top left",
    annotation_font_color="#2DC653",annotation_font_size=11)
peak_yr = yearly.loc[yearly['AQI'].idxmax(),'year']
peak_aqi = yearly['AQI'].max()
fig1.add_annotation(x=peak_yr,y=peak_aqi,text=f"📍 Peak: {peak_aqi:.0f}",showarrow=True,
    arrowhead=2,arrowcolor="#E63946",font=dict(color="#E63946",size=11),
    bgcolor=t['CARD'],bordercolor="#E63946")
fig1.update_layout(**CL,height=400,xaxis_title="Year",yaxis_title="Average AQI",showlegend=False,title="India National Average AQI Trend (2009–2024)")
fig1.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig1.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig1,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> India's AQI peaked around 2016–2018. The sharp dip in 2020 during COVID-19 lockdowns proves industrial and vehicular activity are the primary pollution drivers. 2024 records the lowest AQI in 15 years at ~113.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Chart 2 — Box plot
st.markdown("<div class='section-title'>📦 AQI Distribution Per Year</div>", unsafe_allow_html=True)
fig2 = px.box(df,x='year',y='AQI',color_discrete_sequence=[t['ACCENT']],title="Year-wise AQI Distribution — Spread & Outliers")
fig2.update_layout(**CL,height=420,xaxis_title="Year",yaxis_title="AQI")
fig2.update_traces(marker_color=t['ACCENT'],line_color=t['ACCENT'],
    fillcolor="rgba(0,212,255,0.15)" if t['is_dark'] else "rgba(0,119,182,0.15)",marker_outliercolor="#E63946")
fig2.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
fig2.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig2,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> 2009–2014 boxes are flat — fewer stations were active. From 2015 boxes become fuller. Red outlier dots above 600–900 AQI appear every year representing extreme events like Diwali, crop burning and dust storms.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Chart 3 — Heatmap
st.markdown("<div class='section-title'>🔥 Year × Month AQI Heatmap</div>", unsafe_allow_html=True)
pivot = df.pivot_table(values='AQI',index='year',columns='month',aggfunc='mean').round(0)
pivot.columns = MONTHS
fig3 = go.Figure(data=go.Heatmap(z=pivot.values,x=MONTHS,y=pivot.index.tolist(),
    colorscale=[[0,"#2DC653"],[0.3,"#F9C74F"],[0.6,"#F4A261"],[0.8,"#E63946"],[1,"#6C1515"]],
    hoverongaps=False,hovertemplate="<b>Year:</b> %{y}<br><b>Month:</b> %{x}<br><b>AQI:</b> %{z:.0f}<extra></extra>",
    text=pivot.values.astype(int),texttemplate="%{text}",textfont=dict(size=10,color="white"),
    colorbar=dict(title=dict(text="AQI",font=dict(color=t['TEXT'])),tickfont=dict(color=t['SUBTEXT']))))
fig3.update_layout(**CL,height=520,title="AQI Heatmap — Every Year × Every Month (2009–2024)",xaxis_title="Month",yaxis_title="Year")
fig3.update_xaxes(tickfont=dict(color=t['TEXT'],size=11))
fig3.update_yaxes(tickmode='linear',tickfont=dict(color=t['TEXT'],size=11))
st.plotly_chart(fig3,use_container_width=True)
st.markdown(f"<div class='insight-box'>💡 <b style='color:{t['TEXT']}'>Key Insight:</b> December 2018 (AQI 202) is the single worst month-year in 15 years. The Jul–Aug columns are consistently light green across ALL years — monsoon provides reliable annual relief. The 2020 row is visibly lighter due to COVID lockdown.</div>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Chart 4 — COVID comparison
st.markdown("<div class='section-title'>😷 Pre-COVID vs COVID vs Post-COVID</div>", unsafe_allow_html=True)
df['era'] = pd.cut(df['year'],bins=[2008,2019,2020,2024],labels=['Pre-COVID (2009–2019)','COVID Year (2020)','Post-COVID (2021–2024)'])
era_aqi = df.groupby('era',observed=True)['AQI'].mean().reset_index()
fig4 = px.bar(era_aqi,x='era',y='AQI',color='era',
    color_discrete_map={'Pre-COVID (2009–2019)':'#F4A261','COVID Year (2020)':'#2DC653','Post-COVID (2021–2024)':t['ACCENT']},
    text=era_aqi['AQI'].round(1),title="Average AQI Across Three Eras")
fig4.update_traces(textposition='outside',textfont=dict(color=t['TEXT'],size=13,family='Orbitron'))
fig4.update_layout(**CL,height=380,showlegend=False,xaxis_title="",yaxis_title="Average AQI")
fig4.update_xaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['TEXT']))
fig4.update_yaxes(gridcolor=t['GRID'],linecolor=t['GRID'],tickfont=dict(color=t['SUBTEXT']))
st.plotly_chart(fig4,use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

yearly_all = df.groupby('year')['AQI'].mean()
s1,s2,s3,s4 = st.columns(4)
for col,val,lbl,color in [
    (s1,f"{yearly_all.max():.0f}",f"Worst Year Avg ({int(yearly_all.idxmax())})","#E63946"),
    (s2,f"{yearly_all.min():.0f}",f"Best Year Avg ({int(yearly_all.idxmin())})","#2DC653"),
    (s3,f"{yearly_all.mean():.0f}","15-Year Overall Avg",t['ACCENT']),
    (s4,f"{yearly_all.iloc[-1]-yearly_all.iloc[0]:.0f}","AQI Change (2009→2024)","#F9C74F"),
]:
    with col:
        st.markdown(f"<div style='background:{t['CARD']};border:1px solid {color};border-radius:14px;padding:20px;text-align:center;'><div style='font-family:Orbitron;font-size:1.8rem;font-weight:700;color:{color};'>{val}</div><div style='font-size:0.8rem;color:{t['SUBTEXT']};margin-top:6px;'>{lbl}</div></div>", unsafe_allow_html=True)
