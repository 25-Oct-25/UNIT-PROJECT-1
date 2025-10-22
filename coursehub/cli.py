from . import storage, services
from .utils import cinfo, cgood, cbad, cwarn, ctitle, print_table
from .certificate import generate_certificate
from .ai_global import ask_global
from .mailer import send_email
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

def require(role):
    if not _current_user:
        print(cwarn("Login first.")); return False
    if role and _current_user[1] != role:
        print(cbad(f"Allowed for role: {role}")); return False
    return True

def screen_auth_first():
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
    while True:
        print("\n" + ctitle("Login"))
        print("  1) Login as Student")
        print("  2) Login as Admin")
        print("  0) Exit")
        ch = ask_int("> Choose", 0, 2)
        if ch == 0:
            print(cgood("Bye!")); return False
        if ch == 1:
            login_student(); return True
        if ch == 2:
            login_admin(); return True

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
        if not require("admin"): return
        cid = ask_int("Course ID", 1)
        rows = services.list_resource_links(cid)
        if not rows:
            print(cwarn("No links for this course.")); input(cinfo("Enter to continue...")); return
        table = [[rid, title, url, created] for (rid, title, url, created) in rows]
        print_table(table, headers=["ID","Title","URL","Created"])
        input(cinfo("Enter to continue..."))

    def list_all_courses():
        level = ask("Filter level (beginner/intermediate/advanced) or empty", allow_empty=True) or None
        rows = services.list_courses(level)
        if not rows: print(cwarn("No courses.")); input(cinfo("Enter to continue...")); return
        table = [[cid, title, lvl, price, (summary[:60]+"…") if len(summary)>60 else summary]
                 for (cid, title, lvl, price, summary) in rows]
        print_table(table, headers=["ID","Title","Level","Price","Summary"])
        input(cinfo("Enter to continue..."))

    menu("Admin", [
        ("Add a new course", add_course),
        ("Add course resource link", add_link),
        ("List course links", list_links),
        ("List all courses", list_all_courses),
    ])

def screen_student():
    def enroll():
        if not require("student"): return
        cid = ask_int("Course ID", 1)
        services.enroll(_current_user[0], cid)
        print(cgood("Enrolled (or already).")); input(cinfo("Enter to continue..."))

    def my_courses():
        if not require("student"): return
        rows = services.my_courses(_current_user[0])
        if not rows: print(cwarn("No enrolled courses.")); input(cinfo("Enter to continue...")); return
        table = []
        for (_e, cid, title, lvl, prog, price) in rows:
            bar = "[" + ("#"*(prog//10)).ljust(10, ".") + "]"
            table.append([cid, title, lvl, f"{prog}%", bar, price])
        print_table(table, headers=["ID","Title","Level","Progress","Bar","Price"])
        input(cinfo("Enter to continue..."))

    def update_progress():
        if not require("student"): return
        cid = ask_int("Course ID", 1)
        delta = ask_int("Change (+/-N)")
        newp = services.update_progress(_current_user[0], cid, delta)
        print(cinfo(f"Progress is now {newp}%")); input(cinfo("Enter to continue..."))

    def recommend():
        if not require("student"): return
        rows = services.recommend(_current_user[0])
        if not rows: print(cwarn("No recommendations.")); input(cinfo("Enter to continue...")); return
        table = [[cid, title, lvl, price] for (cid, title, lvl, price, _s) in rows]
        print_table(table, headers=["ID","Title","Level","Price"])
        input(cinfo("Enter to continue..."))

    def course_session():
        if not require("student"): return
        rows = services.my_courses(_current_user[0])
        if not rows: print(cwarn("No enrolled courses.")); input(cinfo("Enter to continue...")); return
        ids = [cid for (_e, cid, _t, _l, _p, _pr) in [(r[0], r[1], r[2], r[3], r[4], r[5]) for r in services.my_courses(_current_user[0])]]
        cid = ask_int("Enter a Course ID you are enrolled in", 1)
        enrolled = any(cid == r[1] for r in rows)
        if not enrolled:
            print(cbad("Not enrolled in this course.")); input(cinfo("Enter to continue...")); return

        def show_links():
            links = services.list_resource_links(cid)
            if not links:
                print(cwarn("No links for this course.")); input(cinfo("Enter to continue...")); return
            table = [[rid, title, url, created] for (rid, title, url, created) in links]
            print_table(table, headers=["ID","Title","URL","Created"])
            input(cinfo("Enter to continue..."))

        def ask_ai_here():
            q = ask("Your question")
            ans = ask_global(q)
            print(ctitle("Answer"))
            print(ans) 
            input(cinfo("Enter to continue..."))

        def certificate_and_email():
            ok, reason = services.can_issue_certificate(_current_user[0], cid)
            if not ok:
                print(cwarn(f"Cannot issue certificate: {reason}")); input(cinfo("Enter to continue...")); return
            course = services.get_course(cid)
            if not course:
                print(cbad("Course not found.")); input(cinfo("Enter to continue...")); return
            path = generate_certificate(_current_user[3], course[1], datetime.now())
            print(cgood(f"Certificate generated: {path}"))
            subj = f"Congratulations, {_current_user[3]}!"
            body = (
                f"Dear {_current_user[3]},\n\n"
                f"Congratulations on completing the course \"{course[1]}\".\n"
                f"Please find your certificate attached.\n\n"
                f"Best regards,\nCourseHub"
            )
            try:
                send_email(_current_user[2], subj, body, attachments=[path])
                print(cgood(f"Certificate sent to: {_current_user[2]}"))
            except Exception as e:
                print(cbad(f"Email sending failed: {e}"))
            input(cinfo("Enter to continue..."))

        menu(f"Course Session #{cid}", [
            ("Show course links", show_links),
            ("Ask AI (inside course)", ask_ai_here),
            ("Generate certificate PDF and email it", certificate_and_email),
        ])

    menu("Student", [
        ("Enroll in a course", enroll),
        ("My courses", my_courses),
        ("Update progress", update_progress),
        ("Recommendations", recommend),
        ("Enter a course session (links + AI + certificate email)", course_session),
    ])

def run_cli():
    global _current_user
    storage.init_db()

    if not screen_auth_first():
        return

    while True:
        if _current_user and _current_user[1] == "admin":
            print("\n" + ctitle("Main Menu (Admin)"))
            print("  1) Admin")
            print("  2) Logout")
            print("  0) Exit")
            ch = ask_int("> Choose", 0, 2)

            if ch == 0:
                print(cgood("Bye!"))
                break

            if ch == 2:
                _current_user = None
                if not screen_auth_first():
                    break
                continue

            if ch == 1:
                screen_admin()

        elif _current_user and _current_user[1] == "student":
            print("\n" + ctitle("Main Menu (Student)"))
            print("  1) Student")
            print("  2) Logout")
            print("  0) Exit")
            ch = ask_int("> Choose", 0, 2)

            if ch == 0:
                print(cgood("Bye!"))
                break

            if ch == 2:
                _current_user = None
                if not screen_auth_first():
                    break
                continue

            if ch == 1:
                screen_student()

        else:
            if not screen_auth_first():
                break
