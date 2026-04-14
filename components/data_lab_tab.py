import streamlit as st
import pandas as pd
from utils.lab_engine import generate_transformation_code, apply_safe_transformation

def render_data_lab():
    st.markdown("""
    <h2 style="font-family:'Space Grotesk',sans-serif;font-weight:600;margin-bottom:4px;">
        🧬 Data Lab
    </h2>
    <p style="color:var(--muted,#6B7280);font-size:14px;margin-bottom:20px;">
        The Table Whisperer. Use plain English to engineer features, create columns, and transform your data.
    </p>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.info("📂 Upload a dataset from the sidebar to start engineering data.")
        return

    df = st.session_state.df

    tab1, tab2 = st.tabs(["✨ AI Transformer", "↩️ History & Undo"])

    with tab1:
        st.markdown("**Describe the transformation you want to apply to this table.**")
        st.markdown("*(e.g., 'Extract the year from Date_Column' or 'Create a Revenue column by multiplying Price and Quantity')*")
        
        with st.form("transform_form"):
            request = st.text_area("Transformation Request", height=100, label_visibility="collapsed")
            col1, col2 = st.columns([1, 4])
            with col1:
                submit = st.form_submit_button("🧪 Apply Transformation", type="primary", use_container_width=True)

        if submit and request:
            with st.spinner("Generating pandas code..."):
                code = generate_transformation_code(request, df)
                
            if code:
                with st.spinner("Applying transformation..."):
                    new_df, summary = apply_safe_transformation(df, code)
                    
                    if "Error" not in summary and "Blocked" not in summary and "not a table" not in summary:
                        # Save current state to undo stack
                        st.session_state.undo_stack.append(df.copy())
                        # Keep history
                        st.session_state.transformation_history.append({
                            "request": request,
                            "code": code,
                            "summary": summary
                        })
                        # Update session state df
                        st.session_state.df = new_df
                        st.success("✅ Transformation successful!")
                        st.rerun()
                    else:
                        st.error(summary)

        # Show current data preview
        st.markdown("### Current Data Preview")
        st.dataframe(st.session_state.df.head(50), use_container_width=True)
        st.caption(f"Showing first 50 rows. Total shape: {st.session_state.df.shape}")

    with tab2:
        st.markdown("### Transformation History")
        
        if not st.session_state.transformation_history:
            st.info("No transformations applied yet.")
        else:
            for i, item in enumerate(reversed(st.session_state.transformation_history)):
                with st.expander(f"Transformation {len(st.session_state.transformation_history) - i}: {item['request'][:50]}..."):
                    st.markdown(f"**Request:** {item['request']}")
                    st.markdown("**Generated Code:**")
                    st.code(item['code'], language='python')
                    
            st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
            if st.button("↩️ Undo Last Transformation", type="secondary"):
                if st.session_state.undo_stack:
                    # Restore df
                    st.session_state.df = st.session_state.undo_stack.pop()
                    # Remove last history item
                    st.session_state.transformation_history.pop()
                    st.success("Last transformation undone!")
                    st.rerun()
                else:
                    st.warning("Nothing to undo.")
