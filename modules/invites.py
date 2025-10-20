# modules/invites.py
import os
from modules.events import load_events
from modules.email_sender import send_email
from modules.ai_email import draft_email

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
    if kind == "eid":       return f"Eid Mubarak! You're invited: {title}"
    if kind == "birthday":  return f"🎂 You're invited: {title}"
    if kind == "graduation":return f"🎓 You're invited: {title}"
    return f"You're invited: {title}"

def _poster_path(event):
    filename = event['title'].replace(' ', '_') + ".png"
    path = os.path.join("data", "posters", filename)
    return path if os.path.exists(path) else None

def send_invites_for_event(event_title: str, tone: str = "polite, friendly", use_html: bool = True):
    events = load_events()
    ev = next((e for e in events if e['title'].lower()==event_title.lower()), None)
    if not ev:
        print("Event not found."); return
    attendees = ev.get('attendees', [])
    if not attendees:
        print("No attendees to invite."); return

    subject = _subject_for(ev)

    # Gemini يصيغ البودي (BODY فقط)
    body_text = draft_email(
        subject=subject,
        audience="attendees",
        tone=tone,
        bullet_points=[
            f"Event: {ev['title']}",
            f"When: {ev['date']}",
            f"Where: {ev.get('location','')}",
            ev.get('description',''),
        ],
        # language=None  # اتركها تلقائي أو مرر 'ar'/'en'
        signature="Ziyad",
    )

    if use_html:
        body = f"""
        <div style="font-family:Segoe UI,Arial,sans-serif;line-height:1.7;color:#111827">
          <div style="font-size:18px; margin-bottom:8px;">{body_text.replace('\n','<br>')}</div>
          <hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0">
          <div style="font-size:12px;color:#6b7280">Sent by Smart Event Manager</div>
        </div>
        """
        is_html = True
    else:
        body = body_text
        is_html = False

    attach = _poster_path(ev)
    attachments = [attach] if attach else None

    sent = 0
    for a in attendees:
        email = (a or {}).get('email')
        if not email: continue
        if send_email(email, subject, body, attachments=attachments, html=is_html):
            sent += 1
    print(f"Invites sent: {sent}/{len(attendees)}")

def send_invites_cli():
    title = input("Event title to invite: ").strip()
    send_invites_for_event(title, use_html=True)
