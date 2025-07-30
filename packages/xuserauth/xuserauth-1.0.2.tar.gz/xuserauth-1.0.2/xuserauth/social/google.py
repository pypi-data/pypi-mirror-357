# xuserauth/social/google.py

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from starlette.config import Config
from starlette.responses import RedirectResponse

# Pull secrets from environment or hardcode for testing
config = Config(environ={
    "GOOGLE_CLIENT_ID": "your-google-client-id",
    "GOOGLE_CLIENT_SECRET": "your-google-client-secret"
})

oauth = OAuth(config)
oauth.register(
    name='google',
    client_id=config("GOOGLE_CLIENT_ID"),
    client_secret=config("GOOGLE_CLIENT_SECRET"),
    access_token_url='https://oauth2.googleapis.com/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'}
)


async def login_with_google(request: Request):
    redirect_uri = request.url_for("auth_google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


async def auth_google_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user_info = await oauth.google.parse_id_token(request, token)

    # Example user_info:
    # {
    #   "sub": "1234567890",
    #   "name": "John Doe",
    #   "email": "john@example.com",
    #   "picture": "https://..."
    # }

    return user_info  # You can create or fetch your user from DB here
