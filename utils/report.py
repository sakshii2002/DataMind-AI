import io
import pandas as pd
from datetime import datetime

def generate_pdf_report(df: pd.DataFrame, quality_report: dict, insights: str, charts: list, filename: str) -> bytes:
    """Generate a PDF report using reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, HRFlowable, Image, PageBreak)
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    import plotly.io as pio

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    ACCENT = colors.HexColor("#5B4FF5")
    ACCENT2 = colors.HexColor("#10B981")
    DARK = colors.HexColor("#1A1D2E")
    MUTED = colors.HexColor("#6B7280")
    BG = colors.HexColor("#F5F6FA")

    title_style = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=22,
                            textColor=DARK, spaceAfter=4, alignment=TA_LEFT)
    subtitle_style = ParagraphStyle("subtitle", fontName="Helvetica", fontSize=11,
                                    textColor=MUTED, spaceAfter=16)
    h2_style = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=14,
                            textColor=ACCENT, spaceBefore=16, spaceAfter=8)
    body_style = ParagraphStyle("body", fontName="Helvetica", fontSize=10,
                                textColor=DARK, spaceAfter=6, leading=15)
    code_style = ParagraphStyle("code", fontName="Courier", fontSize=9,
                                textColor=DARK, spaceAfter=4)

    elements = []

    # Header
    elements.append(Paragraph("DataMind AI", title_style))
    elements.append(Paragraph(f"Data Analysis Report — {filename}", subtitle_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=16))

    # Summary metrics
    elements.append(Paragraph("Dataset Overview", h2_style))
    summary_data = [
        ["Metric", "Value"],
        ["Rows", f"{df.shape[0]:,}"],
        ["Columns", str(df.shape[1])],
        ["Numeric Columns", str(len(df.select_dtypes(include='number').columns))],
        ["Categorical Columns", str(len(df.select_dtypes(include=['object','category']).columns))],
        ["Duplicate Rows", str(quality_report.get("duplicate_rows", 0))],
        ["Data Quality Score", f"{quality_report.get('quality_score', 0)}/100"],
    ]
    t = Table(summary_data, colWidths=[8*cm, 8*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 1), (-1, -1), BG),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDE1F5")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 12))

    # Missing values
    missing_df = quality_report.get("missing", pd.DataFrame())
    if not missing_df.empty:
        elements.append(Paragraph("Missing Values", h2_style))
        mdata = [["Column", "Missing Count", "Missing %"]]
        for _, row in missing_df.iterrows():
            mdata.append([str(row["Column"]), str(row["Missing Count"]), f"{row['Missing %']}%"])
        mt = Table(mdata, colWidths=[8*cm, 5*cm, 4*cm])
        mt.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EF4444")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FEF2F2")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FCA5A5")),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        elements.append(mt)
        elements.append(Spacer(1, 12))

    # Outliers
    outliers_df = quality_report.get("outliers", pd.DataFrame())
    if not outliers_df.empty:
        elements.append(Paragraph("Outlier Analysis (IQR Method)", h2_style))
        odata = [["Column", "Outlier Count", "Outlier %", "Lower Bound", "Upper Bound"]]
        for _, row in outliers_df.iterrows():
            odata.append([str(row["Column"]), str(row["Outlier Count"]),
                          f"{row['Outlier %']}%", str(row["Lower Bound"]), str(row["Upper Bound"])])
        ot = Table(odata, colWidths=[5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        ot.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F59E0B")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FFFBEB")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FCD34D")),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        elements.append(ot)
        elements.append(Spacer(1, 12))

    # AI Insights
    if insights:
        elements.append(PageBreak())
        elements.append(Paragraph("AI-Generated Insights", h2_style))
        for line in insights.split("\n"):
            if line.strip():
                clean = line.replace("**", "").replace("*", "").strip()
                elements.append(Paragraph(clean, body_style))
        elements.append(Spacer(1, 12))

    # Charts
    if charts:
        elements.append(PageBreak())
        elements.append(Paragraph("Visualizations", h2_style))
        for title, fig in charts[:6]:
            try:
                img_bytes = fig.to_image(format="png", width=900, height=450, scale=1.5)
                img_buf = io.BytesIO(img_bytes)
                img = Image(img_buf, width=16*cm, height=8*cm)
                elements.append(Paragraph(title, ParagraphStyle("ct", fontName="Helvetica-Bold",
                                          fontSize=11, textColor=DARK, spaceBefore=12, spaceAfter=6)))
                elements.append(img)
                elements.append(Spacer(1, 8))
            except Exception:
                pass

    # Descriptive stats
    elements.append(PageBreak())
    elements.append(Paragraph("Descriptive Statistics", h2_style))
    desc = df.describe().round(3)
    stat_data = [["Stat"] + list(desc.columns)]
    for idx, row in desc.iterrows():
        stat_data.append([str(idx)] + [str(round(v, 3)) for v in row.values])
    col_count = len(desc.columns) + 1
    col_w = 17.0 / col_count
    st_table = Table(stat_data, colWidths=[col_w*cm] * col_count)
    st_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#DDE1F5")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))
    elements.append(st_table)

    doc.build(elements)
    return buf.getvalue()
