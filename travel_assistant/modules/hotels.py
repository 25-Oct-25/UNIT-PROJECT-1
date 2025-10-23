# modules/hotels.py
# modules/hotels.py
from __future__ import annotations
import datetime as dt
from typing import List, Dict, Tuple
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

# -----------------------------
# Currency conversion (static)
# -----------------------------
CURRENCY_RATES = {
    "USD": 1.00,
    "SAR": 3.75,
    "EUR": 0.92,
}

# -----------------------------
# Helper: validate dates
# -----------------------------
def _validate_dates(check_in: str, check_out: str) -> Tuple[bool, str]:
    """Return (is_valid, message). Dates must be >= today and check_out > check_in."""
    try:
        ci = dt.date.fromisoformat(check_in)
        co = dt.date.fromisoformat(check_out)
    except ValueError:
        return False, "Invalid date format. Use YYYY-MM-DD."

    today = dt.date.today()
    if ci < today:
        return False, "Check-in date is in the past. Please choose a future date."
    if co <= ci:
        return False, "Check-out must be after check-in."
    return True, ""

# -----------------------------
# Helper: choose currency
# -----------------------------
def _choose_currency() -> str:
    console.print("\n[bold cyan]Choose your preferred currency:[/bold cyan]")
    console.print("1) SAR — Saudi Riyal")
    console.print("2) USD — US Dollar")
    console.print("3) EUR — Euro")
    choice = input("Enter your choice (1-3): ").strip()
    return {"1": "SAR", "2": "USD", "3": "EUR"}.get(choice, "USD")

# -----------------------------
# Helper: choose price tier
# -----------------------------
def _choose_price_range() -> str:
    console.print("\n[bold cyan]Choose your preferred price range:[/bold cyan]")
    console.print("1) 💰 Cheap — Budget-friendly")
    console.print("2) 💼 Medium — Balanced comfort")
    console.print("3) 💎 Expensive — Premium experience")
    console.print("4) 🔄 Any — Show all options")
    choice = input("Enter your choice (1-4): ").strip()
    return {"1": "cheap", "2": "medium", "3": "expensive", "4": "any"}.get(choice, "any")

# -----------------------------
# Star visualization
# -----------------------------
def _stars(r: float | int | None) -> str:
    if r is None:
        return "N/A"
    try:
        v = max(0.0, min(5.0, float(r)))
    except Exception:
        return "N/A"
    full = int(round(v))
    return "★" * full + "☆" * (5 - full)

HOTEL_DB: Dict[str, List[Dict]] = {
    # --------- Saudi Arabia ---------
    "riyadh": [
        # cheap
        {"name": "Ibis Riyadh Olaya Street", "category": "cheap", "usd": 70, "rating": 4.0, "address": "Olaya St"},
        {"name": "Holiday Inn Riyadh Al Qasr", "category": "cheap", "usd": 85, "rating": 4.1, "address": "Olaya"},
        {"name": "Centro Waha by Rotana", "category": "cheap", "usd": 90, "rating": 4.2, "address": "Northern Ring Rd"},
        # medium
        {"name": "Crowne Plaza Riyadh RDC", "category": "medium", "usd": 150, "rating": 4.5, "address": "Imam Saud Rd"},
        {"name": "Radisson Blu Hotel, Riyadh", "category": "medium", "usd": 135, "rating": 4.4, "address": "King Abdul Aziz Rd"},
        {"name": "Hyatt Place Riyadh Sulaimania", "category": "medium", "usd": 140, "rating": 4.4, "address": "Sulaimania"},
        # expensive
        {"name": "Hyatt Regency Riyadh Olaya", "category": "expensive", "usd": 240, "rating": 4.6, "address": "Olaya"},
        {"name": "Ritz-Carlton Riyadh", "category": "expensive", "usd": 390, "rating": 4.7, "address": "Makkah Rd"},
        {"name": "Fairmont Ramla Serviced Residences", "category": "expensive", "usd": 300, "rating": 4.6, "address": "King Fahd Rd"},
    ],
    "jeddah": [
        {"name": "Ibis Jeddah City Center", "category": "cheap", "usd": 65, "rating": 4.1, "address": "Madinah Rd"},
        {"name": "Holiday Inn Jeddah Al Salam", "category": "cheap", "usd": 80, "rating": 4.0, "address": "King Khalid Rd"},
        {"name": "Rove Jeddah", "category": "cheap", "usd": 75, "rating": 4.1, "address": "Prince Mohammed Bin Abdulaziz St"},
        {"name": "Radisson Blu Plaza Jeddah", "category": "medium", "usd": 120, "rating": 4.3, "address": "King Abdullah Rd"},
        {"name": "Novotel Jeddah Tahlia", "category": "medium", "usd": 130, "rating": 4.3, "address": "Tahlia St"},
        {"name": "Centro Shaheen by Rotana", "category": "medium", "usd": 125, "rating": 4.4, "address": "Al Madinah Rd"},
        {"name": "Rosewood Jeddah", "category": "expensive", "usd": 350, "rating": 4.6, "address": "Corniche Rd"},
        {"name": "Jeddah Hilton", "category": "expensive", "usd": 280, "rating": 4.5, "address": "North Corniche"},
        {"name": "The Venue Jeddah Corniche", "category": "expensive", "usd": 260, "rating": 4.5, "address": "Corniche"},
    ],
    "makkah": [
        {"name": "Ibis Styles Makkah", "category": "cheap", "usd": 55, "rating": 4.0, "address": "King Fahd Rd"},
        {"name": "Emaar Al Khlil Hotel", "category": "cheap", "usd": 60, "rating": 3.9, "address": "Ajyad"},
        {"name": "Makarem Al Shorofat", "category": "cheap", "usd": 75, "rating": 4.1, "address": "Ajyad"},
        {"name": "Hilton Suites Makkah", "category": "medium", "usd": 180, "rating": 4.6, "address": "Jabal Omar"},
        {"name": "Makkah Hotel", "category": "medium", "usd": 170, "rating": 4.5, "address": "Ibrahim Al Khalil St"},
        {"name": "Swissôtel Makkah", "category": "medium", "usd": 190, "rating": 4.6, "address": "Jabal Omar"},
        {"name": "Fairmont Makkah Clock Royal Tower", "category": "expensive", "usd": 260, "rating": 4.6, "address": "Abraj Al Bait"},
        {"name": "Jabal Omar Hyatt Regency Makkah", "category": "expensive", "usd": 240, "rating": 4.6, "address": "Jabal Omar"},
        {"name": "Raffles Makkah Palace", "category": "expensive", "usd": 420, "rating": 4.8, "address": "Abraj Al Bait"},
    ],
    "madinah": [
        {"name": "Emaar Taiba", "category": "cheap", "usd": 65, "rating": 4.1, "address": "Central Area"},
        {"name": "Dar Al Shohadaa Hotel", "category": "cheap", "usd": 60, "rating": 4.0, "address": "Central Area"},
        {"name": "Al Eiman Taibah", "category": "cheap", "usd": 70, "rating": 4.0, "address": "Central Area"},
        {"name": "Anwar Al Madinah Mövenpick", "category": "medium", "usd": 140, "rating": 4.4, "address": "Central Area"},
        {"name": "Shaza Al Madina", "category": "medium", "usd": 160, "rating": 4.5, "address": "King Fahd Rd"},
        {"name": "Madinah Hilton", "category": "medium", "usd": 170, "rating": 4.5, "address": "Central Area"},
        {"name": "InterContinental Dar Al Iman", "category": "expensive", "usd": 240, "rating": 4.6, "address": "Central Area"},
        {"name": "The Oberoi Madina", "category": "expensive", "usd": 340, "rating": 4.8, "address": "Central Area"},
        {"name": "Crowne Plaza Madinah", "category": "expensive", "usd": 230, "rating": 4.5, "address": "Central Area"},
    ],
    "dammam": [
        {"name": "Ibis Dammam", "category": "cheap", "usd": 55, "rating": 3.9, "address": "King Fahd Rd"},
        {"name": "Tulip Inn Suites", "category": "cheap", "usd": 60, "rating": 4.0, "address": "21st St"},
        {"name": "Watheer Hotel Suite", "category": "cheap", "usd": 65, "rating": 4.0, "address": "Prince Mishal St"},
        {"name": "Novotel Dammam Business Park", "category": "medium", "usd": 110, "rating": 4.3, "address": "King Fahd Rd"},
        {"name": "Park Inn by Radisson Dammam", "category": "medium", "usd": 105, "rating": 4.3, "address": "King Abdullah Bin Abdulaziz Rd"},
        {"name": "Wyndham Garden Dammam", "category": "medium", "usd": 115, "rating": 4.4, "address": "21st St"},
        {"name": "Sheraton Dammam Hotel & Convention Centre", "category": "expensive", "usd": 170, "rating": 4.4, "address": "Prince Mohammed St"},
        {"name": "Braira Dammam Hotel", "category": "expensive", "usd": 160, "rating": 4.4, "address": "King Saud Rd"},
        {"name": "Swiss International Al Hamra", "category": "expensive", "usd": 150, "rating": 4.3, "address": "King Khaled St"},
    ],
    "abha": [
        {"name": "Ibis Styles Abha", "category": "cheap", "usd": 60, "rating": 4.0, "address": "Airport Rd"},
        {"name": "Al Reef Homes Hotel", "category": "cheap", "usd": 55, "rating": 3.9, "address": "Abha"},
        {"name": "Blue Inn Boutique", "category": "cheap", "usd": 75, "rating": 4.2, "address": "Al Soudah Rd"},
        {"name": "Abha Palace Hotel", "category": "medium", "usd": 120, "rating": 4.3, "address": "New Abha"},
        {"name": "OYO 315 Ramz Abha Hotel", "category": "medium", "usd": 95, "rating": 4.0, "address": "Abha"},
        {"name": "Golden Alandalus Hotel", "category": "medium", "usd": 110, "rating": 4.1, "address": "Al Aziziyah"},
        {"name": "Blue Diamond Hotel Abha", "category": "expensive", "usd": 160, "rating": 4.4, "address": "Abha"},
        {"name": "Dar Telal Hotel Suites", "category": "expensive", "usd": 150, "rating": 4.3, "address": "Abha"},
        {"name": "Al Reef Hotel Suites", "category": "expensive", "usd": 170, "rating": 4.4, "address": "Abha"},
    ],
    "alula": [
        {"name": "Gathern AlUla Stays (Budget)", "category": "cheap", "usd": 80, "rating": 4.2, "address": "AlUla"},
        {"name": "Shaden Desert Resort (Std Rooms)", "category": "cheap", "usd": 95, "rating": 4.3, "address": "Hegra Rd"},
        {"name": "Sahary Al Ula Resort (Std)", "category": "cheap", "usd": 90, "rating": 4.1, "address": "AlUla"},
        {"name": "Cloud7 Residence AlUla", "category": "medium", "usd": 160, "rating": 4.4, "address": "City Center"},
        {"name": "Habitas AlUla (Entry Cat.)", "category": "medium", "usd": 220, "rating": 4.6, "address": "Ashar Valley"},
        {"name": "Caravan by Habitas", "category": "medium", "usd": 180, "rating": 4.4, "address": "Ashar Valley"},
        {"name": "Banyan Tree AlUla", "category": "expensive", "usd": 700, "rating": 4.7, "address": "Ashar Valley"},
        {"name": "Shaden Resort (Villas)", "category": "expensive", "usd": 350, "rating": 4.5, "address": "Hegra Rd"},
        {"name": "Habitas AlUla (Canyon)", "category": "expensive", "usd": 500, "rating": 4.7, "address": "Ashar Valley"},
    ],
    # --------- International ---------
    "dubai": [
        {"name": "Rove Downtown", "category": "cheap", "usd": 85, "rating": 4.6, "address": "Downtown Dubai"},
        {"name": "Ibis One Central", "category": "cheap", "usd": 65, "rating": 4.2, "address": "Trade Centre"},
        {"name": "Citymax Hotel Bur Dubai", "category": "cheap", "usd": 55, "rating": 4.0, "address": "Kuwait St"},
        {"name": "Hilton Garden Inn Mall of the Emirates", "category": "medium", "usd": 120, "rating": 4.5, "address": "Al Barsha"},
        {"name": "Millennium Place Marina", "category": "medium", "usd": 150, "rating": 4.6, "address": "Dubai Marina"},
        {"name": "Novotel World Trade Centre", "category": "medium", "usd": 110, "rating": 4.3, "address": "Trade Centre"},
        {"name": "Atlantis The Palm", "category": "expensive", "usd": 420, "rating": 4.7, "address": "The Palm Jumeirah"},
        {"name": "Jumeirah Al Naseem", "category": "expensive", "usd": 520, "rating": 4.8, "address": "Madinat Jumeirah"},
        {"name": "Address Downtown", "category": "expensive", "usd": 480, "rating": 4.7, "address": "Downtown Dubai"},
    ],
    "doha": [
        {"name": "Ibis Doha", "category": "cheap", "usd": 60, "rating": 4.1, "address": "West Bay"},
        {"name": "Holiday Inn Doha - The Business Park", "category": "cheap", "usd": 75, "rating": 4.4, "address": "Najma"},
        {"name": "La Villa Hotel", "category": "cheap", "usd": 50, "rating": 3.9, "address": "Al Asmakh St"},
        {"name": "Hilton Doha", "category": "medium", "usd": 160, "rating": 4.5, "address": "Diplomatic District"},
        {"name": "Marriott Marquis City Center", "category": "medium", "usd": 150, "rating": 4.5, "address": "West Bay"},
        {"name": "Pullman Doha West Bay", "category": "medium", "usd": 140, "rating": 4.5, "address": "West Bay"},
        {"name": "Mandarin Oriental, Doha", "category": "expensive", "usd": 520, "rating": 4.9, "address": "Msheireb Downtown"},
        {"name": "W Doha", "category": "expensive", "usd": 300, "rating": 4.6, "address": "West Bay"},
        {"name": "The Ritz-Carlton, Doha", "category": "expensive", "usd": 350, "rating": 4.7, "address": "West Bay Lagoon"},
    ],
    "cairo": [
        {"name": "Steigenberger Hotel Cairo Pyramids (Std)", "category": "cheap", "usd": 70, "rating": 4.3, "address": "Giza"},
        {"name": "Pyramids Park Resort", "category": "cheap", "usd": 60, "rating": 4.0, "address": "Giza"},
        {"name": "Cairo Paradise Hotel", "category": "cheap", "usd": 45, "rating": 3.9, "address": "Downtown"},
        {"name": "Novotel Cairo El Borg", "category": "medium", "usd": 110, "rating": 4.4, "address": "Zamalek"},
        {"name": "Hilton Cairo Zamalek Residences", "category": "medium", "usd": 130, "rating": 4.4, "address": "Zamalek"},
        {"name": "Holiday Inn Cairo Maadi", "category": "medium", "usd": 120, "rating": 4.3, "address": "Maadi"},
        {"name": "Four Seasons Cairo at Nile Plaza", "category": "expensive", "usd": 380, "rating": 4.8, "address": "Garden City"},
        {"name": "The St. Regis Cairo", "category": "expensive", "usd": 420, "rating": 4.8, "address": "Corniche El Nil"},
        {"name": "Fairmont Nile City", "category": "expensive", "usd": 260, "rating": 4.6, "address": "Nile City Towers"},
    ],
    "amman": [
        {"name": "The House Boutique Suites (Std)", "category": "cheap", "usd": 85, "rating": 4.6, "address": "3rd Circle"},
        {"name": "Amman International Hotel (Std)", "category": "cheap", "usd": 75, "rating": 4.5, "address": "University Rd"},
        {"name": "Landmark Amman (Entry)", "category": "cheap", "usd": 90, "rating": 4.4, "address": "Al Hussein Bin Ali St"},
        {"name": "Crowne Plaza Amman", "category": "medium", "usd": 130, "rating": 4.4, "address": "6th Circle"},
        {"name": "InterContinental Amman (Std)", "category": "medium", "usd": 150, "rating": 4.6, "address": "2nd Circle"},
        {"name": "Amman Rotana (Std)", "category": "medium", "usd": 140, "rating": 4.5, "address": "Abdali"},
        {"name": "Four Seasons Hotel Amman", "category": "expensive", "usd": 350, "rating": 4.8, "address": "5th Circle"},
        {"name": "The St. Regis Amman", "category": "expensive", "usd": 320, "rating": 4.7, "address": "Abdoun"},
        {"name": "W Amman", "category": "expensive", "usd": 260, "rating": 4.6, "address": "Abdali"},
    ],
    "paris": [
        {"name": "ibis Paris Montmartre 18ème", "category": "cheap", "usd": 95, "rating": 4.2, "address": "Boulevard de Clichy"},
        {"name": "Libertel Canal Saint-Martin", "category": "cheap", "usd": 90, "rating": 4.2, "address": "Rue du Château Landon"},
        {"name": "Hotel Darcet", "category": "cheap", "usd": 110, "rating": 4.6, "address": "Rue Darcet"},
        {"name": "Citadines Les Halles Paris", "category": "medium", "usd": 180, "rating": 4.4, "address": "Rue des Lombards"},
        {"name": "Novotel Paris Centre Tour Eiffel", "category": "medium", "usd": 190, "rating": 4.2, "address": "Quai de Grenelle"},
        {"name": "Pullman Paris Tour Eiffel (Std)", "category": "medium", "usd": 220, "rating": 4.5, "address": "Avenue de Suffren"},
        {"name": "Le Bristol Paris", "category": "expensive", "usd": 800, "rating": 4.9, "address": "Rue du Faubourg Saint-Honoré"},
        {"name": "Four Seasons Hotel George V", "category": "expensive", "usd": 1200, "rating": 4.9, "address": "Avenue George V"},
        {"name": "Shangri-La Paris", "category": "expensive", "usd": 950, "rating": 4.8, "address": "Avenue d'Iéna"},
    ],
    "london": [
        {"name": "Zedwell Piccadilly Circus", "category": "cheap", "usd": 120, "rating": 4.2, "address": "Piccadilly"},
        {"name": "Point A Hotel London Kings Cross", "category": "cheap", "usd": 110, "rating": 4.1, "address": "Kings Cross"},
        {"name": "ibis London Blackfriars", "category": "cheap", "usd": 115, "rating": 4.3, "address": "Blackfriars"},
        {"name": "Novotel London Canary Wharf", "category": "medium", "usd": 190, "rating": 4.5, "address": "Canary Wharf"},
        {"name": "Hilton London Tower Bridge", "category": "medium", "usd": 220, "rating": 4.6, "address": "Tooley St"},
        {"name": "The Westminster London, Curio Collection", "category": "medium", "usd": 210, "rating": 4.5, "address": "Westminster"},
        {"name": "The Langham London", "category": "expensive", "usd": 520, "rating": 4.8, "address": "Regent St"},
        {"name": "The Savoy", "category": "expensive", "usd": 650, "rating": 4.8, "address": "Strand"},
        {"name": "Four Seasons Hotel London at Park Lane", "category": "expensive", "usd": 800, "rating": 4.8, "address": "Park Lane"},
    ],
    "new york": [
        {"name": "Pod 39", "category": "cheap", "usd": 120, "rating": 4.2, "address": "E 39th St"},
        {"name": "The Jane Hotel", "category": "cheap", "usd": 130, "rating": 4.1, "address": "Jane St"},
        {"name": "Moxy NYC Times Square (Entry)", "category": "cheap", "usd": 140, "rating": 4.3, "address": "7th Ave"},
        {"name": "The Row NYC (Std)", "category": "medium", "usd": 180, "rating": 4.0, "address": "8th Ave"},
        {"name": "Arlo NoMad", "category": "medium", "usd": 220, "rating": 4.4, "address": "E 31st St"},
        {"name": "Hilton Garden Inn Central Park South", "category": "medium", "usd": 230, "rating": 4.4, "address": "W 54th St"},
        {"name": "The Plaza", "category": "expensive", "usd": 750, "rating": 4.7, "address": "5th Ave"},
        {"name": "Four Seasons Hotel New York Downtown", "category": "expensive", "usd": 800, "rating": 4.7, "address": "Barclay St"},
        {"name": "The St. Regis New York", "category": "expensive", "usd": 950, "rating": 4.8, "address": "2 E 55th St"},
    ],
    "tokyo": [
        {"name": "APA Hotel Shinjuku Gyoemmae", "category": "cheap", "usd": 80, "rating": 4.1, "address": "Shinjuku"},
        {"name": "Sotetsu Fresa Inn Ginza-Nanachome", "category": "cheap", "usd": 85, "rating": 4.3, "address": "Ginza"},
        {"name": "Hotel Mystays Asakusa", "category": "cheap", "usd": 70, "rating": 4.0, "address": "Asakusa"},
        {"name": "Hotel Niwa Tokyo", "category": "medium", "usd": 150, "rating": 4.6, "address": "Chiyoda"},
        {"name": "Mitsui Garden Hotel Ginza", "category": "medium", "usd": 160, "rating": 4.5, "address": "Ginza"},
        {"name": "Shibuya Excel Hotel Tokyu", "category": "medium", "usd": 170, "rating": 4.4, "address": "Shibuya"},
        {"name": "Andaz Tokyo Toranomon Hills", "category": "expensive", "usd": 520, "rating": 4.7, "address": "Toranomon"},
        {"name": "The Peninsula Tokyo", "category": "expensive", "usd": 680, "rating": 4.8, "address": "Marunouchi"},
        {"name": "Mandarin Oriental Tokyo", "category": "expensive", "usd": 760, "rating": 4.9, "address": "Nihonbashi"},
    ],
    "kuala lumpur": [
        {"name": "citizenM Kuala Lumpur Bukit Bintang", "category": "cheap", "usd": 55, "rating": 4.6, "address": "Bukit Bintang"},
        {"name": "Travelodge Bukit Bintang", "category": "cheap", "usd": 40, "rating": 4.1, "address": "Bukit Bintang"},
        {"name": "Hotel Capitol Kuala Lumpur", "category": "cheap", "usd": 38, "rating": 4.0, "address": "Bukit Bintang"},
        {"name": "Parkroyal Collection Kuala Lumpur (Std)", "category": "medium", "usd": 95, "rating": 4.5, "address": "Jalan Sultan Ismail"},
        {"name": "Hilton Kuala Lumpur (Std)", "category": "medium", "usd": 110, "rating": 4.7, "address": "KL Sentral"},
        {"name": "Traders Hotel Kuala Lumpur", "category": "medium", "usd": 120, "rating": 4.6, "address": "KLCC"},
        {"name": "Four Seasons Hotel Kuala Lumpur", "category": "expensive", "usd": 260, "rating": 4.7, "address": "KLCC"},
        {"name": "W Kuala Lumpur", "category": "expensive", "usd": 240, "rating": 4.6, "address": "KLCC"},
        {"name": "The St. Regis Kuala Lumpur", "category": "expensive", "usd": 280, "rating": 4.8, "address": "KL Sentral"},
    ],
    "istanbul": [
        {"name": "Hotel Amira Istanbul", "category": "cheap", "usd": 80, "rating": 4.8, "address": "Sultanahmet"},
        {"name": "Sirkeci Mansion", "category": "cheap", "usd": 75, "rating": 4.7, "address": "Sirkeci"},
        {"name": "Radisson Hotel Istanbul Pera (Entry)", "category": "cheap", "usd": 90, "rating": 4.3, "address": "Pera"},
        {"name": "DoubleTree by Hilton Istanbul Piyalepasa", "category": "medium", "usd": 120, "rating": 4.4, "address": "Beyoglu"},
        {"name": "Novotel Istanbul Bosphorus", "category": "medium", "usd": 140, "rating": 4.5, "address": "Karakoy"},
        {"name": "The Marmara Taksim (Std)", "category": "medium", "usd": 150, "rating": 4.4, "address": "Taksim"},
        {"name": "Ciragan Palace Kempinski", "category": "expensive", "usd": 520, "rating": 4.8, "address": "Besiktas"},
        {"name": "Raffles Istanbul", "category": "expensive", "usd": 480, "rating": 4.8, "address": "Zorlu Center"},
        {"name": "Four Seasons Istanbul at the Bosphorus", "category": "expensive", "usd": 650, "rating": 4.9, "address": "Besiktas"},
    ],
}

NORMALIZED_KEYS = {k.lower(): k for k in HOTEL_DB.keys()}

# -----------------------------
# Main: search_hotels
# -----------------------------
def search_hotels(city: str, check_in: str, check_out: str, adults: int = 1) -> List[Dict]:
    """Display hotels styled like flight results, with filters and real info."""
    ok, msg = _validate_dates(check_in, check_out)
    if not ok:
        console.print(f"[yellow]⚠ {msg}[/yellow]")
        return []

    city_key = city.strip().lower()
    if city_key not in NORMALIZED_KEYS:
        console.print("[yellow]⚠ City not in our hotel database. Try another one.[/yellow]")
        return []

    currency = _choose_currency()
    price_filter = _choose_price_range()
    base_hotels = HOTEL_DB[NORMALIZED_KEYS[city_key]]

    if price_filter in {"cheap", "medium", "expensive"}:
        hotels = [h for h in base_hotels if h["category"] == price_filter]
    else:
        hotels = base_hotels[:]

    if not hotels:
        console.print("[yellow]⚠ No hotels match this filter.[/yellow]")
        return []

    rate = CURRENCY_RATES.get(currency, 1.0)
    out: List[Dict] = []
    for h in hotels:
        price_converted = round(h["usd"] * rate, 2)
        out.append({
            "name": h["name"],
            "city": NORMALIZED_KEYS[city_key].title(),
            "category": h["category"],
            "price": price_converted,
            "currency": currency,
            "rating": h["rating"],
            "stars": _stars(h["rating"]),
            "address": h["address"],
            "check_in": check_in,
            "check_out": check_out,
            "adults": adults,
        })

    out.sort(key=lambda x: (-float(x["rating"]), x["price"]))

    # Beautiful formatted table
    title = f"🏨 Available Hotels in {NORMALIZED_KEYS[city_key].title()} ({currency})"
    table = Table(
        title=title,
        show_lines=True,
        header_style="bold magenta",
        box=box.ROUNDED
    )
    table.add_column("#", justify="center", style="bold yellow")
    table.add_column("Hotel Name", style="bold cyan")
    table.add_column("Category", justify="center")
    table.add_column("Rating", justify="center")
    table.add_column("Price / Night", justify="right", style="bold green")
    table.add_column("Address", justify="center")
    table.add_column("Check-in", justify="center")
    table.add_column("Check-out", justify="center")

    for i, row in enumerate(out, start=1):
        table.add_row(
            str(i),
            row["name"],
            row["category"].title(),
            f"{row['stars']} ({row['rating']:.1f})",
            f"{row['price']} {row['currency']}",
            row["address"],
            row["check_in"],
            row["check_out"],
        )

    console.print("\n")
    console.print(table)
    return out