import typer
from rich.console import Console

app = typer.Typer(help="PhishSentry CLI")
console = Console()

@app.command()
def run():
    console.print("🔍 [bold cyan]Welcome to PhishSentry v1.0[/bold cyan]")
    console.print("[green]Type 'python main.py --help' to see commands.[/green]")

if __name__ == "__main__":
    app()  
