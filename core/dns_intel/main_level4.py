# core/dns_intel/main_level4.py
"""
Level 4 - Risk Scoring & Final Summary
Usage:
    python -m core.dns_intel.main_level4
    python -m core.dns_intel.main_level4 example.com
    python -m core.dns_intel.main_level4 --file data/domains.txt
"""

from pathlib import Path
import argparse
import json
import time
from typing import List, Dict, Any
from datetime import datetime

from .dns_resolver import resolve_records, parse_txt_for_spf_dmarc
from .ip_enrichment import enrich_ips
from .scoring import compute_dns_risk
from .utils import ensure_dirs, load_history, save_history
from .config import DOMAINS_FILE, RESULTS_DIR, ROOT

# سنحفظ في results/level4/
RESULTS_DIR_L4 = (ROOT / "results" / "level4")
RESULTS_DIR_L4.mkdir(parents=True, exist_ok=True)

# طباعة ملخص (ستايل قريب من لقطة الشاشة)
def print_final_summary(i: int, total: int, d: Dict[str, Any]):
    domain = d.get("domain")
    sim_txt = d.get("similarity_text", "")  # لو حبيتِ تضيفين لاحقاً من مرحلة similarity
    spf = d.get("security_flags", {}).get("spf")
    dmarc = d.get("security_flags", {}).get("dmarc")
    mx_count = len(d.get("records", {}).get("MX", []) or [])
    score = d.get("dns_risk_score")
    label = d.get("dns_risk_label")

    # أشياء مفيدة من الإثراء
    providers = []
    enrich = d.get("ip_enrichment", {}) or {}
    for ip, b in enrich.items():
        ptr = (b.get("ptr") or "")
        if ptr:
            providers.append(ptr.split(".")[-2:] if "." in ptr else ptr)
    providers_txt = "" if not providers else " | providers≈" + ", ".join({ ".".join(p) if isinstance(p, list) else str(p) for p in providers })

    status = {
        "HIGH": "SUSPICIOUS",
        "MEDIUM": "UNDER MONITORING",
        "LOW": "REVIEW",
        "SAFE": "SAFE",
    }.get(label, "UNKNOWN")

    print(f"\n[{i}/{total}] {domain}")
    print(f"  → SPF={bool(spf)} | DMARC={bool(dmarc)} | MX={mx_count}{providers_txt}")
    print(f"  → Fast-Flux: {bool(d.get('fast_flux'))}")
    print(f"  → Risk Score: {score/100:.2f} ({label})")
    print(f"  ⚠️  Status: {status}")

def process_domain_level4(domain: str, history: Dict[str, Any]) -> Dict[str, Any]:
    # Level1
    l1 = resolve_records(domain)
    txts = l1["records"].get("TXT", [])
    l1["security_flags"] = parse_txt_for_spf_dmarc(txts) if isinstance(txts, list) else {"spf": False, "dmarc": False}

    # Level2
    ips = l1.get("ips", [])
    l1["ip_enrichment"] = enrich_ips(ips)

    # Level3 (fast-flux) — استخدام نفس تاريخ Level1
    prev = history.get(domain)
    fast_flux = False
    ff_details = {}
    if prev:
        prev_ips = prev.get("last_ips", [])
        prev_seen = prev.get("last_seen")
        if prev_seen:
            try:
                # نافذة 24 ساعة
                last_dt = datetime.fromisoformat(prev_seen.replace("Z", ""))
                delta_h = (datetime.utcnow() - last_dt).total_seconds() / 3600.0
                changed = set(prev_ips) != set(ips)
                if changed and delta_h <= 24:
                    fast_flux = True
                    ff_details = {"previous_ips": prev_ips, "current_ips": ips, "hours_since_last_seen": round(delta_h, 2)}
                else:
                    ff_details = {"previous_ips": prev_ips, "current_ips": ips, "hours_since_last_seen": round(delta_h, 2), "note": "no fast-flux"}
            except Exception:
                ff_details = {"note": "invalid previous timestamp"}
    else:
        ff_details = {"note": "no previous history"}

    l1["fast_flux"] = fast_flux
    l1["fast_flux_details"] = ff_details

    # Level4 (scoring)
    score, breakdown, label = compute_dns_risk(l1)
    l1["dns_risk_score"] = score
    l1["dns_risk_breakdown"] = breakdown
    l1["dns_risk_label"] = label

    # Update history
    history[domain] = {"last_ips": ips, "last_seen": l1.get("queried_at")}

    return l1

def save_result_level4(domain: str, result: Dict[str, Any]):
    safe = domain.replace("/", "_").replace(":", "_")
    (RESULTS_DIR_L4 / f"{safe}.json").write_text(json.dumps(result, indent=2))

def run(domains: List[str]):
    ensure_dirs()
    history = load_history()
    results = []
    total = len(domains)
    for i, d in enumerate(domains, start=1):
        d = d.strip()
        if not d:
            continue
        print(f"[+] Scoring {d}")
        try:
            res = process_domain_level4(d, history)
            save_result_level4(d, res)
            print_final_summary(i, total, res)
            results.append(res)
            time.sleep(0.2)
        except Exception as e:
            print(f"[!] Error processing {d}: {e}")
    save_history(history)
    print(f"\n✅ Level 4 complete. Results saved to: {RESULTS_DIR_L4}")
    return results

def cli():
    p = argparse.ArgumentParser(description="PhishSentry DNS Level4 - Risk Scoring & Final Summary")
    p.add_argument("domains", nargs="*", help="one or more domains")
    p.add_argument("--file", "-f", help="read domains from file (default: data/domains.txt)")
    args = p.parse_args()

    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Domains file not found: {path}")
            return
        domains = [ln.strip() for ln in path.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    elif args.domains:
        domains = args.domains
    else:
        df = Path(DOMAINS_FILE)
        if not df.exists():
            print(f"No domains provided and default file missing: {df}")
            return
        domains = [ln.strip() for ln in df.read_text().splitlines() if ln.strip() and not ln.startswith("#")]

    run(domains)

if __name__ == "__main__":
    cli()
