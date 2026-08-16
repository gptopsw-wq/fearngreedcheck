# -*- coding: utf-8 -*-
import streamlit as st
import streamlit.components.v1 as components
import numpy as np

# Import our existing scraping and dashboard modules
import 공탐지수_시각화 as viz
import dashboard_template

# Streamlit Page Settings
st.set_page_config(
    page_title="한-미 공포 탐욕 지수 비교 대시보드",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Caching data for 1 hour to prevent frequent scraping requests and CNN/KOSPI FGI blockages
@st.cache_data(ttl=3600)
def get_dashboard_html():
    # 1. Fetch live scores
    us_raw = viz.fetch_cnn_data()
    kr_raw = viz.fetch_kr_data()
    if not us_raw or not kr_raw:
        return "<h2>데이터 수집에 실패했습니다. 잠시 후 다시 시도해 주세요.</h2>"
        
    # 2. Process recent 3m data
    processed_data = viz.process_data(us_raw, kr_raw)
    
    # 3. Fetch 10-year historical data
    us_10y_df = viz.fetch_us_10y_csv()
    kr_10y_df = viz.calculate_kr_10y_proxy()
    
    dates_10y, us_10y_scores, kr_10y_scores = viz.process_10y_history(us_10y_df, kr_10y_df)
    
    # 4. Calculate Averages
    if us_10y_scores and kr_10y_scores:
        us_10y_avg = float(np.mean(us_10y_scores))
        kr_10y_avg = float(np.mean(kr_10y_scores))
    else:
        us_10y_avg, kr_10y_avg = 50.0, 50.0
        
    # 5. Inject 10y history and averages into processed_data
    processed_data['history_10y_dates'] = dates_10y
    processed_data['us_history_10y_scores'] = us_10y_scores
    processed_data['kr_history_10y_scores'] = kr_10y_scores
    processed_data['us_history_10y_avg'] = round(us_10y_avg, 1)
    processed_data['kr_history_10y_avg'] = round(kr_10y_avg, 1)
    
    # 6. Generate final HTML content
    html_content = dashboard_template.generate_html(processed_data)
    return html_content

# Fetch and cache HTML dashboard content
html_content = get_dashboard_html()

# Custom CSS to eliminate Streamlit padding and style container
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        iframe {
            background-color: #0b0f19;
            border-radius: 12px;
            border: 1px solid #334155;
        }
    </style>
""", unsafe_allow_html=True)

# Render HTML in Streamlit page with height matching the visualizer dashboard card height
components.html(html_content, height=1900, scrolling=True)
