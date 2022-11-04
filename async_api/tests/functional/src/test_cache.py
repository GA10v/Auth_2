import http

import pytest
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


@pytest.fixture
def genre_cache_exepted():
    return {
        'uuid': es_test_data.genres[0].get('id'),
        'name': es_test_data.genres[0].get('name'),
        'description': es_test_data.genres[0].get('description'),
    }


@pytest.fixture
def person_cache_exepted():
    return [
        {
            'uuid': film.get('id'),
            'title': film.get('title'),
            'imdb_rating': film.get('imdb_rating'),
        }
        for film in es_test_data.movies
    ][0:20]


@pytest.mark.asyncio
async def test_cache(
    make_get_request,
    es_write_data,
    es_drop_data,
    genre_cache_exepted,
    film_cache_exepted,
    person_cache_exepted,
):
    """Поиск в кеше."""

    # Запись данных в Elasticsearch
    await es_write_data(
        index='movies',
        data=es_test_data.movies,
    )
    await es_write_data(
        index='genres',
        data=es_test_data.genres,
    )
    await es_write_data(
        index='persons',
        data=es_test_data.persons,
    )

    # Запись данных в кеш
    genre_id = es_test_data.genres[0].get('id')
    async with make_get_request(
        handler_url=f'/api/v1/genres/{genre_id}',
    ) as response:
        assert response.status == http.HTTPStatus.OK

    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={'sort': '-imdb_rating'},
    ) as response:
        assert response.status == http.HTTPStatus.OK

    person_id = 'e039eedf-4daf-452a-bf92-a0085c68e156'
    async with make_get_request(
        handler_url=f'/api/v1/persons/{person_id}/film',
    ) as response:
        assert response.status == http.HTTPStatus.OK

    # Удаление данных из Elasticsearch

    await es_drop_data(index='movies')
    await es_drop_data(index='genres')
    await es_drop_data(index='persons')

    # Проверка удаления данных из Elasticsearch
    genre_id = es_test_data.genres[2].get('id')
    async with make_get_request(
        handler_url=f'/api/v1/genres/{genre_id}',
    ) as response:
        assert response.status == http.HTTPStatus.NOT_FOUND

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

    person_id = 'efdd1787-8871-4aa9-b1d7-f68e55b913ed'
    async with make_get_request(
        handler_url=f'/api/v1/persons/{person_id}/film',
    ) as response:
        assert response.status == http.HTTPStatus.NOT_FOUND

    # Проверка наличия данных в кеше
    genre_id = es_test_data.genres[0].get('id')
    async with make_get_request(
        handler_url=f'/api/v1/genres/{genre_id}',
    ) as response:
        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == len(genre_cache_exepted), 'Проверка количества полей.'
        assert body == genre_cache_exepted, 'Проверка соответствия данных.'

    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={'sort': '-imdb_rating'},
    ) as response:
        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == len(film_cache_exepted), 'Проверка количества полей.'
        assert body == film_cache_exepted, 'Проверка соответствия данных.'

    person_id = 'e039eedf-4daf-452a-bf92-a0085c68e156'
    async with make_get_request(
        handler_url=f'/api/v1/persons/{person_id}/film',
    ) as response:
        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == len(person_cache_exepted), 'Проверка количества полей.'
        assert body == person_cache_exepted, 'Проверка соответствия данных.'
