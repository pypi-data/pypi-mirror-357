from passlib.context import CryptContext
from typing import Optional

# Default password context (bcrypt)
_default_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def password_hash(password: str, context: Optional[CryptContext] = None) -> str:
    """
    Hash a password securely using bcrypt or the provided CryptContext.

    Args:
        password (str): The plaintext password.
        context (CryptContext, optional): Custom password hashing context.

    Returns:
        str: The hashed password.
    """
    ctx = context or _default_pwd_context
    return ctx.hash(password)


def verify_password(
        plain_password: str, hashed_password: str, context: Optional[CryptContext] = None
) -> bool:
    """
    Verify a plaintext password against a securely hashed password.

    Args:
        plain_password (str): The user-provided plaintext password.
        hashed_password (str): The stored hashed password.
        context (CryptContext, optional): Custom password hashing context.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    ctx = context or _default_pwd_context
    return ctx.verify(plain_password, hashed_password)
