# modules/events.py
import json, os, re
from modules import ui
from datetime import datetime

def list_events_cli():
    events = load_events()
    ui.events_table(events)

DATA_DIR  = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'events.json')
ATT_DIR   = os.path.join(DATA_DIR, 'attendees')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ATT_DIR, exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)


def _slugify_title(title: str) -> str:
    """
    نحول العنوان إلى اسم ملف آمن: أحرف صغيرة + شرطة سفلية
    """
    t = title.strip().lower()
    t = re.sub(r'\s+', '_', t)           # مسافات -> _
    t = re.sub(r'[^\w\-]+', '', t)       # احذف غير الحروف/الأرقام/الشرطة السفلية
    return t or "event"


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
    loc  = input("Location: ").strip()
    create_event(title, date, desc, loc)


def list_events_cli():
    events = load_events()
    if not events:
        print("No events.")
        return
    for i, e in enumerate(events, 1):
        rlist = e.get('reminders', [])
        print(f"{i}. {e['title']} | {e['date']} | {e.get('location','')} | Reminders: {rlist}")


def delete_event_cli():
    events = load_events()
    if not events:
        print("No events found.")
        return

    for i, event in enumerate(events, start=1):
        print(f"{i}. {event['title']} | {event['date']}")

    try:
        choice = int(input("\nEnter the number of the event to delete: ").strip()) - 1
    except ValueError:
        print("Invalid input.")
        return

    if 0 <= choice < len(events):
        deleted_event = events.pop(choice)
        save_events(events)
        print(f"✅ Event '{deleted_event['title']}' deleted successfully!")

        # حذف ملف الحضور المطابق لعنوان الحدث (slug)
        slug = _slugify_title(deleted_event['title'])
        attendees_path = os.path.join(ATT_DIR, f"{slug}.json")
        if os.path.exists(attendees_path):
            try:
                os.remove(attendees_path)
                print(f"🗑️ Deleted attendees file: {attendees_path}")
            except Exception as e:
                print(f"⚠️ Could not delete attendees file: {e}")
        else:
            print("ℹ️ No attendees file found for this event.")
    else:
        print("Invalid choice.")
