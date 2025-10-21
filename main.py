# main.py
from dotenv import load_dotenv
from colorama import init as colorama_init
import os

# واجهة مُحسّنة
from modules import ui

# وظائف المشروع
from modules.events import (
    create_event_cli,
    list_events_cli,
    delete_event_cli,
)
from modules.reminders import start_reminder_loop, add_reminder_cli
from modules.rsvp import add_attendee_cli, list_attendees_cli, mark_attendance_cli
from modules.invites import send_invites_cli
from modules.ai_email import draft_email
from modules.email_sender import send_email
from modules.ai_poster import generate_poster_for_event
from modules.reports import generate_event_report, email_event_report
from modules.rsvp_inbox import start_inbox_watcher
from modules import ui



load_dotenv()
colorama_init(autoreset=True, convert=True)

REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
HF_TOKEN = os.getenv("HF_API_TOKEN", "")

def _auto_engine():
    if REPLICATE_TOKEN:
        return "replicate"
    if HF_TOKEN:
        return "hf"
    return None

# -------------------- أفعال القائمة --------------------

def action_generate_poster():
    ui.section("Generate Poster")
    title = ui.prompt("Event title")
    if not title:
        ui.warning("Title is required.")
        return

    prompt = ui.prompt("Poster prompt (e.g. 'Birthday with neon balloons')")
    if not prompt:
        prompt = (
            "Elegant Eid al-Fitr poster, green and gold theme, glowing lanterns, "
            "crescent moon in the sky, Islamic geometric patterns, Arabic calligraphy 'Eid Mubarak', "
            "cinematic lighting, 4K resolution, professional design"
        )

    detected = _auto_engine()
    engine = None
    if detected is None:
        ui.warning("No image engine tokens found in .env")
        engine = ui.prompt("Engine (replicate/hf)").lower()
    else:
        default_info = f"[{detected}]"
        ans = ui.prompt(f"Engine (replicate/hf) {default_info}")
        engine = (ans.lower() or detected)

    subtitle = ui.prompt("Subtitle (e.g. '2025-10-20 • Jubail')")
    footer   = ui.prompt("Footer (e.g. 'Eid Mubarak 🌙✨') [optional]")
    qr       = ui.prompt("QR text/url (optional)") or None

    try:
        out_path = generate_poster_for_event(
            event_title=title,
            base_prompt=prompt,
            engine=engine,
            subtitle=subtitle,
            footer=footer,
            qr_text=qr,
        )
        ui.success(f"Poster saved at: {out_path}")
    except Exception as e:
        ui.error(f"Poster generation failed: {e}")

def action_draft_sample_email():
    ui.section("Draft Sample Email (AI)")
    body = draft_email(
        subject="Request for access to the training portal",
        audience="HR training team",
        tone="polite, direct",
        bullet_points=[
            "I couldn't sign up with company email",
            "Request permission to register with personal email",
            "I will switch back once the issue is fixed",
        ],
        signature="Ziyad",
    )
    ui.section("AI Email Preview")
    ui.boxed(body, color=ui.F.BLUE)
def action_send_test_email():
    ui.section("Send Test Email (SMTP)")
    to = ui.prompt("To (email)")
    subject = ui.prompt("Subject")
    ui.section("Body")
    body = ui.prompt("Body")
    ok = send_email(to, subject, body, attachments=None)
    ui.success("Sent") if ok else ui.error("Failed")

def action_export_report():
    ui.section("Export Event Report (PDF)")
    title = ui.prompt("Event title")
    try:
        pdf_path = generate_event_report(title)
        ui.success(f"Report saved: {pdf_path}")
    except Exception as e:
        ui.error(f"Failed to generate report: {e}")
    input("Press Enter to continue...")

def action_export_and_email_report():
    ui.section("Export & Email Event Report (PDF)")
    title = ui.prompt("Event title")
    to = ui.prompt("Send to (leave empty to use ORGANIZER_EMAIL/EMAIL_USER)").strip() or None
    try:
        pdf_path = email_event_report(title, to=to)
        ui.success(f"Report generated & emailed. File: {pdf_path}")
    except Exception as e:
        ui.error(f"Failed to email report: {e}")
    input("Press Enter to continue...")

# -------------------- القائمة الرئيسية --------------------

def print_menu_and_get_choice():
    items = [
        ("1", f"{ui.CAL}  Create Event"),
        ("2", "List Events"),
        ("3", "Delete Event"),
        ("4", f"{ui.TIME} Start Reminder Service (background)"),
        ("5", f"{ui.PEOPLE} Add Attendee to Event"),
        ("6", "List Attendees for Event"),
        ("7", "Add Reminder to Event (minutes before)"),
        ("8", f"{ui.POSTER} Generate Poster for Event"),
        ("9", f"{ui.MAIL} Send Invites (AI-written email)"),
        ("10", "Draft a Sample Email (AI)"),
        ("11", "Send Test Email (SMTP)"),
        ("12", "Mark Attendance for Event"),
        ("13", "Export Event Report (PDF)"),
        ("14", "Export & Email Event Report (PDF)"),
        ("15", "Start RSVP Auto-Sync (Inbox watcher)"),
        ("0", "Exit"),
    ]
    return ui.menu("Creative Smart Event Manager", items)

def main():
    while True:
        choice = print_menu_and_get_choice()
        if choice == "1":
            create_event_cli()
            ui.success("Event created.")
            input("Press Enter to continue...")
        elif choice == "2":
            ui.section("Your Events")
            list_events_cli()
            input("Press Enter to continue...")
        elif choice == "3":
            delete_event_cli()
            ui.success("Event deleted (if existed).")
            input("Press Enter to continue...")
        elif choice == "4":
            ui.badge("Reminder loop started", bg=ui.B.GREEN)
            start_reminder_loop()
        elif choice == "5":
            add_attendee_cli()
            ui.success("Attendee added.")
            input("Press Enter to continue...")
        elif choice == "6":
            ui.section("Attendees")
            list_attendees_cli()
            input("Press Enter to continue...")
        elif choice == "7":
            add_reminder_cli()
            ui.success("Reminder added.")
            input("Press Enter to continue...")
        elif choice == "8":
            action_generate_poster()
            input("Press Enter to continue...")
        elif choice == "9":
            send_invites_cli()
            input("Press Enter to continue...")
        elif choice == "10":
            action_draft_sample_email()
            input("Press Enter to continue...")
        elif choice == "11":
            action_send_test_email()
            input("Press Enter to continue...")
        elif choice == "12":
            mark_attendance_cli()
            input("Press Enter to continue...")
        elif choice == "13":
            action_export_report()
        elif choice == "14":
            action_export_and_email_report()
        elif choice in ("15"):
            start_inbox_watcher()
            input("Press Enter to continue...")

        elif choice == "0":
            ui.success("Goodbye!")
            break
        else:
            ui.warning("Invalid choice.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
