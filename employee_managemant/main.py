from colorama import Fore, Style
from system import logic

if __name__ == "__main__":
    print(Fore.BLUE + "===================================")
    print(" Welcome to Employee Management System ")
    print("===================================" + Style.RESET_ALL)
    logic.start()