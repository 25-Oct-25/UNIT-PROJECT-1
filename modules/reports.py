from modules.events import load_events
def simple_report():
    events = load_events()
    print(f"Total events: {len(events)}")
    # further stats can be added: attendees count, most active months, etc.
