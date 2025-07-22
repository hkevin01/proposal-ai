"""
Notification Service Layer
Handles business logic for notifications and alerts.
"""

import logging
import smtplib
from email.mime.text import MIMEText

class NotificationService:
    """Service for notifications and alerts."""

    def __init__(self):
        self.logger = logging.getLogger("NotificationService")
        self.logger.info("NotificationService initialized.")

    def send_email(self, recipient: str, subject: str, body: str) -> bool:
        """Send an email notification."""
        if not recipient or "@" not in recipient:
            self.logger.error("Invalid recipient email: %s", recipient)
            return False
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = 'noreply@proposal-ai.com'
            msg['To'] = recipient
            # SMTP configuration
            smtp_server = 'localhost'  # Replace with actual SMTP server
            smtp_port = 25  # Replace with actual port if needed
            try:
                smtp = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
                smtp.sendmail(msg['From'], [recipient], msg.as_string())
                smtp.quit()
                self.logger.info("Email sent to %s: %s", recipient, subject)
                return True
            except Exception as smtp_err:
                self.logger.error("SMTP error: %s", smtp_err)
                return False
        except Exception as e:
            self.logger.error("Error sending email: %s", e)
            return False

    def send_alert(self, user_id: str, message: str) -> bool:
        """Send an alert to a user (console example)."""
        if not user_id or not message:
            self.logger.error("Invalid alert parameters: %s, %s", user_id, message)
            return False
        try:
            # Example notification logic (e.g., print to console)
            print(f"Alert for {user_id}: {message}")
            self.logger.info("Alert sent to user %s: %s", user_id, message)
            return True
        except Exception as e:
            self.logger.error("Error sending alert: %s", e)
            return False
