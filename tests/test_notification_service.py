"""
Unit tests for NotificationService.
"""
import pytest
from src.services.notification_service import NotificationService

@pytest.fixture
def notification_service():
    return NotificationService()

def test_send_email(notification_service):
    result = notification_service.send_email("test@example.com", "Test", "Body")
    assert result is True

def test_send_alert(notification_service):
    result = notification_service.send_alert("user123", "Alert message")
    assert result is True
