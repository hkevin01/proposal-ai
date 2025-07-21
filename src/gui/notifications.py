# Notification System Stub
class NotificationSystem:
    def __init__(self):
        self.notifications = []

    def send_deadline_reminder(self, deadline):
        self.notifications.append({'type': 'reminder', 'deadline': deadline})
        return True

    def send_submission_confirmation(self, submission_id):
        self.notifications.append({'type': 'confirmation', 'submission_id': submission_id})
        return True

    def send_status_alert(self, submission_id, status):
        self.notifications.append({'type': 'status_alert', 'submission_id': submission_id, 'status': status})
        return True

    def show_notification_history(self):
        return self.notifications
