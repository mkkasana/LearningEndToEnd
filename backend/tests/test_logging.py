"""Tests for logging functionality."""

import logging

import pytest

from app.core.logging_config import mask_sensitive_data


def test_mask_sensitive_data_dict():
    """Test masking sensitive data in dictionaries."""
    data = {
        "email": "user@example.com",
        "password": "secret123",
        "name": "John Doe",
        "token": "abc123",
    }
    
    masked = mask_sensitive_data(data)
    
    assert masked["email"] == "user@example.com"
    assert masked["password"] == "***MASKED***"
    assert masked["name"] == "John Doe"
    assert masked["token"] == "***MASKED***"


def test_mask_sensitive_data_nested_dict():
    """Test masking sensitive data in nested dictionaries."""
    data = {
        "user": {
            "email": "user@example.com",
            "password": "secret123",
        },
        "auth": {
            "access_token": "token123",
            "refresh_token": "refresh456",
        },
    }
    
    masked = mask_sensitive_data(data)
    
    assert masked["user"]["email"] == "user@example.com"
    assert masked["user"]["password"] == "***MASKED***"
    assert masked["auth"]["access_token"] == "***MASKED***"
    assert masked["auth"]["refresh_token"] == "***MASKED***"


def test_mask_sensitive_data_list():
    """Test masking sensitive data in lists."""
    data = [
        {"email": "user1@example.com", "password": "secret1"},
        {"email": "user2@example.com", "password": "secret2"},
    ]
    
    masked = mask_sensitive_data(data)
    
    assert masked[0]["email"] == "user1@example.com"
    assert masked[0]["password"] == "***MASKED***"
    assert masked[1]["email"] == "user2@example.com"
    assert masked[1]["password"] == "***MASKED***"


def test_mask_sensitive_data_case_insensitive():
    """Test that masking is case-insensitive."""
    data = {
        "Password": "secret123",
        "PASSWORD": "secret456",
        "Token": "token123",
        "ACCESS_TOKEN": "token456",
    }
    
    masked = mask_sensitive_data(data)
    
    assert masked["Password"] == "***MASKED***"
    assert masked["PASSWORD"] == "***MASKED***"
    assert masked["Token"] == "***MASKED***"
    assert masked["ACCESS_TOKEN"] == "***MASKED***"


def test_mask_sensitive_data_preserves_non_sensitive():
    """Test that non-sensitive data is preserved."""
    data = {
        "email": "user@example.com",
        "name": "John Doe",
        "age": 30,
        "is_active": True,
        "roles": ["user", "admin"],
    }
    
    masked = mask_sensitive_data(data)
    
    assert masked["email"] == "user@example.com"
    assert masked["name"] == "John Doe"
    assert masked["age"] == 30
    assert masked["is_active"] is True
    assert masked["roles"] == ["user", "admin"]


def test_mask_sensitive_data_max_depth():
    """Test that max depth prevents infinite recursion."""
    # Create deeply nested structure
    data = {"level1": {"level2": {"level3": {"level4": {"level5": {"level6": "value"}}}}}}
    
    # Should not raise an error
    masked = mask_sensitive_data(data, max_depth=3)
    
    # Should have stopped at max depth
    assert "level1" in masked
    assert "level2" in masked["level1"]
    assert "level3" in masked["level1"]["level2"]


def test_mask_sensitive_data_with_none():
    """Test masking with None values."""
    data = {
        "email": "user@example.com",
        "password": None,
        "token": None,
    }
    
    masked = mask_sensitive_data(data)
    
    assert masked["email"] == "user@example.com"
    assert masked["password"] == "***MASKED***"
    assert masked["token"] == "***MASKED***"


def test_mask_sensitive_data_all_sensitive_fields():
    """Test all sensitive fields are masked."""
    sensitive_fields = [
        "password",
        "hashed_password",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "api_key",
        "authorization",
        "cookie",
        "session",
        "csrf_token",
        "new_password",
        "current_password",
        "confirm_password",
    ]
    
    data = {field: f"sensitive_{field}" for field in sensitive_fields}
    data["email"] = "user@example.com"  # Non-sensitive
    
    masked = mask_sensitive_data(data)
    
    # All sensitive fields should be masked
    for field in sensitive_fields:
        assert masked[field] == "***MASKED***", f"Field {field} was not masked"
    
    # Non-sensitive field should be preserved
    assert masked["email"] == "user@example.com"


def test_logging_configuration(caplog):
    """Test that logging is properly configured."""
    caplog.set_level(logging.INFO)
    
    logger = logging.getLogger("app.test")
    logger.info("Test log message")
    
    assert "Test log message" in caplog.text


def test_logging_with_sensitive_data(caplog):
    """Test that sensitive data can be logged safely."""
    caplog.set_level(logging.DEBUG)
    
    logger = logging.getLogger("app.test")
    
    # Simulate logging user data
    user_data = {
        "email": "user@example.com",
        "password": "secret123",
        "name": "John Doe",
    }
    
    # Mask before logging
    masked_data = mask_sensitive_data(user_data)
    logger.debug(f"User data: {masked_data}")
    
    # Check that password is masked in logs
    assert "secret123" not in caplog.text
    assert "***MASKED***" in caplog.text
    assert "user@example.com" in caplog.text
    assert "John Doe" in caplog.text
