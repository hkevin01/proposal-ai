# Proposal CRUD, Version Control, Collaboration Stub
class ProposalManager:
    def __init__(self):
        self.proposals = {}
        self.versions = {}
        self.collaborators = {}

    def save_proposal(self, proposal_id, proposal_data):
        self.proposals[proposal_id] = proposal_data
        return True

    def load_proposal(self, proposal_id):
        return self.proposals.get(proposal_id, None)

    def save_version(self, proposal_id, version_data):
        self.versions.setdefault(proposal_id, []).append(version_data)
        return True

    def get_versions(self, proposal_id):
        return self.versions.get(proposal_id, [])

    def add_collaborator(self, proposal_id, user):
        self.collaborators.setdefault(proposal_id, set()).add(user)
        return True

    def get_collaborators(self, proposal_id):
        return list(self.collaborators.get(proposal_id, set()))
