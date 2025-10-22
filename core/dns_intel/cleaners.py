# core/dns_intel/cleaners.py
from typing import Any, Dict

def _pick(d: Dict[str, Any], keys):
    return {k: d[k] for k in keys if k in d and d[k] not in (None, "", [], {})}

def prune_result(full: Dict[str, Any]) -> Dict[str, Any]:
    """
    ينظّف نتيجة الدومين بإزالة الحقول الفارغة/التكرار والاحتفاظ بالمفيد فقط
    داخل ip_enrichment لكل IP.
    """
    res = dict(full)  # shallow copy
    enr = res.get("ip_enrichment") or {}
    new_enr: Dict[str, Any] = {}

    for ip, bundle in enr.items():
        if not isinstance(bundle, dict):
            continue
        nb: Dict[str, Any] = {}

        # PTR
        ptr = bundle.get("ptr")
        if isinstance(ptr, str) and ptr:
            nb["ptr"] = ptr

        # IPinfo (نحتفظ بالمفيد فقط)
        ipinfo = bundle.get("ipinfo")
        if isinstance(ipinfo, dict) and not any(k in ipinfo for k in ("notice", "error")):
            keep = _pick(ipinfo, ("org", "country", "asn", "asn_org"))
            if keep:
                nb["ipinfo"] = keep

        # AbuseIPDB (نحتفظ بالمفيد فقط)
        abuse = bundle.get("abuse")
        if isinstance(abuse, dict) and not any(k in abuse for k in ("notice", "error")):
            data = abuse.get("data", abuse)
            if isinstance(data, dict):
                keep = _pick(
                    data,
                    (
                        "abuseConfidenceScore", "totalReports", "isWhitelisted",
                        "isp", "usageType", "countryCode", "domain",
                        "hostnames", "lastReportedAt"
                    ),
                )
                if keep:
                    nb["abuse"] = keep

        # VirusTotal (نحتفظ بالستات فقط + سمعة إن وجدت)
        vt = bundle.get("vt")
        if isinstance(vt, dict) and not any(k in vt for k in ("notice", "error")):
            data = vt.get("data", vt)
            attrs = data.get("attributes", {}) if isinstance(data, dict) else {}
            if isinstance(attrs, dict):
                keep: Dict[str, Any] = {}
                stats = attrs.get("last_analysis_stats")
                if isinstance(stats, dict) and stats:
                    keep["last_analysis_stats"] = stats
                if "reputation" in attrs and attrs["reputation"] is not None:
                    keep["reputation"] = attrs["reputation"]
                if keep:
                    nb["vt"] = keep

        new_enr[ip] = nb

    res["ip_enrichment"] = new_enr
    return res
