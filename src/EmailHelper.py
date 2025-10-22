import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import os
from colorama import Fore, Style, init


class EmailHelper:


    def __init__(self):
        load_dotenv()
        self.sender = os.getenv("EMAIL_SENDER")
        self.password = os.getenv("EMAIL_PASSWORD")

        if not self.sender or not self.password:
            print(Fore.RED+"⚠️ Missing email credentials in .env file.")
            print(Fore.RED+"Please add EMAIL_SENDER and EMAIL_PASSWORD.")
            
    
    def send_email(self, to_email, subject, body, attachments=None):
        """
        Send an email with multiple attachments.
        attachments: list of file paths (list[str])
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            # attachment file if exist
            if attachments:
                for path in attachments:
                    if path and os.path.exists(path):
                        with open(path, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(path)}"
                        )
                        msg.attach(part)
                    else:
                        print(Fore.RED+f"⚠️ Attachment not found, skipped: {path}")

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)

            print(Fore.GREEN+f"Email sent successfully to {to_email}")

        except Exception as e:
            print(Fore.RED+f"Error sending email: {e}")
