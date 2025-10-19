from ..core.models import AppState

def log_habits(state: AppState, water_l: float, sleep_h: float, steps: int):
    state.habits_log.append({
        "date": __import__("datetime").date.today().isoformat(),
        "water": water_l, "sleep": sleep_h, "steps": steps
    })

def score_today(state: AppState) -> str:
    if not state.habits_log:
        return "No habits logged yet."
    d = state.habits_log[-1]
    score = 0
    score += 1 if d["water"] >= 3 else 0
    score += 1 if 7 <= d["sleep"] <= 9 else 0
    score += 1 if d["steps"] >= 8000 else 0
    tips = []
    if d["water"] < 3: tips.append("زِد الماء إلى 3 لتر.")
    if not (7 <= d["sleep"] <= 9): tips.append("نظّم نومك بين 7–9 ساعات.")
    if d["steps"] < 8000: tips.append("ارفع خطواتك لـ 8K يوميًا.")
    return f"Habits score: {score}/3. " + (" | ".join(tips) if tips else "Excellent day!")
