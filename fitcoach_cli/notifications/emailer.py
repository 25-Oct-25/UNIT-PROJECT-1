# Path: fitcoach_cli/notifications/email_smtp.py
# Description: Send emails (HTML + plain text) via SMTP with UTF-8 headers and attachments.

import os
import smtplib
import ssl
import mimetypes
from typing import List, Optional, Union
from email.message import EmailMessage
from email.header import Header
from email.utils import formataddr

def _smtp_conf() -> tuple[str, int, str, str, str]:
    """Read SMTP settings from environment variables.

    Required:
        SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL
    """
    host = os.environ.get("SMTP_HOST")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    pwd  = os.environ.get("SMTP_PASS")
    from_addr = os.environ.get("FROM_EMAIL")

    if not (host and user and pwd and from_addr):
        raise RuntimeError(
            "Set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, FROM_EMAIL in environment."
        )
    return host, port, user, pwd, from_addr

def _as_list(x: Union[str, List[str], None]) -> List[str]:
    if not x:
        return []
    if isinstance(x, str):
        return [x]
    return list(x)

def send_email_smtp(
    to: Union[str, List[str]],
    subject: str,
    text: str,
    attachments: Optional[List[str]] = None,
    from_addr: Optional[str] = None,
    html: Optional[str] = None,
    from_name: Optional[str] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
) -> str:
    """Send an email (HTML + plain text) with optional file attachments via SMTP.

    Args:
        to: Recipient email (string or list).
        subject: Email subject (UTF-8 safe).
        text: Plain-text body (fallback if client doesn't render HTML).
        attachments: Optional file paths.
        from_addr: Override sender; defaults to FROM_EMAIL.
        html: Optional HTML body (if provided, sent as multipart/alternative).
        from_name: Optional display name for From (UTF-8 safe, e.g., عربي).
        cc, bcc: Optional CC/BCC recipients.

    Returns:
        "OK" if sent.
    """
    host, port, user, pwd, default_from = _smtp_conf()
    from_addr = from_addr or default_from

    to_list  = _as_list(to)
    cc_list  = _as_list(cc)
    bcc_list = _as_list(bcc)

    if not to_list:
        raise ValueError("Recipient 'to' is required.")

    # Build message
    msg = EmailMessage()

    # Proper UTF-8 headers (Arabic-safe)
    if from_name:
        msg["From"] = formataddr((str(Header(from_name, "utf-8")), from_addr))
    else:
        msg["From"] = from_addr

    msg["To"] = ", ".join(to_list)
    if cc_list:
        msg["Cc"] = ", ".join(cc_list)
    # BCC is not added to headers; included in send list only

    msg["Subject"] = str(Header(subject, "utf-8"))

    # Body: multipart/alternative if HTML is provided
    if html:
        # Text part (fallback)
        msg.set_content(text or "Your email client does not support HTML.")
        # HTML part
        msg.add_alternative(html, subtype="html")
    else:
        # Plain text only
        msg.set_content(text or "")

    # Attachments
    for path in (attachments or []):
        if not os.path.exists(path):
            raise FileNotFoundError(f"Attachment not found: {path}")
        ctype, _ = mimetypes.guess_type(path)
        if ctype is None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        with open(path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=os.path.basename(path),  # filename header handled safely
            )

    # Prepare recipients (To + CC + BCC)
    all_rcpts = to_list + cc_list + bcc_list

    # Connect and send
    ctx = ssl.create_default_context()
    debug = os.getenv("EMAIL_DEBUG") == "1"

    if port == 465:
        with smtplib.SMTP_SSL(host, port, context=ctx) as server:
            if debug:
                server.set_debuglevel(1)
            server.login(user, pwd)
            server.send_message(msg, from_addr=from_addr, to_addrs=all_rcpts)
    else:
        with smtplib.SMTP(host, port) as server:
            if debug:
                server.set_debuglevel(1)
            server.ehlo()
            server.starttls(context=ctx)
            server.ehlo()
            server.login(user, pwd)
            server.send_message(msg, from_addr=from_addr, to_addrs=all_rcpts)

    return "OK"
