# core/dns_intel/utils.py
from pathlib import Path
import json
from typing import Dict, Any
from .config import DATA_DIR, RESULTS_DIR, HISTORY_FILE
import os

# optional rich pretty print
try:
    from rich.console import Console
    from rich.table import Table
    console = Console()
except Exception:
    console = None

def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def load_history() -> Dict[str, Any]:
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_history(history: Dict[str, Any]):
    HISTORY_FILE.write_text(json.dumps(history, indent=2))

def save_result(domain: str, result: Dict[str, Any]):
    safe_name = domain.replace("/", "_").replace(":", "_")
    out_path = RESULTS_DIR / f"{safe_name}.json"
    out_path.write_text(json.dumps(result, indent=2))

def pretty_print(result: Dict[str, Any]):
    records = result.get("records", {}) or {}
    errors  = result.get("errors", {}) or {}
    flags   = result.get("security_flags", {}) or {}

    def join_list(val):
        if isinstance(val, list):
            return ", ".join(val) if val else "-"
        return str(val) if val not in (None, {}) else "-"

    if console:
        t = Table(title=f"Domain: {result.get('domain')}  (queried: {result.get('queried_at')})")
        t.add_column("Field")
        t.add_column("Value", overflow="fold")

        # Core DNS records
        t.add_row("A",     join_list(records.get("A", [])))
        t.add_row("AAAA",  join_list(records.get("AAAA", [])))
        t.add_row("MX",    join_list(records.get("MX", [])))
        t.add_row("NS",    join_list(records.get("NS", [])))
        t.add_row("CNAME", join_list(records.get("CNAME", [])))
        t.add_row("SOA",   join_list(records.get("SOA", [])))

        # TXT (limit visible items)
        txts = records.get("TXT", [])
        if isinstance(txts, list):
            txt_preview = " | ".join(txts[:3]) + ("..." if len(txts) > 3 else "")
            t.add_row("TXT", txt_preview or "-")
        else:
            t.add_row("TXT", str(txts) if txts else "-")

        # Security flags if present
        if flags:
            t.add_row("SPF",   "True" if flags.get("spf") else "False")
            t.add_row("DMARC", "True" if flags.get("dmarc") else "False")

        # Aggregated IPs
        t.add_row("IPs", ", ".join(result.get("ips", [])) or "-")

        # Errors (if any)
        if errors:
            err_msg = " ; ".join(f"{k}: {v}" for k, v in errors.items())
            if len(err_msg) > 300:
                err_msg = err_msg[:300] + "..."
            t.add_row("Errors", err_msg)

        console.print(t)
    else:
        # Fallback: plain JSON including errors and flags
        print(f"---- {result.get('domain')} ----")
        print(json.dumps(result, indent=2))
