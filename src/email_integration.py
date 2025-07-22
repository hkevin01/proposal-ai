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
import logging

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

# Phase 4: Submission Automation - Email Integration
class EmailIntegration:
    def __init__(self):
        self.smtp_configured = False
        self.gmail_api_configured = False

    def setup_smtp(self, server, port, username, password):
        self.smtp_server = server
        self.smtp_port = port
        self.username = username
        self.password = password
        self.smtp_configured = True
        logging.info(f"SMTP configured for {username}@{server}:{port}")

    def setup_gmail_api(self, credentials_path):
        self.gmail_api_configured = True
        logging.info(f"Gmail API configured with credentials at {credentials_path}")

    def send_email(self, to, subject, body, attachments=None):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username if hasattr(self, 'username') else 'your_email@example.com'
            msg['To'] = to if isinstance(to, str) else ', '.join(to)
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
            if self.smtp_configured:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.username, to, msg.as_string())
                server.quit()
                logging.info(f"Email sent to {to}")
                return True
            else:
                logging.error("SMTP not configured.")
                return False
        except Exception as e:
            logging.error(f"Email send failed: {e}")
            return False

    def create_template(self, template_name, content):
        # TODO: Implement email template system
        pass

    def add_attachment(self, file_path):
        # TODO: Implement attachment handling
        pass

    def track_delivery(self, message_id):
        # TODO: Implement delivery confirmation tracking
        pass

# TODO: Add Gmail API integration (OAuth2, Google API client)
# TODO: Add email template system
# TODO: Add delivery confirmation and tracking
