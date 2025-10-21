## Example Project: Smart Event Manager

### Overview:
Smart Event Manager is a command-line application that allows users to create, organize, and manage events easily.  
It enables event organizers to send AI-generated invitations, reminders, and follow-ups via email, as well as generate posters and PDF reports automatically.  
The system has two main roles: **Organizer** and **Attendee**, each with their own set of features to make event planning efficient and intelligent.

---

### Features & User Stories

#### As an **Organizer**, I should be able to:
- Create a new event (title, date, time, location, description).  
- List all created events.  
- Delete existing events.  
- Update any event, attendee, reminder, or poster from a unified update hub.  
- Add attendees (name & email) to an event.  
- View the list of attendees for a specific event.  
- Generate AI-written invitation emails with RSVP options (Accept / Decline).  
- Send invitations to all attendees with one click.  
- Generate AI-designed posters for each event.  
- Add event reminders (e.g., 10 min or 30 min before start time).  
- Automatically send email reminders before each event.  
- Automatically update attendance when guests accept or decline invitations.  
- Generate PDF event reports containing all details and attendees.  
- Export and email these reports directly to recipients.  
- Start an inbox watcher that auto-updates RSVP responses in real-time.  

#### As an **Attendee**, I should be able to:
- Receive a professional AI-written invitation email.  
- Accept or decline the invitation directly via email.  
- Automatically receive reminders before the event starts.  
- Download and open `.ics` calendar attachments.  
- View beautifully formatted posters and event information.  

---

### Usage

Explain to the user how to use your project.  
For example:

- Type `1` → Create Event (add title, date, time, and location).  
- Type `2` → List all created events.  
- Type `3` → Delete an event.  
- Type `4` → Update (Event / Attendees / Reminders / Poster).  
- Type `5` → Start the Reminder Service (runs in background).  
- Type `6` → Add an Attendee to an event.  
- Type `7` → List Attendees for a specific event.  
- Type `8` → Mark Attendance for an event.  
- Type `9` → Add Reminder (minutes before event).  
- Type `10` → Generate AI Poster for an event.  
- Type `11` → Send AI-written Invitations with RSVP buttons.  
- Type `12` → Draft a sample AI email.  
- Type `13` → Send a test email (to verify SMTP settings).  
- Type `14` → Export event report as PDF.  
- Type `15` → Export and email the report.  
- Type `16` → Start the RSVP Auto-Sync Service (auto updates from inbox).  
- Type `0` → Exit the program.  

---

### Project Structure

---

UNIT-PROJECT-1/
├─ assets/
│  └─ fonts/
│     ├─ Cairo.ttf
│     └─ Cairo-Regular.ttf         # (optional) used if you want custom fonts in posters/reports later
├─ data/
│  ├─ attendees/                   # One JSON per event: data/attendees/<event_slug>.json
│  ├─ ics/                         # Auto-generated .ics calendar files for reminders
│  ├─ posters/                     # AI-generated poster images saved here per event
│  ├─ attendees.json               # (legacy) all-events-in-one attendees store (still supported)
│  └─ events.json                  # Stores all events + reminders + metadata
├─ modules/
│  ├─ ai_email.py                  # Draft AI invitation/reminder emails (Gemini if available, else local templates)
│  ├─ ai_poster.py                 # Generate event posters (Replicate/HF/Gemini; adds title/QR)
│  ├─ email_sender.py              # SMTP sender (supports TEST_MODE); single place for sending emails
│  ├─ events.py                    # CRUD operations for events.json (create/list/delete/edit) + CLI helpers
│  ├─ gamification.py              # (optional) simple points/leaderboard system
│  ├─ invites.py                   # Compose & send invitations + RSVP mailto buttons per attendee
│  ├─ reminders.py                 # Background reminder service; sends HTML + .ics reminders to attendees
│  ├─ reports.py                   # Generate PDF event reports & optionally email them (poster + attendees table)
│  ├─ rsvp_inbox.py                # IMAP watcher: auto-update attendance on RSVP emails (Accept/Decline)
│  ├─ rsvp_mailto.py               # Builds the “Accept / Decline” mailto buttons/links for attendees
│  ├─ rsvp.py                      # Read/write attendees for a given event + CLI (add/list/mark attendance)
│  ├─ theme_suggestions.py         # Suggest visual “themes” for posters (fun/optional)
│  ├─ ui.py                        # CLI widgets and colors (headers, boxes, menus, alerts)
│  ├─ update_hub.py                # Central hub for updating events, attendees, reminders, and posters
│  └─ actions.py                   # Quick helper actions (generate poster, draft email, send test email, etc.)
├─ outputs/
│  └─ reports/                     # Generated PDF reports are stored here
├─ .env                            # Environment file (SMTP, IMAP, API keys, etc.)
├─ README.md                       # Project documentation
├─ requirements.txt                # Python dependencies (generated with pip freeze)
├─ main.py                         # The CLI main app (menu + routes to the modules)
└─ list_models.py                  # Utility to list available Gemini models (for debugging)



### NOTE:
Before submitting the final project, please do the following command:  
```bash
pip freeze > requirements.txt
