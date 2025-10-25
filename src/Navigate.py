# Built-in modules
import os
import time
import msvcrt  # For detecting keypress on Windows
from colorama import Fore, Style


class Navigate:
    """Utility class to control terminal navigation and screen transitions."""

    @staticmethod
    def clear_terminal():
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def pause_and_clear(message="↩️ Returning to main menu..."):
        """
        Display a short message before clearing the terminal.
        Waits for the user to press any key to continue.
        Works across Windows, Linux, and macOS.
        """
        print(Fore.LIGHTBLUE_EX + f"\n{message}" + Style.RESET_ALL)
        print(Fore.LIGHTBLACK_EX + "\nPress any key to continue..." + Style.RESET_ALL)

        # ✅ Wait for user key press depending on the OS
        if os.name == "nt":  # Windows
            msvcrt.getch()
        else:
            try:
                input()  # fallback for non-Windows (Enter key)
            except EOFError:
                pass  # in case input stream is closed

        Navigate.clear_terminal()

    @staticmethod
    def show_header(title="🌙 AI INTERACTIVE STORY CREATOR 🌙"):
        """Display a clean header after clearing the terminal."""
        Navigate.clear_terminal()
        print(Fore.CYAN + "═" * 60)
        print(Fore.LIGHTWHITE_EX + title.center(60))
        print(Fore.CYAN + "═" * 60 + Style.RESET_ALL + "\n")
