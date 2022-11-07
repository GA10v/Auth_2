from flask import Blueprint
from services.user.services.oauth import OAuthRegister

oauth_blueprint = Blueprint('oauth', __name__, url_prefix='/api/v1/oauth')


@oauth_blueprint.route('/register/<provider>')
def oauth_register(provider):
    """
    Регистрация нового пользователя через OAuth.
    ---
    post:
     summary: Регистрация нового пользователя через OAuth
     parameters:
      - name: provider
        in: path
        type: string
        required: true
     responses:
       '200':
         description: New user was registered
       '404':
         description: Unsupportable provider
     tags:
       - OAuth
    """
    oauth = OAuthRegister.get_provider(provider)
    return oauth.authorize()


@oauth_blueprint.route('/register-callback/<provider>')
def oauth_register_callback(provider):
    """
    Регистрация нового пользователя через OAuth.
    ---
    get:
     summary: Регистрация нового пользователя через OAuth.
     responses:
       '200':
         description: Login successful
       '403':
         description: Permission denied
       '409':
         description: Email is already in use or social account is already linked to another user
     tags:
       - OAuth
    """
    ...
