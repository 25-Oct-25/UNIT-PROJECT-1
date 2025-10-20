# modules/ai_email.py
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
except ImportError:
    genai = None

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or ""
USE_GEMINI = bool(genai and GEMINI_API_KEY not in ("", "dummy", "sk-..."))

if USE_GEMINI:
    genai.configure(api_key=GEMINI_API_KEY)
    _model = genai.GenerativeModel("gemini-1.5-flash")  # سريع وكويس للنصوص القصيرة

def _looks_arabic(text: str) -> bool:
    # كشف بسيط لعربي
    return any("\u0600" <= ch <= "\u06FF" for ch in (text or ""))

def _event_kind(title: str, bullets: List[str]) -> str:
    s = (title or "") + " " + " ".join(bullets or [])
    s = s.lower()
    if any(k in s for k in ["eid", "عيد", "الفطر", "الأضحى"]): return "eid"
    if any(k in s for k in ["birthday", "ميلاد", "حفلة"]):     return "birthday"
    if any(k in s for k in ["graduation", "تخرج"]):              return "graduation"
    if any(k in s for k in ["meeting","workshop","training","conference","اجتماع"]): return "meeting"
    return "generic"

def _fallback_body(kind: str, lang: str, title: str, when: str, where: str, signature: str) -> str:
    if lang == "ar":
        if kind == "eid":
            return (
                "✨ عيدكم مبارك ✨\n\n"
                "أعزّتنا الكرام،\n\n"
                "يسعدنا دعوتكم للاحتفال بالعيد معنا وسط أجواءٍ مبهجة ولمّة حلوة.\n\n"
                f"🎉 الفعالية: {title}\n"
                f"📅 الموعد: {when}\n"
                f"📍 المكان: {where}\n\n"
                "بانتظاركم بكل حماس!\n\n"
                f"تحياتي،\n{signature}"
            )
        if kind == "birthday":
            return (
                "🎂 دعوة لحفلة عيد ميلاد 🎈\n\n"
                "أهلاً وسهلاً!\n"
                "نحب تشاركونا الفرحة ونحتفل سوا بعيد الميلاد.\n\n"
                f"🎉 الفعالية: {title}\n"
                f"📅 الموعد: {when}\n"
                f"📍 المكان: {where}\n\n"
                "نشوفكم على خير 🤍\n\n"
                f"تحياتي،\n{signature}"
            )
        if kind == "meeting":
            return (
                "مرحبًا فريق العمل،\n\n"
                "تذكير باجتماعنا القادم لمناقشة المستجدات وخطة العمل.\n\n"
                f"🗓 التاريخ والوقت: {when}\n"
                f"📍 المكان: {where}\n"
                f"الموضوع: {title}\n\n"
                f"مع الشكر،\n{signature}"
            )
        # generic
        return (
            "مرحبًا،\n\n"
            f"ندعوكم لحضور: {title}\n\n"
            f"📅 الموعد: {when}\n"
            f"📍 المكان: {where}\n\n"
            f"بانتظار حضوركم.\n\n"
            f"تحياتي،\n{signature}"
        )
    else:
        if kind == "eid":
            return (
                "✨ Eid Mubarak! ✨\n\n"
                "Dear friends,\n\n"
                "We’re delighted to invite you to celebrate Eid together.\n\n"
                f"🎉 Event: {title}\n"
                f"📅 Date & Time: {when}\n"
                f"📍 Location: {where}\n\n"
                "Looking forward to seeing you!\n\n"
                f"Warm regards,\n{signature}"
            )
        if kind == "birthday":
            return (
                "🎂 You're Invited to a Birthday Celebration! 🎈\n\n"
                "Hey everyone!\n"
                "Join us for a fun gathering filled with good vibes and smiles.\n\n"
                f"🎉 Event: {title}\n"
                f"📅 Date & Time: {when}\n"
                f"📍 Location: {where}\n\n"
                "See you there!\n\n"
                f"Cheers,\n{signature}"
            )
        if kind == "meeting":
            return (
                "Dear team,\n\n"
                "This is a reminder for our upcoming meeting.\n\n"
                f"🗓 Date & Time: {when}\n"
                f"📍 Location: {where}\n"
                f"Topic: {title}\n\n"
                f"Best regards,\n{signature}"
            )
        # generic
        return (
            "Dear attendees,\n\n"
            f"You’re invited to {title}.\n\n"
            f"📅 Date & Time: {when}\n"
            f"📍 Location: {where}\n\n"
            f"Kind regards,\n{signature}"
        )

def _extract_detail(prefix: str, bullets: List[str]) -> str:
    for b in bullets or []:
        if b.lower().startswith(prefix.lower()+":"):
            return b.split(":",1)[1].strip()
    return ""

def _debug_mode():
    print(f"[AI] google-generativeai={'OK' if genai else 'MISSING'} | USE_GEMINI={USE_GEMINI}")

def draft_email(
    subject: str,
    audience: str,
    tone: str = "polite",
    bullet_points: Optional[List[str]] = None,
    signature: Optional[str] = "Ziyad",
    language: Optional[str] = None,          # "ar" أو "en" (اختياري)
) -> str:
    """
    يُرجع نص الإيميل (BODY فقط، بدون subject).
    يستعمل Gemini لو متاح، وإلا Fallback جميل + عربي/إنجليزي.
    """
    bullet_points = bullet_points or []
    title = _extract_detail("Event", bullet_points) or subject
    when  = _extract_detail("When", bullet_points)
    where = _extract_detail("Where", bullet_points)

    kind = _event_kind(subject, bullet_points)
    lang = language or ("ar" if (_looks_arabic(subject) or _looks_arabic(" ".join(bullet_points))) else "en")

    if USE_GEMINI:
        try:
            # برومبت نظيف يمنع “Subject:” داخل الجسم
            prompt = (
                f"Write a {tone} invitation email BODY only (no subject line, no markdown) "
                f"in {'Arabic' if lang=='ar' else 'English'} for a {kind} event.\n"
                f"Audience: {audience}\n"
                f"Details:\n"
                f"- Title: {title}\n"
                f"- When: {when}\n"
                f"- Where: {where}\n"
                "Requirements:\n"
                "- Sound natural and warm.\n"
                "- Keep it concise (80–160 words).\n"
                "- If it's Eid, include 'Eid Mubarak' (or 'عيدكم مبارك' in Arabic).\n"
                "- Return ONLY the email body text.\n"
                f"Sign off as {signature}."
            )
            resp = _model.generate_content(prompt)
            body = (resp.text or "").strip()
            if body:
                # حماية إضافية: امسح أي سطر يبدأ بـ Subject:
                if body.lower().startswith("subject:"):
                    body = "\n".join(line for line in body.splitlines() if not line.lower().startswith("subject:")).strip()
                return body
        except Exception as e:
            print(f"[AI] Gemini error: {e}")

    # Fallback محترم
    return _fallback_body(kind, lang, title, when, where, signature)
