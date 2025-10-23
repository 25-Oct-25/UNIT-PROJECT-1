# Prefer package imports (python -m pharmacy_v1.main). If that fails (running
# as a script from inside the package dir), fall back to local imports.
try:
    from pharmacy_v1.pharmacy import *
    from pharmacy_v1.gemini_client import ask_gemini
    from pharmacy_v1.admin import admin_add, admin_update, admin_remove
except Exception:
    from pharmacy import *
    from gemini_client import ask_gemini
    from admin import admin_add, admin_update, admin_remove

# Banner utilities: pyfiglet + colorama (optional). Falls back to simple text when
# dependencies are missing. The banner prints a large 'Smart Pharmacy' in a
# slant-like font with a cyan/green gradient and 'Inventory System' below it.
try:
    import pyfiglet
except Exception:
    pyfiglet = None

try:
    from colorama import Fore, Style, init as _colorama_init
    _colorama_init(autoreset=True)
except Exception:
    Fore = None
    Style = None

import re

def _strip_ansi(s):
    return re.sub(r"\x1b\[[0-9;]*m", "", s)

def print_banner():
    # Generate ascii art (or fallback)
    if pyfiglet and Fore and Style:
        # Large title using pyfiglet
        big = pyfiglet.figlet_format(" Smart Pharmacy", font="slant")

        # Build a blue->purple-ish gradient using available color constants
        palette = [Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

        colored_lines = []
        for line in big.splitlines():
            out = []
            # count visible chars to map gradient
            visible = [c for c in line if c != ' ']
            vlen = len(visible) if visible else 1
            vis_idx = 0
            for ch in line:
                if ch == ' ':
                    out.append(ch)
                else:
                    # map vis_idx across palette
                    ratio = vis_idx / max(1, vlen - 1)
                    # choose color by ratio
                    color_index = int(ratio * (len(palette) - 1))
                    color = palette[color_index]
                    out.append(f"{color}{ch}{Style.RESET_ALL}")
                    vis_idx += 1
            colored_lines.append(''.join(out))

        # subtitle
        subtitle = "Inventory System"

        # compute width (strip ANSI)
        width = max(len(_strip_ansi(l)) for l in colored_lines)

        # Print cyan separator line with centered emoji-style header
        header_text = '🧬 Smart Pharmacy'
        inner_text = f' {header_text} '
        # Ensure total width is at least the length of the header
        if width < len(inner_text):
            width = len(inner_text)
        pad_total = width - len(inner_text)
        left_pad = pad_total // 2
        right_pad = pad_total - left_pad
        cyan_line = Fore.CYAN + ('=' * left_pad) + inner_text + ('=' * right_pad) + Style.RESET_ALL
        print(cyan_line)
        print()

        # print big title centered
        for l in colored_lines:
            raw = _strip_ansi(l)
            pad = max(0, width - len(raw))
            print(' ' * (pad // 2) + l)

        print()
        # small centered subtitle in white
        print(Fore.WHITE + subtitle.center(width) + Style.RESET_ALL)

        # cyan separator dashes (match width of header)
        print(Fore.CYAN + '-' * width + Style.RESET_ALL)
    else:
        # graceful fallback
        if Fore and Style:
            cyan = Fore.CYAN
            white = Fore.WHITE
            reset = Style.RESET_ALL
            print(cyan + '=== 🧬 Smart Pharmacy ===' + reset)
            print()
            print(white + 'Inventory System'.center(40) + reset)
            print(cyan + '----' + reset)
        else:
            print("=== Smart Pharmacy ===\n\nInventory System")

class Menu:
    COMMANDS = {
        "list":       lambda args: list_medicines(),
        "search":     lambda args: search_medicine(args[0]) if args else print("Usage: search <name>"),
        # add <name> [qty]
        "add":        lambda args: (_cmd_add(args) if args else print("Usage: add <name> [qty]")),
        "remove":     lambda args: remove_from_cart(args[0]) if args else print("Usage: remove <name>"),
        "cart":       lambda args: show_cart(),
        "checkout":   lambda args: checkout(),
        "track":      lambda args: track_order(args[0]) if args else print("Usage: track <order_id>"),
        "admin add":     lambda args: admin_add(*args) if len(args) == 4 else print("Usage: admin add <name> <price> <qty> <category>"),
        "admin update":  lambda args: admin_update(*args) if len(args) == 4 else print("Usage: admin update <name> <price> <qty> <category>"),
        "admin remove":  lambda args: admin_remove(args[0]) if args else print("Usage: admin remove <name>"),
        "gemini":     lambda args: print("\nGemini:", ask_gemini(" ".join(args)) if args else ask_gemini(input("Ask Gemini: ")))
    }

    HELP_TEXT = {
        "list": "Show available medicines",
        "search <name>": "Search for a medicine",
        "add <name>": "Add medicine to cart",
        "remove <name>": "Remove medicine from cart",
        "cart": "Show items in cart",
        "checkout": "Proceed to checkout",
        "track <order_id>": "Track order status",
        "admin add <n> <p> <q> <c>": "Add medicine (admin only)",
        "admin update <n> <p> <q> <c>": "Update medicine (admin only)",
        "admin remove <name>": "Remove medicine (admin only)",
        "gemini <question>": "Ask AI for product recommendations (non-medical)",
        "help": "Show this help menu",
        "exit": "Exit system",
    }

    def __init__(self):
        # Print decorative banner
        try:
            print_banner()
        except Exception:
            print("    🧬 Pharmacy Inventory System 🧬 ")

    def show_help(self):
        print("\nAvailable commands:")
        for cmd, desc in self.HELP_TEXT.items():
            print(f"  {cmd:<30} {desc}")

    def start(self):
        while True:
            raw = input("\nCommand > ").strip()
            if not raw:
                continue

            if raw == "exit":
                print("\nGoodbye!\n")
                break

            if raw == "help":
                self.show_help()
                continue

            parts = raw.split()
            cmd = parts[0] if parts[0] != "admin" else "admin " + parts[1] if len(parts) > 1 else None
            args = parts[2:] if cmd and cmd.startswith("admin") else parts[1:]

            action = self.COMMANDS.get(cmd)
            action(args) if action else print("Invalid. Type 'help' to see commands.")

def _cmd_add(args):
    # helper to support optional quantity
    if not args:
        print("Usage: add <name> [qty]")
        return
    name = args[0]
    qty = args[1] if len(args) > 1 else 1
    try:
        add_to_cart(name, qty)
    except TypeError:
        # fallback if add_to_cart signature differs
        add_to_cart(name)
    

if __name__ == "__main__":
    Menu().start()
