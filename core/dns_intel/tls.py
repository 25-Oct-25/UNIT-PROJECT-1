# core/dns_intel/tls.py
import socket, ssl
from datetime import datetime, timezone
from typing import Dict, Any, Optional

def _parse_asn1_time(s: str) -> Optional[datetime]:
    # مثال: 'Oct 15 12:34:56 2025 GMT'
    try:
        return datetime.strptime(s, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    except Exception:
        try:
            return datetime.strptime(s, "%Y%m%d%H%M%SZ").replace(tzinfo=timezone.utc)
        except Exception:
            return None

def fetch_tls_info(domain: str, port: int = 443, timeout: float = 5.0) -> Dict[str, Any]:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
        # CN
        cn = "-"
        subj = cert.get("subject", [])
        for item in subj:
            for (k, v) in item:
                if k == "commonName":
                    cn = v
        # validity
        not_before = _parse_asn1_time(cert.get("notBefore", ""))
        not_after  = _parse_asn1_time(cert.get("notAfter", ""))
        now = datetime.now(timezone.utc)
        valid = (not_before is not None and not_after is not None and not_before <= now <= not_after)
        age_days = None
        if not_before:
            age_days = max(0, int((now - not_before).total_seconds() // 86400))
        return {"valid": bool(valid), "cn": cn, "age_days": age_days}
    except Exception as e:
        return {"error": str(e)}
