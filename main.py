# main.py
from colorama import init
from modules.events import (
    create_event_cli,
    list_events_cli,
    delete_event_cli,
    add_reminder_cli,
)
from modules.reminders import start_reminder_loop
from modules.rsvp import add_attendee_cli, list_attendees_cli
from modules.ai_poster import generate_poster
from modules.invites import send_invites_cli
from modules.ai_email import draft_email
from modules.email_sender import send_email

init(autoreset=True)

def print_menu():
    print("\n=== Creative Smart Event Manager ===")
    print("1.  Create Event")
    print("2.  List Events")
    print("3.  Delete Event")
    print("4.  Start Reminder Service (background)")
    print("5.  Add Attendee to Event")
    print("6.  List Attendees for Event")
    print("7.  Add Reminder to Event (minutes before)")
    print("8.  Generate Poster for Event")
    print("9.  Send Invites (Gemini-written email)")
    print("10. Draft a Sample Email (Gemini)")
    print("11. Send Test Email (manual quick test)")
    print("0.  Exit")

def action_generate_poster():
    title = input("Event title: ").strip()
    prompt = input("Poster prompt (e.g. 'Birthday with neon balloons'): ").strip()
    path = f"data/posters/{title.replace(' ', '_')}.png"
    generate_poster(prompt, path)

def action_draft_sample_email():
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
    print("\n--- Drafted Email Body ---\n")
    print(body)
    print("\n---------------------------\n")

def action_send_test_email():
    to = input("To (email): ").strip()
    subject = input("Subject: ").strip()
    body = input("Body: ").strip()
    ok = send_email(to, subject, body, attachments=None)
    print("✅ Sent" if ok else "❌ Failed")

def main():
    while True:
        print_menu()
        choice = input("Select option: ").strip()
        if choice == "1":
            create_event_cli()
        elif choice == "2":
            list_events_cli()
        elif choice == "3":
            delete_event_cli()
        elif choice == "4":
            print("Starting reminder loop… (Ctrl+C to stop)")
            start_reminder_loop()
        elif choice == "5":
            add_attendee_cli()
        elif choice == "6":
            list_attendees_cli()
        elif choice == "7":
            add_reminder_cli()
        elif choice == "8":
            action_generate_poster()
        elif choice == "9":
            send_invites_cli()  # uses Gemini via ai_email.draft_email
        elif choice == "10":
            action_draft_sample_email()  # Gemini draft preview
        elif choice == "11":
            action_send_test_email()  # quick SMTP sanity check
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
