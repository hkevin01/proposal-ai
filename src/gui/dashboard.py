# Submission Dashboard Stub
class SubmissionDashboard:
    def __init__(self):
        self.submissions = []
        self.deadlines = []
        self.metrics = {}

    def show_dashboard(self):
        return {
            'submissions': self.submissions,
            'deadlines': self.deadlines,
            'metrics': self.metrics
        }

    def update_metrics(self):
        self.metrics = {
            'total_submissions': len(self.submissions),
            'upcoming_deadlines': len([d for d in self.deadlines if d['date'] > '2025-07-21'])
        }
        return self.metrics

    def show_deadline_calendar(self):
        return self.deadlines

    def show_status_overview(self):
        return [{'id': s['id'], 'status': s['status']} for s in self.submissions]
