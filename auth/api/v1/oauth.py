from http import HTTPStatus

from core.config import settings
from flask import Blueprint, jsonify, request
from services.user.payload_models import OAuthPayload
from services.user.services.oauth import OAuthRegister
from utils.exceptions import EmailAlreadyExist, NoAccessError, UniqueConstraintError

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
    if not settings.oauth.providers.check_value(provider):
        return jsonify(message='Unsupportable provider'), HTTPStatus.NOT_FOUND
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
    oauth = OAuthRegister.get_provider(provider)
    try:
        user_social_data = oauth.callback()
    except NoAccessError:
        return jsonify(message='Authentication failed.'), HTTPStatus.FORBIDDEN
    try:
        user_data = OAuthPayload(user_agent=request.headers.get('User-Agent'), **user_social_data.dict())
        oauth.register(user_data)
    except EmailAlreadyExist:
        return jsonify(message='Email is already in use'), HTTPStatus.CONFLICT
    except UniqueConstraintError:
        return jsonify(message='Social account is already linked'), HTTPStatus.CONFLICT

    return jsonify(message='New user was registered'), HTTPStatus.OK
