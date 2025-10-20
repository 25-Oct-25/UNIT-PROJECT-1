"""Progress analysis helpers.

Provides a small helper to estimate average weekly weight change and
return a brief calorie-adjustment suggestion.

Example:
    >>> from progress.adjuster import analyze_weights
    >>> analyze_weights([80.0, 79.8, 79.5, 79.2])
    (-0.8, 'Weight dropping fast. Consider +250–350 kcal.')
"""

from typing import List, Tuple

def analyze_weights(weights: List[float]) -> Tuple[float, str]:
    """Analyze a chronological list of body weights.

    Assumes roughly daily entries; weeks are estimated as ``(n - 1) / 7``.

    Args:
        weights (List[float]): Weights in kilograms, oldest → newest.

    Returns:
        Tuple[float, str]: ``(kg_per_week, suggestion)`` where the first value
        is the average weekly change (negative = losing, positive = gaining).

    """
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
