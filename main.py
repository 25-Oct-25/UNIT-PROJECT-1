import typer
from rich.console import Console
from script.run_scan import run_scan, read_domains, read_brands, BRANDS_PATH, DOMAINS_PATH
from core.brands.actions import add_brand_verified, BrandAddError, BrandExists
from core.brands.remove import remove_brand, BrandNotFound

app = typer.Typer(help="PhishSentry CLI")
console = Console()

@app.command()
def run():
    console.print("🔍 [bold cyan]Welcome to PhishSentry v1.0[/bold cyan]")
    console.print("[green]Type 'python main.py scan --help' to run scanner.[/green]")

@app.command()
def scan(domains: str = DOMAINS_PATH, brands: str = BRANDS_PATH, phase: int = 4, save_json: bool = False):
    """ Scan for malicious (look-alike) domains targeting the configured brands."""
    console.print(f"[dim]Loading domains from:[/dim] {domains}")
    dlist = read_domains(domains)
    blist = read_brands(brands)
    run_scan(domains=dlist, phase=phase, save_json=save_json, brands=blist)

@app.command("add")
def add(name: str):
    """ Verify & add brand """
    try:
        hit = add_brand_verified(name)
        console.print(f"[green]✓ Verified[/green] → {hit.canonical_name}  [dim](conf={hit.confidence:.2f}, src={hit.source})[/dim]")
        if getattr(hit, "website", None):
            console.print(f"[cyan]Website:[/cyan] {hit.website}")
        console.print(f"[green]Added brand:[/green] {name} [dim](saved to {BRANDS_PATH})[/dim]")
    except BrandExists:
        console.print(f"[yellow]Brand already exists:[/yellow] {name}")
    except BrandAddError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(code=1)

@app.command("delete")
def delete(name: str):
    """ Delete brand """
    try:
        remove_brand(name)
        console.print(f"[green]🗑️ Removed brand:[/green] {name}")
    except BrandNotFound as e:
        console.print(f"[red]Brand not found:[/red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
