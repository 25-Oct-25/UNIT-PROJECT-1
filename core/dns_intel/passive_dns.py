# core/dns_intel/passive_dns.py
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from .config import HISTORY_FILE

def _load_hist(path: Path) -> Dict[str, Any]:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}

def passive_dns_lookup(domain: str) -> Dict[str, Any]:
    """
    يحسب عدد الدومينات الأخرى في التاريخ تشترك مع هذا الدومين في أي IP.
    يعتمد على آخر snapshot حفظته أدواتك.
    """
    hist = _load_hist(HISTORY_FILE)
    # نحتاج IPs الحالية من آخر نتيجة محفوظة في results/level4 أو level1؟ نستخدم history آخر مرة
    cur = hist.get(domain, {})
    ips = cur.get("last_ips") or []
    if not ips:
        return {"siblings": 0}

    siblings = set()
    for d, info in hist.items():
        if d == domain:
            continue
        other_ips = set(info.get("last_ips") or [])
        if other_ips & set(ips):
            siblings.add(d)
    return {"siblings": len(siblings)}
