# main.py
import typer
from rich.console import Console

from script.run_scan import run_scan, read_domains, read_brands, BRANDS_PATH, DOMAINS_PATH
from core.brands.actions import add_brand_verified, BrandAddError, BrandExists
from core.brands.remove import remove_brand, BrandNotFound

from reports.quick_report import run_quick_report  # ← التقرير السريع بالذكاء الاصطناعي

app = typer.Typer(help="PhishSentry CLI")
console = Console()


@app.command()
def run():
    """Welcome message"""
    console.print("🔍 [bold cyan]Welcome to PhishSentry v1.0[/bold cyan]")
    console.print("[green]Try: python main.py --help[/green]")


@app.command()
def scan(
    domains: str = DOMAINS_PATH,
    brands: str = BRANDS_PATH,
    phase: int = 4,
    save_json: bool = False,
):
    """Run the phishing domain scanner."""
    console.print(f"[dim]Loading domains from:[/dim] {domains}")
    dlist = read_domains(domains)
    blist = read_brands(brands)
    run_scan(domains=dlist, phase=phase, save_json=save_json, brands=blist)


@app.command("add")
def add(name: str):
    """Verify and add a brand to the brand list."""
    try:
        hit = add_brand_verified(name)
        console.print(
            f"[green]✓ Verified[/green] → {hit.canonical_name}  "
            f"[red](conf={hit.confidence:.2f}, src={hit.source})[/red]"
        )
        if getattr(hit, "website", None):
            console.print(f"[green]Website:[/green] {hit.website}")
        console.print(f"[green]Added brand:[/green] {name} [dim](saved to {BRANDS_PATH})[/dim]")
    except BrandExists:
        console.print(f"[yellow]Brand already exists:[/yellow] {name}")
    except BrandAddError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(code=1)


@app.command("delete")
def delete(name: str):
    """Delete a brand from the brand list."""
    try:
        remove_brand(name)
        console.print(f"[green]🗑️ Removed brand:[/green] {name}")
    except BrandNotFound as e:
        console.print(f"[red]Brand not found:[/red] {e}")
        raise typer.Exit(code=1)


@app.command("report")
def report(
    domain: str,
    url: str = typer.Option(None, help="Landing URL to screenshot; defaults to http://{domain}"),
    no_screenshot: bool = typer.Option(False, "--no-screenshot", help="Skip screenshot capture"),
    open_report: bool = typer.Option(True, "--open/--no-open", help="Open HTML report after generation"),
):
    """Generate an English AI-powered Evidence Report for a given domain."""
    console.print(f"[cyan]Generating report for:[/cyan] {domain}")
    path = run_quick_report(domain=domain, url=url, screenshot=not no_screenshot, open_report=open_report)
    console.print(f"[green]✅ Report generated:[/green] {path}")


if __name__ == "__main__":
    app()
