# xuserauth/social/facebook.py

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from starlette.config import Config
from starlette.responses import RedirectResponse

# Use environment or hardcoded for dev
config = Config(environ={
    "FACEBOOK_CLIENT_ID": "your-facebook-client-id",
    "FACEBOOK_CLIENT_SECRET": "your-facebook-client-secret"
})

oauth = OAuth(config)
oauth.register(
    name='facebook',
    client_id=config("FACEBOOK_CLIENT_ID"),
    client_secret=config("FACEBOOK_CLIENT_SECRET"),
    access_token_url='https://graph.facebook.com/v12.0/oauth/access_token',
    authorize_url='https://www.facebook.com/v12.0/dialog/oauth',
    api_base_url='https://graph.facebook.com/v12.0/',
    client_kwargs={
        'scope': 'email public_profile',
        'token_endpoint_auth_method': 'client_secret_post'
    }
)


async def login_with_facebook(request: Request):
    redirect_uri = request.url_for("auth_facebook_callback")
    return await oauth.facebook.authorize_redirect(request, redirect_uri)


async def auth_facebook_callback(request: Request):
    token = await oauth.facebook.authorize_access_token(request)
    resp = await oauth.facebook.get('me?fields=id,name,email,picture', token=token)
    user_info = resp.json()

    # Example user_info:
    # {
    #   "id": "123456",
    #   "name": "Jane Doe",
    #   "email": "jane@example.com",
    #   "picture": { "data": { "url": "https://..." } }
    # }

    return user_info
