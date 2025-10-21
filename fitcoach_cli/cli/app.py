# -*- coding: utf-8 -*-
# File: fitcoach_cli/cli/app.py
# Functions: 5  (cmd_help, _load, _save, handle, main)
# Key features:
#   - Colored, sectioned CLI help using Colorama (with optional boxes & wide layout)
#   - Central command router (parses tokens via shlex) for auth/profile/plan/recipes/report/email/etc.
#   - Persistent application state (load/save) including RBAC users and report schedules
#   - Email & weekly PDF report integration; background scheduler bootstrap
#   - Theming & color toggle (--no-color), plus Arabic/English language setting

import shlex, sys, datetime, os
from typing import Dict, Any
from dataclasses import asdict
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=False)  # Load .env if present (safe no-op otherwise)

from colorama import Fore, Style
from .console import (
    section, banner, info, success, warn, error, ask,
    set_theme, set_color_enabled
)

# ====== Feature imports ======
from ..core.models import AppState, UserProfile
from ..storage.db import load_state, save_state
from ..nutrition.calculator import bmr_mifflin_st_jeor, tdee, macro_targets
from ..nutrition.adjuster import analyze_weights
from ..training.generator import generate_plan
from ..training.logger import log_workout, last_sessions
from ..training.progression import suggest_loads
from ..training.volume import count_volume
from ..recipes.catalog import suggest
from ..recipes.builder import build_day
from ..plan.groceries import build_grocery_list
from ..plan.export import export_plan_csv
from ..plan.weekly import summarize
from ..plan.report_pdf import build_weekly_pdf
from ..notifications.scheduler import start_report_scheduler_email
from ..notifications.emailer import send_email_smtp
from ..advice.recommend import daily_tips
from ..advice.habits import log_habits, score_today
from ..advice.nudges import nudge
from ..progress.chart_ascii import ascii_plot
from ..auth.roles import (
    add_user, set_role, delete_user,
    login as auth_login, logout as auth_logout,
    current_role, require_role
)

# =====================================================================
# Tab Completion for REPL (إكمال بالأزرار Tab داخل حلقة الإدخال)
# - نستخدم readline (أو pyreadline3 على ويندوز) لإكمال:
#   * الأمر الأساسي، ثم الساب-أمر، ثم الفلاقز المناسبة.
# - هذه الطريقة مناسبة لأن التطبيق REPL ويستخدم shlex وليس argparse.
# =====================================================================
try:
    import readline  # متوفر على macOS/Linux و Git Bash غالبًا
except Exception:
    try:
        import pyreadline3 as readline  # بديل ويندوز
    except Exception:
        readline = None  # إن لم يتوفر، يستمر البرنامج بدون إكمال

# قائمة الأوامر والساب-أوامر المتاحة (للاقتراح)
_REPL_COMMANDS = {
    "help": [],
    "exit": [],
    "quit": [],
    "q": [],

    "auth": ["add-user", "login", "logout", "whoami", "list-users", "role", "delete-user"],
    "profile": ["show", "set"],
    "calories": ["calc"],
    "plan": ["generate", "show", "volume", "groceries"],
    "export": ["csv"],
    "recipes": ["suggest", "build-day"],
    "advice": ["daily"],
    "habits": ["log", "score"],
    "nudge": [],
    "progress": ["log", "analyze", "plot"],
    "workout": ["log", "suggest"],
    "report": ["pdf", "send", "schedule", "brand"],
    "email": ["config", "test"],
    "app": ["lang"],
}

# الفلاقز المقترحة لكل (أمر، ساب-أمر)
_REPL_FLAGS = {
    ("auth", "add-user"): ["--username=", "--role=", "--password="],
    ("auth", "login"):    ["--username=", "--password="],
    ("auth", "role"):     ["set", "--username=", "--role="],
    ("profile", "set"):   ["--sex=", "--age=", "--height=", "--weight=", "--activity=", "--goal="],

    ("plan", "generate"): ["--split=", "--days="],
    ("plan", "groceries"):["--target=", "--P=", "--C=", "--F=", "--filters="],

    ("export", "csv"):    ["--file="],

    ("recipes", "suggest"):   ["--kcal=", "--protein=", "--filters="],
    ("recipes", "build-day"): ["--target=", "--P=", "--C=", "--F=", "--filters="],

    ("habits", "log"):    ["--water=", "--sleep=", "--steps="],
    ("nudge", None):      ["--type="],

    ("progress", "log"):  ["--weight="],

    ("workout", "log"):   ["--day=", "--ex=", "--weight=", "--reps=", "--RPE="],
    ("workout", "suggest"): ["--ex="],

    ("report", "pdf"):    ["--file=", "--days="],
    ("report", "send"):   ["--file=", "--subject=", "--text="],
    ("report", "schedule"): ["add", "list", "remove"],
    ("report", "schedule add"): ["--time=", "--day=", "--file=", "--text=", "--days="],
    ("report", "schedule remove"): ["--id="],
    ("report", "brand"):  ["--title=", "--color=", "--logo="],

    ("email", "config"):  ["--to=", "--from="],
    ("email", "test"):    ["--subject=", "--text="],

    ("app", "lang"):      ["--set="],
}

def _complete_repl(text: str, state: int):
    """الدالة التي يستدعيها readline لإكمال التبويب (Tab Completion)."""
    if readline is None:
        return None
    try:
        buffer = readline.get_line_buffer()
    except Exception:
        buffer = ""
    try:
        tokens = shlex.split(buffer)
        if buffer.endswith(" "):
            tokens.append("")  # يسمح بإكمال التوكن التالي بعد مسافة
    except Exception:
        tokens = buffer.split()

    # 1) أول كلمة: الأمر الأساسي
    if len(tokens) <= 1:
        options = sorted([c for c in _REPL_COMMANDS.keys() if c.startswith(text)])
    # 2) ثاني كلمة: الساب-أمر
    elif len(tokens) == 2:
        cmd = tokens[0]
        subs = _REPL_COMMANDS.get(cmd, [])
        options = sorted([s for s in subs if s.startswith(text)])
    # 3) بقية الكلمات: الفلاقز حسب (cmd, subcmd)
    else:
        cmd = tokens[0]
        sub = tokens[1] if tokens[1] in _REPL_COMMANDS.get(cmd, []) else None

        # حالة خاصة: report schedule لها طبقة ثالثة
        if cmd == "report" and tokens[1:2] == ["schedule"] and len(tokens) >= 3:
            sub2 = tokens[2]
            key = ("report", "schedule " + sub2)
            flags = _REPL_FLAGS.get(key, [])
        else:
            key = (cmd, sub)
            flags = _REPL_FLAGS.get(key, [])

        options = sorted([f for f in flags if f.startswith(text)])

    try:
        return options[state]
    except IndexError:
        return None

def _enable_tab_completion():
    """تفعيل الإكمال بالـTab داخل REPL (Linux/macOS/Git Bash، وعلى Windows عبر pyreadline3)."""
    if readline is None:
        return
    try:
        readline.set_completer_delims(' \t\n')  # اعتبر المسافات فقط فواصل للتوكن
        readline.set_completer(_complete_repl)
        # ربط مفتاح Tab بالإكمال (قد يختلف binding في بعض البيئات)
        try:
            readline.parse_and_bind("tab: complete")
        except Exception:
            readline.parse_and_bind("bind ^I rl_complete")
    except Exception:
        pass
# =================== End of Tab Completion block =====================


def cmd_help(*, box: bool = False, wide: bool = True) -> None:
    """Print the colored CLI help with grouped sections.

    Args:
        box: If True, draw a box/border around each section title.
        wide: If True, pad titles (wider header) for improved readability.
    """
    def add_section(title: str, body: str, color):
        section(title, body, color=color, box=box, wide=wide)

    add_section("Commands", "help | exit", color=Fore.CYAN)

    add_section("Authentication / Roles",
      "auth add-user --username=admin --role=admin --password=secret\n"
      "auth login --username=admin --password=secret\n"
      "auth logout\n"
      "auth whoami\n"
      "auth list-users\n"
      "auth role set --username=user1 --role=coach\n"
      "auth delete-user --username=user1",
      color=Fore.MAGENTA)

    add_section("Profile",
      "profile show\n"
      "profile set --sex=male|female --age=22 --height=183 --weight=110 "
      "--activity=sedentary|light|moderate|active|very_active --goal=cut|bulk|recomp",
      color=Fore.GREEN)

    add_section("Calories / Plan",
      "calories calc\n"
      "plan generate --split=upper-lower|full-body|ppl --days=3..6\n"
      "plan show\n"
      "plan volume",
      color=Fore.YELLOW)

    add_section("Groceries & Export",
      "plan groceries --target=2400 --P=180 --C=250 --F=70 [--filters=chicken,rice]\n"
      "export csv --file=week.csv",
      color=Fore.BLUE)

    add_section("Recipes",
      "recipes suggest --kcal=700 --protein=40 [--filters=chicken,rice]\n"
      "recipes build-day --target=2400 --P=180 --C=250 --F=70 [--filters=chicken,rice]",
      color=Fore.CYAN)

    add_section("Daily Advice & Habits",
      "advice daily\n"
      "habits log --water=3 --sleep=7.5 --steps=9000\n"
      "habits score\n"
      "nudge --type=water|sleep|steps|protein",
      color=Fore.MAGENTA)

    add_section("Progress",
      "progress log --weight=108.5\n"
      "progress analyze\n"
      "progress plot",
      color=Fore.GREEN)

    add_section("Workouts",
      "workout log --day=2 --ex=\"Bench Press\" --weight=80 --reps=8 --RPE=8\n"
      "workout suggest --ex=\"Bench Press\"",
      color=Fore.YELLOW)

    add_section("Reports (PDF)",
      "report pdf --file=week_report.pdf --days=7\n"
      "report brand --title=\"FitCoach — Weekly Report\" --color=#0A84FF --logo=./logo.png\n"
      "report send --file=week_report.pdf --subject=\"FitCoach — Weekly Report\" --text=\"ملخص أسبوعك جاهز\"\n"
      "report schedule add --time=21:00 --day=Sun --file=week_report.pdf --text=\"ملخص أسبوعك جاهز\" --days=7\n"
      "report schedule list\n"
      "report schedule remove --id=1",
      color=Fore.BLUE)

    add_section("Email",
      "email config --to=user@example.com [--from=coach@fitcoach.dev]\n"
      "email test --subject=\"Test\" --text=\"Hello from FitCoach\"",
      color=Fore.CYAN)

    add_section("App Language",
      "app lang --set=ar|en",
      color=Fore.MAGENTA)


# ====== State ======
STATE = AppState()

def _load() -> None:
    """Load the persisted application state (if available) into the global STATE.

    Populates profile, plan, progress, logs, settings, email endpoints, RBAC users,
    current user, and report schedules from the storage backend.

    Side Effects:
        Mutates the global ``STATE`` object with loaded values.
    """
    d = load_state()
    global STATE
    if d:
        p = d.get("profile", {})
        STATE.profile = UserProfile(**p)
        if d.get("plan"):
            from ..core.models import WeeklyPlan, Workout
            wks = []
            for w in d["plan"]["workouts"]:
                wks.append(Workout(Day=w["Day"], Focus=w["Focus"], Exercises=w["Exercises"]))
            STATE.plan = WeeklyPlan(split=d["plan"]["split"], days=d["plan"]["days"], workouts=wks)
        STATE.progress = d.get("progress", [])
        STATE.workouts_log = d.get("workouts_log", [])
        STATE.habits_log = d.get("habits_log", [])
        STATE.settings = d.get("settings", {"lang": "ar", "window": {}, "brand": {}})
        STATE.email_to = d.get("email_to")
        STATE.email_from = d.get("email_from")
        # RBAC
        from ..core.models import User
        STATE.users = [User(**u) if isinstance(u, dict) else u for u in d.get("users", [])]
        STATE.current_user = d.get("current_user")
        STATE.report_schedules = d.get("report_schedules", [])

def _save() -> None:
    """Persist the current STATE to storage.

    Serializes all mutable parts of the global ``STATE`` and invokes ``save_state``.

    Side Effects:
        Writes the serialized state via the storage layer.
    """
    d: Dict[str, Any] = {
        "profile": asdict(STATE.profile),
        "plan": asdict(STATE.plan) if STATE.plan else None,
        "progress": STATE.progress,
        "workouts_log": STATE.workouts_log,
        "habits_log": STATE.habits_log,
        "settings": STATE.settings,
        "email_to": STATE.email_to,
        "email_from": STATE.email_from,
        "users": [asdict(u) for u in STATE.users],
        "current_user": STATE.current_user,
        "report_schedules": STATE.report_schedules,
    }
    save_state(d)

def handle(cmd: str) -> str:
    """Route a single CLI command line to its handler and return the output.

    The router splits the input line with ``shlex`` (so quoted strings are respected),
    matches the primary verb (e.g., ``auth``, ``profile``, ``plan``), parses ``--key=value``
    options into a dictionary where needed, performs RBAC checks, and returns user-friendly
    text results. Returning an empty string means "no additional text to print".

    Args:
        cmd: The raw line entered by the user.

    Returns:
        str: A printable message for the user; empty string for purely-informational actions.
    """
    tokens = shlex.split(cmd)
    if not tokens:
        return ""

    # help (colored)
    if tokens[0] == "help":
        cmd_help(box=True)
        return ""

    # exit
    if tokens[0] in ("exit", "quit", "q"):
        _save(); sys.exit(0)

    # ---------- AUTH ----------
    if tokens[0] == "auth":
        if len(tokens) > 1 and tokens[1] == "add-user":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            username = opts.get("--username"); role = opts.get("--role", "user"); password = opts.get("--password", "")
            if not username or not password:
                return "Usage: auth add-user --username=<name> --role=admin|coach|user --password=<pw>"
            try:
                # First ever user is allowed without RBAC; subsequent additions require admin.
                if STATE.users:
                    err = require_role(STATE, ["admin"])
                    if err: return err
                add_user(STATE, username, role, password); _save()
                return f"User '{username}' added with role '{role}'."
            except Exception as e:
                return f"Error: {e}"
        if len(tokens) > 1 and tokens[1] == "login":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            username = opts.get("--username"); password = opts.get("--password", "")
            if not username or not password:
                return "Usage: auth login --username=<name> --password=<pw>"
            ok = auth_login(STATE, username, password); _save()
            return "Logged in." if ok else "Invalid credentials."
        if len(tokens) > 1 and tokens[1] == "logout":
            auth_logout(STATE); _save(); return "Logged out."
        if len(tokens) > 1 and tokens[1] == "whoami":
            role = current_role(STATE); return f"{STATE.current_user or 'anonymous'} ({role or 'no-role'})"
        if len(tokens) > 1 and tokens[1] == "list-users":
            err = require_role(STATE, ["admin"])
            if err: return err
            if not STATE.users: return "No users."
            lines = ["Users:"] + [f" - {u.username} [{u.role}]" for u in STATE.users]
            return "\n".join(lines)
        if len(tokens) > 1 and tokens[1] == "role" and len(tokens) > 2 and tokens[2] == "set":
            err = require_role(STATE, ["admin"])
            if err: return err
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[3:] if "=" in t)}
            username = opts.get("--username"); role = opts.get("--role")
            if not username or not role:
                return "Usage: auth role set --username=<name> --role=admin|coach|user"
            try:
                set_role(STATE, username, role); _save(); return "Role updated."
            except Exception as e:
                return f"Error: {e}"
        if len(tokens) > 1 and tokens[1] == "delete-user":
            err = require_role(STATE, ["admin"])
            if err: return err
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            username = opts.get("--username")
            if not username: return "Usage: auth delete-user --username=<name>"
            res = delete_user(STATE, username); _save(); return res
        return "Unknown auth command."

    # ---------- PROFILE ----------
    if tokens[0] == "profile":
        if len(tokens) > 1 and tokens[1] == "show":
            p = STATE.profile
            return (f"Sex: {p.sex}\nAge: {p.age}\nHeight: {p.height_cm} cm\nWeight: {p.weight_kg} kg\n"
                    f"Activity: {p.activity}\nGoal: {p.goal}")
        if len(tokens) > 1 and tokens[1] == "set":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            p = STATE.profile
            p.sex = opts.get("--sex", p.sex)
            p.age = int(opts.get("--age", p.age))
            p.height_cm = float(opts.get("--height", p.height_cm))
            p.weight_kg = float(opts.get("--weight", p.weight_kg))
            p.activity = opts.get("--activity", p.activity)
            p.goal = opts.get("--goal", p.goal)
            _save()
            return "Profile updated."
        return "Unknown profile command. Try: profile show | profile set ..."

    # ---------- CALORIES ----------
    if tokens[0] == "calories" and len(tokens) > 1 and tokens[1] == "calc":
        p = STATE.profile
        b = bmr_mifflin_st_jeor(p.sex, p.weight_kg, p.height_cm, p.age)
        t = tdee(b, p.activity)
        target = t - 400 if p.goal == "cut" else t + 250 if p.goal == "bulk" else t
        prot, carbs, fat = macro_targets(p.goal, p.weight_kg, target)
        return (f"BMR: {b:.0f} kcal\nTDEE: {t:.0f} kcal\n"
                f"Target kcal: {target:.0f}\n"
                f"Macros -> Protein: {prot} g | Carbs: {carbs} g | Fat: {fat} g")

    # ---------- PLAN ----------
    if tokens[0] == "plan":
        if len(tokens) > 1 and tokens[1] == "generate":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            split = opts.get("--split", "upper-lower")
            days = int(opts.get("--days", "4"))
            STATE.plan = generate_plan(split, days); _save()
            return f"Plan generated: {split} for {days} days."
        if len(tokens) > 1 and tokens[1] == "show":
            if not STATE.plan: return "No plan yet. Generate one with: plan generate --split=upper-lower --days=4"
            return summarize(STATE.plan)
        if len(tokens) > 1 and tokens[1] == "volume":
            if not STATE.plan: return "Generate a plan first."
            vol = count_volume(STATE.plan)
            if not vol: return "No volume data."
            lines = ["Weekly volume (sessions per muscle):"] + [f" - {m}: {c}" for m, c in sorted(vol.items())]
            return "\n".join(lines)
        if len(tokens) > 1 and tokens[1] == "groceries":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            target = int(opts.get("--target", "2200"))
            P = int(opts.get("--P", "150")); C = int(opts.get("--C", "250")); F = int(opts.get("--F", "70"))
            filters = [s.strip() for s in opts.get("--filters", "").split(",")] if "--filters" in opts else None
            picks, totals, groceries = build_grocery_list(target, P, C, F, filters)
            lines = ["Recipes picked:"] + [f" - {r['name']} ({r['kcal']} kcal, P{r['protein']} C{r['carbs']} F{r['fat']})" for r in picks]
            lines += [f"\nTotals ~ {totals['kcal']} kcal | P{totals['protein']} C{totals['carbs']} F{totals['fat']}"]
            lines += ["\nGroceries:"] + [f" - {k} x{v}" for k, v in groceries.items()]
            return "\n".join(lines)
        return "Unknown plan command."

    # ---------- EXPORT ----------
    if tokens[0] == "export" and len(tokens) > 1 and tokens[1] == "csv":
        opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
        file_path = opts.get("--file", "week.csv")
        if not STATE.plan: return "No plan to export."
        export_plan_csv(STATE.plan, file_path)
        return f"Exported: {os.path.abspath(file_path)}"

    # ---------- RECIPES ----------
    if tokens[0] == "recipes":
        if len(tokens) > 1 and tokens[1] == "suggest":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            kcal = int(opts.get("--kcal", "600")); protein = int(opts.get("--protein", "40"))
            filters = [s.strip() for s in opts.get("--filters", "").split(",")] if "--filters" in opts else None
            res = suggest(kcal, protein, filters)
            if not res: return "No recipes matched. Try widening kcal/protein range."
            lines = ["Suggested recipes:"] + [f" - {r['name']} | {r['kcal']} kcal | P{r['protein']} C{r['carbs']} F{r['fat']} | tags: {','.join(r['tags'])}" for r in res]
            return "\n".join(lines)
        if len(tokens) > 1 and tokens[1] == "build-day":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            target = int(opts.get("--target", "2200")); P = int(opts.get("--P", "150")); C = int(opts.get("--C", "250")); F = int(opts.get("--F", "70"))
            filters = [s.strip() for s in opts.get("--filters", "").split(",")] if "--filters" in opts else None
            picks, totals = build_day(target, P, C, F, filters)
            lines = ["Day plan:"] + [f" - {r['name']} ({r['kcal']} kcal, P{r['protein']} C{r['carbs']} F{r['fat']})" for r in picks]
            lines += [f"\nTotals ~ {totals['kcal']} kcal | P{totals['protein']} C{totals['carbs']} F{totals['fat']}"]
            return "\n".join(lines)
        return "Unknown recipes command."

    # ---------- ADVICE & HABITS ----------
    if tokens[0] == "advice" and len(tokens) > 1 and tokens[1] == "daily":
        tips = daily_tips(STATE.profile)
        return "Daily Advice:\n" + "\n".join([f" - {t}" for t in tips])
    if tokens[0] == "habits":
        if len(tokens) > 1 and tokens[1] == "log":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            water = float(opts.get("--water", "0")); sleep = float(opts.get("--sleep", "0")); steps = int(opts.get("--steps", "0"))
            log_habits(STATE, water, sleep, steps); _save(); return "Habits logged."
        if len(tokens) > 1 and tokens[1] == "score":
            return score_today(STATE)
        return "Unknown habits command."
    if tokens[0] == "nudge":
        opts = {k: v for k, v in (t.split("=", 1) for t in tokens[1:] if "=" in t)}
        return nudge(opts.get("--type", ""))

    # ---------- PROGRESS ----------
    if tokens[0] == "progress":
        if len(tokens) > 1 and tokens[1] == "log":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            if "--weight" not in opts: return "Usage: progress log --weight=<kg>"
            w = float(opts.get("--weight")); STATE.progress.append({"date": datetime.date.today().isoformat(), "weight": w}); _save()
            return f"Logged weight {w} kg."
        if len(tokens) > 1 and tokens[1] == "analyze":
            weights = [x["weight"] for x in STATE.progress[-21:]]  # last 3 weeks
            rate, sug = analyze_weights(weights); return f"Rate: {rate:.2f} kg/week. {sug}"
        if len(tokens) > 1 and tokens[1] == "plot":
            values = [x["weight"] for x in STATE.progress[-40:]]; return ascii_plot(values)
        return "Unknown progress command."

    # ---------- WORKOUTS ----------
    if tokens[0] == "workout":
        if len(tokens) > 1 and tokens[1] == "log":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            day = int(opts.get("--day", "1")); ex = opts.get("--ex", ""); weight = float(opts.get("--weight", "0"))
            reps = int(opts.get("--reps", "0")); RPE = float(opts.get("--RPE", "8"))
            log_workout(STATE, day, ex, weight, reps, RPE); _save(); return "Workout logged."
        if len(tokens) > 1 and tokens[1] == "suggest":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            ex = opts.get("--ex", ""); return suggest_loads(STATE, ex)
        return "Unknown workout command."

    # ---------- REPORT ----------
    if tokens[0] == "report":
        if len(tokens) > 1 and tokens[1] == "pdf":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            file_path = opts.get("--file", "week_report.pdf"); days = int(opts.get("--days", "7"))
            build_weekly_pdf(STATE, file_path, days=days); return f"PDF generated: {os.path.abspath(file_path)}"
        if len(tokens) > 1 and tokens[1] == "send":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            file_path = opts.get("--file", "week_report.pdf")
            subject = opts.get("--subject", "FitCoach — Weekly Report")
            text = opts.get("--text", "Your weekly report is attached.")
            if not STATE.email_to: return "Set Email recipient first: email config --to=user@example.com"
            send_email_smtp(STATE.email_to, subject, text, attachments=[file_path], from_addr=STATE.email_from)
            return "PDF sent via Email."
        if len(tokens) > 1 and tokens[1] == "schedule":
            err = require_role(STATE, ["admin"])
            if err: return err
            if len(tokens) > 2 and tokens[2] == "add":
                opts = {k: v for k, v in (t.split("=", 1) for t in tokens[3:] if "=" in t)}
                time_hhmm = opts.get("--time", "21:00"); day = opts.get("--day", "Sun")
                file_path = opts.get("--file", "week_report.pdf"); text = opts.get("--text", "Your weekly report is attached.")
                days = int(opts.get("--days", "7"))
                new_id = (max([j.get("id", 0) for j in STATE.report_schedules], default=0) + 1)
                STATE.report_schedules.append({"id": new_id, "time_hhmm": time_hhmm, "day": day,
                                               "file": file_path, "text": text, "days": days,
                                               "active": True, "last_sent_date": ""})
                _save(); return f"Added weekly report schedule #{new_id} ({day} {time_hhmm})."
            if len(tokens) > 2 and tokens[2] == "list":
                if not STATE.report_schedules: return "No report schedules."
                lines = ["Report schedules:"] + [f" - #{j['id']} {j['day']} {j['time_hhmm']} file={j.get('file')} last={j.get('last_sent_date','-')}" for j in STATE.report_schedules]
                return "\n".join(lines)
            if len(tokens) > 2 and tokens[2] == "remove":
                opts = {k: v for k, v in (t.split("=", 1) for t in tokens[3:] if "=" in t)}
                jid = int(opts.get("--id", "0")); before = len(STATE.report_schedules)
                STATE.report_schedules = [j for j in STATE.report_schedules if j.get("id") != jid]; _save()
                return "Removed." if len(STATE.report_schedules) < before else "Not found."
        if len(tokens) > 1 and tokens[1] == "brand":
            err = require_role(STATE, ["admin"])
            if err: return err
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            title = opts.get("--title"); color = opts.get("--color"); logo = opts.get("--logo")
            brand = STATE.settings.get("brand", {})
            if title: brand["title"] = title
            if color: brand["color"] = color
            if logo: brand["logo"] = logo
            STATE.settings["brand"] = brand; _save(); return f"Brand set: {brand}"
        return "Unknown report command."

    # ---------- EMAIL ----------
    if tokens[0] == "email":
        if len(tokens) > 1 and tokens[1] == "config":
            err = require_role(STATE, ["admin"])
            if err: return err
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            STATE.email_to = opts.get("--to", STATE.email_to)
            STATE.email_from = opts.get("--from", STATE.email_from)
            _save(); return f"Email set. To={STATE.email_to} From={STATE.email_from or '(env FROM_EMAIL)'}"
        if len(tokens) > 1 and tokens[1] == "test":
            opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
            subj = opts.get("--subject", "FitCoach Test"); text = opts.get("--text", "Hello from FitCoach")
            if not STATE.email_to: return "Please set recipient first: email config --to=user@example.com"
            send_email_smtp(STATE.email_to, subj, text, attachments=[], from_addr=STATE.email_from)
            return "Test email sent."
        return "Unknown email command."

    # ---------- APP ----------
    if tokens[0] == "app" and len(tokens) > 1 and tokens[1] == "lang":
        opts = {k: v for k, v in (t.split("=", 1) for t in tokens[2:] if "=" in t)}
        lang = opts.get("--set")
        if lang not in ("ar", "en"): return "Supported: ar | en"
        STATE.settings["lang"] = lang; _save(); return f"Language set to {lang}."

    return "Unknown command. Type 'help'."

def main() -> None:
    """Application entrypoint: bootstrap theme, show first-run help, start scheduler, and REPL loop.

    Behavior:
        - Loads persisted state.
        - Honors ``--no-color`` flag to disable colored output.
        - Applies a color theme.
        - Prints banner + colored help (boxed).
        - Starts the weekly report email scheduler (non-blocking).
        - Enters a simple REPL (read-eval-print loop) until EOF or 'exit'.

    Side Effects:
        Reads from stdin, writes to stdout, and persists state on exit.
    """
    _load()

    # Honor --no-color if present
    argv = sys.argv[1:]
    if "--no-color" in argv:
        set_color_enabled(False)
        argv = [a for a in argv if a != "--no-color"]

    # Theme
    set_theme(
        primary=Fore.CYAN,
        success=Fore.GREEN,
        warning=Fore.YELLOW,
        danger=Fore.RED,
        muted=Fore.WHITE,
    )

    # First-run banner & help
    banner("FitCoach CLI — type 'help' to see commands, 'exit' to quit.")
    cmd_help(box=True)

    # Start background scheduler
    start_report_scheduler_email(lambda: STATE, build_weekly_pdf, send_email_smtp, interval_sec=30)

    # 🔽 تفعيل إكمال الأوامر بالـTab داخل REPL
    _enable_tab_completion()  # يربط completer بالـreadline (يدعم Git Bash/Unix؛ على ويندوز عبر pyreadline3)

    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                print()
                break
            if not line:
                continue
            out = handle(line)
            if out:
                print(out)
    finally:
        _save()
    print("Goodbye!")
