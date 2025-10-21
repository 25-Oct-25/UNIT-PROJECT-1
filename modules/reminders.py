import time, threading, os
from datetime import datetime, timedelta
from pathlib import Path

from modules.events import load_events, save_events
# Pull SMTP config for logs
from modules.email_sender import send_email, SMTP_SERVER, SMTP_PORT, EMAIL_USER, TEST_MODE

# draft_email is optional; fall back if missing
try:
    from modules.ai_email import draft_email   # nice intro if available
except Exception:
    draft_email = None

# Reuse attendee loader (new/legacy/in-event)
from modules.invites import _load_attendees_anywhere

CHECK_INTERVAL_SECONDS = 60   # check every minute
FIRE_WINDOW_SECONDS    = 120  # +/- 120s grace window
ICS_DIR = Path("data/ics")
ICS_DIR.mkdir(parents=True, exist_ok=True)

_printed_boot_info = False  # print env info once on boot


def _ensure_reminder_objects(ev):
    """
    Support both formats:
    - [10, 60] (old)
    - [{"minutes_before": 10, "fired": false}, ...] (new)
    Convert to objects with fired=False.
    """
    new_list = []
    for r in ev.get('reminders', []):
        if isinstance(r, dict):
            r.setdefault('minutes_before', int(r.get('minutes_before', 0)))
            r.setdefault('fired', False)
            new_list.append(r)
        else:
            new_list.append({'minutes_before': int(r), 'fired': False})
    ev['reminders'] = new_list


def _friendly_delta(minutes_before: int) -> str:
    if minutes_before < 60:
        return f"in {minutes_before} min"
    hours = minutes_before // 60
    rem = minutes_before % 60
    if rem == 0:
        return f"in {hours} hour{'s' if hours > 1 else ''}"
    return f"in {hours}h {rem}m"


def _make_ics(event) -> str:
    """
    Create a simple .ics file and return its path.
    Expects event['date'] = "YYYY-MM-DD HH:MM"
    """
    start = datetime.strptime(event['date'], "%Y-%m-%d %H:%M")
    end = start + timedelta(hours=1)  # default 1h

    def fmt(dt: datetime) -> str:
        return dt.strftime("%Y%m%dT%H%M%S")

    uid = f"{event['title'].replace(' ', '_')}-{fmt(start)}@smart-event-manager"
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Smart Event Manager//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "BEGIN:VEVENT",
        f"UID:{uid}",
        f"DTSTAMP:{fmt(datetime.now())}",
        f"DTSTART:{fmt(start)}",
        f"DTEND:{fmt(end)}",
        f"SUMMARY:{event['title']}",
        f"LOCATION:{event.get('location','')}",
        f"DESCRIPTION:{event.get('description','').replace('\\n',' ')}",
        "END:VEVENT",
        "END:VCALENDAR",
    ]
    path = ICS_DIR / f"{uid}.ics"
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return str(path)


def _build_reminder_subject(event, minutes_before: int) -> str:
    return f"⏰ Reminder: {event['title']} { _friendly_delta(minutes_before) }"


def _build_reminder_body_html(event, minutes_before: int) -> str:
    """
    Minimal HTML reminder body; use draft_email for a nicer intro when available.
    """
    title = event["title"]
    when = event["date"]
    where = event.get("location", "")
    desc  = event.get("description", "")
    friendly = _friendly_delta(minutes_before)

    intro = None
    if callable(draft_email):
        try:
            intro = draft_email(
                subject=f"Reminder: {title}",
                audience="attendees",
                tone="friendly, concise",
                bullet_points=[
                    f"Event: {title}",
                    f"When: {when}",
                    f"Where: {where}",
                    "Short reminder before the event.",
                ],
                signature="",
            )
        except Exception:
            intro = None

    if not intro:
        intro = f"This is a quick reminder for <strong>{title}</strong> happening {friendly}."

    if intro.lower().startswith("subject:"):
        intro = "\n".join([ln for ln in intro.splitlines() if not ln.lower().startswith("subject:")]).strip()

    intro_html = intro.replace("\n", "<br>")

    return f"""
    <div style="font-family:Segoe UI,Arial,sans-serif;line-height:1.7;color:#111827">
      <div style="font-size:16px;margin-bottom:8px">{intro_html}</div>
      <div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:12px;margin-top:8px">
        <div><strong>🗓 When:</strong> {when} (<em>{friendly}</em>)</div>
        <div><strong>📍 Where:</strong> {where}</div>
        {"<div style='margin-top:8px'><strong>ℹ️ Details:</strong> " + desc + "</div>" if desc else ""}
      </div>
      <div style="margin-top:14px">
        <span style="color:#6b7280;">Add to calendar via attached .ics</span>
      </div>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0">
      <div style="font-size:12px;color:#6b7280">Sent by Smart Event Manager</div>
    </div>
    """


def _print_boot_info_once():
    global _printed_boot_info
    if _printed_boot_info:
        return
    _printed_boot_info = True
    print("[Reminder BOOT] SMTP config:")
    print(f"  SMTP_SERVER = {SMTP_SERVER}")
    print(f"  SMTP_PORT   = {SMTP_PORT}")
    print(f"  EMAIL_USER  = {EMAIL_USER}")
    print(f"  TEST_MODE   = {TEST_MODE}")
    if TEST_MODE:
        print("  ⚠️ TEST_MODE=True → no real emails. Set False in .env")


def add_reminder_cli():
    """
    CLI: add a reminder (minutes before event) and store as objects.
    """
    events = load_events()
    if not events:
        print("No events found.")
        return

    print("\nSelect an event to add a reminder:")
    for i, e in enumerate(events, start=1):
        print(f"{i}. {e.get('title','(untitled)')}  —  {e.get('date','?')}")

    try:
        idx = int(input("\nEnter number: ").strip()) - 1
    except ValueError:
        print("Invalid input.")
        return

    if not (0 <= idx < len(events)):
        print("Invalid choice.")
        return

    try:
        minutes = int(input("Notify how many minutes before? (e.g., 30): ").strip() or "30")
    except ValueError:
        print("Invalid minutes.")
        return

    _ensure_reminder_objects(events[idx])

    for r in events[idx]["reminders"]:
        if int(r.get("minutes_before", -1)) == minutes:
            print("ℹ️ This reminder already exists for the event.")
            break
    else:
        events[idx]["reminders"].append({"minutes_before": minutes, "fired": False})
        save_events(events)
        print(f"✅ Reminder ({minutes} min before) added to '{events[idx].get('title','event')}'.")


def check_reminders_once():
    events = load_events()
    now = datetime.now()
    changed = False

    for ev in events:
        _ensure_reminder_objects(ev)

        # Event time
        try:
            event_dt = datetime.strptime(ev['date'], '%Y-%m-%d %H:%M')
        except Exception:
            continue

        for r in ev['reminders']:
            if r.get('fired'):
                continue

            minutes_before = int(r.get('minutes_before', 0))
            reminder_time = event_dt - timedelta(minutes=minutes_before)
            delta = (reminder_time - now).total_seconds()

            # Helpful debug print
            delta_s = int(delta)
            when_str = "now" if -1 <= delta_s <= 1 else \
                       (f"in {delta_s}s" if delta_s > 0 else f"{abs(delta_s)}s ago")
            print(f"[Reminder DEBUG] '{ev['title']}' @{minutes_before}m → fire at {reminder_time} ({when_str})")

            # Fire within the grace window
            if -FIRE_WINDOW_SECONDS <= delta <= FIRE_WINDOW_SECONDS:
                # ICS attachment
                ics_path = _make_ics(ev)
                attachments = [ics_path] if os.path.exists(ics_path) else None

                # Email attendees (any source)
                attendees = _load_attendees_anywhere(ev["title"], ev)
                print(f"[Reminder DEBUG] Found {len(attendees)} attendees for '{ev['title']}'")
                if attendees:
                    emails_preview = ", ".join([(p or {}).get('email','') for p in attendees if (p or {}).get('email')])
                    print(f"[Reminder DEBUG] Will email → {emails_preview}")

                subject = _build_reminder_subject(ev, minutes_before)
                body_html = _build_reminder_body_html(ev, minutes_before)

                sent_to = 0
                for person in attendees:
                    email_addr = (person or {}).get('email')
                    if email_addr:
                        if send_email(email_addr, subject, body_html, attachments=attachments, html=True):
                            sent_to += 1

                print(f"[Reminder] {ev['title']} — {minutes_before} minutes before (sent to {sent_to} attendees)")
                r['fired'] = True
                changed = True

    if changed:
        save_events(events)


def _loop():
    _print_boot_info_once()
    while True:
        check_reminders_once()
        time.sleep(CHECK_INTERVAL_SECONDS)


def start_reminder_loop():
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    print("Reminder background thread started (checks every 60s).")
