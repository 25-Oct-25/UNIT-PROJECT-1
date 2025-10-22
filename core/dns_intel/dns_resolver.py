# core/dns_intel/dns_resolver.py
from typing import Dict, Any, List
from datetime import datetime
import dns.resolver

# dns resolver config (tweak timeouts if needed)
resolver = dns.resolver.Resolver()
resolver.lifetime = 5
resolver.timeout = 3

def resolve_records(domain: str) -> Dict[str, Any]:
    """
    Return DNS records for domain: A, AAAA, MX, NS, TXT, SOA, CNAME and ips list.
    Does not raise on failure; collects errors under 'errors' key.
    """
    out = {
        "domain": domain,
        "queried_at": datetime.utcnow().isoformat() + "Z",
        "records": {},
        "errors": {}
    }
    rtypes = ["A", "AAAA", "MX", "NS", "TXT", "SOA", "CNAME"]
    for r in rtypes:
        try:
            answers = resolver.resolve(domain, r, raise_on_no_answer=False)
            if answers.rrset is None:
                out["records"][r] = []
            else:
                vals = []
                for rr in answers:
                    vals.append(rr.to_text())
                out["records"][r] = vals
        except Exception as e:
            # keep records as empty list (so downstream code won't break)
            out["records"][r] = []
            # store human-friendly error separately
            out["errors"][r] = str(e)

    # collect IPs from A and AAAA only if they are lists of strings
    ips = []
    for a in out["records"].get("A", []):
        if isinstance(a, str) and a:
            ips.append(a)
    for a in out["records"].get("AAAA", []):
        if isinstance(a, str) and a:
            ips.append(a)
    out["ips"] = list(dict.fromkeys(ips))
    return out
# =====================================================================================


def parse_txt_for_spf_dmarc(txt_records: List[str]) -> Dict[str, bool]:
    """
    Check TXT records for SPF and DMARC presence.
    """
    has_spf = False
    has_dmarc = False
    for r in txt_records:
        try:
            s = r if isinstance(r, str) else r.to_text()
        except Exception:
            continue
        low = s.lower()
        if "v=spf1" in low:
            has_spf = True
        if "v=dmarc1" in low:
            has_dmarc = True
    return {"spf": has_spf, "dmarc": has_dmarc}
