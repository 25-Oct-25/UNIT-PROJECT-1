from typing import Dict, Any, Tuple, Optional

TRUSTED_HINTS = [
    "akamai", "akamaitechnologies", "cloudflare", "google", "google llc", "1e100",
    "amazon", "aws", "amazon.com", "amazon technologies", "microsoft", "azure",
    "fastly", "edgekey", "vercel", "github", "netlify", "heroku", "digitalocean",
    "oracle cloud", "ovh", "linode", "iana", "icann"
]

def _as_dict(x) -> Dict[str, Any]:
    return x if isinstance(x, dict) else {}

def _lower(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def _is_trusted_host(bundle: Dict[str, Any]) -> bool:
    b = _as_dict(bundle)
    ipinfo = _as_dict(b.get("ipinfo"))
    org = _lower(ipinfo.get("org")) if isinstance(ipinfo, dict) else ""
    ptr = _lower(b.get("ptr"))
    # check org + ptr against trusted hints
    return any(h in org for h in TRUSTED_HINTS) or any(h in ptr for h in TRUSTED_HINTS)

# ---- VirusTotal parsing ----
def _vt_positives_from_bundle(bundle: Dict[str, Any]) -> int:
    
    b = _as_dict(bundle)
    vt = _as_dict(b.get("vt"))
    # if vt contains notice/error, ignore
    if "notice" in vt or "error" in vt or not vt:
        return 0
    # vt may be the 'data' object directly (as in our enrichment)
    data = _as_dict(vt.get("data")) if isinstance(vt.get("data"), dict) else _as_dict(vt)
    attributes = _as_dict(data.get("attributes"))
    stats = _as_dict(attributes.get("last_analysis_stats"))
    if not stats:
        return 0
    # positives = sum of all categories except harmless/undetected/timeout
    positives = 0
    for k, v in stats.items():
        if k in ("harmless", "undetected", "timeout"):
            continue
        try:
            positives += int(v or 0)
        except Exception:
            continue
    return positives

# ---- AbuseIPDB parsing ----
def _abuse_score_from_bundle(bundle: Dict[str, Any]) -> int:
    b = _as_dict(bundle)
    abuse = _as_dict(b.get("abuse"))
    if not abuse:
        return 0
    # abuse may be returned as {'notice':...} or {'error':...}
    if "notice" in abuse or "error" in abuse:
        return 0
    # If API returned full object under 'data' (typical), use it
    data = _as_dict(abuse.get("data")) if isinstance(abuse.get("data"), dict) else _as_dict(abuse)
    try:
        is_whitelisted = bool(data.get("isWhitelisted"))
    except Exception:
        is_whitelisted = False
    if is_whitelisted:
        return 0
    acs = int(data.get("abuseConfidenceScore") or 0)
    total_reports = int(data.get("totalReports") or 0)
    score = 0
    # weight by confidence first
    if acs >= 50:
        score += 20
    elif acs >= 20:
        score += 12
    elif acs >= 1:
        score += 6
    # add by total reports (guard against duplicates)
    if total_reports >= 50:
        score += 20
    elif total_reports >= 10:
        score += 12
    elif total_reports >= 1:
        score += 6
    # cap contribution per IP to reasonable bound (e.g., 30)
    return min(30, score)

# ---- Main scorer ----
def compute_dns_risk(domain_result: Dict[str, Any]) -> Tuple[int, Dict[str, int], str]:
    score = 0
    details: Dict[str, int] = {}
    src = domain_result.get("dns") or domain_result

    recs   = _as_dict(src.get("records"))
    flags  = _as_dict(src.get("security_flags"))
    ips    = src.get("ips", []) or []
   
    enrich = _as_dict(domain_result.get("ip_enrichment") or src.get("ip_enrichment"))
    fastflux = bool(domain_result.get("fast_flux"))

    # 1) Threat intel from enrichment (VT + Abuse)
    for ip in ips:
        b = _as_dict(enrich.get(ip, {}))
        # ignore ip bundles that are only 'notice' or 'error' (handled by helper)
        vt_pos = _vt_positives_from_bundle(b)
        if vt_pos >= 2:
            add = 35
            details[f"vt_{ip}"] = add
            score += add
        elif vt_pos == 1:
            add = 22
            details[f"vt_{ip}"] = add
            score += add

        abuse_add = _abuse_score_from_bundle(b)
        if abuse_add > 0:
            details[f"abuse_{ip}"] = abuse_add
            score += abuse_add

    # 2) Behavioral: Fast-Flux (strong signal)
    if fastflux:
        details["fast_flux"] = 20
        score += 20

    # 3) Mail/auth signals (light)
    has_mx = isinstance(recs.get("MX"), list) and len(recs.get("MX") or []) > 0 \
             and not (len(recs.get("MX")) == 1 and str(recs.get("MX")[0]).strip() in ("0 .", "0 .."))

    if not flags.get("spf"):
        details["no_spf"] = 5
        score += 5
    if not flags.get("dmarc"):
        details["no_dmarc"] = 5
        score += 5

    if has_mx and (not flags.get("spf") or not flags.get("dmarc")):
        details["mail_misconfig"] = 10
        score += 10

    # 5) cap and label
    score = max(0, min(100, score))

    if score >= 75:
        label = "HIGH"
    elif score >= 50:
        label = "MEDIUM"
    elif score >= 25:
        label = "LOW"
    else:
        label = "SAFE"

    return score, details, label
