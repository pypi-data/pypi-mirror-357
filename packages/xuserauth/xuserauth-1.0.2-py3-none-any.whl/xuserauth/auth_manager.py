from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Callable, Optional, Union, Awaitable, Any
from functools import wraps

from .jwt_utils import create_token, decode_token
from .hashing import password_hash, verify_password
from .roles import has_role
from .exceptions import AuthError, PermissionDenied, UserNotFound, InvalidToken

import jwt  # Needed for exception handling

security = HTTPBearer()


class AuthManager:
    def __init__(
            self,
            user_model,
            jwt_secret: str,
            roles_field: str = "roles",
            subject_field: str = "id",
            hash_algorithm: str = "bcrypt",
            user_loader: Optional[Callable[[str], Awaitable[Any]]] = None
    ):
        self.user_model = user_model
        self.jwt_secret = jwt_secret
        self.roles_field = roles_field
        self.subject_field = subject_field
        self.hash_algorithm = hash_algorithm
        self.user_loader = user_loader

    # ──────────────────────────────────────────────────────
    # 🔐 TOKEN MANAGEMENT
    # ──────────────────────────────────────────────────────

    def generate_token(self, user, expires_in: int = 3600, token_type: str = "access") -> str:
        user_id = getattr(user, self.subject_field)
        payload = {
            "sub": str(user_id),
            "type": token_type
        }
        return create_token(
            email=user_id,
            expires_delta=timedelta(seconds=expires_in),
            secret_key=self.jwt_secret,
            token_type=token_type
        )

    def generate_refresh_token(self, user, expires_in: int = 7 * 86400) -> str:
        return self.generate_token(user, expires_in=expires_in, token_type="refresh")

    def generate_email_verification_token(self, user, expires_in: int = 3600) -> str:
        return self.generate_token(user, expires_in=expires_in, token_type="email")

    def generate_password_reset_token(self, user, expires_in: int = 1800) -> str:
        return self.generate_token(user, expires_in=expires_in, token_type="reset")

    def verify_token(self, token: str) -> dict:
        try:
            return decode_token(token, self.jwt_secret)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            raise InvalidToken(str(e))

    # ──────────────────────────────────────────────────────
    # 👤 USER HANDLING
    # ──────────────────────────────────────────────────────

    async def get_user_by_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise InvalidToken("Missing user ID in token")

        user = await (self.user_loader(user_id) if self.user_loader else self.user_model.get(user_id))

        if not user or not getattr(user, "is_active", True):
            raise UserNotFound()

        # Optional enforcement
        if hasattr(user, "email_verified") and not user.email_verified:
            raise AuthError("Email not verified")

        return user

    async def refresh_access_token(self, refresh_token: str) -> str:
        payload = self.verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise InvalidToken("Invalid token type")

        user_id = payload.get("sub")
        if self.user_loader:
            user = await self.user_loader(user_id)
        else:
            user = await self.user_model.get(user_id)

        if not user:
            raise UserNotFound()

        return self.generate_token(user)

    # ──────────────────────────────────────────────────────
    # 🔐 AUTH DECORATORS
    # ──────────────────────────────────────────────────────

    def require_authenticated(self, func: Callable):
        @wraps(func)
        async def wrapper(user=Depends(self.get_user_by_token), *args, **kwargs):
            return await func(user, *args, **kwargs)

        return wrapper

    def require_role(self, required_role: Union[str, list], use_hierarchy: bool = True):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(user=Depends(self.get_user_by_token), *args, **kwargs):
                if not has_role(user, self.roles_field, required_role, use_hierarchy=use_hierarchy):
                    raise PermissionDenied()
                return await func(user, *args, **kwargs)

            return wrapper

        return decorator

    # ──────────────────────────────────────────────────────
    # 🔒 PASSWORD UTILS
    # ──────────────────────────────────────────────────────

    def hash_password(self, password: str) -> str:
        return password_hash(password)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return verify_password(plain, hashed)
