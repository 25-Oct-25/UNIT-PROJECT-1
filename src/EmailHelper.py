import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv
import os

class EmailHelper:
    """
    إرسال رسائل بريد إلكتروني مع مرفقات متعددة (PDF/TXT...).
    يعتمد على بيانات الدخول من .env:
      EMAIL_SENDER, EMAIL_PASSWORD
    """

    def __init__(self):
        load_dotenv()
        self.sender = os.getenv("EMAIL_SENDER")
        self.password = os.getenv("EMAIL_PASSWORD")

        if not self.sender or not self.password:
            print("⚠️ Missing email credentials in .env file.")
            print("Please add EMAIL_SENDER and EMAIL_PASSWORD.")
            # ما نرفع استثناء عشان ما نكسر البرنامج؛ فقط تنبيه.
    
    def send_email(self, to_email, subject, body, attachments=None):
        """
        إرسال بريد بمرفقات متعددة.
        attachments: قائمة مسارات ملفات (list[str])
        """
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender
            msg["To"] = to_email
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            # إرفاق الملفات إن وجدت
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
                        print(f"⚠️ Attachment not found, skipped: {path}")

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(self.sender, self.password)
                server.send_message(msg)

            print(f"Email sent successfully to {to_email}")

        except Exception as e:
            print(f"Error sending email: {e}")
