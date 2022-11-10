import dataclasses
import datetime
from functools import wraps
from http import HTTPStatus

from core import settings
from db.redis import redis
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request


@dataclasses.dataclass
class Pagination:
    page: int = 1
    size: int = 10


def check_permission(permission: settings.permission):
    """
    Проверка наличия прав для доступа.
    :param permission: код конректного пермишана
    :return func_wrapper: Результат выполнения функции.
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            current_user = get_jwt_identity()
            user = kwargs.get('user_id')
            is_owner = current_user == user
            is_super = claims.get('is_super', False)
            permissions = claims.get('permissions')

            if is_owner or is_super or (permission.value in permissions):
                return func(*args, **kwargs)
            else:
                return jsonify(msg='Permission denied'), HTTPStatus.FORBIDDEN

        return inner

    return func_wrapper


def rate_limit(limit: int = settings.rate_limit.PER_MINUTE):
    """
    Ограничение количества запросов leaky bucket.
    :param limit: Лимит запросов в минуту
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            user_id = get_jwt()['sub']
            pipline = redis.pipeline()
            now = datetime.datetime.utcnow()
            key = f'{user_id}:{now.minute}'
            pipline.incr(key, 1)
            pipline.expire(key, 59)
            request_number = pipline.execute()[0]

            if request_number >= limit:
                return jsonify(msg='Too many requests'), HTTPStatus.TOO_MANY_REQUESTS
            else:
                return func(*args, **kwargs)

        return inner

    return func_wrapper
