import os
import mimetypes
import smtplib
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _smtp_config():
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    pwd  = os.getenv("SMTP_PASS")
    use_tls = os.getenv("SMTP_STARTTLS", "1") not in ("0", "false", "False")
    if not user or not pwd:
        raise RuntimeError("SMTP_USER/SMTP_PASS missing. Put them in .env")
    return host, port, user, pwd, use_tls

def send_email(to_email: str, subject: str, body: str, attachments: list[str] | None = None):
    host, port, user, pwd, use_tls = _smtp_config()

    msg = EmailMessage()
    msg["From"] =f"CourseHub <{user}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if attachments:
        for path in attachments:
            p = Path(path)
            if not p.exists() or not p.is_file():
                continue
            ctype, _ = mimetypes.guess_type(str(p))
            if ctype is None:
                ctype = "application/octet-stream"
            maintype, subtype = ctype.split("/", 1)
            with open(p, "rb") as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=p.name)

    with smtplib.SMTP(host, port) as s:
        if use_tls:
            s.starttls()
        s.login(user, pwd)
        s.send_message(msg)
