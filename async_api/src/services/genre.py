from functools import lru_cache

from fastapi import Depends

from core.logger import logger as _logger
from db.repository import Repository, get_repository
from models.genre import ESGenre

logger = _logger(__name__)


class GenreService:
    def __init__(self, repo: Repository):
        """
        :param repo: класс реализующий интерфейс Repository.
        """
        self.repo = repo

    async def get(self, uuid: str) -> dict | None:
        """
        Получение информации о конкретном жанре
        :param uuid: id жанра в БД
        :return: Объект модели DetailGenre
        """
        doc = await self.repo.get('genres', uuid)
        if doc is None:
            return
        data = ESGenre(**doc['_source']).dict()
        logger.debug('[+] Return genre from elastic. uuid:%s', uuid)
        return data

    async def get_multi(self) -> list[dict] | None:
        """
        Получение информации о всех жанрах.
        :return: Список объектов модели DetailGenre
        """
        docs = await self.repo.get_multi('genres')
        if docs is None:
            return []
        data = [ESGenre(**row['_source']).dict() for row in docs['hits']['hits']]
        logger.debug('[+] Return genres from elastic.')
        return data


@lru_cache()
def get_genre_service(
    repo: Repository = Depends(get_repository),
) -> GenreService:
    """
    Провайдер для GenreService.
    :param repo: класс реализующий интерфейс Repository
    :return: Объект класса GenreService для API
    """
    return GenreService(repo)
