# core/dns_intel/main_level2.py
"""
Main runner for DNS Intelligence - Level 2 (IP Enrichment)
Usage:
    python -m core.dns_intel.main_level2                 # uses data/domains.txt
    python -m core.dns_intel.main_level2 example.com
    python -m core.dns_intel.main_level2 --file data/domains.txt
"""
from .cleaners import prune_result
from pathlib import Path
import argparse
import json
import time
from typing import List, Dict, Any

from .dns_resolver import resolve_records, parse_txt_for_spf_dmarc
from .ip_enrichment import enrich_ips
from .utils import ensure_dirs, load_history, save_history, pretty_print
from .config import DOMAINS_FILE, HISTORY_FILE
from .config import ROOT  # to build results/level2 path easily
import os

RESULTS_DIR_L2 = ROOT / "results" / "level2"
RESULTS_DIR_L2.mkdir(parents=True, exist_ok=True)

def save_result_level2(domain: str, result: Dict[str, Any]):
    safe_name = domain.replace("/", "_").replace(":", "_")
    out_path = RESULTS_DIR_L2 / f"{safe_name}.json"
    out_path.write_text(json.dumps(result, indent=2))

def process_domain_level2(domain: str, history: Dict) -> Dict:
    # First, resolve basic DNS (Level1)
    l1 = resolve_records(domain)
    txts = l1["records"].get("TXT", [])
    if isinstance(txts, list):
        l1["security_flags"] = parse_txt_for_spf_dmarc(txts)
    else:
        l1["security_flags"] = {"spf": False, "dmarc": False}

    # Then, enrich its IPs
    ips = l1.get("ips", [])
    enrichment = enrich_ips(ips)
    l1["ip_enrichment"] = enrichment

    # update in-memory history (we’ll re-use same history file of L1)
    history[domain] = {
        "last_ips": ips,
        "last_seen": l1.get("queried_at")
    }
    return l1

def run(domains: List[str]):
    ensure_dirs()
    history = load_history()
    results = []
    for d in domains:
        d = d.strip()
        if not d:
            continue
        try:
            print(f"[+] Enriching {d}")
            res = process_domain_level2(d, history)

            # ✨ نظّف النتيجة قبل الحفظ/العرض لتقليل الضخامة والتكرار
            res_to_save = prune_result(res)

            save_result_level2(d, res_to_save)
            # نطبع النسخة المنقّاة لتكون متناسقة مع اللي نحفظه
            pretty_print(res_to_save)

            results.append(res_to_save)
            time.sleep(0.2)
        except Exception as e:
            print(f"[!] Error processing {d}: {e}")
    save_history(history)
    print(f"[+] L2 results saved to {RESULTS_DIR_L2}")
    return results


def cli():
    p = argparse.ArgumentParser(description="PhishSentry DNS Level2 (IP Enrichment) runner")
    p.add_argument("domains", nargs="*", help="one or more domains")
    p.add_argument("--file", "-f", help="read domains from a specified file")
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
