# main.py
from dotenv import load_dotenv
from colorama import init as colorama_init
import os

# Polished terminal UI
from modules import ui

# Project features
from modules.events import (
    create_event_cli,
    list_events_cli,
    delete_event_cli,
    edit_event_cli,
    load_events,
)
from modules.reminders import start_reminder_loop, add_reminder_cli
from modules.rsvp import (
    add_attendee_cli,
    list_attendees_cli,
    mark_attendance_cli,
    edit_attendee_cli,
    delete_attendee_cli,
)
from modules.invites import send_invites_cli
from modules.ai_email import draft_email
from modules.email_sender import send_email
from modules.ai_poster import generate_poster_for_event
from modules.reports import generate_event_report, email_event_report
from modules.rsvp_inbox import start_inbox_watcher

load_dotenv()
# Initialize colorama for cross-platform color support
colorama_init(autoreset=True, convert=True) 

# Tokens (for engine auto-detect)
OPENAI_KEY      = os.getenv("OPENAI_API_KEY", "") or os.getenv("OPENAI", "")
REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
HF_TOKEN        = os.getenv("HF_API_TOKEN", "")

# ---------- helpers ----------
def _auto_engine():
    """Detects available AI image engines based on environment tokens."""
    if OPENAI_KEY:
        return "openai"
    if REPLICATE_TOKEN:
        return "replicate"
    if HF_TOKEN:
        return "hf"
    return None

def _yn_prompt(label: str, default_yes: bool = True) -> bool:
    """A helper function for simple Yes/No confirmations."""
    default = "Y" if default_yes else "n"
    while True:
        ans = input(f"{label} ({ui.F.GREEN}Y{ui.F.WHITE}/{ui.F.RED}n{ui.F.WHITE}): ").strip().lower() or default.lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        ui.error("❌ Invalid input. Please enter 'Y' or 'n'.")

def _engine_prompt(default_engine: str | None = None) -> str:
    """Prompts the user to select an AI generation engine."""
    default_engine = default_engine or "openai"
    allowed = ["auto", "openai", "replicate", "recraft", "hf", "gemini"]
    while True:
        choice = (
            ui.prompt(f"Engine [auto/openai/replicate/recraft/hf/gemini] (default: {ui.F.YELLOW}{default_engine}{ui.F.WHITE})")
            .strip().lower()
            or default_engine
        )
        if choice in allowed:
            return choice
        ui.error("❌ Invalid input. Please enter one of: auto, openai, replicate, recraft, hf, gemini")

def _try_generate_poster(*, title: str, prompt: str, subtitle: str, footer: str, qr: str | None, engine: str) -> bool:
    """Attempts to generate a poster and handles immediate exceptions."""
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
        return True
    except Exception as e:
        ui.error(f"Poster generation failed with '{engine}': {e}")
        return False

def _generate_with_retries(*, title: str, prompt: str, subtitle: str, footer: str, qr: str | None, first_engine: str):
    """Handles retries and fallback if the initial AI generation fails."""
    attempts = 0
    engine = first_engine
    while attempts < 3:
        attempts += 1
        if _try_generate_poster(title=title, prompt=prompt, subtitle=subtitle, footer=footer, qr=qr, engine=engine):
            return
        if attempts < 3 and _yn_prompt("Try another engine?", default_yes=True):
            engine = _engine_prompt()
            continue
        break
    ui.warning("Falling back to local poster design was handled inside the generator if needed.")

# -------------------- Menu actions --------------------
def action_generate_poster():
    """Gathers input for generating a new event poster."""
    ui.section("Generate Poster")
    title = ui.prompt("Event title")
    if not title:
        ui.warning("Title is required.")
        return

    prompt = ui.prompt("Poster prompt (e.g. 'Birthday with neon balloons')")
    if not prompt:
        prompt = (
            "Elegant Eid al-Fitr poster, green and gold theme, glowing lanterns, "
            "crescent moon, subtle islamic geometry, premium typography, cinematic lighting, 4K"
        )

    detected = _auto_engine()
    if detected is None:
        ui.warning("No image engine tokens found in .env")
    engine = _engine_prompt(default_engine=(detected or "openai"))

    subtitle = ui.prompt("Subtitle (e.g. '2025-10-20 • Jubail')")
    footer  = ui.prompt("Footer (e.g. 'Eid Mubarak 🌙✨') [optional]")
    qr      = ui.prompt("QR text/url (optional)") or None

    _generate_with_retries(title=title, prompt=prompt, subtitle=subtitle, footer=footer, qr=qr, first_engine=engine)

def action_draft_sample_email():
    """Uses AI to draft a sample email based on bullet points."""
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
    """Performs a manual SMTP test to confirm email settings are working."""
    ui.section("Send Test Email (SMTP)")
    to = ui.prompt("To (email)")
    subject = ui.prompt("Subject")
    ui.section("Body")
    body = ui.prompt("Body")
    ok = send_email(to, subject, body, attachments=None)
    ui.success("Sent") if ok else ui.error("Failed")

def action_export_report():
    """Generates a PDF report for a selected event."""
    ui.section("Export Event Report (PDF)")
    title = ui.prompt("Event title")
    try:
        pdf_path = generate_event_report(title)
        ui.success(f"Report saved: {pdf_path}")
    except Exception as e:
        ui.error(f"Failed to generate report: {e}")
    input("Press Enter to continue...")

def action_export_and_email_report():
    """Generates a PDF report and emails it to the specified recipient."""
    ui.section("Export & Email Event Report (PDF)")
    title = ui.prompt("Event title")
    to = ui.prompt("Send to (leave empty to use ORGANIZER_EMAIL/EMAIL_USER)").strip() or None
    try:
        pdf_path = email_event_report(title, to=to)
        ui.success(f"Report generated & emailed. File: {pdf_path}")
    except Exception as e:
        ui.error(f"Failed to email report: {e}")
    input("Press Enter to continue...")

# -------------------- UPDAT — unified update hub --------------------
def update_hub_cli():
    """The central hub for editing event details, attendees, and posters."""
    while True:
        choice = ui.menu(
            "UPDAT — Update Center",
            [
                ("1", "Update Event info (title/date/location/description)"),
                ("2", "Edit Attendee (name/email)"),
                ("3", "Delete Attendee"),
                ("4", "Add/Update Reminder (minutes before)"),
                ("5", "Regenerate Poster (optional)"),
                ("0", "Back"),
            ],
        )

        if choice == "1":
            edit_event_cli(); input("Press Enter to continue...")
        elif choice == "2":
            edit_attendee_cli(); input("Press Enter to continue...")
        elif choice == "3":
            delete_attendee_cli(); input("Press Enter to continue...")
        elif choice == "4":
            add_reminder_cli(); input("Press Enter to continue...")
        elif choice == "5":
            events = load_events()
            if not events:
                ui.warning("No events found."); input("Press Enter to continue..."); continue

            print("\nSelect an event to regenerate poster:")
            for i, e in enumerate(events, 1):
                print(f"{i}. {e['title']} | {e['date']}")

            try:
                idx = int(input("\nNumber: ").strip()) - 1
            except ValueError:
                ui.warning("Invalid input. Please enter a number.")
                input("Press Enter to continue..."); continue

            if not (0 <= idx < len(events)):
                ui.warning("Invalid choice."); input("Press Enter to continue..."); continue

            ev = events[idx]
            title = ev["title"]

            prompt = input("Poster prompt (leave empty for elegant default): ").strip()
            if not prompt:
                prompt = (
                    "Elegant event poster, soft lights, gold accents, "
                    "clean typography, centered composition, 4k, professional design"
                )

            subtitle = input("Subtitle (e.g., '2025-11-25 • Dammam'): ").strip()
            footer  = input("Footer (optional): ").strip()
            qr      = input("QR text/url (optional): ").strip() or None

            auto_guess = _auto_engine() or "openai"
            engine = _engine_prompt(default_engine=auto_guess)

            _generate_with_retries(title=title, prompt=prompt, subtitle=subtitle, footer=footer, qr=qr, first_engine=engine)
            input("Press Enter to continue...")

        elif choice == "0":
            break
        else:
            ui.warning("Invalid choice."); input("Press Enter to continue...")


# -------------------- NEW Hubs --------------------

def core_management_hub_cli():
    """Handles the main CRUD operations (Create, List, Delete) for events."""
    while True:
        choice = ui.menu(
            "1. Core Event Management",
            [
                ("1", f"{ui.CAL} Create New Event"),
                ("2", "List All Events"),
                ("3", "Delete Event"),
                ("0", "Back to Main Menu"),
            ],
        )
        
        if choice == "1":
            create_event_cli(); ui.success("Event created."); input("Press Enter to continue...")
        elif choice == "2":
            ui.section("Your Events"); list_events_cli(); input("Press Enter to continue...")
        elif choice == "3":
            delete_event_cli(); ui.success("Event deleted (if existed)."); input("Press Enter to continue...")
        elif choice == "0":
            break
        else:
            ui.warning("Invalid choice."); input("Press Enter to continue...")

def attendee_hub_cli():
    """Handles attendee list modifications and attendance tracking."""
    while True:
        choice = ui.menu(
            "2. Attendee Management",
            [
                ("1", f"{ui.PEOPLE} Add Attendee to Event"),
                ("2", "List Attendees for Event"),
                ("3", "Mark Attendance for Event"),
                ("0", "Back to Main Menu"),
            ],
        )

        if choice == "1":
            add_attendee_cli(); ui.success("Attendee added."); input("Press Enter to continue...")
        elif choice == "2":
            ui.section("Attendees"); list_attendees_cli(); input("Press Enter to continue...")
        elif choice == "3":
            mark_attendance_cli(); input("Press Enter to continue...")
        elif choice == "0":
            break
        else:
            ui.warning("Invalid choice."); input("Press Enter to continue...")

def communication_hub_cli():
    """Central hub for sending invitations, drafting emails, and managing RSVP sync."""
    while True:
        choice = ui.menu(
            "3. Communication & Invites",
            [
                ("1", f"{ui.MAIL} Send Invites (AI-written email)"),
                ("2", "Draft a Sample Email (AI)"),
                ("3", "Send Test Email (SMTP)"),
                ("4", "Start RSVP Auto-Sync (Inbox watcher)"),
                ("0", "Back to Main Menu"),
            ],
        )

        if choice == "1":
            send_invites_cli(); input("Press Enter to continue...")
        elif choice == "2":
            action_draft_sample_email(); input("Press Enter to continue...")
        elif choice == "3":
            action_send_test_email(); input("Press Enter to continue...")
        elif choice == "4":
            start_inbox_watcher(); input("Press Enter to continue...")
        elif choice == "0":
            break
        else:
            ui.warning("Invalid choice."); input("Press Enter to continue...")


def report_and_reminders_hub_cli():
    """Handles scheduling background reminders and generating reports."""
    while True:
        choice = ui.menu(
            "5. Reports & Reminders",
            [
                ("1", f"{ui.TIME} Start Reminder Service (background)"),
                ("2", "Add Reminder to Event (minutes before)"),
                ("3", f"{ui.REPORT} Export Event Report (PDF)"),
                ("4", "Export & Email Event Report (PDF)"),
                ("0", "Back to Main Menu"),
            ],
        )

        if choice == "1":
            ui.badge("Reminder loop started", bg=ui.B.GREEN); start_reminder_loop()
            input("Press Enter to continue...")
        elif choice == "2":
            add_reminder_cli(); ui.success("Reminder added."); input("Press Enter to continue...")
        elif choice == "3":
            action_export_report()
        elif choice == "4":
            action_export_and_email_report()
        elif choice == "0":
            break
        else:
            ui.warning("Invalid choice."); input("Press Enter to continue...")


# -------------------- Main menu --------------------
def print_main_menu_and_get_choice():
    """Displays the main, simplified navigation menu."""
    items = [
        ("1", f"{ui.CAL} Core Event Management (Create, List, Delete)"),
        ("2", f"{ui.PEOPLE} Attendee Management (Add, List, Mark)"),
        ("3", f"{ui.MAIL} Communication & Invites (Send, Draft, Test)"),
        ("4", f"{ui.POSTER} Generate Poster for Event"),
        ("5", f"{ui.REPORT} Reports & Reminders (Export, Schedule)"),
        ("6", "UPDATE — Update Center (Edit details, Regenerate Poster)"), # ✅ تم تغيير 9 إلى 6
        ("0", "Exit"),
    ]
    return ui.menu("Creative Smart Event Manager", items)

def main():
    """The main application loop that runs the UI."""
    while True:
        choice = print_main_menu_and_get_choice()
        
        if choice == "1":
            core_management_hub_cli()
        elif choice == "2":
            attendee_hub_cli()
        elif choice == "3":
            communication_hub_cli()
        elif choice == "4":
            # Keeping the direct 'Generate Poster' option on the main menu for quick access
            action_generate_poster(); input("Press Enter to continue...") 
        elif choice == "5":
            report_and_reminders_hub_cli()
        elif choice == "6":    
            update_hub_cli()
        elif choice == "0":
            ui.success("Goodbye! Thank you for using the Smart Event Manager."); break
        else:
            ui.warning("Invalid choice."); input("Press Enter to continue...")

if __name__ == "__main__":
    main()