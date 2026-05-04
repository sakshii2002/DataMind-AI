import streamlit as st
from utils.storyteller import generate_data_story

def render_story_tab():
    st.markdown("""
    <h2 style="font-family:'Space Grotesk',sans-serif;font-weight:600;margin-bottom:4px;">
        📖 AI Data Storyteller
    </h2>
    <p style="color:var(--muted,#6B7280);font-size:14px;margin-bottom:20px;">
        Transforming raw data into a compelling, human-readable narrative.
    </p>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.info("📂 Upload a dataset from the sidebar to hear its story.")
        return

    if "data_story" not in st.session_state:
        st.session_state.data_story = None

    # Top action area
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🎭 Tell the Story", type="primary", use_container_width=True):
            with st.spinner("Writing the narrative..."):
                st.session_state.data_story = generate_data_story(st.session_state.df)
    
    with col2:
        if st.session_state.data_story:
            st.success("The story of your data is ready.")

    if st.session_state.data_story:
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        
        # Display the story in a premium glass container
        st.markdown(f"""
        <div class="glass-card" style="line-height:1.7;">
            {st.session_state.data_story.replace("### ", "#### ").replace("\n", "<br>")}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
        
        # Action button to export or discuss
        if st.button("💬 Discuss this story in Chat"):
            st.session_state.active_tab = "Chat"
            st.session_state.pending_query = "I just read the AI Data Story. Can you elaborate more on Chapter 2 and Chapter 3?"
            st.rerun()
    else:
        # Empty state
        st.markdown(f"""
        <div style="text-align:center; padding:80px 20px; border:2px dashed var(--border); border-radius:20px; opacity:0.6;">
            <div style="font-size:50px; margin-bottom:15px;">📜</div>
            <div style="font-size:18px; font-weight:600;">Every dataset has a story.</div>
            <div style="font-size:14px;">Click the button above to let AI narrate yours.</div>
        </div>
        """, unsafe_allow_html=True)
