"""
Generates a professional PDF report using ReportLab.
Includes cover page, sentiment chart, tables, and formatted summary.
"""
import matplotlib.pyplot as plt
import re
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak)
from reportlab.lib.units import inch
from utils.text_cleaner import clean_markdown

# Visualization
# ============================================================
def add_sentiment_chart(distribution):
    """Generate a pie chart for sentiment distribution and return it as an in-memory image."""
    if not distribution:
        return None

    labels = list(distribution.keys())
    sizes = list(distribution.values())
    colors_palette = ["#4CAF50", "#EEC447", "#EC4C41"]

    # Create chart in memory (not saved to disk)
    buffer = BytesIO()
    plt.figure(figsize=(3, 3))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors_palette)
    plt.title("Sentiment Distribution")
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    return buffer


# PDF Report Generator
# ============================================================
def create_pdf_report(video_title, sentiment_distribution, top_words, gemini_summary, total_comments):
    """Generate a complete, well-formatted PDF report summarizing the analysis."""

    safe_title = re.sub(r'[\\/*?:"<>|]', "", video_title[:40])
    pdf_filename = f"analysis_report_{safe_title}.pdf"

    doc = SimpleDocTemplate(pdf_filename, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)

    styles = getSampleStyleSheet()

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=colors.HexColor("#0B5394"),
        spaceBefore=12,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor="#444444",
    )
    story = []

    # Cover Page 
    story.append(Spacer(1, 100))
    story.append(Paragraph("🎬 YouTube Comment Analysis Report", styles["Heading1"]))
    story.append(Spacer(1, 30))
    story.append(Paragraph(f"<b>Video Title:</b> {video_title}", body_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Paragraph(f"<b>Total Comments:</b> {total_comments}", body_style))
    story.append(PageBreak())

    # Sentiment Section
    story.append(Paragraph("📊 Sentiment Distribution", section_style))
    chart_buffer = add_sentiment_chart(sentiment_distribution)
    if chart_buffer:
        story.append(Image(chart_buffer, width=250, height=250))
        story.append(Spacer(1, 10))
    if not sentiment_distribution or all(v == 0 for v in sentiment_distribution.values()):
        return None

    if sentiment_distribution:
        data = [["Sentiment", "Percentage (%)"]] + [
            [k.capitalize(), f"{v:.1f}"] for k, v in sentiment_distribution.items()
        ]
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B5394")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

    # Keywords Section
    story.append(Paragraph("🔠 Most Frequent Words", section_style))
    if top_words:
        word_data = [["Word", "Count"]] + [[w, str(c)] for w, c in top_words[:10]]
        word_table = Table(word_data, colWidths=[200, 200])
        word_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        story.append(word_table)
    else:
        story.append(Paragraph("No frequent words found.", body_style))
    story.append(Spacer(1, 30))

    #Gemini Summary
    story.append(PageBreak()) 
    story.append(Paragraph("🧠 AI Summary & Feedback", section_style))
    story.append(Spacer(1, 12))
    clean_summary = clean_markdown(gemini_summary)
    for paragraph in clean_summary.split("\n"):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), body_style))
            story.append(Spacer(1, 6))

    story.append(Spacer(1, 20))
    story.append(Paragraph("<i>End of Report</i>", body_style))

    # Header & Footer
    def header_footer(canvas, doc):
        """Draw header and footer on each page."""
        canvas.saveState()
        canvas.setLineWidth(0.5)
        canvas.line(inch, 11.15 * inch, 7.5 * inch, 11.15 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(inch, 0.6 * inch, "Generated by Gemini AI — © 2025")
        canvas.restoreState()

    # Build PDF 
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"✅ PDF report saved as: {pdf_filename}")
