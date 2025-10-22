from colorama import Fore, Style, init
from tabulate import tabulate

init(autoreset=True)

def ctitle(text):
    line = "=" * (len(text) + 8)
    return f"\n{Fore.CYAN}{Style.BRIGHT}{line}\n   {text}\n{line}{Style.RESET_ALL}"

def cinfo(text):
    return f"{Fore.BLUE}{text}{Style.RESET_ALL}"

def cgood(text):
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"

def cwarn(text):
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"

def cbad(text):
    return f"{Fore.RED}{text}{Style.RESET_ALL}"

def print_table(data, headers=None):
    if not data:
        print(cwarn("No data to display."))
        return
    print(Fore.LIGHTWHITE_EX + tabulate(data, headers=headers, tablefmt="fancy_grid"))

def colored_bar(progress):
    blocks = progress // 10
    bar = "#" * blocks + "." * (10 - blocks)
    if progress < 50:
        color = Fore.RED
    elif progress < 90:
        color = Fore.YELLOW
    else:
        color = Fore.GREEN
    return f"{color}[{bar}]{Style.RESET_ALL}"

def show_logo():
    print(f"{Fore.CYAN}{Style.BRIGHT}")
    print("═" * 60)
    print("             🎓  CourseHub Learning System  🎓")
    print("═" * 60)
    print(f"{Style.RESET_ALL}")