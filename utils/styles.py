import streamlit as st

def inject_styles():
    dark = st.session_state.get("dark_mode", False)

    if dark:
        bg       = "#0F1117"
        surface  = "#1A1D27"
        surface2 = "#22263A"
        border   = "#2E3250"
        text     = "#E8EAF6"
        muted    = "#8B92B8"
        accent   = "#7C6FF7"
        accent2  = "#34D399"
        card_bg  = "#1A1D27"
        input_bg = "#22263A"
    else:
        bg       = "#F5F6FA"
        surface  = "#FFFFFF"
        surface2 = "#EEF0FB"
        border   = "#DDE1F5"
        text     = "#1A1D2E"
        muted    = "#6B7280"
        accent   = "#5B4FF5"
        accent2  = "#10B981"
        card_bg  = "#FFFFFF"
        input_bg = "#F8F9FF"

    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    html, body {{ background-color: {bg} !important; color: {text} !important; }}

    .stApp,
    .stApp > div,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > section,
    [data-testid="stAppViewBlockContainer"],
    .main, .main > div, .block-container {{
        background-color: {bg} !important;
        font-family: 'DM Sans', sans-serif !important;
        color: {text} !important;
    }}

    .block-container {{
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {surface} !important;
        border-right: 1px solid {border} !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1);
    }}
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] small {{
        color: {text} !important;
    }}

    header[data-testid="stHeader"] {{
        background-color: transparent !important;
        color: {text} !important;
    }}
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"] {{ display: none !important; }}
    #MainMenu, footer {{ visibility: hidden !important; }}

    h1, h2, h3, h4 {{
        font-family: 'Space Grotesk', sans-serif !important;
        color: {text} !important;
    }}
    p, span, div, label, li {{ color: {text} !important; }}

    [data-testid="stMetric"] {{
        background: {card_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
    }}
    [data-testid="stMetricLabel"] p {{ color: {muted} !important; font-size: 12px !important; }}
    [data-testid="stMetricValue"]  {{ color: {text}  !important; font-size: 24px !important; font-weight: 600 !important; }}

    .stTabs [data-baseweb="tab-list"] {{
        background: {surface2} !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 4px !important;
        border: none !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border-radius: 8px !important;
        color: {muted} !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 13px !important;
        padding: 6px 16px !important;
        border: none !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: {surface} !important;
        color: {accent} !important;
        font-weight: 500 !important;
    }}

    .stButton > button {{
        background: {accent} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        padding: 8px 18px !important;
        transition: opacity 0.2s !important;
    }}
    .stButton > button:hover {{ opacity: 0.85 !important; }}

    .stTextInput input, textarea, [data-baseweb="input"] input {{
        background: {input_bg} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
    }}

    [data-baseweb="select"] > div {{ background: {input_bg} !important; border-color: {border} !important; }}
    [data-baseweb="select"] span, [data-baseweb="select"] div {{ color: {text} !important; }}

    .chat-user {{
        background: {accent};
        color: #fff !important;
        border-radius: 16px 16px 4px 16px;
        padding: 12px 16px;
        max-width: 72%;
        font-size: 14px;
        line-height: 1.5;
        margin-left: auto;
        width: fit-content;
    }}
    .chat-user * {{ color: #fff !important; }}
    .chat-ai {{
        background: {surface};
        color: {text} !important;
        border: 1px solid {border};
        border-radius: 16px 16px 16px 4px;
        padding: 12px 16px;
        max-width: 88%;
        font-size: 14px;
        line-height: 1.6;
        width: fit-content;
    }}
    .chat-ai * {{ color: {text} !important; }}
    .chat-label {{
        font-size: 11px;
        color: {muted} !important;
        margin-bottom: 4px;
        font-weight: 500;
        letter-spacing: 0.04em;
    }}

    .feature-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
        margin: 16px 0 24px;
    }}
    .feature-card {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 16px 18px;
        display: flex;
        align-items: flex-start;
        gap: 12px;
    }}
    .fc-icon  {{ font-size: 22px; line-height: 1; margin-top: 1px; flex-shrink: 0; }}
    .fc-title {{ font-size: 13px; font-weight: 600; color: {text} !important; margin-bottom: 3px; }}
    .fc-desc  {{ font-size: 12px; color: {muted} !important; line-height: 1.4; }}

    .badge {{ display:inline-block; padding:2px 10px; border-radius:20px; font-size:11px; font-weight:600; }}
    .badge-red    {{ background:#FEE2E2; color:#B91C1C !important; }}
    .badge-yellow {{ background:#FEF3C7; color:#92400E !important; }}
    .badge-green  {{ background:#D1FAE5; color:#065F46 !important; }}

    /* ── Streamlit File Uploader Theme Fix ── */
    [data-testid="stFileUploader"] {{
        background: {surface2} !important;
        border: 2px dashed {border} !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }}
    [data-testid="stFileUploaderDropzone"] {{
        background: transparent !important;
        border: none !important;
    }}
    [data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {{
        background: {surface} !important;
        border: 1px solid {border} !important;
        color: {text} !important;
    }}
    [data-testid="stFileUploader"] small {{
        color: {muted} !important;
    }}
    
    [data-testid="stDataFrame"] {{ border-radius: 12px !important; overflow: hidden !important; }}

    [data-testid="stExpander"] {{
        background: {surface} !important;
        border: 1px solid {border} !important;
        border-radius: 12px !important;
    }}

    ::-webkit-scrollbar {{ width:5px; height:5px; }}
    ::-webkit-scrollbar-track {{ background:{surface2}; }}
    ::-webkit-scrollbar-thumb {{ background:{border}; border-radius:10px; }}

    div[data-testid="column"] {{ gap: 0 !important; }}

    /* ── Smooth theme transition ── */
    *, *::before, *::after {{
        transition: background-color 0.25s ease, color 0.15s ease,
                    border-color 0.25s ease !important;
    }}

    /* ── Sidebar secondary (nav) buttons ── */
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
        background: transparent !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 7px 12px !important;
    }}
    section[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
        background: {surface2} !important;
        border-color: {accent} !important;
        color: {accent} !important;
        opacity: 1 !important;
    }}
    /* primary nav button (active tab) */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background: {accent} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-align: left !important;
        padding: 7px 12px !important;
    }}

    /* ── st.toggle (theme switch) ── */
    section[data-testid="stSidebar"] [data-testid="stToggle"] {{
        margin-top: 2px !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stToggle"] label {{
        font-size: 0 !important;   /* hide default label text */
    }}
    /* track */
    section[data-testid="stSidebar"] [role="switch"] {{
        background: {accent} !important;
        border: none !important;
        width: 36px !important;
        height: 20px !important;
        border-radius: 20px !important;
    }}

    /* ── Connect Sheet button full width ── */
    section[data-testid="stSidebar"] [data-testid="stButton"] button[key="load_gs"] {{
        background: {surface2} !important;
        color: {accent} !important;
        border: 1.5px solid {accent} !important;
    }}
    /* ─── vision preview ─── */
    [data-testid="stImage"] {{
        border: 2px solid {border} !important;
        border-radius: 12px !important;
        padding: 4px !important;
        background: {surface} !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    }}
    .vision-badge {{
        background: linear-gradient(135deg, {accent}, #34D399);
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
