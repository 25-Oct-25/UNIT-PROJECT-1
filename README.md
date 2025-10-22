# Example Project: Smart Event Manager

## Overview

Smart Event Manager is a command-line application that allows users to create, organize, and manage events easily. It enables event organizers to send AI-generated invitations, reminders, and follow-ups via email, as well as generate posters and PDF reports automatically. The system has two main roles: **Organizer** and **Attendee**, each with their own set of features to make event planning efficient and intelligent.

---

## Features & User Stories

### As an **Organizer**, I should be able to:

* Create, List, and Delete events (title, date, time, location, description).
* Update any event, attendee, reminder, or poster from a unified update hub (**UPDAT**).
* Add, List, and Mark Attendance for attendees (name & email) for an event.
* Generate AI-designed posters for each event (using **OpenAI DALL·E 3** or fallback local design).
* Generate and Send AI-written invitation emails with RSVP options (Accept / Decline).
* Schedule and Run automatic email reminders before each event.
* Generate and Export PDF event reports, with the option to email them directly.
* Start an inbox watcher that auto-updates RSVP responses in real-time.

### As an **Attendee**, I should be able to:

* Receive a professional AI-written invitation email.
* Accept or decline the invitation directly via email.
* Automatically receive reminders before the event starts.
* Download and open `.ics` calendar attachments for easy scheduling.
* View beautifully formatted posters and event information.

---

## Usage

The application uses a simplified, hierarchical menu system for improved navigation.

### I. Main Menu (Core Navigation)

| Key | Action                    | Leads to...                                          |
| --- | ------------------------- | ---------------------------------------------------- |
| 1   | Core Event Management     | Create, List, Delete Events.                         |
| 2   | Attendee Management       | Add, List, Mark Attendance.                          |
| 3   | Communication & Invites   | Send Invites, Draft AI Email, Test Email, RSVP Sync. |
| 4   | Generate Poster for Event | Quick access to AI Poster Generation.                |
| 5   | Reports & Reminders       | Export Reports, Start Reminder Service.              |
| 6   | **UPDAT** — Update Center | Edit Event/Attendee details, Regenerate Poster.      |
| 0   | Exit                      | Exit the program.                                    |

### II. Example Workflow (To Send Invites)

1. Type `3` → Enter **Communication & Invites Hub**.
2. Type `1` → Send **AI-written Invitations** with RSVP buttons.

---

## Project Structure

```
UNIT-PROJECT-1/
├─ assets/
│  └─ fonts/
│     ├─ Cairo.ttf
│     └─ Cairo-Regular.ttf         # (Optional) Used for custom fonts in posters/reports.
├─ data/
│  ├─ attendees/                   # Event-specific JSON attendee data (<event_slug>.json).
│  ├─ ics/                         # Auto-generated .ics calendar files for reminders.
│  ├─ posters/                     # AI-generated poster images saved here per event.
│  ├─ attendees.json               # Legacy store for all attendees (still supported).
│  └─ events.json                  # Stores all events, reminders, and metadata.
├─ modules/
│  ├─ ai_email.py                  # Draft AI invitation/reminder emails (Gemini/Local templates).
│  ├─ ai_poster.py                 # Generate event posters (OpenAI DALL·E 3/Replicate/HF).
│  ├─ email_sender.py              # SMTP sender; handles all single email sending.
│  ├─ events.py                    # Core CRUD operations for events.json + CLI helpers.
│  ├─ invites.py                   # Composes and sends invitations with RSVP mailto buttons.
│  ├─ reminders.py                 # Background reminder service; sends HTML + .ics reminders.
│  ├─ reports.py                   # Generates and emails PDF event reports.
│  ├─ rsvp_inbox.py                # IMAP watcher: auto-updates attendance on RSVP emails.
│  ├─ rsvp_mailto.py               # Builds the 'Accept / Decline' mailto buttons/links.
│  ├─ rsvp.py                      # Manages attendee read/write/mark attendance functionality.
│  ├─ ui.py                        # CLI widgets, Rich/Colorama styling, headers, and menus.
│  
│  
├─ outputs/
│  └─ reports/                     # Generated PDF reports are stored here.
├─ .env                            # Environment file (SMTP, IMAP, API keys, etc.).
├─ README.md                       # Project documentation.
├─ requirements.txt                # Python dependencies.
└─ main.py                         # The CLI main application (menu + routing logic).
```

---
All required libraries are listed in requirements.txt.
Run:

pip install -r requirements.txt


This will install:

python-dotenv

colorama

art

rich

schedule

requests

qrcode

fpdf2

google-generativeai

openai


# Set up the .env file

In the project root, create a file named .env (if not already there).
Add your credentials and test mode flag:

EMAIL_USER=your_email@example.com
EMAIL_PASS=your_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
TEST_MODE=True

# Optional AI Keys
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
REPLICATE_API_TOKEN=your_replicate_key
HF_API_TOKEN=your_hf_token
### NOTE:
Before submitting the final project, please do the following command:  
```bash
pip freeze > requirements.txt
