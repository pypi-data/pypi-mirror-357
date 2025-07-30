import pytest
from types import SimpleNamespace
from xuserauth.auth_manager import AuthManager
from xuserauth.exceptions import UserNotFound, InvalidToken
from jose import jwt


class FakeUser:
    def __init__(self, id="user123", roles=["user", "admin"], is_active=True):
        self.id = id
        self.email = "test@example.com"
        self.hashed_password = "$2b$12$abcdefghijklmnopqrstuv"
        self.roles = roles
        self.is_active = is_active


@pytest.fixture
def user():
    return FakeUser()


@pytest.fixture
def auth_manager(user):
    async def user_loader(user_id):
        return user if user_id == user.id else None

    return AuthManager(
        user_model=None,
        jwt_secret="testsecret",
        user_loader=user_loader
    )


@pytest.mark.asyncio
async def test_generate_and_verify_token(auth_manager, user):
    token = auth_manager.generate_token(user, expires_in=60)
    payload = auth_manager.verify_token(token)
    assert payload["sub"] == user.id
    assert payload["type"] == "access"


@pytest.mark.asyncio
async def test_refresh_token(auth_manager, user):
    refresh_token = auth_manager.generate_refresh_token(user)
    new_token = await auth_manager.refresh_access_token(refresh_token)
    assert auth_manager.verify_token(new_token)["sub"] == user.id


@pytest.mark.asyncio
async def test_get_user_by_token_valid(auth_manager, user):
    token = auth_manager.generate_token(user)
    credentials = SimpleNamespace(credentials=token)
    result = await auth_manager.get_user_by_token(credentials)
    assert result.id == user.id


@pytest.mark.asyncio
async def test_get_user_by_token_invalid(auth_manager):
    token = jwt.encode({"sub": "invalid"}, "wrongsecret", algorithm="HS256")
    credentials = SimpleNamespace(credentials=token)
    with pytest.raises(InvalidToken):
        await auth_manager.get_user_by_token(credentials)


@pytest.mark.asyncio
async def test_user_not_found(auth_manager):
    async def loader(_): return None

    auth_manager.user_loader = loader
    token = auth_manager.generate_token(FakeUser(id="ghost"))
    credentials = SimpleNamespace(credentials=token)
    with pytest.raises(UserNotFound):
        await auth_manager.get_user_by_token(credentials)
