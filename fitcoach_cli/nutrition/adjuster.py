from typing import List, Tuple

def analyze_weights(weights: List[float]) -> Tuple[float, str]:
    """Return (avg_delta_per_week_kg, suggestion)."""
    if len(weights) < 2:
        return 0.0, "Need more data to analyze progress."
    delta = weights[-1] - weights[0]
    weeks = max((len(weights) - 1) / 7.0, 0.001)
    rate = delta / weeks  # kg/week
    if rate < -0.7:
        sug = "Weight dropping fast. Consider +250–350 kcal."
    elif rate < -0.3:
        sug = "Good cutting pace (~0.3–0.7 kg/week)."
    elif -0.1 <= rate <= 0.1:
        sug = "Stable weight. Adjust ±150–250 kcal."
    elif rate > 0.6:
        sug = "Gaining fast. Consider −200–300 kcal."
    else:
        sug = "Lean bulk pace (~0.2–0.5 kg/week)."
    return rate, sug
