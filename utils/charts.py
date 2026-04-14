import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import io

CHART_PALETTE = ["#5B4FF5", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4", "#EC4899"]

def build_chart(df: pd.DataFrame, config: dict):
    chart_type = config.get("chart_type", "bar")
    x = config.get("x")
    y = config.get("y")
    color = config.get("color")
    title = config.get("title", "Chart")
    agg = config.get("agg", "none")
    template = "plotly_white"

    color_seq = CHART_PALETTE

    try:
        # Aggregate if needed
        plot_df = df.copy()
        if agg in ("sum", "mean", "count") and x and y and y in df.columns:
            group_cols = [x] + ([color] if color and color != "None" else [])
            group_cols = [c for c in group_cols if c in df.columns]
            if agg == "sum":
                plot_df = df.groupby(group_cols)[y].sum().reset_index()
            elif agg == "mean":
                plot_df = df.groupby(group_cols)[y].mean().reset_index()
            elif agg == "count":
                plot_df = df.groupby(group_cols)[y].count().reset_index()

        color_arg = color if color and color != "None" and color in plot_df.columns else None

        if chart_type == "bar":
            fig = px.bar(plot_df, x=x, y=y, color=color_arg, title=title,
                         color_discrete_sequence=color_seq, template=template)
        elif chart_type == "line":
            fig = px.line(plot_df, x=x, y=y, color=color_arg, title=title,
                          color_discrete_sequence=color_seq, template=template)
        elif chart_type == "scatter":
            fig = px.scatter(plot_df, x=x, y=y, color=color_arg, title=title,
                             color_discrete_sequence=color_seq, template=template)
        elif chart_type == "pie":
            fig = px.pie(plot_df, names=x, values=y, title=title,
                         color_discrete_sequence=color_seq)
        elif chart_type == "histogram":
            col = y or x
            fig = px.histogram(plot_df, x=col, color=color_arg, title=title,
                               color_discrete_sequence=color_seq, template=template)
        elif chart_type == "box":
            fig = px.box(plot_df, x=x, y=y, color=color_arg, title=title,
                         color_discrete_sequence=color_seq, template=template)
        elif chart_type == "heatmap":
            numeric_df = plot_df.select_dtypes(include="number")
            corr = numeric_df.corr()
            fig = px.imshow(corr, title=title or "Correlation Heatmap",
                            color_continuous_scale="RdBu_r", template=template)
        else:
            fig = px.bar(plot_df, x=x, y=y, title=title, template=template)

        fig.update_layout(
            font_family="DM Sans",
            title_font_size=15,
            title_font_family="Space Grotesk",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=40, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            colorway=color_seq,
        )
        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(gridcolor="rgba(0,0,0,0.05)", zeroline=False)
        return fig

    except Exception as e:
        st.error(f"Chart error: {e}")
        return None

def chart_to_bytes(fig) -> bytes:
    return fig.to_image(format="png", width=1200, height=600, scale=2)

def auto_charts(df: pd.DataFrame):
    """Generate a set of automatic overview charts."""
    charts = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    if len(numeric_cols) >= 2:
        fig = px.scatter_matrix(df[numeric_cols[:5]], title="Scatter Matrix",
                                color_discrete_sequence=CHART_PALETTE)
        fig.update_layout(font_family="DM Sans", paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)")
        charts.append(("Scatter Matrix", fig))

    for col in numeric_cols[:3]:
        fig = px.histogram(df, x=col, title=f"Distribution: {col}",
                           color_discrete_sequence=CHART_PALETTE,
                           template="plotly_white")
        fig.update_layout(font_family="DM Sans", paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)")
        charts.append((f"Distribution: {col}", fig))

    if cat_cols and numeric_cols:
        cat = cat_cols[0]
        num = numeric_cols[0]
        if df[cat].nunique() <= 20:
            grp = df.groupby(cat)[num].mean().sort_values(ascending=False).reset_index()
            fig = px.bar(grp, x=cat, y=num, title=f"Avg {num} by {cat}",
                         color_discrete_sequence=CHART_PALETTE, template="plotly_white")
            fig.update_layout(font_family="DM Sans", paper_bgcolor="rgba(0,0,0,0)",
                              plot_bgcolor="rgba(0,0,0,0)")
            charts.append((f"Avg {num} by {cat}", fig))

    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        fig = px.imshow(corr, title="Correlation Heatmap", color_continuous_scale="RdBu_r")
        fig.update_layout(font_family="DM Sans", paper_bgcolor="rgba(0,0,0,0)")
        charts.append(("Correlation Heatmap", fig))

    return charts
