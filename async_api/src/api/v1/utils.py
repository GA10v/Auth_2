import dataclasses
import datetime
from enum import Enum

import jwt
from fastapi import HTTPException, Query, Request
from fastapi.security import HTTPBearer

from core.config import settings
from core.logger import logger as _logger

logger = _logger(__name__)


class SortEnum(str, Enum):
    desc_rating = '-imdb_rating'
    asc_rating = 'imdb_rating'


@dataclasses.dataclass
class PaginatedParams:
    num: int = 1
    size: int = 50

    def __init__(
        self,
        num: int = Query(default=1, alias='page[number]', ge=1),
        size: int = Query(default=50, alias='page[size]', ge=1),
    ):
        self.num = num
        self.size = size


def get_decoded_jwt(encoded_token: str) -> dict | None:
    """
    Декодирование Access token'а.
    :param encoded_token: JWT token
    :return: dict
    """
    _token = jwt.decode(
        jwt=encoded_token,
        key=settings.jwt.SECRET_KEY,
        algorithms=[settings.jwt.ALGORITHM],
    )
    return _token if _token['exp'] >= datetime.now() else None


def get_permisions(request: Request) -> list[str]:
    """
    Получение списка permision пользователя.
    :param request: запрос
    :return: permisions: list[str]
    """
    try:
        bearer = HTTPBearer()
        credentials = bearer(request)
        permisions = get_decoded_jwt(credentials.credentials).get('permissions')
        return permisions if permisions else []
    except HTTPException as ex:
        logger.info('Ошибка при получении списка permision пользователя: \n %s', str(ex))
        return []
