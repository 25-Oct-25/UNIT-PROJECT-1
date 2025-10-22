# core/dns_intel/main_level1.py
"""
Main runner for DNS Intelligence - Level 1
Usage:
    python -m core.dns_intel.main_level1           # uses data/domains.txt
    python -m core.dns_intel.main_level1 example.com
    python -m core.dns_intel.main_level1 --file path/to/list.txt
"""

from pathlib import Path
import argparse
import time
from typing import List, Dict

from .dns_resolver import resolve_records, parse_txt_for_spf_dmarc
from .utils import ensure_dirs, load_history, save_history, save_result, pretty_print
from .config import DOMAINS_FILE

def process_domain(domain: str, history: Dict) -> Dict:
    result = resolve_records(domain)
    txts = result["records"].get("TXT", [])
    if isinstance(txts, list):
        result["security_flags"] = parse_txt_for_spf_dmarc(txts)
    else:
        result["security_flags"] = {"spf": False, "dmarc": False}
    # update history in-memory
    history[domain] = {"last_ips": result.get("ips", []), "last_seen": result.get("queried_at")}
    return result

def run(domains: List[str]):
    ensure_dirs()
    history = load_history()
    results = []
    for d in domains:
        d = d.strip()
        if not d:
            continue
        try:
            print(f"[+] Processing {d}")
            res = process_domain(d, history)
            save_result(d, res)
            pretty_print(res)
            results.append(res)
            time.sleep(0.2)
        except Exception as e:
            print(f"[!] Error processing {d}: {e}")
    save_history(history)
    return results

def cli():
    p = argparse.ArgumentParser(description="PhishSentry DNS Level1 runner")
    p.add_argument("domains", nargs="*", help="one or more domains (overrides default file)")
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
