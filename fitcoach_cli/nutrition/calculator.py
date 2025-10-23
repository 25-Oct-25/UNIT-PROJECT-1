# Path: UNIT-PROJECT-1/fitcoach_cli/nutrition/calculator.py
"""Nutrition calculators.

Small helpers to compute BMR (Mifflin–St Jeor), estimate TDEE via activity
factors, and derive macro targets from a daily calorie goal.

Example:
    >>> b = bmr_mifflin_st_jeor("male", 80, 180, 25)
    >>> round(tdee(b, "moderate"))
    2736
    >>> macro_targets("cut", 80, 2400)
    (160, 220, 72)
"""

from typing import Tuple

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

def bmr_mifflin_st_jeor(sex: str, weight_kg: float, height_cm: float, age: int) -> float:
    """Calculate BMR using the Mifflin–St Jeor equation.

    Args:
        sex (str): "male" or "female".
        weight_kg (float): Body weight in kilograms.
        height_cm (float): Height in centimeters.
        age (int): Age in years.

    Returns:
        float: Estimated basal metabolic rate (kcal/day).
    """
    s = 5 if sex.lower() == "male" else -161
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + s

def tdee(bmr: float, activity: str) -> float:
    """Estimate Total Daily Energy Expenditure (TDEE).

    Args:
        bmr (float): Basal metabolic rate (kcal/day).
        activity (str): Activity level key
            ("sedentary", "light", "moderate", "active", "very_active").

    Returns:
        float: Estimated daily calories (kcal/day).
    """
    factor = ACTIVITY_FACTORS.get(activity.lower(), ACTIVITY_FACTORS["moderate"])
    return bmr * factor

def macro_targets(goal: str, weight_kg: float, kcal_target: float) -> Tuple[int, int, int]:
    """Compute daily macro targets from a calorie goal.

    Args:
        goal (str): One of "cut", "bulk", or "recomp".
        weight_kg (float): Body weight in kilograms.
        kcal_target (float): Daily calorie target.

    Returns:
        Tuple[int, int, int]: (protein_g, carbs_g, fat_g).
    """
    if goal.lower() == "cut":
        protein_g = round(weight_kg * 2.0)
        fat_g = round(weight_kg * 0.9)
    elif goal.lower() == "bulk":
        protein_g = round(weight_kg * 1.8)
        fat_g = round(weight_kg * 1.0)
    else:  # recomp
        protein_g = round(weight_kg * 1.9)
        fat_g = round(weight_kg * 0.9)

    kcal_from_protein = protein_g * 4
    kcal_from_fat = fat_g * 9
    carbs_kcal = max(kcal_target - kcal_from_protein - kcal_from_fat, 0)
    carbs_g = round(carbs_kcal / 4)
    return protein_g, carbs_g, fat_g
