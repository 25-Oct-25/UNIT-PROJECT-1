# modules/ai_email.py
import os
from textwrap import dedent
from dotenv import load_dotenv

# ========== Gemini setup ==========
load_dotenv()
_GEMINI_READY = False
try:
    import google.generativeai as genai
    from google.api_core.exceptions import ResourceExhausted
    _API_KEY = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
    if _API_KEY:
        genai.configure(api_key=_API_KEY)
        _GEMINI_READY = True
except Exception:
    # مكتبة غير متوفرة أو مفتاح غير مضبوط — سنستخدم القوالب المحلية
    _GEMINI_READY = False
# ==================================

# نفضّل موديلات flash (المتاحة غالباً في المجاني)
PREFERRED = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-2.0-flash-lite",
]

def _pick_gemini_model():
    """اختيار موديل مناسب يدعم generateContent، مع تفضيل flash/flash-lite وتجنب pro/exp قدر الإمكان."""
    if not _GEMINI_READY:
        return None
    try:
        models = [m for m in genai.list_models()
                  if "generateContent" in getattr(m, "supported_generation_methods", [])]
        names = [m.name for m in models]
        # فضّل flash/flash-lite
        for pref in PREFERRED:
            for n in names:
                if pref in n:
                    return n
        # تجنّب pro/exp لو نقدر
        for n in names:
            if "pro" not in n and "exp" not in n:
                return n
        return names[0] if names else None
    except Exception:
        return None

# -------- تصنيف نوع الحدث --------
def _detect_kind(subject: str = "", title: str = "") -> str:
    s = f"{subject} {title}".lower()
    if any(k in s for k in ["birthday", "عيد ميلاد", "حفلة"]):
        return "birthday"
    if any(k in s for k in ["eid", "عيد"]):
        return "eid"
    if any(k in s for k in ["graduation", "تخرج"]):
        return "graduation"
    if any(k in s for k in ["meeting", "workshop", "training", "conference", "اجتماع"]):
        return "meeting"
    return "generic"

def _extract_info(bullet_points):
    info = {"title": "", "when": "", "where": "", "desc": ""}
    bullet_points = bullet_points or []
    for b in bullet_points:
        if not b:
            continue
        low = b.lower()
        if low.startswith("event:"):
            info["title"] = b.split(":", 1)[1].strip()
        elif low.startswith("when:"):
            info["when"] = b.split(":", 1)[1].strip()
        elif low.startswith("where:"):
            info["where"] = b.split(":", 1)[1].strip()
        else:
            info["desc"] = (info["desc"] + "\n" + b).strip() if info["desc"] else b.strip()
    return info

def _apply_tone(base: str, tone: str) -> str:
    tone = (tone or "").lower()
    # لمسات بسيطة حسب النغمة
    if any(k in tone for k in ["playful", "fun", "exciting", "cheerful"]):
        return base.replace("Warm regards,", "Can’t wait to celebrate!").replace("Best regards,", "Cheers,")
    if any(k in tone for k in ["polite", "elegant", "professional"]):
        return base.replace("Hey friends,", "Dear guests,").replace("Hi everyone,", "Dear attendees,")
    if any(k in tone for k in ["warm", "heartfelt", "kind", "friendly"]):
        return base.replace("Best regards,", "Warm wishes,")
    return base

# -------- قوالب محلية (Fallback) --------
def _birthday_email(info, signature, rich=True):
    title = info["title"] or "Birthday Celebration"
    body = dedent(f"""
    Dear friends,

    It’s time to celebrate a very special day — {title}!{" 🎂🎉" if rich else ""} 
    Join us for a cozy evening with cake, music, and heartfelt wishes.

    • Event: {title}
    • Date & Time: {info['when'] or '-'}
    • Location: {info['where'] or '-'}

    {("Notes: " + info['desc']) if info['desc'] else ""}

    Dress to feel good, bring your smiles, and let’s make memories together.
    Please RSVP at your convenience.

    Warm wishes,
    {signature}
    """).strip()
    return body

def _eid_email(info, signature, rich=True):
    body = dedent(f"""
    Dear friends,

    Eid Mubarak!{" 🌙✨" if rich else ""} We’re delighted to invite you to celebrate Eid together.
    Expect warm company, sweet treats, and a joyful gathering.

    • Event: {info['title'] or 'Eid Gathering'}
    • Date & Time: {info['when'] or '-'}
    • Location: {info['where'] or '-'}

    {("Notes: " + info['desc']) if info['desc'] else ""}

    Wishing you and your families joy and blessings. We hope to see you there!

    Warm regards,
    {signature}
    """).strip()
    return body

def _graduation_email(info, signature, rich=True):
    body = dedent(f"""
    Dear friends,

    You’re invited to celebrate a proud milestone — {info['title'] or 'Graduation Ceremony'}!{" 🎓" if rich else ""} 
    Join us as we honor hard work, dedication, and the next chapter ahead.

    • Event: {info['title'] or 'Graduation'}
    • Date & Time: {info['when'] or '-'}
    • Location: {info['where'] or '-'}

    {("Highlights: " + info['desc']) if info['desc'] else ""}

    Your presence would mean a lot. Please RSVP at your convenience.

    Best regards,
    {signature}
    """).strip()
    return body

def _meeting_email(info, signature, rich=True):
    body = dedent(f"""
    Dear attendees,

    You’re invited to {info['title'] or 'the meeting'}.
    We’ll share updates, align on next steps, and capture action items.

    • Date & Time: {info['when'] or '-'}
    • Location: {info['where'] or '-'}
    {("• Agenda: " + info['desc']) if info['desc'] else ""}

    Kindly confirm your attendance. Looking forward to a productive session.

    Best regards,
    {signature}
    """).strip()
    return body

def _generic_email(info, signature, rich=True):
    body = dedent(f"""
    Dear guests,

    You’re invited to {info['title'] or 'our event'}.
    We’re gathering to share good moments and great company.

    • Date & Time: {info['when'] or '-'}
    • Location: {info['where'] or '-'}
    {("• Details: " + info['desc']) if info['desc'] else ""}

    We’d love to have you with us. Please RSVP at your convenience.

    Best regards,
    {signature}
    """).strip()
    return body

def _local_fallback(kind: str, info: dict, signature: str, tone: str, rich: bool) -> str:
    if kind == "birthday":
        body = _birthday_email(info, signature, rich=rich)
    elif kind == "eid":
        body = _eid_email(info, signature, rich=rich)
    elif kind == "graduation":
        body = _graduation_email(info, signature, rich=rich)
    elif kind == "meeting":
        body = _meeting_email(info, signature, rich=rich)
    else:
        body = _generic_email(info, signature, rich=rich)
    return _apply_tone(body, tone)

# -------- Gemini drafting --------
def _gemini_draft(subject, audience, tone, info, signature, kind) -> str:
    """صياغة البريد عبر Gemini مع اختيار موديل مناسب وفلاتر للأخطاء الشائعة."""
    if not _GEMINI_READY:
        raise RuntimeError("Gemini not configured")

    model_name = _pick_gemini_model() or "models/gemini-2.0-flash"
    model = genai.GenerativeModel(model_name=model_name)

    guidance = f"""
You are a helpful copywriter. Write an engaging invitation email in English.
Style: {tone}. Keep it warm, natural, and human.
Event kind: {kind}.
Subject (context): {subject}
Audience: {audience}
Details:
- Event: {info.get('title') or '-'}
- Date & Time: {info.get('when') or '-'}
- Location: {info.get('where') or '-'}
- Notes: {info.get('desc') or ''}

Requirements:
- Start with a friendly greeting (e.g., "Dear friends," / "Dear guests,").
- 1–2 short intro sentences that set the mood.
- Clear bullet/line items for date, time, and location (use simple lines with • or clear separators).
- One warm closing line encouraging attendance/RSVP.
- End with the signature: {signature}
- IMPORTANT: Do NOT include the Subject line inside the body.
"""

    try:
        resp = model.generate_content(guidance)
        # حاول قراءة النص بعدة طرق لضمان التوافق
        text = (getattr(resp, "text", None) or "").strip()
        if not text:
            try:
                text = resp.candidates[0].content.parts[0].text.strip()
            except Exception:
                text = ""
        if not text:
            raise RuntimeError("Empty response from Gemini")
        return text
    except ResourceExhausted as e:
        # كوتا/ريت ليمت — رجّع سبب واضح ليستخدم القالب المحلي
        raise RuntimeError(f"Gemini quota/rate limit on {model_name}: {e.message}")
    except Exception as e:
        # أي خطأ آخر — نسمح للطبقة العليا تسوي fallback
        raise RuntimeError(f"Gemini draft error: {e}")

# -------- Public API --------
def draft_email(
    subject: str,
    audience: str,
    tone: str = "polite, friendly",
    bullet_points: list | None = None,
    signature: str = "Organizer",
    language: str = "en",
    event_kind: str | None = None,
    rich: bool = True,
) -> str:
    """
    يُرجع BODY فقط (بدون Subject).
    - إن وجد GEMINI_API_KEY/GOOGLE_API_KEY سيستخدم Gemini لكتابة الإيميل بنبرة احترافية.
    - إن لم يوجد أو فشل الاستدعاء، سيستخدم القوالب المحلية المحسّنة.
    """
    info = _extract_info(bullet_points)
    kind = event_kind or _detect_kind(subject, info.get("title", ""))

    # المطلوب إنجليزي لمشروعك؛ نتجاهل العربية هنا
    if language.lower().startswith("ar"):
        language = "en"

    # جرّب Gemini أولاً لو متاح
    if _GEMINI_READY:
        try:
            return _gemini_draft(subject, audience, tone, info, signature, kind)
        except Exception as e:
            # سقوط لطيف على القالب المحلي
            print(f"⚠️ Gemini draft failed, using local template. Reason: {e}")

    # رجوع للقوالب المحلية
    return _local_fallback(kind, info, signature, tone, rich)
