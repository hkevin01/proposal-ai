# Phase 16: Collaboration & Community Sharing

## Goals
- Enable sharing of proposals with teams
- Add commenting and feedback features
- Support team management and collaboration

## Implementation
- CollaborationManager in `src/community/collaboration.py`
- Config in `config/collaboration_settings.json`

## Next Steps
- Integrate collaboration features into GUI and API
- Expand documentation and add usage examples

## API Usage Example
```python
import requests
# Share a proposal
requests.post('http://localhost:8000/collaboration/share', json={"proposal_id": 1, "team": "TeamA"})
# Add a comment
requests.post('http://localhost:8000/collaboration/comment', json={"proposal_id": 1, "comment": "Great proposal!"})
# Create a team
requests.post('http://localhost:8000/collaboration/team', json={"team_name": "TeamA", "members": ["alice", "bob"]})
```

## GUI Usage Example
```python
window.share_proposal(1, "TeamA")
window.add_comment(1, "Great proposal!")
window.create_team("TeamA", ["alice", "bob"])
```
