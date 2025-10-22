# core/dns_intel/main_level3.py
"""
Level 3 - Temporal Analysis & Fast-Flux Detection
Usage:
    python -m core.dns_intel.main_level3
    python -m core.dns_intel.main_level3 example.com
    python -m core.dns_intel.main_level3 --file data/domains.txt
"""

from pathlib import Path
import argparse
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

from .dns_resolver import resolve_records, parse_txt_for_spf_dmarc
from .utils import ensure_dirs, load_history, save_history, save_result, pretty_print
from .config import DOMAINS_FILE, HISTORY_FILE, RESULTS_DIR

# default window for fast-flux detection (in hours)
FAST_FLUX_WINDOW_HOURS = 24

def detect_fast_flux(domain: str, current_ips: List[str], history: Dict[str, Any], window_hours: int = FAST_FLUX_WINDOW_HOURS) -> Dict[str, Any]:
    """
    Returns a dict with fast-flux signal:
    { "fast_flux": bool, "details": { "previous_ips": [...], "changed_within_hours": ..., "since": "..."} }
    """
    prev_entry = history.get(domain)
    res = {"fast_flux": False, "details": {}}
    if not prev_entry:
        # No history — can't say it's fast-flux, but record initial
        res["details"] = {"note": "no previous history"}
        return res

    prev_ips = prev_entry.get("last_ips", [])
    last_seen = prev_entry.get("last_seen")
    if not last_seen:
        res["details"] = {"note": "previous entry missing timestamp"}
        return res

    try:
        last_dt = datetime.fromisoformat(last_seen.replace("Z", ""))
    except Exception:
        # fallback: if malformed timestamp
        res["details"] = {"note": "invalid previous timestamp"}
        return res

    delta_hours = (datetime.utcnow() - last_dt).total_seconds() / 3600.0
    ips_changed = set(prev_ips) != set(current_ips)

    res["details"].update({
        "previous_ips": prev_ips,
        "current_ips": current_ips,
        "hours_since_last_seen": round(delta_hours, 2),
    })

    # If IPs changed and change within window_hours => flag fast-flux
    if ips_changed and delta_hours <= window_hours:
        res["fast_flux"] = True
        res["details"]["reason"] = f"IPs changed within {window_hours}h"
    else:
        res["fast_flux"] = False
        if ips_changed:
            res["details"]["reason"] = f"IPs changed but >{window_hours}h since last seen"
        else:
            res["details"]["reason"] = "IPs unchanged"

    return res

def process_domain_level3(domain: str, history: Dict[str, Any]) -> Dict[str, Any]:
    # resolve (as in level1)
    l1 = resolve_records(domain)
    txts = l1["records"].get("TXT", [])
    if isinstance(txts, list):
        l1["security_flags"] = parse_txt_for_spf_dmarc(txts)
    else:
        l1["security_flags"] = {"spf": False, "dmarc": False}

    # detect fast-flux using history
    ff = detect_fast_flux(domain, l1.get("ips", []), history, FAST_FLUX_WINDOW_HOURS)
    l1["fast_flux"] = ff.get("fast_flux", False)
    l1["fast_flux_details"] = ff.get("details", {})

    # update history with current snapshot (we keep last_seen and last_ips)
    history[domain] = {"last_ips": l1.get("ips", []), "last_seen": l1.get("queried_at")}

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
            print(f"[+] Level3: Analyzing {d}")
            res = process_domain_level3(d, history)
            # save result in results/level1 or level3 (we'll use level3 folder)
            # create level3 folder under RESULTS_DIR
            level3_dir = RESULTS_DIR.parent / "level3"
            level3_dir.mkdir(parents=True, exist_ok=True)
            out_path = level3_dir / f"{d.replace('/', '_')}.json"
            out_path.write_text(json.dumps(res, indent=2))
            pretty_print(res)
            results.append(res)
            time.sleep(0.15)
        except Exception as e:
            print(f"[!] Error processing {d}: {e}")
    # persist history
    save_history(history)
    print("[+] Level3 complete. Results in results/level3/")
    return results

def cli():
    p = argparse.ArgumentParser(description="PhishSentry DNS Level3 - Fast-Flux detection")
    p.add_argument("domains", nargs="*", help="one or more domains or none to use default file")
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
