from . import storage, services

_current_user = None

def ask(prompt, allow_empty=False):
    while True:
        s = input(f"{prompt}: ").strip()
        if s or allow_empty:
            return s
        print("This field is required.")

def ask_int(prompt, min_v=None, max_v=None):
    while True:
        s = ask(prompt)
        try:
            x = int(s)
            if (min_v is not None and x < min_v) or (max_v is not None and x > max_v):
                print("Out of range."); continue
            return x
        except ValueError:
            print("Enter a valid number.")

def menu(title, options):
    while True:
        print(f"\n== {title} ==")
        for i, (label, _) in enumerate(options, start=1):
            print(f"  {i}) {label}")
        print("  0) Back")
        ch = ask_int("> Choose", 0, len(options))
        if ch == 0: return
        _, fn = options[ch-1]
        fn()

def screen_auth():
    def login_student():
        email = ask("Email"); name = ask("Name")
        uid = services.ensure_user(email, name, "student")
        global _current_user; _current_user = (uid, "student", email, name)
        print(f"Logged in as student: {name}")
    def login_admin():
        pin = ask("PIN (1234)"); 
        if pin != "1234": print("Wrong PIN"); return
        email = ask("Admin email"); name = ask("Admin name")
        uid = services.ensure_user(email, name, "admin")
        global _current_user; _current_user = (uid, "admin", email, name)
        print(f"Logged in as admin: {name}")
    def whoami():
        print("Not logged in." if not _current_user else f"{_current_user[3]} <{_current_user[2]}> ({_current_user[1]})")
    def logout():
        global _current_user; _current_user=None; print("Logged out")
    menu("Auth", [
        ("Login as Student", login_student),
        ("Login as Admin", login_admin),
        ("Who am I?", whoami),
        ("Logout", logout),
    ])

def screen_courses():
    def list_all():
        level = ask("Filter by level (beginner/intermediate/advanced) or empty", allow_empty=True) or None
        rows = services.list_courses(level)
        if not rows: print("No courses."); return
        for (cid, title, lvl, price, summary) in rows:
            short = (summary[:60]+"…") if len(summary)>60 else summary
            print(f"[{cid}] {title} ({lvl}) - {price:.2f} SAR | {short}")
    def search():
        kw = ask("Keyword")
        rows = services.search_courses(kw)
        if not rows: print("No results."); return
        for (cid, title, lvl, price, summary) in rows:
            short = (summary[:60]+"…") if len(summary)>60 else summary
            print(f"[{cid}] {title} ({lvl}) - {price:.2f} SAR | {short}")
    def show():
        cid = ask_int("Course ID", 1)
        r = services.get_course(cid)
        if not r: print("Not found."); return
        cid, title, lvl, price, summary = r
        print(f"#{cid} | {title}\nLevel: {lvl}\nPrice: {price:.2f} SAR\nSummary: {summary}")
    menu("Courses", [
        ("List courses", list_all),
        ("Search courses", search),
        ("Show course details", show),
    ])

def screen_student():
    def enroll():
        if not _current_user or _current_user[1] != "student": print("Login as student first"); return
        cid = ask_int("Course ID", 1)
        services.enroll(_current_user[0], cid)
        print("Enrolled (or already).")
    def my_courses():
        if not _current_user or _current_user[1] != "student": print("Login as student first"); return
        rows = services.my_courses(_current_user[0])
        if not rows: print("No enrolled courses."); return
        for (_e, cid, title, lvl, prog, price) in rows:
            print(f"[{cid}] {title} ({lvl}) — progress {prog}% — {price:.2f} SAR")
    menu("Student", [
        ("Enroll in a course", enroll),
        ("My courses", my_courses),
    ])

def run_cli():
    storage.init_db()
    print("🎓 CourseHub — Numbered Menus")
    while True:
        print("\n== Main Menu ==")
        print("  1) Auth")
        print("  2) Courses")
        print("  3) Student")
        print("  0) Exit")
        ch = ask_int("> Choose", 0, 3)
        if ch == 0: print("Bye!"); break
        if ch == 1: screen_auth()
        elif ch == 2: screen_courses()
        elif ch == 3: screen_student()
