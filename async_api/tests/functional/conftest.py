import asyncio
from contextlib import asynccontextmanager

import aiohttp
import orjson
import pytest
import pytest_asyncio
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from settings import test_settings


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()

    yield loop

    loop.close()


@pytest_asyncio.fixture(scope='session')
async def es_client():
    es = AsyncElasticsearch(hosts=test_settings.es_host)

    yield es

    await es.close()


@pytest_asyncio.fixture(scope='session')
async def redis_client():
    rd = Redis(host=test_settings.redis_host)

    yield rd

    await rd.close()


@pytest_asyncio.fixture(scope='session')
async def aiohttp_client():
    async with aiohttp.ClientSession() as client:
        yield client


@pytest_asyncio.fixture(scope='module', autouse=True)
async def create_index(es_client: AsyncElasticsearch):
    for index in test_settings.es_index:
        if not await es_client.indices.exists(index=index):
            await es_client.indices.create(index=index, body=test_settings.es_index_mapping.get(index))
    yield
    for index in test_settings.es_index:
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index, ignore=[400, 404])


def get_es_bulk_query(es_data: list[dict], index: str, id_field: str):
    bulk_query = []
    for row in es_data:
        bulk_query.extend(
            [
                orjson.dumps({'index': {'_index': index, '_id': row[id_field]}}).decode('utf-8'),
                orjson.dumps(row).decode('utf-8'),
            ],
        )
    return '\n'.join(bulk_query) + '\n'


@pytest_asyncio.fixture
def es_write_data(es_client: AsyncElasticsearch):
    async def inner(index: str, data: list[dict]):
        bulk_query = get_es_bulk_query(data, index, test_settings.es_id_field)

        response = await es_client.bulk(bulk_query, refresh=True)

        if response['errors']:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture
def es_drop_data(es_client: AsyncElasticsearch):
    async def inner(index: str):
        await es_client.indices.delete(index=index, ignore=[400, 404])

    return inner


@pytest_asyncio.fixture
def make_get_request(aiohttp_client: aiohttp.ClientSession):
    @asynccontextmanager
    async def inner(
        handler_url: str,
        query_data: dict | None = None,
        headers: dict | None = None,
    ):
        url = ''.join([test_settings.service_url, handler_url])

        if query_data:
            async with aiohttp_client.get(url, params=query_data) as response:
                yield response
        elif headers:
            async with aiohttp_client.get(url, headers=headers) as response:
                yield response
        else:
            async with aiohttp_client.get(url) as response:
                yield response

    return inner


@pytest_asyncio.fixture
def make_post_request(aiohttp_client: aiohttp.ClientSession):
    @asynccontextmanager
    async def inner(
        handler_url: str,
        query_data: dict | None = None,
        headers: dict | None = None,
    ):
        url = ''.join([test_settings.service_url, handler_url])

        if query_data:
            async with aiohttp_client.post(url, params=query_data) as response:
                yield response
        elif headers:
            async with aiohttp_client.post(url, headers=headers) as response:
                yield response
        else:
            async with aiohttp_client.post(url) as response:
                yield response

    return inner
