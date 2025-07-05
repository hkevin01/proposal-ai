# Profiles Directory

This directory stores user profiles and uploaded resumes.

## Structure:
- `user_<id>/` - Individual user folders
  - `resume.pdf` - Original resume file
  - `profile.json` - Parsed profile data
  - `matches/` - Saved opportunity matches

## Security Note:
Ensure this directory has appropriate permissions in production and consider encryption for sensitive data.
