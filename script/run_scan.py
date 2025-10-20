import sys, os, time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from rich.console import Console
from core.io import read_brands, read_domains
from core.normalize import normalize_domain_to_token
from core.similarity import calculate_similarity

BRANDS_PATH  = "data/brands.txt"
DOMAINS_PATH = "data/domains.txt"

def risk_label(score: float) -> str:
    if score >= 0.85: return "HIGH"
    if score >= 0.70: return "MEDIUM"
    return "LOW"

def status_text(label: str) -> str:
    if label == "HIGH":
        return "SUSPICIOUS - possible credential phish"
    if label == "MEDIUM":
        return "UNDER MONITORING"
    return "SAFE"

def main():
    console = Console()
    start = time.perf_counter()

    brands  = read_brands(BRANDS_PATH)
    domains = read_domains(DOMAINS_PATH)
    total   = len(domains)

    console.print("\n🔎 [green]PhishSentry v3.0 — Brand & Threat Intelligence (Similarity-only)[/green]")
    console.print("-" * 66 + "\n")
    console.print("[red]Target brands loaded:[/red] [green]" + ", ".join(brands) + "[/green]")
    console.print("CT logs & [red]Passive DNS:[/red] [green]disabled (this phase shows similarity only)[/green]")
    console.print("[red]AI Risk Classifier:[/red] [green]disabled (not in this phase)[/green]")
    console.print("-" * 66 + "\n")

    high = med = low = 0

    for i, dom in enumerate(domains, start=1):
        token = normalize_domain_to_token(dom)

        best_score = 0.0
        for b in brands:
            s = calculate_similarity(token, b)
            if s > best_score:
                best_score = s

        label = risk_label(best_score)
        if label == "HIGH":   high += 1
        elif label == "MEDIUM": med += 1
        else:
            low += 1
            continue  

        console.print(f"[bright_black][[/bright_black][red]{i}[/red][green]/{total}[/green][bright_black]][/bright_black] [green]{dom}[/green]")
        console.print(f" [green] → [green][red]Similarity: {best_score:.2f}[/red]")
        console.print(f"  ⚠️ [red]Status:[/red] [green]{status_text(label)}[/green]\n")

    elapsed = time.perf_counter() - start

    console.print(f"[green]✅ Scan completed in {elapsed:.2f}s[/green]")
    console.print(f"[red]Total domains scanned: {total}[/red]")
    console.print(f"[red]Detected high-risk: {high} | medium: {med} | safe: {low}[/red]")
    console.print("-" * 66)
    console.print("Use later phases to enable DNS/WHOIS/TLS/CT when ready.")

if __name__ == "__main__":
    main()


