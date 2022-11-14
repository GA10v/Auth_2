from http import HTTPStatus

from core.config import settings
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required, verify_jwt_in_request
from utils.exceptions import NotFoundError

from .components.fastapi_schemas import UserInfo as InfoSchem
from .utils import check_permission, rate_limit

fastapi_blueprint = Blueprint('fastapi', __name__, url_prefix='/api/v1/fastapi')


@fastapi_blueprint.route('/', methods=('GET',))
@jwt_required()
@rate_limit()
@check_permission(permission=settings.permission.User)
def info():  # noqa: C901
    """
    Получение прав пользователя.
    ---
    get:
     security:
      - AccessAuth: []
     summary: Получение прав пользователя
     responses:
       '200':
         description: Ok
       '204':
         description: Role list is empty
       '401':
         description: Missing Authorization Header
       '404':
         description: Not found
     tags:
       - FastApi
    """
    if request.method == 'GET':
        verify_jwt_in_request()
        claims = get_jwt()
        try:
            user_id = get_jwt_identity()
        except NotFoundError:
            return jsonify(message='Not found'), HTTPStatus.NOT_FOUND
        _info = {
            'auth': True,
            'is_super': claims.get('is_super', False),
            'user': user_id,
            'permissions': claims.get('permissions'),
        }
        return jsonify(auth=InfoSchem().dumps(**_info)), HTTPStatus.OK
