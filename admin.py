# admin.py
from rich.console import Console
from rich.table import Table

console = Console()

class AdminPanel:
    def __init__(self, data, save_callback=None):
        self.data = data
        self.save_callback = save_callback

    def show_panel(self):
        while True:
            console.print("\n[bold magenta]ADMIN PANEL[/bold magenta]", style="bold on blue")
            console.print(
                "1) View Users\n"
                "2) Reset User Data\n"
                "3) Delete User\n"
                "4) Delete All Users\n"
                "5) Exit Admin"
            )
            choice = input("Enter choice: ").strip()

            if choice == "1":
                table = Table(title="User Overview")
                table.add_column("Username")
                table.add_column("Score")
                table.add_column("Streak")
                table.add_column("Total Commutes")
                for u, info in self.data.items():
                    table.add_row(
                        u,
                        str(info.get("score", 0)),
                        str(info.get("streak", 0)),
                        str(len(info.get("history", [])))
                    )
                console.print(table)

            elif choice == "2":
                user = input("Enter username to reset: ").strip()
                if user in self.data:
                    self.data[user]["history"] = []
                    self.data[user]["score"] = 0
                    self.data[user]["streak"] = 0
                    console.print(f"[red]{user}'s data has been reset![/red]")
                    if callable(self.save_callback):
                        self.save_callback(self.data)
                else:
                    console.print("[red]User not found.[/red]")

            elif choice == "3":
                user = input("Enter username to delete: ").strip()
                if user in self.data:
                    confirm = input(f"Are you sure you want to delete {user}? This cannot be undone (yes/no): ").strip().lower()
                    if confirm in {"yes","y"}:
                        del self.data[user]
                        console.print(f"[red]{user} has been deleted![/red]")
                        if callable(self.save_callback):
                            self.save_callback(self.data)
                    else:
                        console.print("[yellow]Deletion cancelled.[/yellow]")
                else:
                    console.print("[red]User not found.[/red]")

            elif choice == "4":
                confirm = input("Are you sure you want to DELETE ALL USERS? This cannot be undone (yes/no): ").strip().lower()
                if confirm in {"yes","y"}:
                    self.data.clear()
                    console.print("[red]All users have been deleted![/red]")
                    if callable(self.save_callback):
                        self.save_callback(self.data)
                else:
                    console.print("[yellow]Deletion cancelled.[/yellow]")

            elif choice == "5":
                break

            else:
                console.print("[red]Invalid choice.[/red]")



