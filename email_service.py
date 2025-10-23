import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from rich.console import Console

console = Console()

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


def send_email(to_email, subject, message):
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        console.print("⚠️"" Email or password not set in .env file!", style="#c67a7a")
        return

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SENDER_EMAIL # Sender
        msg['To'] = to_email# Recipient
        msg.set_content(message)



        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)

        console.print(f"✅ Email sent to [bold]{to_email}[/bold]", style="#8EA891")

    except Exception as e:
        # Handle any errors during sending
        console.print(f"⚠️"" Error sending email: {e}", style="#c67a7a")

