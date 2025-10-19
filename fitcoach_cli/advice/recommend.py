from typing import List
from ..core.models import UserProfile

def daily_tips(profile: UserProfile) -> List[str]:
    tips = [
        "اشرب 30–40 مل ماء لكل كجم من وزنك يوميًا.",
        "نم 7–9 ساعات — النوم يرفع التعافي وحساسية الإنسولين.",
        "وزّع البروتين على 3–5 وجبات (0.4–0.6 g/kg).",
        "ابدأ التمرين بحركات مركبة، ثم اعزل العضلات الضعيفة.",
        "ارفع الأحمال تدريجيًا مع هامش 2–3 تكرارات.",
    ]
    if profile.goal.lower() == "cut":
        tips.append("عجز 300–500 سعرة، وأكثر خضار وألياف لتقليل الجوع.")
    elif profile.goal.lower() == "bulk":
        tips.append("فائض 200–300 سعرة يكفي لبناء عضل مع تقليل الدهون.")
    else:
        tips.append("ثبّت السعرات قريبًا من TDEE وركّز على القوة.")
    return tips
