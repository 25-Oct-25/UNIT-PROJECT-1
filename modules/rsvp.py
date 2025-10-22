import json, os, re
from modules.events import load_events, save_events
from modules import ui

ATT_DIR = "data/attendees"
os.makedirs(ATT_DIR, exist_ok=True)


def _attendees_path(event_title: str) -> str:
    safe = event_title.replace(" ", "_").lower()
    return f"{ATT_DIR}/{safe}.json"


def load_attendees(event_title):
    """Read attendees list from JSON."""
    path = _attendees_path(event_title)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_attendees(event_title, attendees):
    """Write attendees back to JSON."""
    path = _attendees_path(event_title)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(attendees, f, ensure_ascii=False, indent=2)


def _valid_email(s: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", s or ""))


# =============== CLI: Add / List / Toggle ===============

def add_attendee_cli():
    event_title = input("Event title: ").strip()
    name = input("Attendee name: ").strip()
    email = input("Attendee email: ").strip()

    if not name or not email:
        ui.warning("Name and email are required.")
        return
    if not _valid_email(email):
        ui.warning("Invalid email format.")
        return

    attendees = load_attendees(event_title)
    attendees.append({"name": name, "email": email, "attended": False})
    save_attendees(event_title, attendees)
    ui.success(f"Added attendee: {name} ({email})")


def list_attendees_cli():
    event_title = input("Event title: ").strip()
    attendees = load_attendees(event_title)
    if hasattr(ui, "attendees_table") and callable(ui.attendees_table):
        ui.attendees_table(event_title, attendees)
    else:
        if not attendees:
            print("No attendees found.")
            return
        print(f"\nAttendees for '{event_title}':")
        for i, a in enumerate(attendees, 1):
            status = "✅ Attended" if a.get("attended") else "❌ Not attended"
            print(f"{i}. {a.get('name','-')} - {a.get('email','-')} ({status})")


def mark_attendance_cli():
    """Toggle attended/absent for a single attendee."""
    event_title = input("Event title: ").strip()
    attendees = load_attendees(event_title)
    if not attendees:
        ui.warning("No attendees found for this event.")
        return

    # Show table before choosing
    if hasattr(ui, "attendees_table") and callable(ui.attendees_table):
        ui.attendees_table(event_title, attendees)
    else:
        print(f"\nAttendees for '{event_title}':")
        for i, a in enumerate(attendees, 1):
            status = "✅" if a.get("attended") else "❌"
            print(f"{i}. {a.get('name','-')} - {a.get('email','-')} ({status})")

    try:
        index = int(input("\nSelect attendee number to toggle attendance: ").strip()) - 1
    except ValueError:
        ui.error("Invalid input. Please enter a number.")
        return

    if 0 <= index < len(attendees):
        attendees[index]["attended"] = not attendees[index].get("attended", False)
        save_attendees(event_title, attendees)
        new_status = "Attended" if attendees[index]["attended"] else "Absent"
        ui.success(f"Updated {attendees[index].get('name','?')} → {new_status}")
    else:
        ui.warning("Invalid number.")


# =============== NEW: Edit / Delete Attendee ===============

def edit_attendee_cli():
    """Edit name/email for an attendee."""
    event_title = input("Event title: ").strip()
    attendees = load_attendees(event_title)
    if not attendees:
        ui.warning("No attendees found for this event.")
        return

    # List first
    if hasattr(ui, "attendees_table") and callable(ui.attendees_table):
        ui.attendees_table(event_title, attendees)
    else:
        print(f"\nAttendees for '{event_title}':")
        for i, a in enumerate(attendees, 1):
            print(f"{i}. {a.get('name','-')} - {a.get('email','-')}")

    try:
        idx = int(input("\nSelect attendee number to edit: ").strip()) - 1
    except ValueError:
        ui.error("Invalid input. Please enter a number.")
        return

    if not (0 <= idx < len(attendees)):
        ui.warning("Invalid choice.")
        return

    a = attendees[idx]
    print("Leave blank to keep current value.")
    new_name = input(f"New name [{a.get('name','')}]: ").strip()
    new_email = input(f"New email [{a.get('email','')}]: ").strip()

    if new_email and not _valid_email(new_email):
        ui.warning("Invalid email format.")
        return

    if new_name:
        a["name"] = new_name
    if new_email:
        a["email"] = new_email

    save_attendees(event_title, attendees)
    ui.success("Attendee updated.")


def delete_attendee_cli():
    """Delete an attendee from an event."""
    event_title = input("Event title: ").strip()
    attendees = load_attendees(event_title)
    if not attendees:
        ui.warning("No attendees found for this event.")
        return

    # List first
    if hasattr(ui, "attendees_table") and callable(ui.attendees_table):
        ui.attendees_table(event_title, attendees)
    else:
        print(f"\nAttendees for '{event_title}':")
        for i, a in enumerate(attendees, 1):
            print(f"{i}. {a.get('name','-')} - {a.get('email','-')}")

    try:
        idx = int(input("\nSelect attendee number to delete: ").strip()) - 1
    except ValueError:
        ui.error("Invalid input. Please enter a number.")
        return

    if not (0 <= idx < len(attendees)):
        ui.warning("Invalid choice.")
        return

    removed = attendees.pop(idx)
    save_attendees(event_title, attendees)
    ui.success(f"Removed: {removed.get('name','?')} ({removed.get('email','?')})")
