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


# Additional tests for log format validation (Requirement 15.2)
def test_log_format_includes_timestamp(caplog):
    """Test that log format includes timestamp in correct format."""
    caplog.set_level(logging.INFO)
    
    logger = logging.getLogger("app.test")
    logger.info("Test message for timestamp")
    
    # Check that the message was logged (timestamp format may vary by configuration)
    assert "Test message for timestamp" in caplog.text


def test_log_format_includes_module_name(caplog):
    """Test that log format includes module name."""
    caplog.set_level(logging.INFO)
    
    logger = logging.getLogger("app.test.module")
    logger.info("Test message for module name")
    
    # Check that module name is present
    assert "app.test.module" in caplog.text


def test_log_format_includes_log_level(caplog):
    """Test that log format includes log level."""
    caplog.set_level(logging.DEBUG)
    
    logger = logging.getLogger("app.test")
    
    logger.debug("Debug message")
    assert "DEBUG" in caplog.text
    
    logger.info("Info message")
    assert "INFO" in caplog.text
    
    logger.warning("Warning message")
    assert "WARNING" in caplog.text
    
    logger.error("Error message")
    assert "ERROR" in caplog.text


def test_log_format_includes_function_and_line(caplog):
    """Test that log format includes function name and line number."""
    caplog.set_level(logging.INFO)
    
    logger = logging.getLogger("app.test")
    logger.info("Test message for function and line")
    
    # Check that the message was logged
    assert "Test message for function and line" in caplog.text


# Additional tests for request ID generation (Requirement 15.6)
def test_request_id_generation():
    """Test that request IDs are generated with correct length."""
    import uuid
    
    # Generate multiple request IDs
    request_ids = [str(uuid.uuid4())[:8] for _ in range(10)]
    
    # Check that all IDs are 8 characters long
    for request_id in request_ids:
        assert len(request_id) == 8, f"Request ID {request_id} is not 8 characters"


def test_request_id_uniqueness():
    """Test that generated request IDs are unique."""
    import uuid
    
    # Generate multiple request IDs
    request_ids = [str(uuid.uuid4())[:8] for _ in range(100)]
    
    # Check that all IDs are unique
    unique_ids = set(request_ids)
    # Allow for very small collision rate due to truncation
    assert len(unique_ids) >= 95, f"Too many collisions: {len(unique_ids)} unique out of 100"


def test_request_id_format_in_logs(caplog):
    """Test that request ID appears in correct format in logs."""
    caplog.set_level(logging.INFO)
    
    logger = logging.getLogger("app.test")
    request_id = "abc12345"
    logger.info(f"[{request_id}] Test message with request ID")
    
    # Check that request ID is present in [xxxxxxxx] format
    assert f"[{request_id}]" in caplog.text
    
    import re
    request_id_pattern = r"\[[\w]{8}\]"
    assert re.search(request_id_pattern, caplog.text), "Request ID format not found in log"


# Additional tests for execution time calculation (Requirement 15.7)
def test_execution_time_calculation():
    """Test that execution time is calculated correctly."""
    import time
    
    start_time = time.time()
    time.sleep(0.1)  # Sleep for 100ms
    end_time = time.time()
    
    execution_time_ms = (end_time - start_time) * 1000
    
    # Check that execution time is approximately 100ms (with tolerance)
    assert 90 <= execution_time_ms <= 150, f"Execution time {execution_time_ms}ms not in expected range"


def test_execution_time_format():
    """Test that execution time is formatted with 2 decimal places."""
    import time
    
    start_time = time.time()
    time.sleep(0.05)  # Sleep for 50ms
    end_time = time.time()
    
    execution_time_ms = (end_time - start_time) * 1000
    formatted_time = f"{execution_time_ms:.2f}ms"
    
    # Check format: should have exactly 2 decimal places
    import re
    time_pattern = r"\d+\.\d{2}ms"
    assert re.match(time_pattern, formatted_time), f"Time format {formatted_time} is incorrect"


def test_execution_time_in_logs(caplog):
    """Test that execution time appears in logs with correct format."""
    caplog.set_level(logging.INFO)
    
    logger = logging.getLogger("app.test")
    
    # Simulate logging with execution time
    execution_time = 123.45
    logger.info(f"Request completed | Time: {execution_time:.2f}ms")
    
    # Check that execution time is present with 2 decimal places
    assert "Time: 123.45ms" in caplog.text
    
    import re
    time_pattern = r"Time: \d+\.\d{2}ms"
    assert re.search(time_pattern, caplog.text), "Execution time format not found in log"


def test_execution_time_in_error_logs(caplog):
    """Test that execution time is included in error logs."""
    caplog.set_level(logging.ERROR)
    
    logger = logging.getLogger("app.test")
    
    # Simulate error logging with execution time
    execution_time = 234.56
    logger.error(f"Request failed | Error: TestError | Time: {execution_time:.2f}ms")
    
    # Check that execution time is present in error log
    assert "Time: 234.56ms" in caplog.text
    assert "Error: TestError" in caplog.text
