from elasticsearch import AsyncElasticsearch, NotFoundError
from elasticsearch_dsl import Search

from core.config import settings
from core.logger import logger as _logger

logger = _logger(__name__)

es: AsyncElasticsearch = AsyncElasticsearch(hosts=settings.elastic.hosts)


class ElasticRepository:
    def __init__(self, client: AsyncElasticsearch = es):
        self.client = client

    async def get(self, index: str, _id: str) -> dict | None:
        """
        Получение данных из Elasticsearch по id.
        :param index: название индекса в elasticsearch
        :param _id: id документа
        :return: Ответ elasticsearch в виде dict
        """
        try:
            doc = await self.client.get(index, _id)
        except NotFoundError:
            logger.info('Trying to get non-existent document with id: %s, in index: %s', _id, index)
            return None
        return doc

    async def get_multi(self, index: str, search: Search = None) -> dict | None:
        """
        Получение всех данных индекса из Elasticsearch.
        :param index: название индекса в elasticsearch
        :param search: Объект класса Search
        :return: Ответ elasticsearch в виде dict
        """
        if search is None:
            body = {
                'query': {'match_all': {}},
                'size': 10_000,
            }
        else:
            body = search.to_dict()
        try:
            doc = await self.client.search(index=index, body=body)
        except NotFoundError:
            logger.info('No results found for all query in index: %s', index)
            return None
        return doc

    async def search(self, index: str, search: Search) -> dict | None:
        """
        Получение данных из Elasticsearch по определенному запросу.
        :param index: название индекса в elasticsearch
        :param search: Объект класса Search
        :return: Ответ elasticsearch в виде dict
        """
        try:
            query = search.to_dict()
            docs = await self.client.search(index=index, body=query)
        except NotFoundError:
            logger.info('No results found for query: \n%s\nIn index: %s', search.to_dict(), index)
            return None
        return docs
