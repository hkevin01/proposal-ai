"""
Initial database schema for Phase 1: Requirements & Research
"""

from dataclasses import dataclass
from typing import Optional

@dataclass
class Organization:
    id: int
    name: str
    industry: str
    website: str
    contact_info: Optional[str] = None

@dataclass
class Event:
    id: int
    name: str
    organization_id: int
    date: str
    description: Optional[str] = None
    url: Optional[str] = None

@dataclass
class Proposal:
    id: int
    event_id: int
    user_id: int
    status: str
    submission_date: Optional[str] = None
    document_path: Optional[str] = None

@dataclass
class User:
    id: int
    name: str
    email: str
    affiliation: Optional[str] = None
