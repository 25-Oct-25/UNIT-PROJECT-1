import os
import re
import time
import imaplib
import email
from email.header import decode_header, make_header
from typing import Optional, Tuple

from dotenv import load_dotenv
load_dotenv()

from modules.rsvp import load_attendees, save_attendees
from modules.events import load_events, save_events
from modules import ui

IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
IMAP_PORT   = int(os.getenv("IMAP_PORT", "993"))
EMAIL_USER  = os.getenv("EMAIL_USER", "")
EMAIL_PASS  = os.getenv("EMAIL_PASS", "")

# Subject patterns agreed with mailto buttons (keep in sync with invites.py)
SUBJ_ACCEPT_PREFIX = "RSVP ACCEPT — "
SUBJ_DECLINE_PREFIX = "RSVP DECLINE — "

POLL_SECONDS = 60  # check every minute

def _apply_rsvp_decision(event_title: str, attendee_email: str, accept: bool) -> bool:
    """Update attendance across files (attendees/<event>.json and events.json)."""
    attendee_email = (attendee_email or "").strip().lower()
    changed = False

    # 1) attendees/<event>.json
    attendees = load_attendees(event_title)
    for a in attendees:
        if (a.get("email") or "").strip().lower() == attendee_email:
            a["attended"] = bool(accept)
            changed = True
            break
    if changed:
        save_attendees(event_title, attendees)

    # 2) inline copy within events.json (if present)
    events = load_events()
    ev_changed = False
    for ev in events:
        if ev.get("title", "").lower() == event_title.lower():
            for a in ev.get("attendees", []):
                if (a.get("email") or "").strip().lower() == attendee_email:
                    a["attended"] = bool(accept)
                    ev_changed = True
                    break
            break
    if ev_changed:
        save_events(events)

    return changed or ev_changed

def _decode(s):
    if not s:
        return ""
    try:
        return str(make_header(decode_header(s)))
    except Exception:
        return s

def _extract_event_from_subject(subj: str) -> Tuple[Optional[str], Optional[bool]]:
    subj = _decode(subj).strip()
    if subj.startswith(SUBJ_ACCEPT_PREFIX):
        return subj[len(SUBJ_ACCEPT_PREFIX):].strip(), True
    if subj.startswith(SUBJ_DECLINE_PREFIX):
        return subj[len(SUBJ_DECLINE_PREFIX):].strip(), False
    return None, None

def _extract_attendee_from_body(text: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Expected body from mailto:
      Event: <title>
      Attendee: <Name> <email>
      Response: ACCEPT | DECLINE
    """
    event = None
    name  = None
    email_addr = None

    # Event
    m = re.search(r"Event:\s*(.+)", text, re.IGNORECASE)
    if m: event = m.group(1).strip()

    # Attendee: Ziyad <z@x.com>
    m = re.search(r"Attendee:\s*(.+?)\s*<([^>]+)>", text, re.IGNORECASE)
    if m:
        name = m.group(1).strip()
        email_addr = m.group(2).strip()

    # Fallback: grab <email> if present anywhere
    if not email_addr:
        m2 = re.search(r"<([^>]+)>", text)
        if m2:
            email_addr = m2.group(1).strip()

    return event, name, email_addr

def _walk_text(payload) -> str:
    if payload.is_multipart():
        parts = []
        for part in payload.walk():
            ctype = part.get_content_type()
            if ctype in ("text/plain", "text/html"):
                try:
                    charset = part.get_content_charset() or "utf-8"
                    parts.append(part.get_payload(decode=True).decode(charset, errors="ignore"))
                except Exception:
                    pass
        return "\n".join(parts)
    else:
        try:
            charset = payload.get_content_charset() or "utf-8"
            return payload.get_payload(decode=True).decode(charset, errors="ignore")
        except Exception:
            return payload.get_payload() or ""

def _connect():
    if not (EMAIL_USER and EMAIL_PASS):
        raise RuntimeError("EMAIL_USER/EMAIL_PASS not configured in .env")
    M = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    M.login(EMAIL_USER, EMAIL_PASS)
    return M

def poll_inbox_once(mark_seen: bool = True) -> int:
    """
    Read unseen emails with 'RSVP ' in subject,
    apply decisions to attendance,
    return count processed.
    """
    try:
        M = _connect()
    except Exception as e:
        ui.error(f"IMAP login failed: {e}")
        return 0

    processed = 0
    try:
        M.select("INBOX")
        # Unseen and has RSVP in subject
        status, data = M.search(None, '(UNSEEN SUBJECT "RSVP ")')
        if status != "OK":
            return 0
        ids = data[0].split()
        for msg_id in ids:
            status, msg_data = M.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            try:
                msg = email.message_from_bytes(msg_data[0][1])
                subj = _decode(msg.get("Subject", ""))
                event_from_subj, accept_from_subj = _extract_event_from_subject(subj)

                body_text = _walk_text(msg)
                event_from_body, _, attendee_email = _extract_attendee_from_body(body_text)

                # Prefer subject for decision, fallback to body
                if accept_from_subj is None:
                    accept_from_subj = True if re.search(r"Response:\s*ACCEPT", body_text, re.I) else False if re.search(r"Response:\s*DECLINE", body_text, re.I) else None

                # Event from subject first, then body
                event_title = event_from_subj or event_from_body

                if event_title and attendee_email and accept_from_subj is not None:
                    ok = _apply_rsvp_decision(event_title, attendee_email, accept=accept_from_subj)
                    if ok:
                        state = "Attended" if accept_from_subj else "Absent"
                        ui.success(f"[RSVP] {attendee_email} → {state} @ {event_title}")
                    else:
                        ui.warning(f"[RSVP] Not found in records: {attendee_email} @ {event_title}")
                    processed += 1
                else:
                    ui.warning("[RSVP] Could not parse message (missing event/email/decision).")

            except Exception as e:
                ui.error(f"[RSVP] Parse error: {e}")

            # Mark as seen to avoid re-processing
            if mark_seen:
                try:
                    M.store(msg_id, '+FLAGS', '\\Seen')
                except Exception:
                    pass

    finally:
        try:
            M.close()
            M.logout()
        except Exception:
            pass

    return processed

def start_inbox_watcher():
    """Background polling every 60s."""
    import threading
    def _loop():
        ui.badge("RSVP inbox watcher started", bg="green")
        while True:
            cnt = poll_inbox_once(mark_seen=True)
            if cnt:
                ui.kv("RSVP processed", str(cnt))
            time.sleep(POLL_SECONDS)

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    ui.success("Started RSVP auto-sync (email → attendance).")
