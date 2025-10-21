# modules/email_sender.py  (استبدل كامل send_email بهذا الإصدار)
import os
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage

load_dotenv()
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT') or 587)
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
TEST_MODE = os.getenv('TEST_MODE','True').lower() in ('1','true','yes')

def send_email(to_email, subject, body, attachments=None, html=False):
    """
    attachments: list of file paths
    html: if True send as text/html, else text/plain
    """
    if not SMTP_SERVER or not SMTP_PORT or not EMAIL_USER:
        print(f"[EMAIL CONFIG] Missing SMTP config. SMTP_SERVER={SMTP_SERVER}, SMTP_PORT={SMTP_PORT}, EMAIL_USER={EMAIL_USER}")
        return False

    if TEST_MODE:
        print(f"[TEST MODE] Would send email")
        print(f"  SMTP: {SMTP_SERVER}:{SMTP_PORT}")
        print(f"  FROM: {EMAIL_USER}")
        print(f"  TO  : {to_email}")
        print(f"  HTML: {html}  Attachments: {attachments}")
        print(f"  Subject: {subject}\n  Body(1st 400 chars): {body[:400]}...")
        return True

    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject

    if html:
        msg.add_alternative(body, subtype='html')
    else:
        msg.set_content(body)

    if attachments:
        for path in attachments:
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=os.path.basename(path))
            except Exception as e:
                print(f"[Attachment error] {path}: {e}")

    try:
        print(f"[SMTP] Connecting {SMTP_SERVER}:{SMTP_PORT} as {EMAIL_USER} -> {to_email} (html={html})")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=60) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"[SMTP] Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"[SMTP ERROR] {type(e).__name__}: {e}")
        return False
