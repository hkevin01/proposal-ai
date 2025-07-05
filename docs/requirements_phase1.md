# Phase 1: Requirements & Research

## User Stories
- As a user, I want to search for proposal opportunities relevant to my field.
- As a user, I want to see a list of organizations and events accepting proposals.
- As a user, I want to know the requirements for each proposal submission.
- As a developer, I want a clear schema for storing organizations, events, and requirements.

## Target Organizations & Events
- International Astronautical Congress (IAC)
- NASA solicitations
- ESA calls for proposals
- Industry competitions
- Government grants
- Private sector innovation challenges

## Existing Solutions & Technologies
- GrantForward, InfoEd, and other grant search platforms
- Web scraping tools: BeautifulSoup, Scrapy
- NLP: spaCy, HuggingFace Transformers
- Automation: Selenium, Playwright

## Initial Database Schema (Draft)
- Organization: id, name, industry, website, contact_info
- Event: id, name, organization_id, date, description, url
- Proposal: id, event_id, user_id, status, submission_date, document_path
- User: id, name, email, affiliation

## Data Sources
- Official organization websites
- Event calendars
- Newsletters and mailing lists

## Deliverables
- This document (requirements_phase1.md)
- Updated test plan and progress files
