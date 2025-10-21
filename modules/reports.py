# modules/report.py
import os
from datetime import datetime
from fpdf import FPDF

from modules.events import load_events
from modules.rsvp import load_attendees
from modules.invites import _poster_path  # reuse poster path
from modules.email_sender import send_email
from dotenv import load_dotenv
load_dotenv()

def email_event_report(event_title: str, to: str | None = None) -> str:
   
    pdf_path = generate_event_report(event_title)

    to = (to or
          os.getenv("ORGANIZER_EMAIL") or
          os.getenv("EMAIL_USER"))
    if not to:
        raise RuntimeError("No recipient email found. Set ORGANIZER_EMAIL or EMAIL_USER in .env")

    subject = f"[Report] Event: {event_title}"
    body = (
        f"Hello,\n\n"
        f"Please find attached the PDF report for the event \"{event_title}\".\n\n"
        f"Regards,\nSmart Event Manager"
    )

    ok = send_email(to, subject, body, attachments=[pdf_path])
    if not ok:
        raise RuntimeError("Failed to send report email.")
    return pdf_path


# -------- settings --------
POSTER_MAX_W_MM = 90   # << poster width on A4 (smaller footprint)

def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

class ReportPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Event Report", ln=True, align="C")
        self.ln(2)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", size=9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 8, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 0, "L")
        self.cell(0, 8, f"Page {self.page_no()}", 0, 0, "R")

def _kv(pdf: ReportPDF, key: str, value: str):
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(35, 8, f"{key}:", 0, 0)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 8, value if value else "-")
    pdf.ln(1)

def _stats(attendees):
    total = len(attendees)
    attended = sum(1 for a in attendees if a.get("attended"))
    absent = total - attended
    return total, attended, absent

def _attendees_table(pdf: ReportPDF, attendees):
    if not attendees:
        pdf.set_font("Helvetica", "I", 12)
        pdf.cell(0, 8, "No attendees.", ln=True)
        return

    # headers
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_fill_color(235, 235, 235)
    pdf.cell(60, 8, "Name",  border=1, align="L", fill=True)
    pdf.cell(80, 8, "Email", border=1, align="L", fill=True)
    pdf.cell(30, 8, "Status",border=1, align="C", fill=True)
    pdf.ln(8)

    # rows
    pdf.set_font("Helvetica", "", 11)
    fill = False
    for a in attendees:
        name   = (a.get("name")  or "-")[:40]
        email  = (a.get("email") or "-")[:60]
        status = "Attended" if a.get("attended") else "Absent"

        pdf.set_fill_color(248, 248, 248) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(60, 8, name,   border=1, fill=True)
        pdf.cell(80, 8, email,  border=1, fill=True)
        pdf.cell(30, 8, status, border=1, align="C", fill=True)
        pdf.ln(8)
        fill = not fill

def generate_event_report(event_title: str, poster_max_w_mm: int = POSTER_MAX_W_MM) -> str:
    """Generate a clean English PDF report and save it under outputs/reports/"""
    events = load_events()
    ev = next((e for e in events if e["title"].lower() == event_title.lower()), None)
    if not ev:
        raise RuntimeError("Event not found.")

    attendees = load_attendees(event_title)
    total, attended, absent = _stats(attendees)

    pdf = ReportPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 10, ev["title"], ln=True, align="C")
    pdf.ln(3)

    # Event info
    _kv(pdf, "Date & Time", ev.get("date", "-"))
    _kv(pdf, "Location",    ev.get("location", "-"))
    _kv(pdf, "Description", ev.get("description", "-"))

    # Poster (small)
    poster = _poster_path(ev)
    if poster and os.path.exists(poster):
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Poster", ln=True)

        try:
            x = (210 - poster_max_w_mm) / 2  # center on A4 width
            y = pdf.get_y()
            pdf.image(poster, x=x, y=y, w=poster_max_w_mm)
            # estimate height to push cursor (keep it smaller footprint)
            # A4 width: 210mm. Our poster is portrait; scale ~1.5x height to width typically.
            approx_h = poster_max_w_mm * 1.4
            pdf.ln(approx_h + 2)
        except Exception:
            pdf.set_font("Helvetica", "I", 11)
            pdf.cell(0, 8, f"(Could not embed poster: {os.path.basename(poster)})", ln=True)

    # Summary
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Attendance Summary", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 7, f"Total invited: {total}", ln=True)
    pdf.cell(0, 7, f"Attended: {attended}", ln=True)
    pdf.cell(0, 7, f"Absent: {absent}", ln=True)

    # Table
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Attendees", ln=True)
    _attendees_table(pdf, attendees)

    # Save
    _ensure_dir("outputs/reports")
    safe = ev["title"].replace(" ", "_")
    out_path = os.path.join("outputs", "reports", f"{safe}.pdf")
    pdf.output(out_path)
    return out_path
