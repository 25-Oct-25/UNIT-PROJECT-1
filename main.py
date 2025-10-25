# main.py
import sys, os
import getpass  
from datetime import datetime
from time import time
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from core.analyzer import analyze_files
from core.metadata_extractor import extract_metadata
from core.encryptor import encrypt_file, decrypt_file, generate_key
from core.result_manager import save_results

def main():
    console = Console()
    username = getpass.getuser()  

    console.print(Panel.fit(f"👋 Welcome, [bold cyan]{username}[/bold cyan]!\n"
                            "Your Digital Forensic CLI Toolkit is ready 🔍",
                            border_style="magenta", title="System Login"))

    console.print("\n[bold magenta]🕵️‍♀️ Digital Forensic CLI Toolkit[/bold magenta]\n", justify="center")

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Option", justify="center")
    table.add_column("Description", justify="left")

    table.add_row("1️⃣", "Analyze files")
    table.add_row("2️⃣", "Extract file metadata")
    table.add_row("3️⃣", "Save analysis results")
    table.add_row("4️⃣", "Encrypt results")
    table.add_row("5️⃣", "Decrypt results")
    table.add_row("6️⃣", "Exit")
    table.add_row("7️⃣", "Select and analyze a specific case")

    console.print(table)
    choice = console.input("\n[bold yellow]Select an option (1-7):[/bold yellow] ").strip()

    if choice == "1":
        directory = console.input("📁 Enter directory path: ").strip()
        keyword = console.input("🔍 Enter keyword to search (or press Enter to skip): ").strip()
        secure = console.input("🔒 Enable secure mode? (y/n): ").lower() == "y"

        console.print(f"\n[cyan]Analyzing files in {directory}...[/cyan]")
        start = time()
        results = analyze_files(directory, keyword)
        output_path = save_results(results, secure=secure)
        end = time()

        with open("forensic_log.txt", "a") as log:
            log.write(f"[{datetime.now()}] User: {username} | Option: {choice} | Directory: {directory}\n")

        if secure and output_path:
            if not os.path.exists("output/secret.key"):
                generate_key()
            console.print("[yellow]Encrypting results automatically...[/yellow]")
            encrypt_file(output_path)
            console.print("[green]✅ Secure mode complete: Results encrypted successfully.[/green]")

        console.print(f"[cyan]⏱️ Analysis completed in {end - start:.2f} seconds[/cyan]")
        console.print(Panel.fit("Operation completed successfully ✅", border_style="green"))

    elif choice == "2":
        file_path = console.input("📂 Enter file path: ").strip()
        metadata = extract_metadata(file_path)
        console.print(Panel(str(metadata), title="File Metadata", border_style="blue"))

    elif choice == "3":
        file_name = console.input("📝 Enter analyzed file name: ").strip()
        data = {"file": file_name, "status": "analyzed"}
        secure = console.input("🔒 Enable secure mode? (y/n): ").lower() == "y"
        save_results(data, secure=secure)
        console.print(Panel.fit("Operation completed successfully ✅", border_style="green"))

    elif choice == "4":
        file_path = console.input("Enter result file path to encrypt: ").strip()
        if not os.path.exists("output/secret.key"):
            generate_key()
        encrypt_file(file_path)
        console.print("[green]✅ File encrypted successfully![/green]")

    elif choice == "5":
        file_path = console.input("Enter encrypted file path to decrypt: ").strip()
        decrypt_file(file_path)
        console.print("[green]✅ File decrypted successfully![/green]")

    elif choice == "6":
        console.print("\n[bold magenta]Exiting Forensic CLI Toolkit 👋[/bold magenta]")
        console.print(Panel.fit(
            f"🧾 Session Summary\n"
            f"User: [bold cyan]{username}[/bold cyan]\n"
            f"Session Ended: [bold yellow]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/bold yellow]\n"
            "Thank you for using the system 🔐",
            border_style="green", title="Goodbye")
        )

    elif choice == "7":
        cases_dir = os.path.join(os.path.dirname(__file__), "cases")

        if not os.path.exists(cases_dir):
            console.print("[red]⚠️ No cases folder found.[/red]")
            return

        case_folders = [f for f in os.listdir(cases_dir) if os.path.isdir(os.path.join(cases_dir, f))]

        if not case_folders:
            console.print("[red]⚠️ No cases available for analysis.[/red]")
            return

        console.print(f"\n📁 [cyan]Found {len(case_folders)} case(s): {', '.join(case_folders)}[/cyan]")
        console.print("\n🎯 Choose which case you want to analyze:")

        for idx, case in enumerate(case_folders, start=1):
            console.print(f"[bold cyan]{idx}[/bold cyan]. {case}")

        choice_case = console.input("\nEnter the case number: ").strip()

        try:
            case_index = int(choice_case) - 1
            if case_index < 0 or case_index >= len(case_folders):
                console.print("[red]❌ Invalid selection. Please run again and choose a valid case number.[/red]")
                return
        except ValueError:
            console.print("[red]❌ Invalid input. Please enter a number.[/red]")
            return

        selected_case = case_folders[case_index]
        secure_mode = console.input("🔒 Enable secure mode? (y/n): ").lower() == "y"

        console.print(f"\n[bold yellow]🔍 Processing selected case:[/bold yellow] [green]{selected_case}[/green]")
        case_path = os.path.join(cases_dir, selected_case)

        start = time()
        results = analyze_files(case_path, keyword="")
        output_path = save_results(results, secure=secure_mode)

        if secure_mode and output_path:
            if not os.path.exists("output/secret.key"):
                generate_key()
            encrypt_file(output_path)
            console.print(f"[green]✅ Case {selected_case} encrypted and saved successfully![/green]")

        end = time()
        console.print(f"[cyan]⏱️ Total processing time: {end - start:.2f} seconds[/cyan]")
        console.print(Panel.fit(f"📋 [bold]Case {selected_case} analyzed successfully ✅[/bold]",
                                border_style="cyan", title="Case Analysis Complete"))

    else:
        console.print("[red]❌ Invalid choice. Try again![/red]")


if __name__ == "__main__":
    main()
