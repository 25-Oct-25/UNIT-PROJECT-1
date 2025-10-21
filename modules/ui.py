# modules/ui.py
import os, sys, shutil
from colorama import init as colorama_init, Fore as F, Back as B, Style as S

# Windows: فعل ANSI تلقائي
colorama_init(autoreset=True, convert=True)

# رموز جميلة (مع بدائل لو ما دعمت الايموجي)
OK = "✅"
WARN = "⚠️"
ERR = "❌"
MAIL = "✉️"
STAR = "⭐"
TIME = "⏰"
POSTER = "🖼️"
PEOPLE = "👥"
CAL = "📅"

# لو ترميز الكونسول مو UTF-8 (إيموجي يطلع خرابيط)
if os.name == "nt" and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    OK, WARN, ERR, MAIL, STAR, TIME, POSTER, PEOPLE, CAL = "[OK]", "[!]", "[X]", "[MAIL]", "[*]", "[TIME]", "[IMG]", "[PEOPLE]", "[CAL]"

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def term_width():
    try:
        return shutil.get_terminal_size().columns
    except Exception:
        return 80

def rule(char="─", color=F.BLUE):
    w = term_width()
    print(color + char * w + S.RESET_ALL)

def header(title: str):
    w = term_width()
    title = f" {title} ".upper()
    pad = (w - len(title)) // 2
    print(F.CYAN + ("─" * max(pad, 0)) + title + ("─" * max(pad, 0)) + S.RESET_ALL)

def section(title: str):
    print(F.MAGENTA + S.BRIGHT + f"• {title}" + S.RESET_ALL)

def kv(key: str, val: str):
    print(F.WHITE + S.BRIGHT + f"{key}: " + S.RESET_ALL + F.WHITE + f"{val}" + S.RESET_ALL)

def bullet(text: str):
    print(F.WHITE + f" - {text}" + S.RESET_ALL)

def success(msg: str):
    print(F.GREEN + S.BRIGHT + f"{OK} {msg}" + S.RESET_ALL)

def warning(msg: str):
    print(F.YELLOW + S.BRIGHT + f"{WARN} {msg}" + S.RESET_ALL)

def error(msg: str):
    print(F.RED + S.BRIGHT + f"{ERR} {msg}" + S.RESET_ALL)

def prompt(label: str) -> str:
    return input(F.CYAN + S.BRIGHT + f"{label}: " + S.RESET_ALL).strip()

def menu(title: str, items: list[tuple[str, str]]):
    """items: list of (key, label)"""
    clear()
    header(title)
    rule()
    for k, label in items:
        print(F.YELLOW + S.BRIGHT + f"{k:>2}. " + S.RESET_ALL + F.WHITE + f"{label}" + S.RESET_ALL)
    rule()
    return input(F.CYAN + S.BRIGHT + "Select option: " + S.RESET_ALL).strip()

def boxed(text: str, color=F.WHITE):
    w = term_width()
    lines = [l.rstrip() for l in text.splitlines()] or [""]
    maxw = min(max(len(l) for l in lines), w-6)
    print(color + "┌" + "─"*(maxw+2) + "┐" + S.RESET_ALL)
    for l in lines:
        print(color + "│ " + S.RESET_ALL + l[:maxw] + " "*(maxw-len(l[:maxw])) + color + " │" + S.RESET_ALL)
    print(color + "└" + "─"*(maxw+2) + "┘" + S.RESET_ALL)

def badge(text: str, bg=B.BLUE, fg=F.WHITE):
    print(bg + fg + S.BRIGHT + f" {text} " + S.RESET_ALL)
