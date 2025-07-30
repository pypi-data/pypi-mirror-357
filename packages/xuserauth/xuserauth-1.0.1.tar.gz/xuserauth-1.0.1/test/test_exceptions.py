import pytest
from fastapi import HTTPException
from xuserauth.exceptions import (
    XUserAuthException, AuthError, PermissionDenied, InvalidToken, UserNotFound
)


def test_auth_error_raises_http_unauthorized():
    with pytest.raises(HTTPException) as e:
        raise AuthError("No token")
    assert e.value.status_code == 401
    assert "No token" in str(e.value.detail)


def test_permission_denied():
    with pytest.raises(PermissionDenied):
        raise PermissionDenied()


def test_invalid_token_custom_message():
    with pytest.raises(InvalidToken) as e:
        raise InvalidToken("bad signature")
    assert e.value.status_code == 401
    assert "bad signature" in str(e.value.detail)


def test_user_not_found_exception():
    with pytest.raises(UserNotFound):
        raise UserNotFound()
