import dataclasses
from enum import Enum

from fastapi import Query


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
