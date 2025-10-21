# modules/ui.py (نسخة Rich)
import os, sys, shutil
from colorama import init as colorama_init
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.rule import Rule
from rich.align import Align
from rich.box import SIMPLE_HEAVY, MINIMAL_DOUBLE_HEAD
from rich.text import Text

# نفعل Colorama لويندوز (للتوافق)
colorama_init(autoreset=True, convert=True)
console = Console()

# أيقونات (مع بدائل لو ما يدعم الإيموجي)
OK = "✅"; WARN = "⚠️"; ERR = "❌"; MAIL = "✉️"; STAR = "⭐"; TIME = "⏰"; POSTER = "🖼️"; PEOPLE = "👥"; CAL = "📅"
if os.name == "nt" and (not sys.stdout.encoding or sys.stdout.encoding.lower() not in ("utf-8","utf8")):
    OK, WARN, ERR, MAIL, STAR, TIME, POSTER, PEOPLE, CAL = "[OK]", "[!]", "[X]", "[MAIL]", "[*]", "[TIME]", "[IMG]", "[PEOPLE]", "[CAL]"

# ألوان مختصرة (متوافقة مع بقية الكود)
class F:
    BLUE   = "blue"
    CYAN   = "cyan"
    GREEN  = "green"
    MAGENTA= "magenta"
    YELLOW = "yellow"
    WHITE  = "white"
class B:
    GREEN = "green"
class S:
    BRIGHT = ""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def term_width():
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80

def rule(char="─", color=F.BLUE):
    console.print(Rule(character=char, style=color))

def header(title: str):
    console.print(Rule(title.upper(), style="cyan bold"))

def section(title: str):
    console.print(f"[magenta bold]• {title}[/]")

def kv(key: str, val: str):
    t = Text.assemble((f"{key}: ", "bold white"), (val or "-", "white"))
    console.print(t)

def bullet(text: str):
    console.print(f"[white]- {text}[/]")

def success(msg: str):
    console.print(f"[bold green]{OK} {msg}[/]")

def warning(msg: str):
    console.print(f"[bold yellow]{WARN} {msg}[/]")

def error(msg: str):
    console.print(f"[bold red]{ERR} {msg}[/]")

def prompt(label: str) -> str:
    return console.input(f"[bold cyan]{label}: [/]").strip()

def boxed(text: str, color=F.WHITE):
    console.print(Panel.fit(Text.from_markup(text) if isinstance(text, str) else text,
                            border_style=color, padding=(1,2)))

def badge(text: str, bg=B.GREEN, fg=F.WHITE):
    console.print(Panel.fit(f"[bold]{text}[/]", style="black on green", padding=(0,2)))

# ===== جداول جاهزة للاستخدام =====
def table(headers: list[str], rows: list[list[str]], title: str | None = None):
    """جدول بسيط وأنيق."""
    tbl = Table(title=title, box=SIMPLE_HEAVY, show_lines=False, header_style="bold cyan")
    for h in headers:
        tbl.add_column(h, overflow="fold")
    for r in rows:
        tbl.add_row(*[str(c) if c is not None else "-" for c in r])
    console.print(tbl)

def menu(title: str, items: list[tuple[str, str]]):
    """items: list of (key, label) — يطبع جدول خيارات بشكل مرتب ويرجع اختيار المستخدم."""
    clear()
    header(title)
    tbl = Table(box=MINIMAL_DOUBLE_HEAD, header_style="bold cyan")
    tbl.add_column("Key", style="yellow", justify="right", no_wrap=True)
    tbl.add_column("Action", style="white")
    for k, label in items:
        tbl.add_row(k, label)
    console.print(tbl)
    return console.input("[bold cyan]Select option: [/]").strip()

# ===== عناصر عرض متخصصة للمشروع =====
def events_table(events: list[dict]):
    if not events:
        warning("No events.")
        return
    rows = []
    for e in events:
        rows.append([e.get("title","-"), e.get("date","-"), e.get("location","-"),
                     ", ".join([str(r) for r in e.get("reminders", [])]) or "-"])
    table(["Title","Date","Location","Reminders"], rows, title="Your Events")

def attendees_table(event_title: str, attendees: list[dict]):
    if not attendees:
        warning("No attendees found.")
        return
    rows = []
    for a in attendees:
        rows.append([a.get("name","-"), a.get("email","-"), "Attended ✅" if a.get("attended") else "Not attended ❌"])
    table([f"Attendees for '{event_title}'","Email","Status"], rows)
