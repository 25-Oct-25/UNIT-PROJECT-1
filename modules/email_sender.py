# modules/email_sender.py
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
    if TEST_MODE:
        print(f"[TEST MODE] Would send email to {to_email}: {subject}\nHTML={html}\n{body[:400]}...\nAttachments: {attachments}")
        return True

    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject

    if html:
        msg.add_alternative(body, subtype='html')
    else:
        msg.set_content(body)

    # attach files
    if attachments:
        for path in attachments:
            try:
                with open(path, 'rb') as f:
                    data = f.read()
                msg.add_attachment(data, maintype='application', subtype='octet-stream', filename=os.path.basename(path))
            except Exception as e:
                print(f"Attachment error: {e}")

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
