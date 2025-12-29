from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Raised when authentication fails"""

    def __init__(self, detail: str = "Could not validate credentials") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class InactiveUserError(HTTPException):
    """Raised when user account is inactive"""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )


class PermissionDeniedError(HTTPException):
    """Raised when user lacks required permissions"""

    def __init__(self, detail: str = "Not enough permissions") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ResourceNotFoundError(HTTPException):
    """Raised when requested resource is not found"""

    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found"
        )


class ResourceAlreadyExistsError(HTTPException):
    """Raised when resource already exists"""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class EmailAlreadyExistsError(HTTPException):
    """Raised when email already exists in system"""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
