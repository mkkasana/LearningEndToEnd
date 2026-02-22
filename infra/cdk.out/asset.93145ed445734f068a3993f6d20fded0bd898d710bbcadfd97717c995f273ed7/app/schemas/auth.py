from pydantic import Field
from sqlmodel import SQLModel


class Token(SQLModel):
    """JSON payload containing access token"""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """Contents of JWT token"""

    sub: str | None = None


class NewPassword(SQLModel):
    """Password reset request"""

    token: str
    new_password: str = Field(min_length=8, max_length=128)
