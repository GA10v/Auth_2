from functools import lru_cache

from elasticsearch_dsl import Q, Search
from fastapi import Depends

from core.logger import logger as _logger
from db.repository import Repository, get_repository
from models.film import ESFilm

logger = _logger(__name__)


class FilmService:
    def __init__(self, repo: Repository):
        """
        :param repo:  класс реализущией интерфейс Repository
        """
        self.repo = repo

    async def get_by_id(self, film_id: str) -> dict | None:
        """
        Получение и запись информации о фильме.
        :param film_id: id фильма
        :return: Объект модели DetailFilmResponse
        """
        doc = await self.repo.get('movies', film_id)
        if doc is None:
            return
        data = ESFilm(**doc['_source']).dict()
        logger.debug('[+] Return film from elastic. id:%s', film_id)
        return data

    async def get_by_search(self, **kwargs) -> list[dict] | None:
        """
        Получение и запись списка данных о фильмах.
        :param kwargs: Параметры запроса
        :return: Список объектов модели FilmResponse
        """
        start = (kwargs['page_num'] - 1) * kwargs['page_size']
        stop = kwargs['page_size'] * kwargs['page_num']
        search = Search(index='movies').query('match_all')[start:stop]
        if query := kwargs.get('query'):
            search = search.query('multi_match', query=query, fuzziness='auto')
        if sort := kwargs.get('sort'):
            search = search.sort(sort)
        if _filter := kwargs.get('_filter'):
            search = search.query('bool', should=[Q('nested', path='genre', query=Q('match', genre__id=_filter))])
        docs = await self.repo.search('movies', search)
        if docs is None:
            return
        data = [ESFilm(**row['_source']).dict() for row in docs['hits']['hits']]
        logger.debug('[+] Return films from elastic.')
        return data


@lru_cache()
def get_film_service(
    repo: Repository = Depends(get_repository),
) -> FilmService:
    """
    Провайдер для FilmService.
    :param repo: класс реализующий интерфейс Repository
    :return: Объект класса FilmService для API.
    """
    return FilmService(repo)
