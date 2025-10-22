import json, os, re, shutil
from datetime import datetime
from modules import ui

DATA_DIR     = 'data'
DATA_FILE    = os.path.join(DATA_DIR, 'events.json')
ATT_DIR      = os.path.join(DATA_DIR, 'attendees')
POSTERS_DIR  = os.path.join(DATA_DIR, 'posters')

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ATT_DIR, exist_ok=True)
os.makedirs(POSTERS_DIR, exist_ok=True)

# Create events file if missing
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)


def _slugify_title(title: str) -> str:
    """
    Turn title into a safe filename: lowercase + underscores
    """
    t = title.strip().lower()
    t = re.sub(r'\s+', '_', t)           # spaces → _
    t = re.sub(r'[^\w\-]+', '', t)       # drop non-word chars
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
    """
    Pretty table if ui.events_table exists, otherwise plain list.
    """
    events = load_events()
    if not events:
        print("No events.")
        return

    # Use UI table if available
    table_fn = getattr(ui, "events_table", None)
    if callable(table_fn):
        ui.events_table(events)
        return

    # Simple fallback
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

        # Remove attendees file with matching slug
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

        # Remove poster if present
        poster_path = os.path.join(POSTERS_DIR, f"{deleted_event['title'].replace(' ', '_')}.png")
        if os.path.exists(poster_path):
            try:
                os.remove(poster_path)
                print(f"🗑️ Deleted poster file: {poster_path}")
            except Exception as e:
                print(f"⚠️ Could not delete poster file: {e}")
    else:
        print("Invalid choice.")


# ===== NEW: Update event (title/date/location/description) =====

def update_event(old_title: str,
                 new_title: str | None = None,
                 new_date: str | None = None,
                 new_location: str | None = None,
                 new_description: str | None = None) -> bool:
    """
    Update event fields. If title changes, rename attendees & poster files accordingly.
    Returns True if updated.
    """
    events = load_events()
    ev = next((e for e in events if e['title'].lower() == old_title.lower()), None)
    if not ev:
        print("Event not found.")
        return False

    # Validate date if provided
    if new_date:
        try:
            datetime.strptime(new_date, "%Y-%m-%d %H:%M")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD HH:MM")
            return False

    # If title changed, move related files
    if new_title and new_title.strip() and new_title != ev['title']:
        old_slug = _slugify_title(ev['title'])
        new_slug = _slugify_title(new_title)

        # attendees rename
        old_att = os.path.join(ATT_DIR, f"{old_slug}.json")
        new_att = os.path.join(ATT_DIR, f"{new_slug}.json")
        if os.path.exists(old_att):
            try:
                shutil.move(old_att, new_att)
                print(f"↪ Renamed attendees file → {os.path.basename(new_att)}")
            except Exception as e:
                print(f"⚠️ Failed to rename attendees file: {e}")

        # poster rename
        old_poster = os.path.join(POSTERS_DIR, f"{ev['title'].replace(' ','_')}.png")
        new_poster = os.path.join(POSTERS_DIR, f"{new_title.replace(' ','_')}.png")
        if os.path.exists(old_poster):
            try:
                shutil.move(old_poster, new_poster)
                print(f"↪ Renamed poster → {os.path.basename(new_poster)}")
            except Exception as e:
                print(f"⚠️ Failed to rename poster: {e}")

        ev['title'] = new_title

    # Other fields
    if new_date:
        ev['date'] = new_date
    if new_location is not None:
        ev['location'] = new_location
    if new_description is not None:
        ev['description'] = new_description

    save_events(events)
    print("✅ Event updated.")
    return True


def edit_event_cli():
    """
    Interactive editor for title/date/location/description.
    Leave blank to keep current values.
    """
    events = load_events()
    if not events:
        print("No events.")
        return

    print("\nSelect event to edit:")
    for i, e in enumerate(events, 1):
        print(f"{i}. {e['title']} | {e['date']} | {e.get('location','')}")

    try:
        idx = int(input("\nNumber: ").strip()) - 1
    except ValueError:
        print("Invalid input.")
        return

    if not (0 <= idx < len(events)):
        print("Invalid choice.")
        return

    ev = events[idx]
    print("\nLeave blank to keep current value.")
    nt  = input(f"New title [{ev['title']}]: ").strip()
    nd  = input(f"New date [{ev['date']}] (YYYY-MM-DD HH:MM): ").strip()
    nl  = input(f"New location [{ev.get('location','')}]: ").strip()
    nds = input(f"New description [{ev.get('description','')}]: ").strip()

    update_event(
        old_title=ev['title'],
        new_title=nt or None,
        new_date=nd or None,
        new_location=nl if nl != "" else None,
        new_description=nds if nds != "" else None,
    )
