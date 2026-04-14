import streamlit as st
from utils.state import init_state

st.set_page_config(
    page_title="DataMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_state()

from utils.styles import inject_styles
inject_styles()

from components.sidebar import render_sidebar
from components.main_view import render_main_view

render_sidebar()
render_main_view()
