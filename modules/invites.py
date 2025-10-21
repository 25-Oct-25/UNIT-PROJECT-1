import os
import tempfile
import subprocess
import platform
import json

from modules.rsvp_mailto import build_mailto_buttons_html, build_mailto_text
from modules.events import load_events
from modules.email_sender import send_email
from modules.ai_email import draft_email
from modules.rsvp import load_attendees as load_attendees_for_event
from modules import ui

# -------- Helpers --------
def _event_kind(title: str) -> str:
    t = (title or "").lower()
    if any(k in t for k in ["eid", "عيد"]): return "eid"
    if any(k in t for k in ["birthday", "عيد ميلاد", "حفلة"]): return "birthday"
    if any(k in t for k in ["graduation", "تخرج"]): return "graduation"
    if any(k in t for k in ["meeting","workshop","training","conference","اجتماع"]): return "meeting"
    return "generic"

def _subject_for(event):
    kind = _event_kind(event['title'])
    title = event['title']
    if kind == "eid":        return f"Eid Mubarak! You're invited: {title}"
    if kind == "birthday":   return f"🎂 You're invited: {title}"
    if kind == "graduation": return f"🎓 You're invited: {title}"
    return f"You're invited: {title}"

def _poster_path(event):
    filename = event['title'].replace(' ', '_') + ".png"
    path = os.path.join("data", "posters", filename)
    return path if os.path.exists(path) else None

def _ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def _personalize_body(body: str, name: str, is_html: bool) -> str:
    """Swap greeting to 'Dear {name},' when possible."""
    if not name:
        return body
    if is_html:
        lower = body.lower()
        if lower.strip().startswith("dear"):
            parts = body.split("<br>", 1)
            head = f"Dear {name},"
            if len(parts) == 1:
                return head + "<br>" + parts[0]
            return head + "<br>" + parts[1]
        else:
            return f"Dear {name},<br><br>{body}"
    else:
        if body.lower().startswith("dear"):
            lines = body.splitlines()
            lines[0] = f"Dear {name},"
            return "\n".join(lines)
        return f"Dear {name},\n\n{body}"

def _open_in_editor_with_text(initial_text: str) -> str:
    """Open system editor for quick edits; return the edited text."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".txt", encoding="utf-8") as tmp:
        tmp.write(initial_text)
        tmp_path = tmp.name

    system = platform.system()
    try:
        if system == "Windows":
            os.system(f'notepad "{tmp_path}"')
        elif system == "Darwin":
            subprocess.call(["open", tmp_path])
        else:
            subprocess.call(["xdg-open", tmp_path])
    except Exception as e:
        print(f"⚠️ Failed to open editor: {e}")
        print("Paste your edits manually below. Finish with an empty line.\n")
        edited = []
        while True:
            line = input()
            if line == "":
                break
            edited.append(line)
        return "\n".join(edited).strip()

    try:
        with open(tmp_path, "r", encoding="utf-8") as f:
            edited_text = f.read().strip()
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass
    return edited_text or initial_text

def _load_attendees_anywhere(event_title: str, ev: dict):
    """
    Find attendees from multiple sources in order:
    1) data/attendees/<event>.json (new)
    2) data/attendees.json legacy format {"EventTitle": [...]}
    3) ev['attendees'] if present
    """
    attendees = load_attendees_for_event(event_title)
    if attendees:
        return attendees

    legacy_path = os.path.join("data", "attendees.json")
    if os.path.exists(legacy_path):
        try:
            with open(legacy_path, "r", encoding="utf-8") as f:
                legacy = json.load(f)
            attendees = legacy.get(event_title) or legacy.get(ev.get("title", ""))
            if attendees:
                return attendees
        except Exception:
            pass

    return ev.get("attendees", [])

# -------- Core sending --------
def send_invites_for_event(
    event_title: str,
    tone: str = "polite, friendly",
    use_html: bool = True,
    preview_and_edit: bool = True
):
    events = load_events()
    ev = next((e for e in events if e['title'].lower() == event_title.lower()), None)
    if not ev:
        ui.error("Event not found.")
        return

    attendees = _load_attendees_anywhere(event_title, ev)
    if not attendees:
        ui.warning("No attendees to invite.")
        return

    subject = _subject_for(ev)

    # 1) AI draft (BODY only)
    body_text = draft_email(
        subject=subject,
        audience="attendees",
        tone=tone,
        bullet_points=[
            f"Event: {ev['title']}",
            f"When: {ev['date']}",
            f"Where: {ev.get('location','')}",
            ev.get('description','')
        ],
        signature="Ziyad"
    )

    # 2) Preview + optional edit
    if preview_and_edit:
        ui.section("AI Generated Email Preview")
        ui.boxed(body_text, color=ui.F.BLUE)

        subj_edit = input(f"Edit subject? (current: '{subject}') (y/N): ").strip().lower()
        if subj_edit == "y":
            new_subj = input("New subject: ").strip()
            if new_subj:
                subject = new_subj

        choice = input("Edit body in editor? (Y/n): ").strip().lower()
        if choice != "n":
            body_text = _open_in_editor_with_text(body_text)

    # Save preview copy
    _ensure_dir("outputs")
    with open(os.path.join("outputs", "last_invite_preview.txt"), "w", encoding="utf-8") as f:
        f.write(f"Subject: {subject}\n\n{body_text}")

    # 3) Build base body (HTML or plain)
    if use_html:
        wrapped = (
            '<div style="font-family:Segoe UI,Arial,sans-serif;line-height:1.7;color:#111827">'
            f'<div style="font-size:16px">{body_text.replace("\n","<br>")}</div>'
            '<hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0">'
            '<div style="font-size:12px;color:#6b7280">Sent by Smart Event Manager</div>'
            '</div>'
        )
        is_html = True
    else:
        wrapped = body_text
        is_html = False

    # 4) Attachment (poster)
    attach = _poster_path(ev)
    attachments = [attach] if attach else None

    # Final preview
    ui.section("Final Preview")
    ui.kv("Subject", subject)
    ui.boxed(body_text, color=ui.F.CYAN)
    print()  # spacer

    if input("Send now? (Y/n): ").strip().lower() == "n":
        ui.warning("Cancelled by user.")
        return

    # 5) Send personalized emails + inject RSVP links/buttons
    sent = 0
    for a in attendees:
        name  = (a or {}).get('name', '').strip()
        email = (a or {}).get('email', '').strip()
        if not email:
            continue

        if use_html:
            rsvp_html = build_mailto_buttons_html(ev["title"], name, email)
            # Insert buttons before first <hr> if possible, else append
            low = wrapped.lower()
            idx = low.find("<hr")
            if idx != -1:
                recipient_wrapped = wrapped[:idx] + rsvp_html + wrapped[idx:]
            else:
                recipient_wrapped = wrapped + rsvp_html
            final_body = _personalize_body(recipient_wrapped, name, is_html=True)
        else:
            rsvp_text = "\n\n" + build_mailto_text(ev["title"], name, email)
            final_body = _personalize_body(wrapped + rsvp_text, name, is_html=False)

        ok = send_email(email, subject, final_body, attachments=attachments, html=use_html)
        if ok:
            sent += 1

    ui.success(f"Invites sent: {sent}/{len(attendees)}")

# -------- CLI --------
def send_invites_cli():
    title = input("Event title to invite: ").strip()
    default_tone = "polite, friendly"
    tone = input(f"Tone (default: {default_tone}): ").strip() or default_tone
    html_choice = input("Send as HTML? (Y/n): ").strip().lower()
    use_html = (html_choice != "n")
    edit_choice = input("Preview & edit before sending? (Y/n): ").strip().lower()
    preview_and_edit = (edit_choice != "n")
    send_invites_for_event(title, tone=tone, use_html=use_html, preview_and_edit=preview_and_edit)
