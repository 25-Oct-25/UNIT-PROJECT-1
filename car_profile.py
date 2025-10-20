from rich.console import Console
from rich.table import Table
class Car:
    def __init__ (self, make, model, year, price_usd, origin_country):
        self.make =make
        self.model =model
        self.year =year
        self.price_usd=price_usd
        self.origin_country=origin_country
    
    def display(self):
        """Prints the car's details in a clean format."""
        print(f"--- {self.year} {self.make} {self.model} ---")
        print(f"  Price: ${self.price_usd:,.2f}")
        print(f"  Origin: {self.origin_country}")


    def print_car_info(self):
        """Prints the car's details in a table"""
        console = Console()
        table = Table(title="🚘 Car Information", style="bold blue")

        table.add_column("Attribute", style="bold white")
        table.add_column("Value", style="white")

        table.add_row("Origin Country", f"[cyan]{self.origin_country}[/cyan]")
        table.add_row("Base Price (USD)", f"[green]{self.price_usd:,.2f}[/green]")
        table.add_row("Year", f"[yellow]{self.year}[/yellow]")
        table.add_row("Make", f"[white]{self.make}[/white]")
        table.add_row("Model", f"[magenta]{self.model}[/magenta]")

        console.print(table)