# core/brands/remove.py
from pathlib import Path
import shutil
from script.run_scan import read_brands, BRANDS_PATH
from core.brands.verifier import load_brands_db, save_brands_db

class BrandNotFound(Exception): ...

def remove_brand(name: str):
    """
    يحذف البراند من brands.txt و brands_db.json
    يرجّع True عند النجاح، ويرفع BrandNotFound لو الاسم غير موجود.
    """
    name = (name or "").strip()
    p = Path(BRANDS_PATH)
    if not p.exists():
        raise BrandNotFound(f"{name} (brands.txt missing)")

    brands = read_brands(BRANDS_PATH)
    lowered = [b.lower() for b in brands]
    if name.lower() not in lowered:
        raise BrandNotFound(name)

    # backup ثم كتابة الملف بدون الاسم
    shutil.copy2(p, p.with_suffix(".bak"))
    idx = lowered.index(name.lower())
    del brands[idx]
    p.write_text("\n".join(brands) + ("\n" if brands else ""), encoding="utf-8")

    # حذف من قاعدة metadata إن وجد
    db = load_brands_db()
    key = name.lower()
    if key in db:
        del db[key]
        save_brands_db(db)

    return True
