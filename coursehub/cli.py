from . import storage, services
from .utils import cinfo, cgood, cbad, cwarn, ctitle, print_table
from .certificate import generate_certificate
from .ai_global import ask_global
from datetime import datetime

_current_user = None

def ask(prompt, allow_empty=False):
    while True:
        s = input(f"{prompt}: ").strip()
        if s or allow_empty:
            return s
        print(cwarn("This field is required."))

def ask_int(prompt, min_v=None, max_v=None):
    while True:
        s = ask(prompt)
        try:
            x = int(s)
            if (min_v is not None and x < min_v) or (max_v is not None and x > max_v):
                print(cwarn("Out of range.")); continue
            return x
        except ValueError:
            print(cbad("Enter a valid number."))

def menu(title, options):
    while True:
        print("\n" + ctitle(title))
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
        print(cgood(f"Logged in as student: {name}"))
    def login_admin():
        pin = ask("PIN (1234)")
        if pin != "1234": print(cbad("Wrong PIN")); return
        email = ask("Admin email"); name = ask("Admin name")
        uid = services.ensure_user(email, name, "admin")
        global _current_user; _current_user = (uid, "admin", email, name)
        print(cgood(f"Logged in as admin: {name}"))
    def whoami():
        print(cwarn("Not logged in.") if not _current_user else cinfo(f"{_current_user[3]} <{_current_user[2]}> ({_current_user[1]})"))
    def logout():
        global _current_user; _current_user=None; print(cgood("Logged out"))
    menu("Auth", [
        ("Login as Student", login_student),
        ("Login as Admin", login_admin),
        ("Who am I?", whoami),
        ("Logout", logout),
    ])

def screen_courses():
    def list_all():
        level = ask("Filter level (beginner/intermediate/advanced) or empty", allow_empty=True) or None
        rows = services.list_courses(level)
        if not rows: print(cwarn("No courses.")); return
        table = [[cid, title, lvl, price, (summary[:60]+"…") if len(summary)>60 else summary]
                 for (cid, title, lvl, price, summary) in rows]
        print_table(table, headers=["ID","Title","Level","Price","Summary"])
        input(cinfo("Enter to continue..."))
    def search():
        kw = ask("Keyword")
        rows = services.search_courses(kw)
        if not rows: print(cwarn("No results.")); return
        table = [[cid, title, lvl, price, (summary[:60]+"…") if len(summary)>60 else summary]
                 for (cid, title, lvl, price, summary) in rows]
        print_table(table, headers=["ID","Title","Level","Price","Summary"])
        input(cinfo("Enter to continue..."))
    def show():
        cid = ask_int("Course ID", 1)
        r = services.get_course(cid)
        if not r: print(cwarn("Not found.")); return
        cid, title, lvl, price, summary = r
        print(ctitle(f"Course #{cid}"))
        print(f"Title: {title}\nLevel: {lvl}\nPrice: {price:.2f} SAR\nSummary: {summary}")
        input(cinfo("Enter to continue..."))
    menu("Courses", [
        ("List courses", list_all),
        ("Search courses", search),
        ("Show course details", show),
    ])

def require(role):
    if not _current_user:
        print(cwarn("Login first from 'Auth' menu.")); return False
    if role and _current_user[1] != role:
        print(cbad(f"Allowed for role: {role}")); return False
    return True

def screen_student():
    def enroll():
        if not require("student"): return
        cid = ask_int("Course ID", 1)
        services.enroll(_current_user[0], cid)
        print(cgood("Enrolled (or already).")); input(cinfo("Enter to continue..."))
    def my_courses():
        if not require("student"): return
        rows = services.my_courses(_current_user[0])
        if not rows: print(cwarn("No enrolled courses.")); return
        table = []
        for (_e, cid, title, lvl, prog, price) in rows:
            bar = "[" + ("#"*(prog//10)).ljust(10, ".") + "]"
            table.append([cid, title, lvl, f"{prog}%", bar, price])
        print_table(table, headers=["ID","Title","Level","Progress","Bar","Price"])
        input(cinfo("Enter to continue..."))
    def progress():
        if not require("student"): return
        cid = ask_int("Course ID", 1)
        delta = ask_int("Change (+/-N)")
        newp = services.update_progress(_current_user[0], cid, delta)
        print(cinfo(f"Progress is now {newp}%")); input(cinfo("Enter to continue..."))
    def recommend():
        if not require("student"): return
        rows = services.recommend(_current_user[0])
        if not rows: print(cwarn("No recommendations.")); return
        table = [[cid, title, lvl, price] for (cid, title, lvl, price, _s) in rows]
        print_table(table, headers=["ID","Title","Level","Price"])
        input(cinfo("Enter to continue..."))
    def certificate():
        if not require("student"): return
        cid = ask_int("Course ID", 1)
        ok, reason = services.can_issue_certificate(_current_user[0], cid)
        if not ok:
            print(cwarn(f"Cannot issue certificate: {reason}")); input(cinfo("Enter to continue...")); return
        course = services.get_course(cid)
        if not course: print(cbad("Course not found.")); input(cinfo("Enter to continue...")); return
        path = generate_certificate(_current_user[3], course[1], datetime.now())
        print(cgood(f"Certificate generated: {path}")); input(cinfo("Enter to continue..."))
    menu("Student", [
        ("Enroll in a course", enroll),
        ("My courses", my_courses),
        ("Update progress", progress),
        ("Recommendations", recommend),
        ("Generate PDF certificate", certificate),
    ])

def screen_admin():
    def add_course():
        if not require("admin"): return
        title = ask("Course title")
        level = ask("Level (beginner/intermediate/advanced)")
        price = float(ask("Price (number)"))
        summary = ask("Summary")
        cid = services.add_course(title, level, price, summary)
        print(cgood(f"Added course #{cid}")); input(cinfo("Enter to continue..."))
    def add_link():
        if not require("admin"): return
        try:
            cid   = ask_int("Course ID", 1)
            title = ask("Link title")
            url   = ask("URL")
            rid = services.add_resource_link(cid, title, url)
            print(cgood(f"Link added id={rid} for course #{cid}"))
        except Exception as e:
            print(cbad(str(e)))
        input(cinfo("Enter to continue..."))
    def list_links():
        cid = ask_int("Course ID", 1)
        rows = services.list_resource_links(cid)
        if not rows: print(cwarn("No links for this course.")); return
        table = [[rid, title, url, created] for (rid, title, url, created) in rows]
        print_table(table, headers=["ID","Title","URL","Created"])
        input(cinfo("Enter to continue..."))
    menu("Admin", [
        ("Add a new course", add_course),
        ("Add course resource link", add_link),
        ("List course links", list_links),
    ])

def screen_ai_global():
    def ask_any():
        q = ask("Your question")
        ans = ask_global(q)
        print(ctitle("Answer")); print(ans)
        input(cinfo("Enter to continue..."))
    return menu("Global AI (Gemini)", [("Ask a general question", ask_any),])

def run_cli():
    storage.init_db()
    print(ctitle("🎓 CourseHub — Numbered Menus"))
    while True:
        print("\n" + ctitle("Main Menu"))
        print("  1) Auth")
        print("  2) Courses")
        print("  3) Student")
        print("  4) Admin")
        print("  5) Global AI")
        print("  0) Exit")
        ch = ask_int("> Choose", 0, 5)
        if ch == 0: print(cgood("Bye!")); break
        if ch == 1: screen_auth()
        elif ch == 2: screen_courses()
        elif ch == 3: screen_student()
        elif ch == 4: screen_admin()
        elif ch == 5: screen_ai_global()
