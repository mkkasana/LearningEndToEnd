"""Unit tests for Auth schemas."""

import pytest
from pydantic import ValidationError

from app.schemas.auth import Token, TokenPayload, NewPassword


@pytest.mark.unit
class TestToken:
    """Tests for Token schema."""

    def test_valid_token(self) -> None:
        """Test Token with valid data."""
        token = Token(access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        assert token.access_token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token.token_type == "bearer"

    def test_token_custom_type(self) -> None:
        """Test Token with custom token_type."""
        token = Token(access_token="test_token", token_type="custom")
        assert token.token_type == "custom"

    def test_token_access_token_required(self) -> None:
        """Test Token requires access_token."""
        with pytest.raises(ValidationError) as exc_info:
            Token()
        assert "access_token" in str(exc_info.value)

    def test_token_default_type(self) -> None:
        """Test Token default token_type is 'bearer'."""
        token = Token(access_token="test")
        assert token.token_type == "bearer"


@pytest.mark.unit
class TestTokenPayload:
    """Tests for TokenPayload schema."""

    def test_valid_token_payload(self) -> None:
        """Test TokenPayload with valid data."""
        payload = TokenPayload(sub="user@example.com")
        assert payload.sub == "user@example.com"

    def test_token_payload_optional_sub(self) -> None:
        """Test TokenPayload with no sub (optional)."""
        payload = TokenPayload()
        assert payload.sub is None

    def test_token_payload_with_uuid_sub(self) -> None:
        """Test TokenPayload with UUID as sub."""
        payload = TokenPayload(sub="550e8400-e29b-41d4-a716-446655440000")
        assert payload.sub == "550e8400-e29b-41d4-a716-446655440000"


@pytest.mark.unit
class TestNewPassword:
    """Tests for NewPassword schema."""

    def test_valid_new_password(self) -> None:
        """Test NewPassword with valid data."""
        new_pwd = NewPassword(
            token="reset_token_123",
            new_password="newsecurepassword123",
        )
        assert new_pwd.token == "reset_token_123"
        assert new_pwd.new_password == "newsecurepassword123"

    def test_new_password_token_required(self) -> None:
        """Test NewPassword requires token."""
        with pytest.raises(ValidationError) as exc_info:
            NewPassword(new_password="newsecurepassword123")
        assert "token" in str(exc_info.value)

    def test_new_password_password_required(self) -> None:
        """Test NewPassword requires new_password."""
        with pytest.raises(ValidationError) as exc_info:
            NewPassword(token="reset_token_123")
        assert "new_password" in str(exc_info.value)

    def test_new_password_min_length(self) -> None:
        """Test NewPassword password minimum length (8 chars)."""
        with pytest.raises(ValidationError) as exc_info:
            NewPassword(token="reset_token", new_password="short")
        assert "new_password" in str(exc_info.value)

    def test_new_password_max_length(self) -> None:
        """Test NewPassword password maximum length (128 chars)."""
        with pytest.raises(ValidationError) as exc_info:
            NewPassword(token="reset_token", new_password="a" * 129)
        assert "new_password" in str(exc_info.value)

    def test_new_password_exactly_8_chars(self) -> None:
        """Test NewPassword with exactly 8 characters (minimum)."""
        new_pwd = NewPassword(token="reset_token", new_password="12345678")
        assert len(new_pwd.new_password) == 8

    def test_new_password_exactly_128_chars(self) -> None:
        """Test NewPassword with exactly 128 characters (maximum)."""
        new_pwd = NewPassword(token="reset_token", new_password="a" * 128)
        assert len(new_pwd.new_password) == 128
