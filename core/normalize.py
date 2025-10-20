from __future__ import annotations
import re
from urllib.parse import urlparse
import tldextract

IDNA_SAFE = True  

def normalize_domain_to_token(raw: str) -> str:

    host = raw.strip()

    if "://" in host:
        host = urlparse(host).hostname or host

    ext = tldextract.extract(host)
    sub = ext.subdomain
    dom = ext.domain

    if IDNA_SAFE:
        try:
            dom = dom.encode("ascii", "ignore").decode("ascii")
        except Exception:
            pass

    sub_parts = [p for p in sub.split(".") if p and p.lower() != "www"]
    base = "-".join(sub_parts + [dom]) if sub_parts else dom

    token = base.lower()
    token = token.replace("_", "-").replace(".", "-")
    token = re.sub(r"[^a-z0-9\-]+", "", token) 
    token = re.sub(r"-{2,}", "-", token).strip("-")  

    return token

