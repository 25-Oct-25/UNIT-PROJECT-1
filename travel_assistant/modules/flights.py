import json, os

FLIGHTS_FILE = "data/flights.json"

os.makedirs(os.path.dirname(FLIGHTS_FILE), exist_ok=True)

def load_flights():
    if not os.path.exists(FLIGHTS_FILE):
        return []
    with open(FLIGHTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_flights(flights):
    with open(FLIGHTS_FILE, "w", encoding="utf-8") as f:
        json.dump(flights, f, ensure_ascii=False, indent=2)

def add_flight(destination, departure_city, departure_date, price, airline):
    flights = load_flights()
    flight = {
        "destination": destination,
        "departure_city": departure_city,
        "departure_date": departure_date,
        "price": price,
        "airline": airline
    }
    flights.append(flight)
    save_flights(flights)

def search_flights(destination=None, departure_city=None, departure_date=None):
    flights = load_flights()
    results = []
    for f in flights:
        if destination and f["destination"].lower() != destination.lower():
            continue
        if departure_city and f["departure_city"].lower() != departure_city.lower():
            continue
        if departure_date and f["departure_date"] != departure_date:
            continue
        results.append(f)
    return results

def filter_by_price(flights, option="cheapest"):
    if option == "cheapest":
        return sorted(flights, key=lambda x: x["price"])
    elif option == "expensive":
        return sorted(flights, key=lambda x: x["price"], reverse=True)
    elif option == "average":
        return sorted(flights, key=lambda x: abs(x["price"] - sum(f["price"] for f in flights)/len(flights)))
    else:
        return flights
