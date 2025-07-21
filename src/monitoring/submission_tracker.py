# Submission Tracking Stub
class SubmissionTracker:
    def __init__(self):
        self.submissions = {}

    def track_submission(self, proposal_id, status, deadline):
        self.submissions[proposal_id] = {'status': status, 'deadline': deadline}
        return True

    def get_submission_status(self, proposal_id):
        return self.submissions.get(proposal_id, None)
