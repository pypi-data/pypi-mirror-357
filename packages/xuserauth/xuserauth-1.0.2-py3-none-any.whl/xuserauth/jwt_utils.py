# xuserauth/jwt_utils.py

from typing import Any, Dict
from datetime import datetime, timedelta, timezone
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from xuserauth.exceptions import InvalidToken


def create_token(
        email: str,
        expires_delta: timedelta,
        secret_key: str,
        token_type: str = "access",
        auth_provider: str = "local"
) -> str:
    """
    Generate a short-lived JWT access token.

    Args:
        email (str): The email of the authenticated user.
        expires_delta (timedelta): The expiration duration of the token.
        secret_key (str): The secret key used to sign the token.
        algorithm (str): The algorithm used for signing the JWT.
        auth_provider (str, optional): The authentication provider (default: "local").

    Returns:
        str: The encoded JWT access token.
        :param email:
        :param expires_delta:
        :param secret_key:
        :param auth_provider:
        :param token_type:
    """
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "sub": email,
        "auth_provider": auth_provider,
        "type": token_type,
    }
    return jwt.encode(to_encode, secret_key, algorithm="HS256")


def decode_token(token: str, secret: str, algorithm: str = "HS256") -> Dict[str, Any]:
    """
    Decode and verify a JWT token using the given secret and algorithm.

    Args:
        token (str): The JWT token to decode.
        secret (str): The secret key used to verify the token.
        algorithm (str, optional): The algorithm used to decode the token (default: "HS256").

    Returns:
        Dict[str, Any]: The decoded token payload.

    Raises:
        Exception: If the token is expired or invalid.
    """
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except ExpiredSignatureError:
        raise InvalidToken("Token has expired")
    except InvalidTokenError:
        raise InvalidToken("Invalid token")
