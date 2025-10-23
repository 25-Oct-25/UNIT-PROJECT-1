import time
import itertools
import threading
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import box
from colorama import init

from modules.auth import register, login
from modules.flights import search_flights
from modules.hotels import search_hotels
from modules.bookings import (
    add_flight_booking,
    add_hotel_booking,
    view_user_bookings,
    view_all_bookings,
)

init(autoreset=True)
console = Console()

def show_banner() -> None:
    console.clear()
    console.print("[bold magenta]\n✈  TRAVEL ASSISTANT SYSTEM[/bold magenta]")
    console.rule("[cyan]Your Smart Travel Management Tool[/cyan]\n")

def short_spinner(text: str = "Working...", seconds: float = 1.8) -> None:
    stop = False
    spinner = itertools.cycle(["|", "/", "-", "\\"])

    def run():
        while not stop:
            console.print(f"[cyan]{next(spinner)}[/cyan] {text}", end="\r")
            time.sleep(0.1)

    t = threading.Thread(target=run, daemon=True)
    t.start()
    time.sleep(seconds)
    stop = True
    time.sleep(0.05)
    console.print(" " * 60, end="\r")

def main_menu() -> None:
    show_banner()
    while True:
        table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED)
        table.add_column("Option", style="bold yellow", justify="center")
        table.add_column("Action", style="white")
        table.add_row("1", "🔐 Login")
        table.add_row("2", "🧾 Register")
        table.add_row("3", "🚪 Exit")

        console.print(table)
        choice = input("\nChoose an option (1-3): ").strip()

        if choice == "1":
            user = login()
            if user:
                user_menu(user)
                show_banner()
        elif choice == "2":
            register()
        elif choice == "3":
            console.print("[bold red]Goodbye! See you next trip ✈[/bold red]")
            break
        else:
            console.print("[red]Invalid option. Please enter 1, 2, or 3.[/red]")

def user_menu(user: dict) -> None:
    while True:
        console.clear()
        console.rule(f"[bold green]Welcome, {user['username']}![/bold green]")

        table = Table(show_header=True, header_style="bold blue", box=box.SIMPLE_HEAVY)
        table.add_column("Option", style="bold yellow", justify="center")
        table.add_column("Action", style="white")
        table.add_row("1", "✈ Search for Flights")
        table.add_row("2", "🏨 Search for Hotels")
        table.add_row("3", "🧾 View My Flight Bookings")
        table.add_row("4", "🧳 View My Hotel Bookings")
        if user.get("role") == "admin":
            table.add_row("5", "📋 View All Bookings (Admin)")
            table.add_row("6", "🚪 Logout")
        else:
            table.add_row("5", "🚪 Logout")

        console.print(table)
        choice = input("\nChoose an option: ").strip()

        if choice == "1":
            origin = input("Enter Departure city or airport code: ").strip()
            dest = input("Enter destination city or airport code: ").strip()
            date = input("Enter departure date (YYYY-MM-DD): ").strip()
            pax = input("Enter number of passengers: ").strip()
            passengers = int(pax) if pax.isdigit() else 1

            console.print("\n[cyan]Searching for available flights...[/cyan]")
            short_spinner("Searching flights...")
            flights = search_flights(origin, dest, date, passengers)

            if not flights:
                console.print("[yellow]⚠ No flights found. Returning to previous menu...[/yellow]")
                time.sleep(1.2)
                continue

            selection = input("\nEnter the row number to book or press Enter to cancel: ").strip()
            if not selection.isdigit():
                console.print("[cyan]No flight selected. Back to menu.[/cyan]")
                time.sleep(0.8)
                continue

            idx = int(selection)
            if idx < 1 or idx > len(flights):
                console.print("[red]Invalid selection. Back to menu.[/red]")
                time.sleep(0.8)
                continue

            chosen = flights[idx-1]
            console.print("\n[bold cyan]Booking Summary[/bold cyan]:")
            console.print(f"✈ Flight: {chosen['flight_number']} | Airline: {chosen['airline']}")
            console.print(f"📍 From: {chosen['from']} → {chosen['to']}")
            console.print(f"🕓 Departure: {chosen['departure']} | Arrival: {chosen['arrival']}")
            console.print(f"⏱ Duration: {chosen['duration']} | 💰 Price: {chosen['price']} {chosen['currency']}")
            confirm = input("\nConfirm booking? (y/n): ").strip().lower()
            if confirm == "y":
                add_flight_booking(user["username"], chosen)
                console.print("[green]✅ Your flight has been booked successfully![/green]")
            else:
                console.print("[red]❌ Booking canceled.[/red]")
            input("\nPress Enter to continue...")

        elif choice == "2":
            city = input("Enter city name: ").strip()
            check_in = input("Enter check-in date (YYYY-MM-DD): ").strip()
            check_out = input("Enter check-out date (YYYY-MM-DD): ").strip()
            adults_str = input("Number of adults: ").strip()
            adults = int(adults_str) if adults_str.isdigit() else 1

            console.print("\n[magenta]Searching for hotel offers...[/magenta]")
            short_spinner("Searching hotels...")
            hotels = search_hotels(city, check_in, check_out, adults)

            if not hotels:
                console.print("[yellow]⚠ No hotels found. Returning to previous menu...[/yellow]")
                time.sleep(1.2)
                continue

            selection = input("\nEnter the row number to book or press Enter to cancel: ").strip()
            if not selection.isdigit():
                console.print("[cyan]No hotel selected. Back to menu.[/cyan]")
                time.sleep(0.8)
                continue

            idx = int(selection)
            if idx < 1 or idx > len(hotels):
                console.print("[red]Invalid selection. Back to menu.[/red]")
                time.sleep(0.8)
                continue

            chosen = hotels[idx-1]
            console.print("\n[bold cyan]Booking Summary[/bold cyan]:")
            console.print(f"🏨 Hotel: {chosen['name']} ")
            console.print(f"🗓 Stay: {chosen['check_in']} → {chosen['check_out']}")
            console.print(f"💰 Price: {chosen['price']} {chosen['currency']} | ⭐ Rating: {chosen['rating']}")
            confirm = input("\nConfirm booking? (y/n): ").strip().lower()
            if confirm == "y":
                add_hotel_booking(user["username"], chosen)
                console.print("[green]✅ Your hotel has been booked successfully![/green]")
            else:
                console.print("[red]❌ Booking canceled.[/red]")
            input("\nPress Enter to continue...")

        elif choice == "3":
            view_user_bookings(user["username"], "flight")
            input("\nPress Enter to continue...")

        elif choice == "4":
            view_user_bookings(user["username"], "hotel")
            input("\nPress Enter to continue...")

        elif choice == "5" and user.get("role") == "admin":
            view_all_bookings()
            input("\nPress Enter to continue...")

        elif (choice == "5" and user.get("role") != "admin") or (choice == "6" and user.get("role") == "admin"):
            console.print("[bold red]Logged out successfully.[/bold red]")
            break
        else:
            console.print("[red]Invalid option. Please try again.[/red]")

if __name__ == "__main__":
    main_menu()