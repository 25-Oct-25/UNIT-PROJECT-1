# core/brands/actions.py
from pathlib import Path
from script.run_scan import read_brands, BRANDS_PATH   # نفس مصدر المسار
from core.brands.verifier import BrandVerifier, add_verified_brand

class BrandAddError(Exception): ...
class BrandExists(Exception): ...

def add_brand_verified(name: str):
    """
    يتحقق من البراند عبر BrandVerifier ثم يضيفه للـ brands.txt
    يرجّع كائن hit (فيه canonical_name, website, confidence, source).
    يرفع استثناء إذا فشل التحقق أو كان موجود مسبقًا.
    """
    name = (name or "").strip()
    if not name:
        raise BrandAddError("Empty brand name")

    existing = read_brands(BRANDS_PATH)
    if any(b.lower() == name.lower() for b in existing):
        raise BrandExists(name)

    v = BrandVerifier()
    hit = v.verify(name)
    if not hit or hit.confidence < 0.75:
        raise BrandAddError(f"Cannot verify '{name}' with high confidence")

    # append to brands.txt
    Path(BRANDS_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(BRANDS_PATH, "a", encoding="utf-8") as f:
        f.write(name + "\n")

    # store metadata (brands_db.json) عبر helper موجود في verifier.py
    add_verified_brand(name, hit)
    return hit
