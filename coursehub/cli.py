from .storage import init_db

def run_cli():
    init_db()
    print("CourseHub setup OK. Type 'exit' to quit.")
    while True:
        cmd = input("> ").strip().lower()
        if cmd in ("exit", "quit"):
            break
