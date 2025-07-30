# xuserauth/exceptions.py

from fastapi import HTTPException, status


class XUserAuthException(HTTPException):
    """Base exception for all xuserauth-related errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)


class AuthError(XUserAuthException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class PermissionDenied(XUserAuthException):
    def __init__(self, detail: str = "You do not have permission to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class InvalidToken(XUserAuthException):
    def __init__(self, detail: str = "Token is invalid or expired"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class UserNotFound(XUserAuthException):
    def __init__(self, detail: str = "User not found or inactive"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
