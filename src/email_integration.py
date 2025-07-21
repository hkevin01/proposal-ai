"""
Email Integration Module for Proposal AI
Handles sending proposals via SMTP and Gmail API
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import List, Optional

class EmailSender:
    """Handles sending emails with attachments via SMTP"""
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, to: List[str], subject: str, body: str, attachments: Optional[List[str]] = None) -> bool:
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        attachments = attachments or []
        for file_path in attachments:
            if not os.path.isfile(file_path):
                continue
            part = MIMEBase('application', 'octet-stream')
            with open(file_path, 'rb') as f:
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
            msg.attach(part)
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.username, to, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            print(f"Email send failed: {e}")
            return False

# TODO: Add Gmail API integration (OAuth2, Google API client)
# TODO: Add email template system
# TODO: Add delivery confirmation and tracking
