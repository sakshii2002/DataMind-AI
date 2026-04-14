import streamlit as st
import io
from utils.charts import build_chart, auto_charts, chart_to_bytes
from utils.ai import generate_chart_config

def render_charts():
    st.markdown("""
    <h2 style="font-family:'Space Grotesk',sans-serif;font-weight:600;margin-bottom:4px;">
        📊 Smart Chart Builder
    </h2>
    <p style="color:var(--muted,#6B7280);font-size:14px;margin-bottom:20px;">
        Describe what you want to visualize, or build charts manually.
    </p>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.info("📂 Upload a dataset from the sidebar to start generating charts.")
        return

    df = st.session_state.df

    tab1, tab2, tab3 = st.tabs(["🤖 AI Chart", "🛠️ Manual Builder", "🔄 Auto Overview"])

    # --- AI Chart Generation ---
    with tab1:
        st.markdown("Describe the chart you want, or **upload a screenshot** to recreate it:")
        
        with st.form("ai_chart_form"):
            col_text, col_img = st.columns([2, 1])
            
            with col_text:
                prompt = st.text_input("Prompt (optional with image)", 
                                       placeholder="e.g. Show me a bar chart of sales by region",
                                       label_visibility="visible")
            
            with col_img:
                uploaded_img = st.file_uploader("Inspiration Image", type=["jpg", "png", "jpeg"],
                                                label_visibility="visible")
            
            gen = st.form_submit_button("✨ Generate AI Chart", use_container_width=True)

        if gen:
            if not prompt.strip() and not uploaded_img:
                st.warning("Please provide a text prompt or an image to generate a chart.")
            else:
                with st.spinner("🤖 AI is analyzing your request..."):
                    try:
                        from utils.ai import analyze_chart_image, generate_chart_config
                        
                        config = None
                        if uploaded_img:
                            # Visual analysis
                            img_bytes = uploaded_img.read()
                            config = analyze_chart_image(img_bytes, df, prompt.strip() if prompt.strip() else None)
                        elif prompt.strip():
                            # Text-only analysis
                            config = generate_chart_config(prompt, df)

                        if config:
                            # Show side-by-side preview if image was used
                            if uploaded_img:
                                preview_col, chart_col = st.columns([1, 2])
                                with preview_col:
                                    st.markdown("<p style='font-size:12px;opacity:0.6;margin-bottom:4px;'>YOUR INSPIRATION:</p>", unsafe_allow_html=True)
                                    st.image(uploaded_img, use_container_width=True)
                                with chart_col:
                                    fig = build_chart(df, config)
                                    if fig:
                                        st.plotly_chart(fig, use_container_width=True, key="vision_chart")
                                        st.session_state.generated_charts.append((config.get("title", "Chart"), fig))
                            else:
                                fig = build_chart(df, config)
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True, key="ai_generated_chart")
                                    st.session_state.generated_charts.append((config.get("title", "Chart"), fig))
                            
                            # Standard download/info section
                            if "fig" in locals() and fig:
                                dl_col, _ = st.columns([1, 5])
                                with dl_col:
                                    img_bytes = fig.to_image(format="png", width=1200, height=600, scale=2)
                                    st.download_button("⬇️ PNG", img_bytes, f"{config.get('title','chart')}.png",
                                                       mime="image/png", use_container_width=True)
                                st.caption(f"Suggested Configuration: {config}")
                        else:
                            st.warning("⚠️ The AI was unable to generate a chart configuration. Try a clearer prompt or a simpler image.")
                    except Exception as e:
                        st.error(f"Error: {e}")


    # --- Manual Builder ---
    with tab2:
        cols = list(df.columns)
        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

        col1, col2 = st.columns(2)
        with col1:
            chart_type = st.selectbox("Chart Type", ["bar", "line", "scatter", "pie", "histogram", "box", "heatmap"])
            x_col = st.selectbox("X Axis", [None] + cols)
            y_col = st.selectbox("Y Axis", [None] + numeric_cols)
        with col2:
            color_col = st.selectbox("Color By (optional)", [None] + cols)
            title = st.text_input("Chart Title", value=f"{chart_type.title()} Chart")
            agg = st.selectbox("Aggregation", ["none", "sum", "mean", "count"])

        if st.button("🎨 Build Chart", use_container_width=False):
            config = {"chart_type": chart_type, "x": x_col, "y": y_col,
                      "color": color_col, "title": title, "agg": agg}
            fig = build_chart(df, config)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="manual_builder_chart")
                st.session_state.generated_charts.append((title, fig))
                try:
                    img_bytes = fig.to_image(format="png", width=1200, height=600, scale=2)
                    st.download_button("⬇️ Download PNG", img_bytes, f"{title}.png", mime="image/png")
                except Exception:
                    st.info("Install kaleido for image download: pip install kaleido")

    # --- Auto Overview ---
    with tab3:
        if st.button("🔄 Generate Overview Charts", use_container_width=False):
            with st.spinner("Generating charts..."):
                charts = auto_charts(df)
                st.session_state.generated_charts = charts
                if not charts:
                    st.warning("Not enough data variety to generate overview charts.")

        if st.session_state.generated_charts:
            for i in range(0, len(st.session_state.generated_charts), 2):
                cols = st.columns(2)
                for j, col in enumerate(cols):
                    if i + j < len(st.session_state.generated_charts):
                        title, fig = st.session_state.generated_charts[i + j]
                        with col:
                            st.plotly_chart(fig, use_container_width=True, key=f"auto_chart_{i}_{j}")
                            try:
                                img_bytes = fig.to_image(format="png", width=900, height=450, scale=2)
                                st.download_button(f"⬇️ {title}", img_bytes, f"{title}.png",
                                                   mime="image/png", key=f"dl_{i}_{j}")
                            except Exception:
                                pass
