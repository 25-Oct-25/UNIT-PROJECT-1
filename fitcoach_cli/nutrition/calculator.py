from typing import Tuple

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

def bmr_mifflin_st_jeor(sex: str, weight_kg: float, height_cm: float, age: int) -> float:
    s = 5 if sex.lower() == "male" else -161
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + s

def tdee(bmr: float, activity: str) -> float:
    factor = ACTIVITY_FACTORS.get(activity.lower(), ACTIVITY_FACTORS["moderate"])
    return bmr * factor

def macro_targets(goal: str, weight_kg: float, kcal_target: float) -> Tuple[int, int, int]:
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
