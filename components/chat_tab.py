import streamlit as st
import re
from utils.ai import chat_with_data

FEATURES = [
    ("🔍", "Data Quality", "Detect missing values, duplicates & outliers automatically"),
    ("📊", "Smart Charts", "AI picks the best chart type from plain English"),
    ("💡", "AI Insights", "Surface hidden patterns & trends in seconds"),
    ("📄", "PDF Reports", "Download full analysis reports with one click"),
]

def _handle_ai_response(user_text):
    """Callback-style function to process AI messages."""
    if not user_text:
        return
    
    # 1. Add user message
    st.session_state.chat_history.append({"role": "user", "content": user_text})
    
    # 2. This will be processed in the main render loop to show a spinner
    st.session_state["pending_query"] = user_text

def render_chat():
    st.markdown("""
    <div style="text-align:center;margin-bottom:24px;">
        <h2 style="font-family:'Space Grotesk',sans-serif;font-weight:600;margin-bottom:6px;">
            💬 Chat with Your Data
        </h2>
        <p style="font-size:14px;opacity:0.75;">
            Ask anything about your dataset — insights, patterns, trends, or what to visualize next.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Welcome message (first time)
    if not st.session_state.chat_history:
        if st.session_state.df is not None:
            df = st.session_state.df
            welcome = f"👋 Hi! I've loaded **{st.session_state.filename}** — {df.shape[0]:,} rows × {df.shape[1]} columns.\n\nWhat would you like to know about your data?"
            st.session_state.chat_history.append({"role": "assistant", "content": welcome})
        else:
            # Show welcome card with feature grid
            st.markdown("""
            <div style="text-align:center;padding:12px 0 8px;">
                <div style="font-size:40px;margin-bottom:8px;">🧠</div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:18px;font-weight:600;margin-bottom:6px;">
                    Welcome to DataMind AI
                </div>
                <div style="font-size:14px;opacity:0.65;margin-bottom:20px;">
                    Upload a CSV or PDF from the sidebar to get started
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Feature cards grid
            st.markdown('<div class="feature-grid">', unsafe_allow_html=True)
            for icon, title, desc in FEATURES:
                st.markdown(f"""
                <div class="feature-card">
                    <div class="fc-icon">{icon}</div>
                    <div>
                        <div class="fc-title">{title}</div>
                        <div class="fc-desc">{desc}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            return

    # Process pending query if it exists (show spinner here)
    if st.session_state.get("pending_query"):
        query = st.session_state.pop("pending_query")
        with st.spinner("Thinking..."):
            # Pass history EXCLUDING the latest user message which we just added
            # Actually, chat_with_data handles the user_msg separately, so history should be previous turns.
            response = chat_with_data(query, st.session_state.df, st.session_state.chat_history[:-1])
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

    # Render chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;align-items:flex-end;margin:8px 0;">
                <div class="chat-label" style="text-align:right;margin-right:2px;">You</div>
                <div class="chat-user">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Simple markdown rendering with some support for bold
            content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', msg["content"])
            content = content.replace("\n", "<br>")
            st.markdown(f"""
            <div style="display:flex;flex-direction:column;align-items:flex-start;margin:8px 0;">
                <div class="chat-label" style="margin-left:2px;">🧠 DataMind AI</div>
                <div class="chat-ai">{content}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Quick prompt chips (only when data loaded)
    if st.session_state.df is not None:
        st.markdown("<p style='font-size:12px;opacity:0.55;margin-bottom:6px;'>Quick prompts:</p>",
                    unsafe_allow_html=True)
        chips = ["Summarize this dataset", "What are the key trends?", "Find anomalies", "Suggest visualizations"]
        cols = st.columns(len(chips))
        for i, chip in enumerate(chips):
            with cols[i]:
                # Use standard button with proper callback logic
                if st.button(chip, key=f"chip_btn_{i}", use_container_width=True):
                    _handle_ai_response(chip)
                    st.rerun()

    # Chat input form
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input("", placeholder="Ask about your data...",
                                       label_visibility="collapsed")
        with col2:
            submitted = st.form_submit_button("Send →", use_container_width=True)

    if submitted and user_input.strip():
        _handle_ai_response(user_input.strip())
        st.rerun()

    # Add a reset button at the very bottom
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
            st.session_state.chat_history = []
            st.rerun()
