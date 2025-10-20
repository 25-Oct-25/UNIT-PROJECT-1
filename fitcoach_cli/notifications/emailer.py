# Path: fitcoach_cli/notifications/email_smtp.py
# Description: Send plain-text emails (optionally with attachments) via SMTP using env-based config.

import os
import smtplib
import ssl
import mimetypes
from typing import List, Optional
from email.message import EmailMessage

def _smtp_conf() -> tuple[str, int, str, str, str]:
    """Read SMTP settings from environment variables.

    Required:
        SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL

    Returns:
        tuple[str, int, str, str, str]: (host, port, user, password, from_addr)

    Raises:
        RuntimeError: If any required variable is missing.
    """
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    pwd  = os.environ.get("SMTP_PASS")
    from_addr = os.environ.get("FROM_EMAIL")
    if not (host and user and pwd and from_addr):
        raise RuntimeError("Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL in environment.")
    return host, port, user, pwd, from_addr

def send_email_smtp(to: str, subject: str, text: str, attachments: Optional[List[str]] = None, from_addr: Optional[str] = None) -> str:
    """Send a plain-text email with optional file attachments via SMTP (STARTTLS).

    Args:
        to (str): Recipient email address.
        subject (str): Email subject line.
        text (str): Plain-text body.
        attachments (Optional[List[str]]): File paths to attach.
        from_addr (Optional[str]): Override sender address; defaults to FROM_EMAIL.

    Returns:
        str: "OK" if the message was sent.

    Raises:
        RuntimeError: If SMTP config is incomplete.
        FileNotFoundError: If an attachment path does not exist.
        smtplib.SMTPException: For SMTP-related errors.
    """
    host, port, user, pwd, default_from = _smtp_conf()
    from_addr = from_addr or default_from

    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = from_addr, to, subject
    msg.set_content(text)

    for path in (attachments or []):
        ctype, _ = mimetypes.guess_type(path)
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(path),
            )

    ctx = ssl.create_default_context()
    with smtplib.SMTP(host, port) as server:
        server.starttls(context=ctx)
        server.login(user, pwd)
        server.send_message(msg)
    return "OK"
