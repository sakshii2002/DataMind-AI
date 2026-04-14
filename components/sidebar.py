import streamlit as st
import pandas as pd
import io
import re

# ── helpers ─────────────────────────────────────────────────────────────────

def _reset_data_state():
    st.session_state.data_quality_report = None
    st.session_state.generated_charts = []
    st.session_state.chat_history = []
    st.session_state.uploaded = True


def _load_csv(uploaded):
    try:
        df = pd.read_csv(uploaded)
        st.session_state.df = df
        st.session_state.filename = uploaded.name
        _reset_data_state()
        st.success(f"✅ Loaded **{uploaded.name}** — {df.shape[0]:,} rows × {df.shape[1]} cols")
    except Exception as e:
        st.error(f"CSV error: {e}")


def _load_excel(uploaded):
    try:
        xf = pd.ExcelFile(uploaded, engine="openpyxl")
        sheet_names = xf.sheet_names
        if len(sheet_names) == 1:
            df = xf.parse(sheet_names[0])
        else:
            sheet = st.selectbox("Select sheet", sheet_names, key="excel_sheet_sel")
            df = xf.parse(sheet)
        st.session_state.df = df
        st.session_state.filename = uploaded.name
        _reset_data_state()
        st.success(f"✅ Loaded **{uploaded.name}** — {df.shape[0]:,} rows × {df.shape[1]} cols")
    except Exception as e:
        st.error(f"Excel error: {e}")


def _load_pdf(uploaded):
    try:
        import pdfplumber
        with pdfplumber.open(uploaded) as pdf:
            # Try to find tables
            tables = []
            for page in pdf.pages:
                t = page.extract_table()
                if t:
                    tables.extend(t)
            
            if tables:
                # Assuming first row of first table is header
                df = pd.DataFrame(tables[1:], columns=tables[0])
                st.session_state.df = df
                st.session_state.filename = uploaded.name
                _reset_data_state()
                st.success(f"✅ Extracted table from PDF: {df.shape[0]} × {df.shape[1]}")
            else:
                st.warning("No table found in PDF. Using text extraction context...")
                st.session_state.filename = uploaded.name
                # You might handle text-only PDF differently if needed
    except Exception as e:
        st.error(f"PDF error: {e}")


def _load_google_sheet(url: str):
    """Convert a standard Google Sheets URL to a CSV export URL and load it."""
    try:
        # Support share URLs: /edit, /htmlview, /pub, bare /d/<id> etc.
        match = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", url)
        if not match:
            st.error("❌ Could not parse a valid Google Sheets ID from that URL.")
            return
        sheet_id = match.group(1)

        # Check for a specific gid
        gid_match = re.search(r"gid=(\d+)", url)
        gid = gid_match.group(1) if gid_match else "0"

        csv_url = (
            f"https://docs.google.com/spreadsheets/d/{sheet_id}"
            f"/export?format=csv&gid={gid}"
        )
        df = pd.read_csv(csv_url)
        st.session_state.df = df
        st.session_state.filename = f"GoogleSheet_{sheet_id[:8]}.csv"
        _reset_data_state()
        st.success(
            f"✅ Loaded Google Sheet — {df.shape[0]:,} rows × {df.shape[1]} cols"
        )
    except Exception as e:
        st.error(f"Google Sheets error: {e}\n\n_Make sure the sheet is publicly shared (Anyone with link → Viewer)._")


# ── sidebar CSS injected inline ──────────────────────────────────────────────

_TOGGLE_CSS = """
<style>
/* ─── theme toggle ─── */
.theme-toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 6px 0 4px;
}
.theme-toggle-label {
    font-size: 13px;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 6px;
}
</style>
"""

# ── main render ──────────────────────────────────────────────────────────────

def render_sidebar():
    # Inject toggle CSS once
    st.sidebar.markdown(_TOGGLE_CSS, unsafe_allow_html=True)

    with st.sidebar:
        # ── Logo ──────────────────────────────────────────────────────────
        dark = st.session_state.get("dark_mode", False)
        accent = "#7C6FF7" if dark else "#5B4FF5"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:4px 0 18px;">
            <div style="width:36px;height:36px;border-radius:10px;
                        background:linear-gradient(135deg,{accent},#34D399);
                        display:flex;align-items:center;justify-content:center;font-size:20px;
                        box-shadow:0 2px 10px {accent}55;">🧠</div>
            <div>
                <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:15px;">
                    DataMind AI</div>
                <div style="font-size:11px;opacity:.55;">Powered by Gemini</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Theme Toggle ──────────────────────────────────────────────────
        st.markdown("**🎨 Appearance**")

        col_lbl, col_btn = st.columns([3, 1])
        with col_lbl:
            icon  = "☀️" if dark else "🌙"
            label = "Light Mode" if dark else "Dark Mode"
            st.markdown(
                f"<div style='font-size:13px;padding-top:6px'>{icon} {label}</div>",
                unsafe_allow_html=True,
            )
        with col_btn:
            toggled = st.toggle(
                "Toggle theme",
                value=dark,
                key="theme_toggle",
                help="Switch between dark and light mode",
                label_visibility="collapsed",
            )
            if toggled != dark:
                st.session_state.dark_mode = toggled
                st.rerun()

        st.divider()

        # ── Data Upload (Unified) ──────────────────────────────────────────
        st.markdown("**📂 Upload Data**")
        
        uploaded = st.file_uploader(
            "Drop your CSV, Excel, or PDF here",
            type=["csv", "xlsx", "xls", "pdf"],
            label_visibility="collapsed",
            key="unified_uploader",
        )
        
        if uploaded:
            # Build a unique ID for this upload to prevent re-loading raw data on every rerun
            # (which would overwrite cleaned data in session_state)
            upload_id = f"{uploaded.name}_{uploaded.size}"
            if st.session_state.get("last_upload_id") != upload_id:
                if uploaded.name.endswith(".csv"):
                    _load_csv(uploaded)
                elif uploaded.name.endswith((".xlsx", ".xls")):
                    _load_excel(uploaded)
                elif uploaded.name.endswith(".pdf"):
                    _load_pdf(uploaded)
                
                st.session_state.last_upload_id = upload_id

        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        st.markdown("**🔗 Google Sheet URL**")
        gs_url = st.text_input(
            "Google Sheet URL",
            placeholder="Paste public link here...",
            label_visibility="collapsed",
            key="gs_url_input",
        )
        if st.button("Connect Sheet", key="load_gs", use_container_width=True):
            if gs_url.strip():
                with st.spinner("Fetching sheet…"):
                    _load_google_sheet(gs_url.strip())
            else:
                st.warning("Please enter a Google Sheets URL first.")

        st.divider()

        # ── Dataset Info ──────────────────────────────────────────────────
        if st.session_state.df is not None:
            df = st.session_state.df
            fname = st.session_state.get("filename", "dataset")
            num_cols  = len(df.select_dtypes(include="number").columns)
            text_cols = len(df.select_dtypes(include=["object", "category"]).columns)
            missing   = int(df.isnull().sum().sum())

            bg_card  = "#1A1D27" if dark else "#F8F9FF"
            txt_info = "#E8EAF6" if dark else "#1A1D2E"
            muted    = "#8B92B8" if dark else "#6B7280"
            bdr      = "#2E3250" if dark else "#DDE1F5"

            st.markdown(f"""
            <div style="background:{bg_card};border:1px solid {bdr};
                        border-radius:12px;padding:12px 14px;margin-bottom:4px;">
                <div style="font-size:12px;font-weight:700;color:{accent};
                            margin-bottom:8px;letter-spacing:.04em;">📊 DATASET</div>
                <div style="font-size:12px;line-height:2;color:{txt_info};">
                    🗂 <b>{fname}</b><br>
                    <span style='color:{muted}'>Rows</span>
                    &nbsp;<b style='float:right'>{df.shape[0]:,}</b><br>
                    <span style='color:{muted}'>Columns</span>
                    &nbsp;<b style='float:right'>{df.shape[1]}</b><br>
                    <span style='color:{muted}'>Numeric cols</span>
                    &nbsp;<b style='float:right'>{num_cols}</b><br>
                    <span style='color:{muted}'>Text cols</span>
                    &nbsp;<b style='float:right'>{text_cols}</b><br>
                    <span style='color:{muted}'>Missing values</span>
                    &nbsp;<b style='float:right;color:{"#F87171" if missing else "#34D399"}'>{missing}</b>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.divider()

        # ── Navigation ────────────────────────────────────────────────────
        st.markdown("**🧭 Navigation**")
        tabs = [
            ("💬 Chat",         "Chat"),
            ("📊 Charts",       "Charts"),
            ("🔍 Data Quality", "Data Quality"),
            ("📋 Dashboard",    "Dashboard"),
            ("🔮 Predictions",  "Predictions"),
            ("🧬 Data Lab",     "Data Lab"),
            ("⬇️ Download",     "Download"),
        ]
        for display, label in tabs:
            active = st.session_state.active_tab == label
            if st.button(
                display,
                key=f"nav_{label}",
                use_container_width=True,
                type="primary" if active else "secondary",
            ):
                st.session_state.active_tab = label
                st.rerun()

        st.divider()
        st.caption("DataMind AI v1.0")
