from rich.console import Console 
from rich.panel import Panel 
from rich.align import Align 
from user_service import register_user, login_user, reset_password_flow
from campaign_manager import display_campaigns, add_campaign, join_campaign, display_campaign_members
from security import validate_password, get_valid_email
import os


os.system('cls' if  os.name=='nt'else 'clear')


console = Console()

def main():

    title = Panel (
   "FLIGHT CAMPAIGN MANAGER ✈️", border_style="white", padding=(0,2) ,expand=False)
    console.print(Align.center(title))


    while True:
        console.print("[bold bright_white]1.[/bold bright_white] [bold #8773a1]Leader[/bold #8773a1]")
        console.print("[bold bright_white]2.[/bold bright_white] [bold #8773a1]Member[/bold #8773a1]")
        console.print("[bold bright_white]3.[/bold bright_white] [bold #8773a1]Exit[/bold #8773a1]")

        choice = console.input("\n[bold bright_white]Select your role:[/bold bright_white] ")
        if choice == '1':
            leader_menu() # Enter leader menu
        elif choice == '2':
            member_menu() # Enter member menu
        elif choice == '3':
            console.print(" THANK YOU FOR USING FLIGHT CAMPAIGN MANAGER! 🛫", style="#8EA891")
            break
        else:
            console.print("⚠️"" Invalid choice.", style="#c67a7a")



# Leader menu
def leader_menu():
    while True:
        console.print("\n[bold bright_white]1.[/bold bright_white] [bold #8773a1]Login[/bold #8773a1]")
        console.print("[bold bright_white]2.[/bold bright_white] [bold #8773a1]Register[/bold #8773a1]")
        console.print("[bold bright_white]3.[/bold bright_white] [bold #8773a1]Forgot Password[/bold #8773a1]")
        console.print("[bold bright_white]4.[/bold bright_white] [bold #8773a1]Back[/bold #8773a1]")

        choice = input("Choose an option: ")
        if choice == '1':
            email = input("Email: ")
            password = input("Password: ")
            if login_user(email, password, 'Leader'):
                leader_dashboard(email)
                break
        elif choice == '2':
            register_flow('Leader')
            break
        elif choice == '3':
            email = input("Enter your email for reset: ")
            reset_password_flow(email)
        elif choice == '4':
            break


# Member menu
def member_menu():
    while True:
        console.print("\n[bold bright_white]1.[/bold bright_white] [bold #8773a1]Login[/bold #8773a1]")
        console.print("[bold bright_white]2.[/bold bright_white] [bold #8773a1]Register[/bold #8773a1]")
        console.print("[bold bright_white]3.[/bold bright_white] [bold #8773a1]Forgot Password[/bold #8773a1]")
        console.print("[bold bright_white]4.[/bold bright_white] [bold #8773a1]Back[/bold #8773a1]")

        choice = input("Choose an option: ")
        if choice == '1':
            email = input("Email: ")
            password = input("Password: ")
            if login_user(email, password, 'Member'):
                member_dashboard(email) # Open member dashboard
                break
        elif choice == '2':
            register_flow('Member') # Register a new member
            break
        elif choice == '3':
            email = input("Enter your email for reset: ")
            reset_password_flow(email)
        elif choice == '4':
            break


# User registration flow
def register_flow(role):
    while True:
        name = input("Full name : ").strip()
        if len(name.split()) < 2:
            console.print("⚠️"" Name must include first and last name.", style="#c67a7a")
            continue
        break

    while True:
        email_input = input("Email: ").strip()
        if not email_input:
           console.print("⚠️"" Email cannot be empty.", style="#c67a7a")   
           continue

        email = get_valid_email(email_input) # Validate email
        if email:
            break

    while True:
       password = input("Password: ").strip()
       if not password:
        console.print("⚠️"" Password cannot be empty.", style="#c67a7a")
        continue

       verify_password = input("Verify Password: ").strip()
       if password != verify_password:
          console.print("⚠️"" Passwords do not match.", style="#c67a7a")
          continue

       break

    if register_user(email, password, role, name):
        if role == 'Leader':
            leader_dashboard(email) # Open leader dashboard after registration
        else:
            member_dashboard(email) # Open member dashboard after registration



# Leader dashboard
def leader_dashboard(email):
    while True:
        console.print("\n👤 Leader Dashboard", style="#CDC9DF")
        console.print("===================")
        console.print("[bold bright_white]1.[/bold bright_white] [bold #8773a1]Display campaigns[/bold #8773a1]")
        console.print("[bold bright_white]2.[/bold bright_white] [bold #8773a1]Add campaign[/bold #8773a1]")
        console.print("[bold bright_white]3.[/bold bright_white] [bold #8773a1]View campaign members[/bold #8773a1]")
        console.print("[bold bright_white]4.[/bold bright_white] [bold #8773a1]Exit[/bold #8773a1]")

        choice = input("Select option: ")
        if choice == '1':
            display_campaigns()# Show all campaigns
        elif choice == '2':
            add_campaign(email) # Add new campaign
        elif choice == '3':
            display_campaign_members(email) # Show campaign members
        elif choice == '4':
            break



# Member dashboard
def member_dashboard(email):
    while True:
        console.print("\n👥 Member Dashboard", style="#CDC9DF")
        console.print("===================")
        console.print("[bold bright_white]1.[/bold bright_white] [bold #8773a1]Display campaigns[/bold #8773a1]")
        console.print("[bold bright_white]2.[/bold bright_white] [bold #8773a1]Join a campaign[/bold #8773a1]")
        console.print("[bold bright_white]3.[/bold bright_white] [bold #8773a1]Exit[/bold #8773a1]")

        choice = input("Select option: ")
        if choice == '1':
            display_campaigns() # Show campaigns
        elif choice == '2':
            name = input("Your full name: ")
            join_campaign(name, email)  # Join a campaign
        elif choice == '3':
            break


if __name__ == "__main__":
    main()
