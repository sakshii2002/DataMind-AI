import streamlit as st
from utils.data_quality import analyze_data_quality, clean_data

def _score_color(score):
    if score >= 80:
        return "#10B981", "🟢"
    elif score >= 60:
        return "#F59E0B", "🟡"
    else:
        return "#EF4444", "🔴"

def render_quality():
    st.markdown("""
    <h2 style="font-family:'Space Grotesk',sans-serif;font-weight:600;margin-bottom:4px;">
        🔍 Data Quality Analysis
    </h2>
    <p style="color:var(--muted,#6B7280);font-size:14px;margin-bottom:20px;">
        Detect missing values, duplicates, outliers, and data type issues.
    </p>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.info("📂 Upload a dataset from the sidebar to analyze data quality.")
        return

    df = st.session_state.df

    col1, col2 = st.columns([1, 4])
    with col1:
        run = st.button("🔍 Run Analysis", use_container_width=True)

    if run or st.session_state.data_quality_report is not None:
        if run:
            with st.spinner("Analyzing data quality..."):
                st.session_state.data_quality_report = analyze_data_quality(df)

        report = st.session_state.data_quality_report
        score = report.get("quality_score", 0)
        color, icon = _score_color(score)

        # Score banner
        st.markdown(f"""
        <div style="background:var(--surface,#fff);border:1px solid var(--border,#DDE1F5);
                    border-radius:12px;padding:20px 24px;margin-bottom:20px;
                    display:flex;align-items:center;gap:20px;">
            <div style="font-size:48px;font-weight:700;font-family:'Space Grotesk',sans-serif;color:{color};">
                {score}
            </div>
            <div>
                <div style="font-size:14px;font-weight:600;color:var(--text);">{icon} Data Quality Score</div>
                <div style="font-size:12px;color:var(--muted,#6B7280);margin-top:4px;">
                    {'Excellent — dataset is clean and ready for analysis.' if score >= 80
                     else 'Fair — some issues detected, review below.' if score >= 60
                     else 'Poor — significant issues found, cleaning recommended.'}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Key metrics
        m1, m2, m3, m4 = st.columns(4)
        missing_df = report.get("missing", None)
        missing_count = missing_df.shape[0] if missing_df is not None and not missing_df.empty else 0
        m1.metric("Missing Cols", missing_count)
        m2.metric("Duplicate Rows", report.get("duplicate_rows", 0),
                  f"{report.get('duplicate_pct', 0)}%")
        outliers_df = report.get("outliers", None)
        outlier_count = outliers_df.shape[0] if outliers_df is not None and not outliers_df.empty else 0
        m3.metric("Cols w/ Outliers", outlier_count)
        m4.metric("Total Rows", f"{df.shape[0]:,}")

        st.markdown("---")

        tab1, tab2, tab3, tab4 = st.tabs(["🕳️ Missing Values", "👯 Duplicates", "📈 Outliers", "🧹 Clean Data"])

        with tab1:
            missing_df = report.get("missing")
            if missing_df is not None and not missing_df.empty:
                st.markdown(f"**{missing_df.shape[0]} columns have missing values:**")
                for _, row in missing_df.iterrows():
                    pct = row["Missing %"]
                    badge = "badge-red" if pct > 30 else "badge-yellow" if pct > 10 else "badge-green"
                    cols = st.columns([3, 1, 1, 2])
                    cols[0].write(f"**{row['Column']}**")
                    cols[1].write(f"{row['Missing Count']} rows")
                    cols[2].markdown(f"<span class='badge {badge}'>{pct}%</span>", unsafe_allow_html=True)
                    cols[3].progress(min(int(pct), 100))
            else:
                st.success("✅ No missing values found!")

        with tab2:
            dup = report.get("duplicate_rows", 0)
            pct = report.get("duplicate_pct", 0)
            if dup > 0:
                st.warning(f"⚠️ **{dup} duplicate rows** found ({pct}% of dataset)")
                st.dataframe(df[df.duplicated()].head(20), use_container_width=True)
            else:
                st.success("✅ No duplicate rows found!")

        with tab3:
            outliers_df = report.get("outliers")
            if outliers_df is not None and not outliers_df.empty:
                st.markdown("**Outliers detected using IQR method:**")
                st.dataframe(outliers_df, use_container_width=True)
                import plotly.express as px
                numeric_cols = df.select_dtypes(include="number").columns.tolist()
                if numeric_cols:
                    col_select = st.selectbox("View distribution for:", numeric_cols)
                    fig = px.box(df, y=col_select, title=f"Box Plot: {col_select}",
                                 color_discrete_sequence=["#5B4FF5"])
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                     font_family="DM Sans")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("✅ No significant outliers detected!")

        with tab4:
            st.markdown("**Select cleaning operations:**")
            col1, col2 = st.columns(2)
            with col1:
                drop_dup = st.checkbox("Remove duplicate rows", value=True)
                fill_num = st.checkbox("Fill numeric nulls with median", value=True)
            with col2:
                fill_cat = st.checkbox("Fill text nulls with mode", value=True)
                drop_rows = st.checkbox("Drop rows with any null", value=False)

            if st.button("🧹 Apply Cleaning", type="primary"):
                opts = {
                    "drop_duplicates": drop_dup,
                    "fill_numeric": fill_num,
                    "fill_categorical": fill_cat,
                    "drop_missing_rows": drop_rows,
                }
                with st.spinner("Cleaning data..."):
                    cleaned_df, log = clean_data(df, opts)

                for msg in log:
                    st.success(msg)

                st.session_state.df = cleaned_df
                st.session_state.data_quality_report = None

                csv = cleaned_df.to_csv(index=False).encode("utf-8")
                st.download_button("⬇️ Download Cleaned CSV", csv,
                                   f"cleaned_{st.session_state.filename or 'data.csv'}",
                                   mime="text/csv")
                st.info("✅ Cleaned data is now loaded. Re-run analysis to verify.")
