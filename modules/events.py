import json, os
from datetime import datetime

DATA_FILE = os.path.join('data', 'events.json')
os.makedirs('data', exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

def load_events():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_events(events):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(events, f, ensure_ascii=False, indent=2)

def create_event(title, date_str, description, location):
    events = load_events()
    if any(e['title'].lower() == title.lower() for e in events):
        print(f"Event '{title}' already exists.")
        return False
    try:
        datetime.strptime(date_str, '%Y-%m-%d %H:%M')
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD HH:MM")
        return False
    event = {
        "title": title,
        "date": date_str,
        "description": description,
        "location": location,
        "reminders": [],
        "poster": None,
        "attendees": []
    }
    events.append(event)
    save_events(events)
    print(f"Event '{title}' created for {date_str}")
    return True

# === CLI Functions ===

def create_event_cli():
    title = input("Title: ").strip()
    date = input("Date (YYYY-MM-DD HH:MM): ").strip()
    desc = input("Description: ").strip()
    loc = input("Location: ").strip()
    create_event(title, date, desc, loc)

def list_events_cli():
    events = load_events()
    if not events:
        print("No events.")
        return
    for i, e in enumerate(events, 1):
        print(f"{i}. {e['title']} | {e['date']} | {e['location']} | Reminders: {e.get('reminders', [])}")

def delete_event_cli():
    events = load_events()
    if not events:
        print("No events.")
        return
    for i, e in enumerate(events, 1):
        print(f"{i}. {e['title']} | {e['date']}")
    idx = input("Enter number to delete: ").strip()
    try:
        idx = int(idx) - 1
        if 0 <= idx < len(events):
            removed = events.pop(idx)
            save_events(events)
            print(f"Deleted: {removed['title']}")
        else:
            print("Invalid index.")
    except ValueError:
        print("Invalid input.")

def add_reminder_cli():
    events = load_events()
    if not events:
        print("No events.")
        return
    for i, e in enumerate(events, 1):
        print(f"{i}. {e['title']} | {e['date']}")
    idx = input("Select event #: ").strip()
    try:
        idx = int(idx) - 1
        if not (0 <= idx < len(events)):
            print("Invalid index.")
            return
    except ValueError:
        print("Invalid input.")
        return
    minutes = input("Reminder (minutes before): ").strip()
    try:
        m = int(minutes)
    except ValueError:
        print("Invalid minutes.")
        return
    events[idx].setdefault('reminders', []).append(m)
    save_events(events)
    print(f"Added reminder {m} min before for '{events[idx]['title']}'")
