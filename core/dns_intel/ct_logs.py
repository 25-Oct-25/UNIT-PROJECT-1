# core/dns_intel/ct_logs.py
import requests
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

def query_ct_logs(domain: str, days: int = 7, timeout: float = 8.0) -> Dict[str, Any]:
    try:
        url = f"https://crt.sh/?q={domain}&output=json"
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "PhishSentry/1.0"})
        if r.status_code != 200:
            return {"error": f"http {r.status_code}"}
        try:
            items = r.json()
        except ValueError:
            return {"error": "invalid_json"}
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        new_count = 0
        for it in items:
            # الحقول مختلفة أحيانًا: اختر تاريخ الإصدار
            ts = it.get("not_before") or it.get("entry_timestamp") or ""
            try:
                # crt.sh يعيد timestamps بأشكال مختلفة؛ جرّب أكثر من صيغة
                for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
                    try:
                        d = datetime.strptime(ts[:len(fmt)], fmt).replace(tzinfo=timezone.utc)
                        break
                    except Exception:
                        d = None
                if d and d >= cutoff:
                    new_count += 1
            except Exception:
                continue
        return {"new_certs": new_count}
    except Exception as e:
        return {"error": str(e)}
