import pytest
from starlette.requests import Request
from xuserauth.social.google import login_with_google


@pytest.mark.skip(reason="Requires SessionMiddleware to test Google OAuth flow.")
@pytest.mark.asyncio
async def test_google_login_redirect():
    req = Request(scope={"type": "http", "method": "GET", "path": "/", "headers": []})
    req.url_for = lambda name: "https://example.com/auth/google/callback"
    response = await login_with_google(req)
    assert response.status_code in [302, 307]
