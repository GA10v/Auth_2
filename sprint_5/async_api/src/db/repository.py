from typing import Protocol

from core.logger import logger as _logger
from db.elastic import ElasticRepository

logger = _logger(__name__)


class Repository(Protocol):
    async def get(self, *args, **kwargs) -> dict | None:
        ...

    async def get_multi(self, *args, **kwargs) -> dict | None:
        ...

    async def search(self, *args, **kwargs) -> dict | None:
        ...


database: Repository = ElasticRepository()


async def get_repository() -> Repository:
    return database
