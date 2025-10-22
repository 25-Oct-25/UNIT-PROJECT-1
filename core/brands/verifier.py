from __future__ import annotations
import os, json, re
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
import requests

OPENCORP_API_KEY   = os.getenv("OPENCORP_API_KEY")
BRANDFETCH_API_KEY = os.getenv("BRANDFETCH_API_KEY")

BRANDS_DB = Path("data/brands_db.json")  

@dataclass
class BrandHit:
    name: str
    canonical_name: str
    website: Optional[str]
    confidence: float
    source: str
    meta: Dict[str, Any]

class BrandVerifier:
    
    def __init__(self, session: Optional[requests.Session] = None):
        self.s = session or requests.Session()
        self.s.headers.update({"User-Agent": "PhishSentry/verify"})

    # ---- مزود 1: Wikidata (مجاني) ----
    def _wd_search(self, query: str) -> Optional[BrandHit]:
        try:
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

    def verify(self, brand: str) -> Optional[BrandHit]:
        brand = brand.strip()
        best = self._wd_search(brand)
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
