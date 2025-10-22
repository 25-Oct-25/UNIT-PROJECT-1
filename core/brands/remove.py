from pathlib import Path
import shutil
from script.run_scan import read_brands, BRANDS_PATH
from core.brands.verifier import load_brands_db, save_brands_db

class BrandNotFound(Exception): ...

def remove_brand(name: str):
    name = (name or "").strip()
    p = Path(BRANDS_PATH)
    if not p.exists():
        raise BrandNotFound(f"{name} (brands.txt missing)")

    brands = read_brands(BRANDS_PATH)
    lowered = [b.lower() for b in brands]
    if name.lower() not in lowered:
        raise BrandNotFound(name)

    shutil.copy2(p, p.with_suffix(".bak"))
    idx = lowered.index(name.lower())
    del brands[idx]
    p.write_text("\n".join(brands) + ("\n" if brands else ""), encoding="utf-8")

    db = load_brands_db()
    key = name.lower()
    if key in db:
        del db[key]
        save_brands_db(db)

    return True
