from typing import List, Dict
from ..recipes.builder import build_day

TAG_TO_ITEMS = {
    "chicken": ["دجاج صدور", "بهارات", "زيت زيتون"],
    "rice": ["أرز بسمتي"],
    "oats": ["شوفان", "حليب قليل الدسم"],
    "yogurt": ["زبادي يوناني"],
    "tuna": ["تونة علب", "مكرونة"],
    "beef": ["لحم مفروم قليل الدهن", "تورتيلا"],
    "snack": ["مكسرات", "فاكهة"],
    "pasta": ["مكرونة قمح صلب"],
    "meal": ["خضار مشكلة"],
    "wrap": ["تورتيلا قمح"],
    "breakfast": ["عسل", "فاكهة"],
}

def grocery_from_recipes(recipes: List[Dict]) -> Dict[str, int]:
    items: Dict[str,int] = {}
    for r in recipes:
        for t in r.get("tags", []):
            for it in TAG_TO_ITEMS.get(t, []):
                items[it] = items.get(it, 0) + 1
    return items

def build_grocery_list(target_kcal:int, P:int, C:int, F:int, filters:List[str]|None=None):
    picks, totals = build_day(target_kcal, P, C, F, filters)
    groceries = grocery_from_recipes(picks)
    return picks, totals, groceries
