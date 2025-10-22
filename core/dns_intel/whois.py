# core/dns_intel/whois.py
from typing import Dict, Any, Optional
import datetime as dt

def _to_date(x) -> Optional[str]:
    try:
        if isinstance(x, list) and x:
            x = x[0]
        if hasattr(x, 'isoformat'):
            return x.isoformat()
        return str(x)
    except Exception:
        return None

def fetch_whois_info(domain: str) -> Dict[str, Any]:
    try:
        import whois  # python-whois
        w = whois.whois(domain)
        created = _to_date(w.creation_date)
        org = (w.org or w.owner or w.registrant_organization or w.registrant_name or None)
        registrar = w.registrar or None
        return {
            "created": created,
            "org": org or "Private",
            "registrar": registrar or "-"
        }
    except Exception as e:
        return {"error": str(e)}
