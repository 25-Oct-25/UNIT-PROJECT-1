import json, os
from modules.events import load_events, save_events

def add_attendee(event_title, name, email):
    events = load_events()
    for ev in events:
        if ev['title'].lower() == event_title.lower():
            ev.setdefault('attendees', []).append({'name': name, 'email': email, 'status':'pending'})
            save_events(events)
            print(f"Added attendee {name} <{email}> to {event_title}")
            return True
    print("Event not found.")
    return False

def list_attendees(event_title):
    events = load_events()
    for ev in events:
        if ev['title'].lower() == event_title.lower():
            atts = ev.get('attendees', [])
            if not atts:
                print("No attendees yet.")
                return
            for a in atts:
                print(f"- {a.get('name')} | {a.get('email')} | {a.get('status')}")
            return
    print("Event not found.")

# CLI wrappers
def add_attendee_cli():
    title = input("Event title: ").strip()
    name  = input("Attendee name: ").strip()
    email = input("Attendee email: ").strip()
    add_attendee(title, name, email)

def list_attendees_cli():
    title = input("Event title: ").strip()
    list_attendees(title)
