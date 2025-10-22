import sys, os, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List, Optional, Dict, Any, Callable
from pathlib import Path
from rich.console import Console

from core.io import read_brands, read_domains
from core.normalize import normalize_domain_to_token
from core.similarity import calculate_similarity

# core DNS/Enrichment/Scoring/Utils
try:
    from core.dns_intel.dns_resolver import resolve_records, parse_txt_for_spf_dmarc
except Exception:
    resolve_records = None
    parse_txt_for_spf_dmarc = None

try:
    from core.dns_intel.ip_enrichment import enrich_ips
except Exception:
    enrich_ips = None

try:
    from core.dns_intel.scoring import compute_dns_risk
except Exception:
    compute_dns_risk = None

try:
    from core.dns_intel.utils import load_history, save_history
except Exception:
    load_history = lambda: {}
    save_history = lambda h: None

# Optional advanced modules (may not exist). We'll import if present.
def safe_import(modpath: str, name: str) -> Optional[Callable]:
    try:
        mod = __import__(modpath, fromlist=[name])
        return getattr(mod, name)
    except Exception:
        return None

fetch_tls_info = safe_import("core.dns_intel.tls", "fetch_tls_info")
fetch_whois_info = safe_import("core.dns_intel.whois", "fetch_whois_info")
query_ct_logs = safe_import("core.dns_intel.ct_logs", "query_ct_logs")
passive_dns_lookup = safe_import("core.dns_intel.passive_dns", "passive_dns_lookup")

BRANDS_PATH  = "data/brands.txt"
DOMAINS_PATH = "data/domains.txt"

console = Console()

# display thresholds
SHOW_THRESHOLD = 0.70
TAG_BRAND_THRESHOLD = 0.70
FAST_FLUX_WINDOW_HOURS = 24.0

def risk_label_from_similarity(score: float) -> str:
    if score >= 0.85: return "HIGH"
    if score >= 0.70: return "MEDIUM"
    return "LOW"

def status_text(label: str) -> str:
    if label == "HIGH":   return "SUSPICIOUS – possible credential phish"
    if label == "MEDIUM": return "UNDER MONITORING"
    return "SAFE"

# UI helpers
def print_header(brands: List[str], dns_enabled: bool):
    console.print()
    #console.print("🔎 [bold green]PhishSentry v3.0 – Brand & Threat Intelligence[/bold green]")
    console.rule()
    console.print(f"[red]Target brands loaded:[/red] [green]{', '.join(brands)}[/green]")
    if dns_enabled:
        console.print("CT logs & [red]Passive DNS:[/red] [green]enabled[/green]")
        #console.print("[red]AI Risk Classifier:[/red] [green]active[/green]")
    else:
        console.print("CT logs & [red]Passive DNS:[/red] [green]disabled (this phase shows similarity only)[/green]")
        #console.print("[red]Risk Classifier:[/red] [green]disabled (not in this phase)[/green]")
    console.rule()

def print_footer(elapsed_s: float, total: int, high: int, med: int, low: int):
    console.print(f"[green]✅ Scan completed in {elapsed_s:.2f}s[/green]")
    console.print(f"[red]Total domains scanned: {total}[/red]")
    console.print(f"[red]Detected high-risk: {high} | medium: {med} | safe: {low}[/red]")
    console.rule()

def _first_ip_for_display(dns_result: dict) -> str:
    records   = (dns_result or {}).get("records", {}) or {}
    errors    = (dns_result or {}).get("errors", {}) or {}
    a_list    = records.get("A") or []
    ips_all   = dns_result.get("ips") or []

    if a_list:
        return a_list[0]
    if ips_all:
        return ips_all[0]
    err_a = (errors.get("A") or "").lower()
    nx = ("does not exist" in err_a) or ("nxdomain" in err_a)
    return "NXDOMAIN" if nx else "UNRESOLVED"

def print_dns_line(dns_result: dict, whois_info: Optional[dict]):
    mx_count = len(((dns_result or {}).get("records", {}) or {}).get("MX") or [])
    ip0 = _first_ip_for_display(dns_result)
    registrar = "-"
    if isinstance(whois_info, dict):
        registrar = whois_info.get("registrar") or whois_info.get("org") or "-"
    # Print core DNS + registrar if present
    if registrar and registrar != "-":
        console.print(f" [green]→[/green] [red]DNS:[/red][green] MX= {mx_count} | A= {ip0} | Registrar= {registrar}[/green]")
    else:
        console.print(f" [green]→[/green] [red]DNS:[/red][green] MX= {mx_count} | A= {ip0}[/green]")

def print_tls_line(tls_info: Optional[dict]):
    if not tls_info:
        console.print(f" [green]→[/green] [red]TLS:[/red] [green]Not available[/green]")
        return
    valid = "Valid" if tls_info.get("valid") else "Invalid"
    cn = tls_info.get("cn") or "-"
    age = tls_info.get("age_days")
    age_txt = f" | Age= {age} days" if age is not None else ""
    console.print(f" [green]→[/green] [red]TLS:[/red] [green]{valid} | CN= {cn} {age_txt}[/green]")

def print_whois_line(whois_info: Optional[dict]):
    if not whois_info:
        console.print(f" [green]→[/green] [red]WHOIS:[/red] [green]Not available[/green]")
        return
    created = whois_info.get("created") or whois_info.get("creation_date") or "-"
    org = whois_info.get("org") or whois_info.get("registrant_org") or whois_info.get("org_name") or "Private"
    console.print(f" [green]→[/green] [red]WHOIS:[/red] [green]Created= {created} | Org= {org}[/green]")

def print_ct_line(ct_info: Optional[dict]):
    if not ct_info:
        console.print(f" [green]→[/green] [red]CT Logs:[/red] [green]Not available[/green]")
        return
    new_certs = ct_info.get("new_certs", 0)
    console.print(f" [green]→[/green] [red]CT Logs:[/red] [green]{new_certs} new certificate detected[/green]")

def print_passive_dns_line(pd_info: Optional[dict]):
    if not pd_info:
        console.print(f" [green]→[/green] [red]Passive DNS:[/red] [green]Not available[/green]")
        return
    siblings = pd_info.get("siblings")
    if siblings is None:
        console.print(f" [green]→[/green] [red]Passive DNS:[/red] [green]Not available[/green]")
    else:
        note = " (possible campaign)" if siblings and siblings >= 3 else ""
        console.print(f" [green]→[/green] [red]Passive DNS:[/red] [green]{siblings} domains share same IP {note}[/green]")

def print_domain_block(idx_shown: int, total: int, dom: str, sim_score: float,
                       best_brand: Optional[str], dns_res: Optional[dict],
                       whois_info: Optional[dict], tls_info: Optional[dict],
                       ct_info: Optional[dict], pd_info: Optional[dict],
                       risk_score: Optional[int], risk_label: Optional[str]):
    console.print(f"[bright_black][[/bright_black][red]{idx_shown}[/red][green]/{total}[/green][bright_black]][/bright_black] [bold green]{dom}[/bold green]")

    # similarity line (+ brand name if above threshold)
    if best_brand and sim_score >= TAG_BRAND_THRESHOLD:
        console.print(f" [green]→[/green] [red]Similarity:[/red] [red]{sim_score:.2f}[/red] [bright_black]({best_brand})[/bright_black]")
    else:
        console.print(f" [green]→[/green] [red]Similarity:[/red] [red]{sim_score:.2f}[/red]")

    # DNS + Registrar
    if dns_res is not None:
        print_dns_line(dns_res, whois_info)

    # TLS
    print_tls_line(tls_info)

    # WHOIS
    print_whois_line(whois_info)

    # CT
    print_ct_line(ct_info)

    # Passive DNS
    print_passive_dns_line(pd_info)

    # AI Risk
    if risk_score is not None and risk_label is not None:
        console.print(f" [green]→[/green] [red]Risk Score:[/red] [green]{risk_score/100:.2f} ({risk_label})[/green]")
        if   risk_label == "HIGH":   console.print(f" [red]⚠️ Status:[/red] [red]{status_text('HIGH')}[/red]")
        elif risk_label == "MEDIUM": console.print(f" [red]⚠️ Status:[/red] [green]{status_text('MEDIUM')}[/green]")
    console.print()

# fast-flux lite
def fast_flux_lite(domain: str, current_ips: List[str], history: Dict[str, Any], queried_at_iso: Optional[str]) -> bool:
    prev = history.get(domain)
    if not prev:
        return False
    prev_ips = prev.get("last_ips") or []
    last_seen = prev.get("last_seen")
    if not last_seen:
        return False
    try:
        from datetime import datetime
        last_dt = datetime.fromisoformat(last_seen.replace("Z", ""))
        now_dt  = datetime.fromisoformat((queried_at_iso or last_seen).replace("Z", ""))
        delta_h = (now_dt - last_dt).total_seconds() / 3600.0
        changed = set(prev_ips) != set(current_ips)
        return bool(changed and delta_h <= FAST_FLUX_WINDOW_HOURS)
    except Exception:
        return False

# orchestrator
def analyze_one(domain: str, brands: List[str], history: Dict[str, Any], use_dns: bool) -> dict:
    row: Dict[str, Any] = {"domain": domain}
    token = normalize_domain_to_token(domain)

    # similarity
    best_brand = None
    best_score = 0.0
    for b in brands:
        try:
            s = calculate_similarity(token, b)
        except Exception:
            s = 0.0
        if s > best_score:
            best_score = s
            best_brand = b
    row["similarity"] = best_score
    row["best_brand"] = best_brand

    # skip heavy collectors if DNS disabled
    if not use_dns or resolve_records is None:
        return row

    # Level1 DNS
    try:
        dns_res = resolve_records(domain)
        txts = dns_res.get("records", {}).get("TXT", [])
        if isinstance(txts, list) and parse_txt_for_spf_dmarc:
            dns_res["security_flags"] = parse_txt_for_spf_dmarc(txts)
    except Exception as e:
        dns_res = {"records": {}, "errors": {"_dns": str(e)}}
    row["dns"] = dns_res

    # Level2 Enrichment (safe guarded)
    try:
        ips = dns_res.get("ips") or []
        if enrich_ips and ips:
            try:
                row["ip_enrichment"] = enrich_ips(ips)
            except Exception as e:
                row["ip_enrichment"] = {"_error": str(e)}
        else:
            row["ip_enrichment"] = {}
    except Exception:
        row["ip_enrichment"] = {}

    # Level3 extras: WHOIS, TLS, CT, Passive DNS (call if functions exist)
    whois_info = None
    tls_info = None
    ct_info = None
    pd_info = None

    # WHOIS
    try:
        if fetch_whois_info:
            whois_info = fetch_whois_info(domain)
    except Exception:
        whois_info = None

    # TLS
    try:
        if fetch_tls_info:
            tls_info = fetch_tls_info(domain)
    except Exception:
        tls_info = None

    # CT logs
    try:
        if query_ct_logs:
            ct_info = query_ct_logs(domain)
    except Exception:
        ct_info = None

    # Passive DNS
    try:
        if passive_dns_lookup:
            pd_info = passive_dns_lookup(domain)
    except Exception:
        pd_info = None

    row["whois"] = whois_info
    row["tls"] = tls_info
    row["ct"] = ct_info
    row["passive_dns"] = pd_info

    # Level3 fast-flux (lite)
    try:
        ff = fast_flux_lite(domain, dns_res.get("ips") or [], history, dns_res.get("queried_at"))
        row["fast_flux"] = ff
    except Exception:
        row["fast_flux"] = False

    # Level4 scoring (if available)
    try:
        if compute_dns_risk:
            score, breakdown, label = compute_dns_risk(row)
            row["dns_risk_score"] = score
            row["dns_risk_label"] = label
            row["dns_risk_breakdown"] = breakdown
        else:
            row["dns_risk_score"] = None
            row["dns_risk_label"] = None
            row["dns_risk_breakdown"] = {}
    except Exception as e:
        row["dns_risk_score"] = None
        row["dns_risk_label"] = None
        row["dns_risk_breakdown"] = {"_error": str(e)}

    # update history snapshot
    try:
        history[domain] = {"last_ips": dns_res.get("ips") or [], "last_seen": dns_res.get("queried_at")}
    except Exception:
        pass

    return row

def run_scan(domains: List[str], phase: int = 4, save_json: bool = False, brands: Optional[List[str]] = None):
    t0 = time.perf_counter()
    brands = brands or read_brands(BRANDS_PATH)
    domains = domains or read_domains(DOMAINS_PATH)
    total   = len(domains)
    dns_on  = (phase >= 2)

    history = load_history() or {}

    print_header(brands, dns_on)

    high = med = low = 0
    shown_idx = 0

    for dom in domains:
        try:
            with console.status(f"[dim]scanning {dom}...[/dim]", spinner="dots"):
                row = analyze_one(dom, brands, history, use_dns=dns_on)
        except Exception as e:
            console.print(f"[red]skip {dom}[/red] [dim]({e})[/dim]")
            continue

        risk_label = row.get("dns_risk_label")
        risk_score = row.get("dns_risk_score")

        similarity = float(row.get("similarity") or 0.0)
        ai_score = float(row.get("ai_risk_score") or 0.0)

        if risk_label is None:
            low += 1
            #continue

        if   risk_label == "HIGH":
            high += 1
        elif risk_label == "MEDIUM":
            med += 1
        else:
            low += 1
            #continue  

        shown_idx += 1
        print_domain_block(
            idx_shown=shown_idx,
            total=len(domains),
            dom=dom,
            sim_score=float(row.get("similarity") or 0.0),
            best_brand=row.get("best_brand"),
            dns_res=row.get("dns"),
            whois_info=row.get("whois"),
            tls_info=row.get("tls"),
            ct_info=row.get("ct"),
            pd_info=row.get("passive_dns"),
            risk_score=risk_score,
            risk_label=risk_label,
    )

        if save_json:
            outdir = Path("results/level4"); outdir.mkdir(parents=True, exist_ok=True)
            (outdir / f"{dom.replace('/', '_')}.json").write_text(
                str({
                    "domain": dom,
                    "similarity": row.get("similarity"),
                    "dns": row.get("dns"),
                    "whois": row.get("whois"),
                    "tls": row.get("tls"),
                    "ct": row.get("ct"),
                    "passive_dns": row.get("passive_dns"),
                    "ip_enrichment": row.get("ip_enrichment"),
                    "fast_flux": row.get("fast_flux"),
                    "dns_risk_score": risk_score,
                    "dns_risk_label": risk_label,
                }),
                encoding="utf-8"
            )

    # persist history
    save_history(history)
    print_footer(time.perf_counter() - t0, total, high, med, low)

if __name__ == "__main__":
    run_scan(read_domains(DOMAINS_PATH), phase=4, save_json=False)
