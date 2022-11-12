import dataclasses
import datetime
from enum import Enum

import jwt
from fastapi import Query

from core.config import settings


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


def get_jwt(token: str) -> dict | None:
    _token = jwt.decode(
        jwt=token,
        key=settings.jwt.SECRET_KEY,
        algorithms=[settings.jwt.ALGORITHM],
    )
    return _token if _token['exp'] >= datetime.now() else None


def get_permisions() -> list:
    ...
