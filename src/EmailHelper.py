#Built-in modules
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
#External libraries
from dotenv import load_dotenv
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
            # Attach files safely (with protection from missing/corrupted files)
            if attachments:
                for path in attachments:
                    try:
                        if not path or not os.path.exists(path):
                            print(Fore.YELLOW + f"⚠️ Skipped missing file: {path}")
                            continue

                        with open(path, "rb") as f:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(f.read())

                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(path)}"
                        )
                        msg.attach(part)
                    except Exception as e:
                        print(Fore.RED + f"⚠️ Error attaching file {path}: {e}")

            
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)


            print(Fore.GREEN + f"\n✅ Email sent successfully to {to_email} ✉️\n" + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED+f"Error sending email: {e}")
