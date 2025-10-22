# core/dns_intel/ip_enrichment.py
from typing import Dict, Any, List, Optional, Tuple
import time
import requests
import dns.resolver
import dns.reversename

from .config import IPINFO_TOKEN, ABUSEIPDB_KEY, VT_APIKEY

# DNS resolver (PTR)
resolver = dns.resolver.Resolver()
resolver.lifetime = 5
resolver.timeout = 3

# ---------- Helpers ----------

def _ok(data: Any) -> Dict[str, Any]:
    return {"ok": True, "data": data}

def _notice(msg: str) -> Dict[str, Any]:
    return {"ok": False, "notice": msg}

def _err(msg: str, status: Optional[int] = None, retry_after: Optional[str] = None, body: Optional[Any] = None) -> Dict[str, Any]:
    out = {"ok": False, "error": msg}
    if status is not None:
        out["status"] = status
    if retry_after is not None:
        out["retry_after"] = retry_after
    if body is not None:
        out["body"] = body
    return out

def _get_json(url: str, headers: Dict[str, str], params: Dict[str, Any] = None, timeout: float = 10.0) -> Dict[str, Any]:
    """HTTP GET with robust error handling; returns {'ok':..., 'data'/notice/error/...}"""
    try:
        r = requests.get(url, headers=headers, params=params or {}, timeout=timeout)
    except requests.exceptions.Timeout:
        return _err("timeout", body=None)
    except requests.exceptions.RequestException as e:
        return _err(f"request_error: {e}")
    # Handle HTTP status
    retry_after = r.headers.get("Retry-After")
    if r.status_code == 429:
        return _err("rate_limited", status=429, retry_after=retry_after, body=r.text)
    if 500 <= r.status_code < 600:
        return _err("server_error", status=r.status_code, body=r.text)
    if r.status_code >= 400:
        # include a small slice of body
        body = r.text[:400] if r.text else None
        return _err("http_error", status=r.status_code, body=body)
    # Parse JSON
    try:
        return _ok(r.json())
    except ValueError:
        return _err("invalid_json", body=r.text[:400] if r.text else None)

# ---------- Enrichment primitives ----------

def reverse_dns(ip: str) -> Optional[str]:
    try:
        rev = dns.reversename.from_address(ip)
        answers = resolver.resolve(rev, "PTR", raise_on_no_answer=False)
        if answers.rrset is None or len(answers) == 0:
            return None
        return answers[0].to_text().rstrip(".")
    except Exception:
        return None

def ipinfo_lookup(ip: str) -> Dict[str, Any]:
    if not IPINFO_TOKEN:
        return {"notice": "no_ipinfo_token"}
    url = f"https://ipinfo.io/{ip}/json"
    headers = {"Authorization": f"Bearer {IPINFO_TOKEN}"}
    res = _get_json(url, headers, timeout=8)
    # normalize: if ok -> return payload; else keep notice/error structure
    return res["data"] if res.get("ok") else {k: v for k, v in res.items() if k != "ok"}

def abuseipdb_check(ip: str) -> Dict[str, Any]:
    if not ABUSEIPDB_KEY:
        return {"notice": "no_abuseipdb_key"}
    url = "https://api.abuseipdb.com/api/v2/check"
    params = {"ipAddress": ip, "maxAgeInDays": 90}
    headers = {"Accept": "application/json", "Key": ABUSEIPDB_KEY}
    res = _get_json(url, headers, params=params, timeout=10)
    return res["data"] if res.get("ok") else {k: v for k, v in res.items() if k != "ok"}

def virustotal_ip_check(ip: str) -> Dict[str, Any]:
    if not VT_APIKEY:
        return {"notice": "no_vt_key"}
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": VT_APIKEY}
    res = _get_json(url, headers, timeout=12)
    return res["data"] if res.get("ok") else {k: v for k, v in res.items() if k != "ok"}

# ---------- Batch orchestrator ----------

def enrich_ips(ips: List[str], sleep_between: float = 0.4) -> Dict[str, Any]:
    """
    Enrich each IP with:
      - ptr (reverse DNS)
      - ipinfo (if token present) -> dict or {'notice':...}/{ 'error':..., 'status':... }
      - abuse (if key present)    -> same shape
      - vt (if key present)       -> same shape
    Returns: { ip: { 'ptr': str|None, 'ipinfo': {...}, 'abuse': {...}, 'vt': {...} } }
    """
    out: Dict[str, Any] = {}
    for ip in ips:
        bundle: Dict[str, Any] = {}
        bundle["ptr"] = reverse_dns(ip)

        # Optional external APIs (only if keys exist)
        ipinfo_res = ipinfo_lookup(ip)
        if ipinfo_res:
            bundle["ipinfo"] = ipinfo_res

        abuse_res = abuseipdb_check(ip)
        if abuse_res:
            bundle["abuse"] = abuse_res

        vt_res = virustotal_ip_check(ip)
        if vt_res:
            bundle["vt"] = vt_res

        out[ip] = bundle
        time.sleep(sleep_between)
    return out
