# modules/rsvp.py
import json, os
from modules.events import load_events, save_events
from modules import ui  



def _attendees_path(event_title):
    os.makedirs("data/attendees", exist_ok=True)
    safe = event_title.replace(" ", "_").lower()
    return f"data/attendees/{safe}.json"

def load_attendees(event_title):
    """تحميل قائمة الحضور من ملف JSON"""
    path = _attendees_path(event_title)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_attendees(event_title, attendees):
    """حفظ قائمة الحضور بعد التعديل"""
    path = _attendees_path(event_title)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(attendees, f, ensure_ascii=False, indent=2)

def add_attendee_cli():
    event_title = input("Event title: ").strip()
    name = input("Attendee name: ").strip()
    email = input("Attendee email: ").strip()
    attendees = load_attendees(event_title)
    attendees.append({"name": name, "email": email, "attended": False})
    save_attendees(event_title, attendees)
    print(f"✅ Added attendee: {name} ({email})")

def list_attendees_cli():
    event_title = input("Event title: ").strip()
    attendees = load_attendees(event_title)
    ui.attendees_table(event_title, attendees)

def mark_attendance_cli():
    event_title = input("Event title: ").strip()
    attendees = load_attendees(event_title)
    if not attendees:
        print("No attendees found for this event.")
        return

    # طباعة جدول قبل الاختيار
    ui.attendees_table(event_title, attendees)

    try:
        index = int(input("\nSelect attendee number to toggle attendance: ")) - 1
        if 0 <= index < len(attendees):
            attendees[index]["attended"] = not attendees[index].get("attended", False)
            save_attendees(event_title, attendees)
            new_status = "Attended" if attendees[index]["attended"] else "Absent"
            ui.success(f"Updated {attendees[index]['name']} → {new_status}")
        else:
            ui.warning("Invalid number.")
    except ValueError:
        ui.error("Invalid input. Please enter a number.")