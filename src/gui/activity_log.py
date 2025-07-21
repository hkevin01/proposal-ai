# User Activity Logging Stub
class ActivityLog:
    def __init__(self):
        self.activities = []

    def log_activity(self, username, action, timestamp):
        self.activities.append({'username': username, 'action': action, 'timestamp': timestamp})
        return True

    def get_activity_history(self, username):
        return [a for a in self.activities if a['username'] == username]
