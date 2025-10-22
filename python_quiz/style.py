from colorama import Fore, Style, init
from art import tprint

# Enable colors with auto-reset
init(autoreset=True)

# Defaults (can be overridden by apply_color_config)
EASY_CLR   = Fore.GREEN
MEDIUM_CLR = Fore.YELLOW
HARD_CLR   = Fore.RED
TITLE_CLR  = Fore.CYAN
OK_CLR     = Fore.GREEN
WARN_CLR   = Fore.MAGENTA

HEADER_WIDTH = 34  # length of the lines above/below the subtitle

_COLOR_MAP = {
    "black": Fore.BLACK,
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
}

def apply_color_config(colors: dict | None):
    """Override default colors using names from config.json."""
    global EASY_CLR, MEDIUM_CLR, HARD_CLR, TITLE_CLR, OK_CLR, WARN_CLR
    if not colors:
        return
    EASY_CLR   = _COLOR_MAP.get(str(colors.get("easy", "")).lower(), EASY_CLR)
    MEDIUM_CLR = _COLOR_MAP.get(str(colors.get("medium", "")).lower(), MEDIUM_CLR)
    HARD_CLR   = _COLOR_MAP.get(str(colors.get("hard", "")).lower(), HARD_CLR)
    TITLE_CLR  = _COLOR_MAP.get(str(colors.get("title", "")).lower(), TITLE_CLR)
    OK_CLR     = _COLOR_MAP.get(str(colors.get("ok", "")).lower(), OK_CLR)
    WARN_CLR   = _COLOR_MAP.get(str(colors.get("warn", "")).lower(), WARN_CLR)

def color_level_tag(level_en: str) -> str:
    """Return the color based on difficulty label."""
    l = level_en.strip().lower()
    if l == "easy":
        return EASY_CLR
    if l == "medium":
        return MEDIUM_CLR
    return HARD_CLR  # hard

def colored(text: str, clr: str) -> str:
    """Wrap text with the color and reset."""
    return f"{clr}{text}{Style.RESET_ALL}"

def print_title():
    """Print banner 'Python', then a small 'Python', then centered 'Python Challenge' with equal lines."""
    print(TITLE_CLR)
    tprint("Welcome", font="small")  
    tprint("Python", font="small") 
    print(Style.RESET_ALL)

def print_winner_banner(winner_names: list, is_tie: bool):
    """
    Print winner banner:
    - Big ASCII 'Congratulations!' in green-style OK_CLR
    - Either single champion name or tie list
    """
    print()
    print(OK_CLR, end="")
    tprint("Congratulations!", font="banner")
    print(Style.RESET_ALL, end="")
    bar = "=" * (HEADER_WIDTH + 20)
    print(OK_CLR + bar)
    if is_tie:
        print(f"Tie winners: {', '.join(winner_names)}")
    else:
        print(f"Champion: {winner_names[0]}")
    print(bar + Style.RESET_ALL)
