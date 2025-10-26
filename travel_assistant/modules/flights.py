# flights.py — Flight search + table rendering (currency & price selection included)
from __future__ import annotations
import requests
from typing import List, Dict
from rich.table import Table
from rich.console import Console
from rich import box

from modules.amadeus_api import get_access_token

console = Console()


def _get_iata_code(city_name: str) -> str | None:
    """Local mapping for common cities (fast, no API call)."""
    known = {
        "riyadh": "RUH", "jeddah": "JED", "dubai": "DXB", "dammam": "DMM",
        "abha": "AHB", "najran": "EAM", "medina": "MED", "madinah": "MED",
        "makkah": "JED", "mecca": "JED", "doha": "DOH", "amman": "AMM",
        "cairo": "CAI",
    }
    code = known.get(city_name.strip().lower())
    if code:
        console.print(f"[cyan]Using local IATA code for {city_name} → {code}[/cyan]")
    return code


def _choose_currency() -> str:
    console.print("\n[bold]Choose your preferred currency:[/bold]")
    console.print("1) SAR — Saudi Riyal")
    console.print("2) USD — US Dollar")
    choice = input("Enter your choice (1-2): ").strip()
    return {"1": "SAR", "2": "USD"}.get(choice, "USD")


def _choose_price_range() -> str:
    console.print("\n[bold]Choose your preferred price range:[/bold]")
    console.print("1) 💰 Cheap — Budget-friendly")
    console.print("2) 💼 Medium — Balanced")
    console.print("3) 💎 Expensive — Premium")
    console.print("4) 🔄 Any — Show all")
    choice = input("Enter your choice (1-4): ").strip()
    return {"1": "cheap", "2": "medium", "3": "expensive", "4": "any"}.get(choice, "any")


def search_flights(
    origin_city: str,
    destination_city: str,
    date: str,
    passengers: int = 1,
    price_filter: str = "any",
) -> List[Dict]:
    """
    Queries Amadeus for flight offers, prints a Rich table, returns a list of flights.
    If empty, prints a friendly message and returns [].
    """
    token = get_access_token()
    if not token:
        console.print("[red]❌ Failed to get access token.[/red]")
        return []

    origin = origin_city if len(origin_city) == 3 else _get_iata_code(origin_city)
    dest = destination_city if len(destination_city) == 3 else _get_iata_code(destination_city)

    if not origin or not dest:
        console.print("[red]⚠ Invalid origin/destination code or city.[/red]")
        return []

    currency = _choose_currency()
    price_filter = _choose_price_range()

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": dest,
        "departureDate": date,
        "adults": passengers,
        "max": 20,
        "currencyCode": currency,
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=25)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        console.print(f"[red]❌ Network error while searching flights: {e}[/red]")
        return []

    raw_offers = payload.get("data", [])
    if not raw_offers:
        console.print("[yellow]⚠ No flights found for your search.[/yellow]")
        return []

    carriers_dict = payload.get("dictionaries", {}).get("carriers", {})
    flights: List[Dict] = []

    for offer in raw_offers:
        try:
            price = float(offer["price"]["total"])
            curr = offer["price"]["currency"]
            itin = offer["itineraries"][0]
            seg0 = itin["segments"][0]
            carrier = seg0["carrierCode"]
            flight_no = seg0["number"]
            dep = seg0["departure"]["at"]
            arr = seg0["arrival"]["at"]
            duration = itin.get("duration", "N/A").replace("PT", "").lower()
            seats = offer.get("numberOfBookableSeats", "N/A")
            flights.append({
                "flight_number": f"{carrier}{flight_no}",
                "airline": carriers_dict.get(carrier, carrier),
                "price": price,
                "currency": curr,
                "from": origin,
                "to": dest,
                "departure": dep,
                "arrival": arr,
                "duration": duration,
                "seats": seats,
            })
        except Exception:
            continue

    if not flights:
        console.print("[yellow]⚠ No flights could be parsed. Try again later.[/yellow]")
        return []

    # price band filter
    prices = [f["price"] for f in flights]
    avg = sum(prices) / len(prices) if prices else 0
    if price_filter == "cheap":
        flights = [f for f in flights if f["price"] <= avg * 0.8]
    elif price_filter == "medium":
        flights = [f for f in flights if avg * 0.8 < f["price"] < avg * 1.2]
    elif price_filter == "expensive":
        flights = [f for f in flights if f["price"] >= avg * 1.2]

    if not flights:
        console.print("[yellow]⚠ No flights match this price range. Returning to previous menu...[/yellow]")
        return []

    flights.sort(key=lambda x: x["price"])

    table = Table(
        title=f"🛫 Available Flights (Currency: {currency})",
        show_lines=True, header_style="bold magenta", box=box.ROUNDED
    )
    table.add_column("#", justify="center", style="bold yellow")
    table.add_column("Airline", style="cyan")
    table.add_column("Flight No", justify="center")
    table.add_column("From → To", justify="center")
    table.add_column("Departure", justify="center", style="green")
    table.add_column("Arrival", justify="center", style="red")
    table.add_column("Duration", justify="center")
    table.add_column("Seats", justify="center")
    table.add_column("Price", justify="right", style="bold")

    for i, f in enumerate(flights, 1):
        dep = f["departure"].split("T")[1] if "T" in f["departure"] else f["departure"]
        arr = f["arrival"].split("T")[1] if "T" in f["arrival"] else f["arrival"]
        table.add_row(
            str(i),
            f["airline"],
            f["flight_number"],
            f"{f['from']} → {f['to']}",
            dep,
            arr,
            f["duration"],
            str(f["seats"]),
            f"{f['price']} {f['currency']}",
        )

    console.print("\n")
    console.print(table)
    return flights