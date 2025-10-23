# Path: fitcoach_cli/habits/nudges.py
# Description: Lightweight nudges for common habits (water, sleep, steps, protein).

def nudge(kind: str) -> str:
    """Return a short habit nudge message.

    Args:
        kind (str): One of "water", "sleep", "steps", "protein".

    Returns:
        str: Nudge message (default encouragement if kind is unknown).
    """
    msgs = {
        "water": "ذكّر نفسك بكوب ماء الآن — 250 مل.",
        "sleep": "اضبط منبّه الاستعداد للنوم قبل 45 دقيقة.",
        "steps": "خذ لفة 10 دقائق—هتضيف ~1000 خطوة.",
        "protein": "أضف مصدر بروتين لكل وجبة—زبادي/بيض/دجاج/تونة.",
    }
    return msgs.get(kind, "Keep going! أنت على الطريق الصحيح.")
