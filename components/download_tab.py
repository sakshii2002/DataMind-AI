import streamlit as st
import io
from utils.data_quality import analyze_data_quality
from utils.charts import auto_charts
from utils.ai import generate_insights

def render_download():
    st.markdown("""
    <h2 style="font-family:'Space Grotesk',sans-serif;font-weight:600;margin-bottom:4px;">
        ⬇️ Download Reports & Data
    </h2>
    <p style="color:var(--muted,#6B7280);font-size:14px;margin-bottom:20px;">
        Export your analysis as PDF reports, cleaned CSV, or individual charts.
    </p>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.info("📂 Upload a dataset from the sidebar to enable downloads.")
        return

    df = st.session_state.df

    # --- PDF Report ---
    st.markdown("### 📄 Full PDF Report")
    st.markdown("""
    <div style="background:var(--surface2,#EEF0FB);border:1px solid var(--border,#DDE1F5);
                border-radius:12px;padding:16px 20px;margin-bottom:16px;">
        <p style="font-size:13px;color:var(--text);margin:0 0 8px;">
            The PDF report includes:
        </p>
        <ul style="font-size:13px;color:var(--muted,#6B7280);margin:0;padding-left:20px;line-height:2;">
            <li>Dataset overview & summary statistics</li>
            <li>Missing values, duplicates & outlier analysis</li>
            <li>AI-generated insights</li>
            <li>Auto-generated charts & visualizations</li>
            <li>Descriptive statistics table</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🤖 Generate & Download PDF Report", type="primary", use_container_width=False):
        with st.spinner("Building your report... (this may take 30-60 seconds)"):
            try:
                # Run quality analysis
                quality = analyze_data_quality(df)

                # Generate insights
                try:
                    insights = generate_insights(df)
                except Exception:
                    insights = "AI insights unavailable. Check your API key."

                # Generate charts
                try:
                    charts = auto_charts(df)
                except Exception:
                    charts = []

                # Build PDF
                from utils.report import generate_pdf_report
                pdf_bytes = generate_pdf_report(
                    df, quality, insights, charts,
                    st.session_state.filename or "dataset.csv"
                )

                fname = (st.session_state.filename or "dataset").replace(".csv", "").replace(".pdf", "")
                st.download_button(
                    "⬇️ Download PDF Report",
                    pdf_bytes,
                    f"{fname}_datamind_report.pdf",
                    mime="application/pdf",
                    use_container_width=False,
                )
                st.success("✅ Report generated! Click the button above to download.")

            except Exception as e:
                st.error(f"Error generating report: {e}")
                st.info("Make sure reportlab is installed: `pip install reportlab`")

    st.markdown("---")

    # --- CSV Downloads ---
    st.markdown("### 📊 Data Downloads")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Raw Data**")
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv,
                           st.session_state.filename or "data.csv",
                           mime="text/csv", use_container_width=True)

    with col2:
        st.markdown("**Descriptive Stats**")
        stats_csv = df.describe().round(4).to_csv().encode("utf-8")
        st.download_button("⬇️ Stats CSV", stats_csv, "descriptive_stats.csv",
                           mime="text/csv", use_container_width=True)

    with col3:
        st.markdown("**Data Dictionary**")
        import pandas as pd
        dd = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.values,
            "Non-Null": df.notnull().sum().values,
            "Null": df.isnull().sum().values,
            "Unique": df.nunique().values,
        })
        dd_csv = dd.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Dict CSV", dd_csv, "data_dictionary.csv",
                           mime="text/csv", use_container_width=True)

    st.markdown("---")

    # --- Chart Downloads ---
    if st.session_state.generated_charts:
        st.markdown("### 🖼️ Download Charts")
        st.caption(f"{len(st.session_state.generated_charts)} charts generated")
        for i, (title, fig) in enumerate(st.session_state.generated_charts):
            with st.expander(f"📊 {title}"):
                st.plotly_chart(fig, use_container_width=True)
                col1, col2 = st.columns(2)
                try:
                    img_bytes = fig.to_image(format="png", width=1200, height=600, scale=2)
                    col1.download_button("⬇️ PNG", img_bytes, f"{title}.png",
                                        mime="image/png", key=f"png_{i}")
                    svg_bytes = fig.to_image(format="svg")
                    col2.download_button("⬇️ SVG", svg_bytes, f"{title}.svg",
                                        mime="image/svg+xml", key=f"svg_{i}")
                except Exception:
                    st.info("Install kaleido for image exports: `pip install kaleido`")
    else:
        st.info("💡 Generate charts in the **Charts** tab to download them here.")
