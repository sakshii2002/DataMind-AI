import streamlit as st
from components.chat_tab import render_chat
from components.charts_tab import render_charts
from components.quality_tab import render_quality
from components.dashboard_tab import render_dashboard
from components.predictions_tab import render_predictions
from components.data_lab_tab import render_data_lab
from components.radar_tab import render_radar
from components.story_tab import render_story_tab
from components.download_tab import render_download

def render_main_view():
    tab = st.session_state.active_tab

    if tab == "Chat":
        render_chat()
    elif tab == "Charts":
        render_charts()
    elif tab == "Data Quality":
        render_quality()
    elif tab == "Anomaly Radar":
        render_radar()
    elif tab == "Data Story":
        render_story_tab()
    elif tab == "Dashboard":
        render_dashboard()
    elif tab == "Predictions":
        render_predictions()
    elif tab == "Data Lab":
        render_data_lab()
    elif tab == "Download":
        render_download()
