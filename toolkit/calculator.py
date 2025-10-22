from rich.console import Console
from rich.table import Table
VAT_RATE = 0.15      #15% Value Added Tax
CUSTOMS_RATE = 0.05  #5% Customs Duty
INSURANCE_RATE = 0.015  #1.5% of car price (optional marine insurance)

SHIPPING_COSTS = {
    'USA': 1500,
    'GERMANY': 1200,
    'JAPAN': 1800,
    'UAE': 500
}
DEFAULT_SHIPPING_COST = 2000  #Cost for countries not in the dictionary
USD_TO_SAR = 3.75  #Exchange rate

class Calculator:
    @staticmethod
    def calculate_customs(price_usd, shipping_usd):
        """Calculates customs duty (5% of car price + shipping)."""
        return (price_usd + shipping_usd) * CUSTOMS_RATE

    @staticmethod
    def calculate_insurance(price_usd):
        """Calculates marine insurance (default 1.5% of the car price)."""
        return price_usd * INSURANCE_RATE

    @staticmethod
    def calculate_vat(price_usd, shipping_usd, insurance_usd, customs_usd):
        """
        Calculates VAT (15%) on total of price + shipping + insurance + customs.
        """
        total_before_vat = price_usd + shipping_usd + insurance_usd + customs_usd
        return total_before_vat * VAT_RATE

    @staticmethod
    def get_shipping_cost(origin_country):
        """
        Returns the shipping cost based on the origin country.
        """
        return SHIPPING_COSTS.get(origin_country.upper(), DEFAULT_SHIPPING_COST)

    @staticmethod
    def calculate_total_cost(car):
        """
        Calculates the total landed cost for a given car object.
        """
        #Get shipping cost
        shipping = Calculator.get_shipping_cost(car.origin_country)

        #Calculate insurance
        insurance = Calculator.calculate_insurance(car.price_usd)

        #Calculate customs
        customs = Calculator.calculate_customs(car.price_usd, shipping)

        #Calculate VAT
        vat = Calculator.calculate_vat(car.price_usd, shipping, insurance, customs)

        #Sum up everything
        total_cost_usd = car.price_usd + shipping + insurance + customs + vat

        #Convert all to SAR
        return {
            'base_price': car.price_usd * USD_TO_SAR,
            'shipping': shipping * USD_TO_SAR,
            'insurance': insurance * USD_TO_SAR,
            'customs': customs * USD_TO_SAR,
            'vat': vat * USD_TO_SAR,
            'total_cost': total_cost_usd * USD_TO_SAR
        }
    
    def print_colored_summary(cost_details):
        """
        Prints The Car's cost in a table.
        """
        console = Console()
        table = Table(title="Car Import Cost Summary", style="bold cyan")

        table.add_column("Item", style="bold white")
        table.add_column("Amount (SAR)", justify="right")

        table.add_row("Base Price SAR", f"[cyan]{cost_details['base_price']:.2f}[/cyan]")
        table.add_row("Shipping SAR", f"[blue]{cost_details['shipping']:.2f}[/blue]")
        table.add_row("Insurance SAR", f"[magenta]{cost_details['insurance']:.2f}[/magenta]")
        table.add_row("Customs SAR", f"[yellow]{cost_details['customs']:.2f}[/yellow]")
        table.add_row("VAT SAR", f"[red]{cost_details['vat']:.2f}[/red]")

        table.add_section()
        table.add_row("TOTAL SAR", f"[bold green]{cost_details['total_cost']:.2f}[/bold green]")

        console.print(table)
