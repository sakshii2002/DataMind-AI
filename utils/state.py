import streamlit as st

def init_state():
    defaults = {
        "dark_mode": False,
        "df": None,
        "filename": None,
        "chat_history": [],
        "active_tab": "Chat",
        "generated_charts": [],
        "data_quality_report": None,
        "uploaded": False,
        "transformation_history": [],
        "undo_stack": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
