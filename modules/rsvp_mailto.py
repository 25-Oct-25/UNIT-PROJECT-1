import os, urllib.parse
from dotenv import load_dotenv
load_dotenv()

# Where replies go (organizer)
ORGANIZER_EMAIL = (
    os.getenv("ORGANIZER_EMAIL")
    or os.getenv("EMAIL_USER")               # fallback to sender account
)

def _mailto_link(to_email: str, subject: str, body: str) -> str:
    s = urllib.parse.quote(subject, safe="")
    b = urllib.parse.quote(body, safe="")
    return f"mailto:{to_email}?subject={s}&body={b}"

def build_mailto_buttons_html(event_title: str, attendee_name: str, attendee_email: str) -> str:
    if not ORGANIZER_EMAIL:
        # If organizer email is missing, show a friendly warning
        return "<p style='color:#dc2626'>Organizer email is not configured.</p>"

    subj_ok  = f"RSVP ACCEPT — {event_title}"
    subj_ng  = f"RSVP DECLINE — {event_title}"
    base     = (f"Event: {event_title}\n"
                f"Attendee: {attendee_name or '-'} <{attendee_email}>\n")

    link_ok  = _mailto_link(ORGANIZER_EMAIL, subj_ok,  base + "Response: ACCEPT")
    link_ng  = _mailto_link(ORGANIZER_EMAIL, subj_ng,  base + "Response: DECLINE")

    return f"""
    <div style="margin-top:16px">
      <a href="{link_ok}"
         style="display:inline-block;background:#16a34a;color:#fff;text-decoration:none;
                padding:10px 16px;border-radius:8px;margin-right:8px">✅ أقبل الدعوة</a>
      <a href="{link_ng}"
         style="display:inline-block;background:#dc2626;color:#fff;text-decoration:none;
                padding:10px 16px;border-radius:8px">❌ أعتذر عن الحضور</a>
    </div>
    """

def build_mailto_text(event_title: str, attendee_name: str, attendee_email: str) -> str:
    if not ORGANIZER_EMAIL:
        return "Organizer email not configured."
    subj_ok  = f"RSVP ACCEPT — {event_title}"
    subj_ng  = f"RSVP DECLINE — {event_title}"
    base     = (f"Event: {event_title}\nAttendee: {attendee_name or '-'} <{attendee_email}>\n")
    link_ok  = _mailto_link(ORGANIZER_EMAIL, subj_ok, base + "Response: ACCEPT")
    link_ng  = _mailto_link(ORGANIZER_EMAIL, subj_ng, base + "Response: DECLINE")
    return f"RSVP:\nAccept: {link_ok}\nDecline: {link_ng}"
