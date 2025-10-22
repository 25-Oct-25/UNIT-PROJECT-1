# core/brands/verifier.py
from __future__ import annotations
import os, json, re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import requests

# مفاتيح من البيئة (اختيارية)
OPENCORP_API_KEY   = os.getenv("OPENCORP_API_KEY")
BRANDFETCH_API_KEY = os.getenv("BRANDFETCH_API_KEY")

BRANDS_DB = Path("data/brands_db.json")  # نخزن فيه تفاصيل البراندات المتحققة

@dataclass
class BrandHit:
    name: str
    canonical_name: str
    website: Optional[str]
    confidence: float
    source: str
    meta: Dict[str, Any]

class BrandVerifier:
    """
    يحاول التحقق من اسم البراند عبر عدة مزودات:
    1) Wikidata (مجاني)  2) OpenCorporates (مفتاح اختياري)  3) Brandfetch (مفتاح اختياري)
    يدمج النتائج ويقرّر.
    """
    def __init__(self, session: Optional[requests.Session] = None):
        self.s = session or requests.Session()
        self.s.headers.update({"User-Agent": "PhishSentry/verify"})

    # ---- مزود 1: Wikidata (مجاني) ----
    def _wd_search(self, query: str) -> Optional[BrandHit]:
        try:
            # بحث
            r = self.s.get("https://www.wikidata.org/w/api.php", params={
                "action":"wbsearchentities", "search":query, "language":"en",
                "format":"json", "type":"item", "limit": 1
            }, timeout=8)
            r.raise_for_status()
            data = r.json()
            if not data.get("search"):
                return None
            item = data["search"][0]
            qid = item["id"]
            # جلب خصائص
            r2 = self.s.get("https://www.wikidata.org/w/api.php", params={
                "action":"wbgetentities", "ids":qid, "format":"json", "props":"labels|aliases|claims|sitelinks"
            }, timeout=8)
            r2.raise_for_status()
            ent = r2.json()["entities"][qid]
            label = ent.get("labels", {}).get("en", {}).get("value") or item.get("label") or query
            aliases = [a["value"] for a in ent.get("aliases", {}).get("en", [])]
            # موقع رسمي P856 إن وجد
            website = None
            claims = ent.get("claims", {})
            if "P856" in claims and claims["P856"]:
                website = claims["P856"][0]["mainsnak"]["datavalue"]["value"]
            # هل الكيان شركة/علامة؟ (تقريب: نبحث عن وجود sitelinks وموقع)
            has_sitelinks = bool(ent.get("sitelinks"))
            conf = 0.70
            if website: conf += 0.10
            if aliases and any(a.lower() == query.lower() for a in aliases): conf += 0.05
            conf = min(conf, 0.90)
            return BrandHit(
                name=query,
                canonical_name=label,
                website=website,
                confidence=conf,
                source="wikidata",
                meta={"qid": qid, "aliases_en": aliases}
            )
        except Exception:
            return None

    # ---- مزود 2: OpenCorporates (اختياري) ----
    def _opencorp(self, query: str) -> Optional[BrandHit]:
        if not OPENCORP_API_KEY:
            return None
        try:
            r = self.s.get("https://api.opencorporates.com/v0.4/companies/search", params={
                "q": query,
                "api_token": OPENCORP_API_KEY,
                "per_page": 1
            }, timeout=8)
            r.raise_for_status()
            js = r.json()
            arr = (js.get("results") or {}).get("companies") or []
            if not arr:
                return None
            comp = arr[0].get("company", {})
            name = comp.get("name") or query
            # موقع إن توفر
            website = comp.get("website") or comp.get("registered_address_in_full")
            conf = 0.75
            if name.lower() == query.lower(): conf += 0.10
            return BrandHit(
                name=query,
                canonical_name=name,
                website=website,
                confidence=min(conf, 0.92),
                source="opencorporates",
                meta={"jurisdiction": comp.get("jurisdiction_code"), "company_number": comp.get("company_number")}
            )
        except Exception:
            return None

    # ---- مزود 3: Brandfetch (اختياري) ----
    def _brandfetch(self, query: str) -> Optional[BrandHit]:
        if not BRANDFETCH_API_KEY:
            return None
        # نحاول استنتاج دومين من الاسم (بسيط). إن كان للمستخدم دومين رسمي من Wikidata نفضّل استخدامه.
        guess_domain = self._guess_domain(query)
        try:
            headers = {"Authorization": f"Bearer {BRANDFETCH_API_KEY}"}
            # ملاحظة: قد تختلف نقطة النهاية حسب الخطة—عدّلها لوثائقك
            r = self.s.get(f"https://api.brandfetch.io/v2/brands/{guess_domain}", headers=headers, timeout=8)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            js = r.json()
            name = (js.get("name") or query).strip()
            website = js.get("domain") or js.get("website")
            conf = 0.80
            if website and guess_domain in (website or ""):
                conf += 0.05
            return BrandHit(
                name=query,
                canonical_name=name,
                website=website,
                confidence=min(conf, 0.95),
                source="brandfetch",
                meta={"raw": js}
            )
        except Exception:
            return None

    @staticmethod
    def _guess_domain(name: str) -> str:
        # تخمين دومين بسيط من الاسم (للاستخدام مع براندفيتش)
        n = re.sub(r"[^A-Za-z0-9]+", "", name).lower()
        # استثناءات بسيطة
        if n in ("stc","mystc"): return "stc.com.sa"
        if n in ("alrajhibank","alrajhi","rajhibank"): return "alrajhibank.com.sa"
        return f"{n}.com"

    def verify(self, brand: str) -> Optional[BrandHit]:
        brand = brand.strip()
        # Wikidata أولاً (مجاني)
        best = self._wd_search(brand)

        # OpenCorporates إن متاح
        oc = self._opencorp(brand)
        if oc and (not best or oc.confidence > best.confidence):
            best = oc

        # Brandfetch إن متاح
        bf = self._brandfetch(best.website if (best and best.website) else brand)
        if bf and (not best or bf.confidence > best.confidence):
            best = bf

        return best

def load_brands_db() -> Dict[str, Any]:
    if BRANDS_DB.exists():
        try:
            return json.loads(BRANDS_DB.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_brands_db(db: Dict[str, Any]) -> None:
    BRANDS_DB.parent.mkdir(parents=True, exist_ok=True)
    BRANDS_DB.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

def add_verified_brand(name: str, hit: BrandHit) -> None:
    db = load_brands_db()
    key = name.strip().lower()
    db[key] = {
        "input": name,
        "canonical_name": hit.canonical_name,
        "website": hit.website,
        "confidence": hit.confidence,
        "source": hit.source,
        "meta": hit.meta,
    }
    save_brands_db(db)
