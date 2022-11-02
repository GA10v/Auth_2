from functools import lru_cache

from elasticsearch_dsl import Q, Search
from fastapi import Depends

from core.logger import logger as _logger
from db.repository import Repository, get_repository
from models.film import ESFilm
from models.person import ESPerson

logger = _logger(__name__)


class PersonService:
    def __init__(self, repo: Repository):
        """
        :param repo: класс реализующий интерфейс Repository
        """
        self.repo = repo

    async def get_by_id(self, person_id: str) -> dict | None:
        """
        Получение и запись информации о персоне.
        :param person_id: id персоны
        :return: Объект модели DetailPerson
        """
        doc = await self.repo.get('persons', person_id)
        if doc is None:
            return
        data = ESPerson(**doc['_source']).dict()
        logger.debug('[+] Return person from elastic. id: %s', person_id)
        return data

    async def get_person_by_search(self, **kwargs) -> list[dict] | None:
        """
        Получение и запись списка данных о фильмах.
        :param kwargs: Параметры запроса
        :return: Список объектов модели DetailPerson
        """
        start = (kwargs['page_num'] - 1) * kwargs['page_size']
        stop = kwargs['page_size'] * kwargs['page_num']
        search = Search(index='persons').query('multi_match', query=kwargs['query'], fuzziness='auto')[start:stop]
        docs = await self.repo.search('persons', search)
        if docs is None:
            return
        data = [ESPerson(**row['_source']).dict() for row in docs['hits']['hits']]
        logger.debug('[+] Return persons from elastic.')
        return data

    async def get_film_person_by_search(self, **kwargs) -> list[dict] | None:
        """
        Получение и запись списка данных о фильмах.
        :param kwargs: Параметры запроса
        :return: Список объектов модели FilmResponse
        """
        search = (
            Search(index='movies')
            .sort('-imdb_rating')
            .query(
                'bool',
                should=[
                    Q('nested', path='actors', query=Q('match', actors__id=kwargs['_person'])),
                    Q('nested', path='writers', query=Q('match', writers__id=kwargs['_person'])),
                    Q('nested', path='director', query=Q('match', director__id=kwargs['_person'])),
                ],
            )[0:10_000]
        )
        docs = await self.repo.search('movies', search)
        if docs is None:
            return
        data = [ESFilm(**row['_source']).dict() for row in docs['hits']['hits']]
        logger.debug('[+] Return person films from elastic.')
        return data


@lru_cache()
def get_person_service(
    repo: Repository = Depends(get_repository),
) -> PersonService:
    """
    Провайдер для PersonService.
    :param repo: класс реализующий интерфейс Repository
    :return: Объект класса PersonService
    """
    return PersonService(repo)
