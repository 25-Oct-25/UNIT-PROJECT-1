# fitcoach_cli/cli/console.py
from colorama import init, Fore, Style
init(autoreset=True, convert=True, strip=False)

def section(title: str, body: str, color=Fore.CYAN, bright: bool = True) -> None:
    ttl = title.strip()
    line = "─" * len(ttl)
    print((Style.BRIGHT if bright else "") + color + ttl + Style.RESET_ALL)
    print(color + line + Style.RESET_ALL)
    print(color + body.rstrip() + Style.RESET_ALL, end="\n\n")
