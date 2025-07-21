"""
Centralized error handling utilities and custom exceptions for Proposal AI.
"""

class ProposalAIError(Exception):
    """Base exception for Proposal AI."""
    pass

class DatabaseError(ProposalAIError):
    """Exception for database-related errors."""
    pass

class NotificationError(ProposalAIError):
    """Exception for notification-related errors."""
    pass

class AnalyticsError(ProposalAIError):
    """Exception for analytics-related errors."""
    pass
