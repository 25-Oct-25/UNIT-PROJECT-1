from rich.console import Console
from rich.table import Table

console = Console()

def add_to_cart(cart, service):
    cart.append(service)
    console.print(f"[green]✅ Added to cart:[/green] {service['service'].replace('_',' ').title()}")

def show_cart(cart):
    if not cart:
        console.print("[red]🛍️ Your cart is empty![/red]")
        return 0 
# طريقة عرض الجدول
    table = Table(title="🛒 Your Cart", show_lines=True)
    table.add_column("Service", style="cyan")
    table.add_column("Base Price (SAR)", style="green")
    table.add_column("Discount", style="yellow")
    table.add_column("Final Price (SAR)", style="magenta")

    total = 0
    for item in cart:
        table.add_row(
            item['service'].replace('_',' ').title(),
            str(item['price']),
            str(item['discount']),
            str(item['final_price'])
        )
        total += item['final_price']

    table.add_row("[bold]Total[/bold]", "", "", f"[bold green]{total}[/bold green]")
    console.print(table)
    return total

def clear_cart(cart):
    cart.clear()
    console.print("[blue]🧹 Cart cleared![/blue]")
