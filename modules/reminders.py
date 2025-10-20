# modules/reminders.py
import time, threading, os
from datetime import datetime, timedelta
from modules.events import load_events, save_events
from modules.email_sender import send_email
from modules.ai_email import draft_email   # نستخدمه كـ (خياري) لصياغة ألطف
from pathlib import Path

CHECK_INTERVAL_SECONDS = 60  # افحص كل 60 ثانية
ICS_DIR = Path("data/ics")
ICS_DIR.mkdir(parents=True, exist_ok=True)

def _ensure_reminder_objects(ev):
    """
    يدعم شكلين لقائمة reminders:
    - [10, 60] أرقام فقط (قديم)
    - [{"minutes_before": 10, "fired": false}, ...] (جديد)
    ويحوّل الأرقام إلى كائنات مع fired=False.
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
    ينشئ ملف .ics للحدث ويرجع المسار.
    الحدث مخزن كوقت محلي (naive). بنسجله كتاريخ محلي.
    """
    # توقّع تنسيق: YYYY-MM-DD HH:MM
    start = datetime.strptime(event['date'], "%Y-%m-%d %H:%M")
    # لنفترض مدة افتراضية ساعة إذا ما عندنا مدة
    end = start + timedelta(hours=1)

    def fmt(dt: datetime) -> str:
        # صيغة ICS: YYYYMMDDTHHMMSS
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
    قالب HTML أنيق للتذكير. إن توفر Gemini، نستخدمه لتوليد فقرة مقدمة ألطف.
    """
    title = event["title"]
    when = event["date"]
    where = event.get("location", "")
    desc  = event.get("description", "")
    friendly = _friendly_delta(minutes_before)

    # مقدمة محسّنة عبر Gemini (اختياري) – وإلا fallback بسيط
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
        # language يحدد تلقائيًا حسب اللغة المكتوبة
    ) or f"This is a quick reminder for <strong>{title}</strong> happening {friendly}."

    # نحذف أي "Subject:" لو ظهرت من الموديل بالخطأ
    if intro.lower().startswith("subject:"):
        intro = "\n".join([ln for ln in intro.splitlines() if not ln.lower().startswith("subject:")]).strip()

    # حوّل الأسطر لـ <br>
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
        <a href="#" style="display:inline-block;background:#2563eb;color:#fff;text-decoration:none;padding:10px 14px;border-radius:8px">View Details</a>
        <span style="color:#6b7280;margin-left:8px">Add to calendar via attached .ics</span>
      </div>
      <hr style="border:none;border-top:1px solid #e5e7eb;margin:16px 0">
      <div style="font-size:12px;color:#6b7280">Sent by Smart Event Manager</div>
    </div>
    """

def check_reminders_once():
    events = load_events()
    now = datetime.now()
    changed = False

    for ev in events:
        _ensure_reminder_objects(ev)

        # وقت الحدث
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

            if 0 <= delta <= CHECK_INTERVAL_SECONDS:
                # جهّز رسالة التذكير
                subject = _build_reminder_subject(ev, minutes_before)
                body_html = _build_reminder_body_html(ev, minutes_before)

                # مرفق ICS
                ics_path = _make_ics(ev)
                attachments = [ics_path] if os.path.exists(ics_path) else None

                # إرسال لكل الحضور
                attendees = ev.get('attendees', [])
                sent_to = 0
                for person in attendees:
                    email = (person or {}).get('email')
                    if email:
                        if send_email(email, subject, body_html, attachments=attachments, html=True):
                            sent_to += 1

                print(f"[Reminder] {ev['title']} — {minutes_before} minutes before (sent to {sent_to} attendees)")
                r['fired'] = True
                changed = True

    if changed:
        save_events(events)

def _loop():
    while True:
        check_reminders_once()
        time.sleep(CHECK_INTERVAL_SECONDS)

def start_reminder_loop():
    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    print("Reminder background thread started (checks every 60s).")
