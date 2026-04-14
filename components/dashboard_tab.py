import streamlit as st
import plotly.express as px
from utils.ai import generate_insights
from utils.charts import auto_charts
from utils.data_quality import analyze_data_quality

PALETTE = ["#5B4FF5", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"]

def render_dashboard():
    st.markdown("""
    <h2 style="font-family:'Space Grotesk',sans-serif;font-weight:600;margin-bottom:4px;">
        📋 Analytics Dashboard
    </h2>
    <p style="color:var(--muted,#6B7280);font-size:14px;margin-bottom:20px;">
        Full overview of your dataset with AI insights and key visualizations.
    </p>
    """, unsafe_allow_html=True)

    if st.session_state.df is None:
        st.info("📂 Upload a dataset from the sidebar to view the dashboard.")
        return

    df = st.session_state.df
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # Top metrics
    st.markdown("### 📊 Dataset Snapshot")
    m_cols = st.columns(5)
    metrics = [
        ("Total Rows", f"{df.shape[0]:,}"),
        ("Columns", str(df.shape[1])),
        ("Numeric", str(len(numeric_cols))),
        ("Categorical", str(len(cat_cols))),
        ("Missing %", f"{round(df.isnull().sum().sum() / (df.shape[0]*df.shape[1]) * 100, 1)}%"),
    ]
    for mcol, (label, val) in zip(m_cols, metrics):
        mcol.metric(label, val)

    st.markdown("---")

    # AI Insights
    st.markdown("### 💡 AI Insights")
    col1, _ = st.columns([1, 5])
    with col1:
        gen_btn = st.button("✨ Generate Insights", use_container_width=True)

    if gen_btn:
        with st.spinner("🤖 Analyzing your data..."):
            try:
                insights = generate_insights(df)
                st.session_state["dashboard_insights"] = insights
            except Exception as e:
                st.error(f"Error: {e}")

    if "dashboard_insights" in st.session_state:
        insights = st.session_state["dashboard_insights"]
        import re
        lines = [l for l in insights.split("\n") if l.strip()]
        for line in lines:
            clean = re.sub(r'\*\*(.*?)\*\*', r'**\1**', line)
            st.markdown(clean)

    st.markdown("---")

    # Numeric stats
    if numeric_cols:
        st.markdown("### 📈 Numeric Summary")
        desc = df[numeric_cols].describe().T.round(3)
        desc = desc[["count", "mean", "std", "min", "25%", "50%", "75%", "max"]]
        st.dataframe(desc, use_container_width=True)

        st.markdown("### 📊 Distributions")
        cols_per_row = 3
        for i in range(0, min(len(numeric_cols), 9), cols_per_row):
            row_cols = st.columns(cols_per_row)
            for j, rcol in enumerate(row_cols):
                if i + j < len(numeric_cols):
                    c = numeric_cols[i + j]
                    fig = px.histogram(df, x=c, title=c, color_discrete_sequence=PALETTE,
                                       template="plotly_white", nbins=30)
                    fig.update_layout(showlegend=False, margin=dict(l=10,r=10,t=30,b=10),
                                     paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                     font_family="DM Sans", title_font_size=13, height=200)
                    fig.update_xaxes(showgrid=False)
                    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
                    rcol.plotly_chart(fig, use_container_width=True, key=f"dash_dist_{i}_{j}")

    # Correlation heatmap
    if len(numeric_cols) >= 2:
        st.markdown("### 🔗 Correlation Matrix")
        corr = df[numeric_cols].corr().round(3)
        fig = px.imshow(corr, color_continuous_scale="RdBu_r", text_auto=True,
                        title="Feature Correlations", aspect="auto")
        fig.update_layout(font_family="DM Sans", paper_bgcolor="rgba(0,0,0,0)", height=400)
        st.plotly_chart(fig, use_container_width=True, key="dash_corr_matrix")

    # Categorical overview
    if cat_cols:
        st.markdown("### 🔤 Categorical Columns")
        cols_to_show = [c for c in cat_cols if df[c].nunique() <= 30][:6]
        for i in range(0, len(cols_to_show), 2):
            row_cols = st.columns(2)
            for j, rcol in enumerate(row_cols):
                if i + j < len(cols_to_show):
                    c = cols_to_show[i + j]
                    vc = df[c].value_counts().head(10).reset_index()
                    vc.columns = [c, "count"]
                    fig = px.bar(vc, x="count", y=c, orientation="h",
                                title=f"Top values: {c}", color_discrete_sequence=PALETTE,
                                template="plotly_white")
                    fig.update_layout(showlegend=False, margin=dict(l=10,r=10,t=30,b=10),
                                     paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                     font_family="DM Sans", height=250, title_font_size=13)
                    fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.05)")
                    fig.update_yaxes(showgrid=False)
                    rcol.plotly_chart(fig, use_container_width=True, key=f"dash_cat_{i}_{j}")

    # Data preview
    st.markdown("### 🗃️ Data Preview")
    n = st.slider("Rows to preview", 5, min(100, df.shape[0]), 10)
    st.dataframe(df.head(n), use_container_width=True)
