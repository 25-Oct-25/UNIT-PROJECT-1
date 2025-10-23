# bookings.py — Save/view bookings with rich tables (flights & hotels)
from __future__ import annotations
import json
import os
from datetime import datetime
from typing import List, Dict
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "bookings.json")


def load_bookings() -> List[Dict]:
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        content = f.read().strip()
        return json.loads(content) if content else []


def save_bookings(bookings: List[Dict]) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(bookings, f, indent=4)


def add_flight_booking(username: str, flight: Dict) -> None:
    bookings = load_bookings()
    booking = {
        "username": username,
        "type": "flight",
        "flight_number": flight.get("flight_number"),
        "airline": flight.get("airline"),
        "from": flight.get("from"),
        "to": flight.get("to"),
        "departure": flight.get("departure"),
        "arrival": flight.get("arrival"),
        "price": flight.get("price"),
        "currency": flight.get("currency", "USD"),
        "duration": flight.get("duration"),
        "date_booked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    bookings.append(booking)
    save_bookings(bookings)
    console.print("[green]✅ Flight booking saved successfully![/green]")


def add_hotel_booking(username: str, hotel: Dict) -> None:
    bookings = load_bookings()
    booking = {
        "username": username,
        "type": "hotel",
        "name": hotel.get("name"),
        "room": hotel.get("room"),
        "price": hotel.get("price"),
        "currency": hotel.get("currency", "USD"),
        "check_in": hotel.get("check_in"),
        "check_out": hotel.get("check_out"),
        "rating": hotel.get("rating", "N/A"),
        "date_booked": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    bookings.append(booking)
    save_bookings(bookings)
    console.print("[green]✅ Hotel booking saved successfully![/green]")


def view_user_bookings(username: str, booking_type: str | None = None) -> None:
    bookings = load_bookings()
    user_bookings = [b for b in bookings if b.get("username") == username]
    if booking_type:
        user_bookings = [b for b in user_bookings if b.get("type") == booking_type]

    if not user_bookings:
        console.print(f"[yellow]⚠ No {booking_type or ''} bookings found for {username}. Returning to previous menu...[/yellow]")
        return

    title = f"{username}'s {booking_type.capitalize()} Bookings" if booking_type else f"{username}'s Bookings"
    table = Table(title=f"📋 {title}", show_lines=True, header_style="bold magenta", box=box.ROUNDED)

    if booking_type == "flight":
        table.add_column("#")
        table.add_column("From → To")
        table.add_column("Airline")
        table.add_column("Flight No")
        table.add_column("Departure")
        table.add_column("Arrival")
        table.add_column("Price", justify="right")
        table.add_column("Booked At")

        for i, b in enumerate(user_bookings, 1):
            table.add_row(
                str(i),
                f"{b.get('from','?')} → {b.get('to','?')}",
                b.get("airline", "N/A"),
                b.get("flight_number", "N/A"),
                b.get("departure", "N/A"),
                b.get("arrival", "N/A"),
                f"{b.get('price','N/A')} {b.get('currency','')}",
                b.get("date_booked", "N/A"),
            )

    elif booking_type == "hotel":
        table.add_column("#")
        table.add_column("Hotel")
        table.add_column("Room")
        table.add_column("Price", justify="right")
        table.add_column("Currency")
        table.add_column("Check-in")
        table.add_column("Check-out")
        table.add_column("Booked At")

        for i, b in enumerate(user_bookings, 1):
            table.add_row(
                str(i),
                b.get("name", "N/A"),
                b.get("room", "N/A"),
                str(b.get("price", "N/A")),
                b.get("currency", "N/A"),
                b.get("check_in", "N/A"),
                b.get("check_out", "N/A"),
                b.get("date_booked", "N/A"),
            )

    else:
        table.add_column("#")
        table.add_column("Type")
        table.add_column("Details")
        table.add_column("Price", justify="right")
        table.add_column("Booked At")

        for i, b in enumerate(user_bookings, 1):
            if b.get("type") == "flight":
                details = f"{b.get('from','?')} → {b.get('to','?')} | {b.get('airline','N/A')} {b.get('flight_number','')}"
                price = f"{b.get('price','N/A')} {b.get('currency','')}"
                table.add_row(str(i), "Flight", details, price, b.get("date_booked", "N/A"))
            elif b.get("type") == "hotel":
                details = f"{b.get('name','N/A')} | Room: {b.get('room','N/A')} | {b.get('check_in','?')} → {b.get('check_out','?')}"
                price = f"{b.get('price','N/A')} {b.get('currency','')}"
                table.add_row(str(i), "Hotel", details, price, b.get("date_booked", "N/A"))

    console.print("\n")
    console.print(table)


def view_all_bookings() -> None:
    bookings = load_bookings()
    if not bookings:
        console.print("[yellow]⚠ No bookings in the system yet. Returning to previous menu...[/yellow]")
        return

    table = Table(title="📋 All Bookings (Admin)", show_lines=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("#")
    table.add_column("User")
    table.add_column("Type")
    table.add_column("Details")
    table.add_column("Price", justify="right")
    table.add_column("Booked At")

    for i, b in enumerate(bookings, 1):
        btype = b.get("type", "flight")
        if btype == "flight":
            details = f"{b.get('from','?')} → {b.get('to','?')} | {b.get('airline','N/A')} {b.get('flight_number','')}"
            price = f"{b.get('price','N/A')} {b.get('currency','')}"
        elif btype == "hotel":
            details = f"{b.get('name','N/A')} | Room: {b.get('room','N/A')} | {b.get('check_in','?')} → {b.get('check_out','?')}"
            price = f"{b.get('price','N/A')} {b.get('currency','')}"
        else:
            details = "Unknown"
            price = "N/A"

        table.add_row(
            str(i),
            b.get("username", "N/A"),
            btype.capitalize(),
            details,
            price,
            b.get("date_booked", "N/A"),
        )

    console.print("\n")
    console.print(table)