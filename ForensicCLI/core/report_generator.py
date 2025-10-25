# ForensicCLI/core/report_generator.py
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf_report(case_name, analysis_dict, output_dir="output/reports"):
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(output_dir, f"{case_name}_report_{ts}.pdf")

    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Forensic Case Report: {case_name}")
    y -= 30
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 30

    def write_line(text):
        nonlocal y
        c.drawString(50, y, text)
        y -= 15
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 10)

    # summary 
    write_line(f"Directory: {analysis_dict.get('directory','-')}")
    write_line(f"Files Scanned: {analysis_dict.get('files_scanned',0)}")
    write_line(f"Images Found: {analysis_dict.get('images_found',0)}")
    write_line(f"CSV Found: {analysis_dict.get('csv_found',False)}")

    # CSV data
    ds = analysis_dict.get("dataset_summary", {})
    if ds:
        write_line("---- Dataset Summary ----")
        write_line(f"CSV Path: {ds.get('csv_path','-')}")
        write_line(f"Rows: {ds.get('rows','-')}")
        write_line(f"Columns: {ds.get('columns','-')}")
        write_line(f"Missing Values: {ds.get('missing_values','-')}")
        labels = ds.get("label_counts", {})
        if labels:
            write_line(f"Label Counts: {labels}")

    # قواعد الشبهات
    write_line("---- Suspicious Rules ----")
    write_line(f"Suspicious Rule Hits: {analysis_dict.get('suspicious_rule_hits',0)}")
    for d in analysis_dict.get("rule_details", []):
        write_line(f"- {d}")

    c.showPage()
    c.save()
    return pdf_path
