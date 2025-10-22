from tabulate import tabulate
from colorama import init, Fore, Style
init(autoreset=True)

def cinfo(t):  return f"{Fore.CYAN}{t}{Style.RESET_ALL}"
def cgood(t):  return f"{Fore.GREEN}{t}{Style.RESET_ALL}"
def cbad(t):   return f"{Fore.RED}{t}{Style.RESET_ALL}"
def cwarn(t):  return f"{Fore.YELLOW}{t}{Style.RESET_ALL}"
def ctitle(t): return f"{Style.BRIGHT}{t}{Style.RESET_ALL}"

def print_table(rows, headers):
    if not rows:
        print(cwarn("No data to show.")); return
    print(tabulate(rows, headers=headers, tablefmt="github", floatfmt=".2f"))