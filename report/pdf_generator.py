"""
Generates a professional PDF report using ReportLab.
Includes cover page, sentiment chart, tables, and formatted summary.
"""
import re
from io import BytesIO
from datetime import datetime

import requests
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.platypus import (Paragraph, Spacer, Table, TableStyle, Image, PageBreak)

from utils.pdf_utils import get_pdf_styles, create_doc, header_footer
from utils.text_cleaner import clean_markdown

# Visualization
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

def add_analysis_sections(pdf_content, sentiment_distribution, top_words, gemini_summary, styles):
    """Append sentiment chart, top words, and Gemini summary sections to the PDF."""
    heading, subheading, body, section = styles
    # Sentiment Section
    pdf_content.append(Paragraph("📊 Sentiment Distribution", section))
    chart_buffer = add_sentiment_chart(sentiment_distribution)
    if chart_buffer:
        pdf_content.append(Image(chart_buffer, width=250, height=250))
        pdf_content.append(Spacer(1, 10))

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
        pdf_content.append(table)
        pdf_content.append(Spacer(1, 20))

    # Keywords
    pdf_content.append(Paragraph("🔠 Most Frequent Words", section))
    if top_words:
        word_data = [["Word", "Count"]] + [[w, str(c)] for w, c in top_words[:10]]
        word_table = Table(word_data, colWidths=[200, 200])
        word_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        pdf_content.append(word_table)
    else:
        pdf_content.append(Paragraph("No frequent words found.", body))
    pdf_content.append(Spacer(1, 30))

    # Gemini Summary
    pdf_content.append(PageBreak())
    pdf_content.append(Paragraph("🧠 AI Summary & Feedback", section))
    clean_summary = clean_markdown(gemini_summary)
    for paragraph in clean_summary.split("\n"):
        if paragraph.strip():
            pdf_content.append(Paragraph(paragraph.strip(), body))
            pdf_content.append(Spacer(1, 6))

    pdf_content.append(Spacer(1, 20))
    pdf_content.append(Paragraph("<i>End of Report</i>", body))

    return pdf_content


def youtube_channel_report(channel_info, thumb):
    '''Create a PDF Report For Youtube Channel with sentiment & AI analysis.'''
    safe_title = re.sub(r'[\\/*?:"<>|]', "", channel_info["title"])
    pdf_filename = f"channel_report_{safe_title}.pdf"

    #style
    doc = create_doc(pdf_filename)
    heading, subheading, body, section = get_pdf_styles()

    # Download and save the thumbnail
    thumbnail_path = "thumbnail.jpg"
    with open(thumbnail_path, "wb") as f:
        if not thumb or not str(thumb).startswith("http"):
            print(f"⚠️ Invalid thumbnail URL ({thumb}). Using default placeholder instead.")
            thumb = "https://via.placeholder.com/300x200?text=No+Thumbnail"
        f.write(requests.get(thumb).content)

    pdf_content = []

    # Cover Page 
    pdf_content.append(Spacer(1, 10))
    pdf_content.append(Image(thumbnail_path, width=220, height=130))
    pdf_content.append(Spacer(1, 20))
    pdf_content.append(Paragraph("YouTube Channel Analytics Report", heading))
    pdf_content.append(Spacer(1, 10))
    pdf_content.append(Paragraph(f"<b>Channel:</b> {channel_info['title']}", body))
    pdf_content.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", body))
    pdf_content.append(Spacer(1, 20))

    # Static TABLE 
    summary_data = [
        ["Published On", channel_info["published_at"]],
        ["Total Views", f"{channel_info['view_count']}"],
        ["Subscribers", f"{channel_info['subscriber_count']}"],
        ["Total Videos", f"{channel_info['video_count']}"],
    ]

    table = Table(summary_data, colWidths=[150, 300])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("BOX", (0, 0), (-1, -1), 0.25, colors.gray),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
            ("ALIGN", (0, 0), (0, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E3F2FD")),
        ])
    )
    pdf_content.append(table)
    pdf_content.append(Spacer(1, 20))

    #Description 
    pdf_content.append(Paragraph("📝 Channel Description", subheading))
    pdf_content.append(Paragraph(channel_info["description"], body))
    pdf_content.append(Spacer(1, 20))

    # Top videos  
    pdf_content.append(Paragraph("🔥 Top 5 Viewed Videos", subheading))
    for idx, v in enumerate(channel_info["top_videos"], start=1):
        pdf_content.append(
            Paragraph(f"<b>{idx}.</b> {v['title']} — {v['views']} views", body)
        )
        pdf_content.append(Spacer(1, 6))


    doc.build(pdf_content, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"✅ PDF report saved as: {pdf_filename}")

# PDF Report Generator
def create_pdf_report(video_title, sentiment_distribution, top_words, gemini_summary, total_comments):
    """Create a PDF report summarizing the analysis."""

    safe_title = re.sub(r'[\\/*?:"<>|]', "", video_title[:40])
    pdf_filename = f"analysis_report_{safe_title}.pdf"
    
    #Style
    doc = create_doc(pdf_filename)
    heading, subheading, body, section = get_pdf_styles()


    pdf_content = []

    # Cover Page
    pdf_content.append(Spacer(1, 100))
    pdf_content.append(Paragraph("🎬 YouTube Comment Analysis Report", heading))
    pdf_content.append(Spacer(1, 30))
    pdf_content.append(Paragraph(f"<b>Video Title:</b> {video_title}", body))
    pdf_content.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", body))
    pdf_content.append(Paragraph(f"<b>Total Comments:</b> {total_comments}", body))
    pdf_content.append(PageBreak())

    styles = (heading, subheading, body, section)

    add_analysis_sections(pdf_content, sentiment_distribution, top_words, gemini_summary, styles)

    # Build PDF
    doc.build(pdf_content, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"✅ PDF report saved as: {pdf_filename}")