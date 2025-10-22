# email_ella.py
import smtplib
from email.message import EmailMessage
from colorama import Fore, Style

def send_email(sender_email, sender_password, to_email, subject, message):
    if not sender_email or not sender_password:
        print(Fore.RED + "⚠️ Please provide sender email and password!" + Style.RESET_ALL)
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = to_email
        msg.set_content(message)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(Fore.GREEN + f"✅ Email sent to {to_email}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"❌ Error sending email: {e}" + Style.RESET_ALL)
