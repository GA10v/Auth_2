import datetime
import http

import jwt
import pytest
from settings import test_settings
from testdata import index_fillings as es_test_data


@pytest.fixture
def film_cache_exepted():
    return [
        {
            'uuid': film.get('id'),
            'title': film.get('title'),
            'imdb_rating': film.get('imdb_rating'),
        }
        for film in es_test_data.movies
    ]


@pytest.mark.asyncio
async def test_cache(
    make_get_request,
    make_post_request,
    es_write_data,
    es_drop_data,
    film_cache_exepted,
):
    """Поиск в кеше."""

    # Запись данных в Elasticsearch
    await es_write_data(
        index='movies',
        data=es_test_data.movies,
    )

    # Запись данных в кеш
    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={'sort': '-imdb_rating'},
    ) as response:
        assert response.status == http.HTTPStatus.OK

    # Удаление данных из Elasticsearch
    await es_drop_data(index='movies')

    # Проверка удаления данных из Elasticsearch
    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={
            'sort': '-imdb_rating',
            'page[number]': 1,
            'page[size]': 50,
            'filter[genre]': 'fb58fd7f-7afd-447f-b833-e51e45e2a778',
        },
    ) as response:
        assert response.status == http.HTTPStatus.NOT_FOUND

    # Проверка наличия данных в кеше
    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={'sort': '-imdb_rating'},
    ) as response:
        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == len(film_cache_exepted), 'Проверка количества полей.'
        assert body == film_cache_exepted, 'Проверка соответствия данных.'

    # Попытка удалнеия данных из кеша (неверный токен)
    token = jwt.encode(
        {'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=10), 'iat': datetime.datetime.utcnow()},
        'wrong secret',
        algorithm='HS256',
    )
    async with make_post_request(
        handler_url='/api/v1/services/flush-cache',
        headers={'Authorization': f'Bearer {token}'},
    ) as response:
        assert response.status == http.HTTPStatus.UNAUTHORIZED

    # Удфление данных из кеша
    token = jwt.encode(
        {'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=10), 'iat': datetime.datetime.utcnow()},
        test_settings.SECRET,
        algorithm='HS256',
    )
    async with make_post_request(
        handler_url='/api/v1/services/flush-cache',
        headers={'Authorization': f'Bearer {token}'},
    ) as response:
        assert response.status == http.HTTPStatus.OK

    # Проверка удаления данных из кеша
    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={'sort': '-imdb_rating'},
    ) as response:
        assert response.status == http.HTTPStatus.NOT_FOUND
