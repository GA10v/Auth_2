import http

import pytest
from testdata import index_fillings as es_test_data


@pytest.fixture
def film_by_id_exepted():
    return {
        'uuid': es_test_data.movies[0].get('id'),
        'title': 'The Man',
        'imdb_rating': 8.5,
        'description': 'Man',
        'genre': [
            {'uuid': '6c162475-c7ed-4461-9184-001ef3d9f26e', 'name': 'Action'},
            {'uuid': 'fb58fd7f-7afd-447f-b833-e51e45e2a778', 'name': 'Sci-Fi'},
        ],
        'actors': [{'uuid': '26e83050-29ef-4163-a99d-b546cac208f8', 'full_name': 'Ann'}],
        'writers': [{'uuid': 'e039eedf-4daf-452a-bf92-a0085c68e156', 'full_name': 'Ben'}],
        'directors': [{'uuid': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', 'full_name': 'Stan'}],
    }


@pytest.fixture
def film_full_exepted():
    return [
        {
            'uuid': film.get('id'),
            'title': film.get('title'),
            'imdb_rating': film.get('imdb_rating'),
        }
        for film in es_test_data.movies
    ]


@pytest.fixture
def film_pagination_exepted():
    def key(rating):
        return -rating['imdb_rating']

    return sorted(
        [
            {
                'uuid': film.get('id'),
                'title': film.get('title'),
                'imdb_rating': film.get('imdb_rating'),
            }
            for film in es_test_data.movies
        ],
        key=key,
    )


@pytest.mark.asyncio
async def test_film_by_id(make_get_request, es_write_data, film_by_id_exepted):
    """Поиск по id."""

    await es_write_data(
        index='movies',
        data=es_test_data.movies,
    )
    film_id = es_test_data.movies[0].get('id')
    async with make_get_request(
        handler_url=f'/api/v1/films/{film_id}',
    ) as response:

        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == len(film_by_id_exepted), 'Проверка количества полей'
        assert body == film_by_id_exepted, 'Проверка соответствия данных'

    wrong_film_id = 'f000-000-000-000-000'
    async with make_get_request(
        handler_url=f'/api/v1/films/{wrong_film_id}',
    ) as response:

        assert response.status == http.HTTPStatus.NOT_FOUND, 'Проверка поиска по несуществующему id.'


@pytest.mark.asyncio
async def test_full_films(make_get_request, es_write_data, film_full_exepted):
    """Поиск всех фильмов."""

    await es_write_data(
        index='movies',
        data=es_test_data.movies,
    )
    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={'sort': '-imdb_rating'},
    ) as response:

        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == len(film_full_exepted), 'Проверка наличия всех фильмов.'

        def desc(rating):
            return -rating['imdb_rating']

        assert body == sorted(film_full_exepted, key=desc), 'Проверка соответствия данных (DESC).'

    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={'sort': 'imdb_rating'},
    ) as response:

        def asc(rating):
            return rating['imdb_rating']

        body = await response.json()
        assert body == sorted(film_full_exepted, key=asc), 'Проверка соответствия данных (ASC).'

    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={'sort': 'title'},
    ) as response:

        assert response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY, 'Проверка сортировки с невалидными данными.'


@pytest.mark.asyncio
async def test_pagination_films(make_get_request, es_write_data, film_pagination_exepted):
    """Поиск фильмов на определенной странице."""

    await es_write_data(
        index='movies',
        data=es_test_data.movies,
    )
    page_num = 2
    page_size = 10
    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={
            'sort': '-imdb_rating',
            'page[number]': page_num,
            'page[size]': page_size,
        },
    ) as response:

        start = (page_num - 1) * page_size
        stop = page_size * page_num

        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == page_size, 'Проверка наличия всех фильмов.'
        assert body == film_pagination_exepted[start:stop], 'Проверка соответствия данных.'

    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={
            'sort': '-imdb_rating',
            'page[number]': 0,
            'page[size]': 10,
        },
    ) as response:

        assert (
            response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY
        ), 'Проверка пагинации с невалидными данными (page[number] < 1).'

    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={
            'sort': '-imdb_rating',
            'page[number]': 1,
            'page[size]': -10,
        },
    ) as response:

        assert (
            response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY
        ), 'Проверка пагинации с невалидными данными (page[size] < 1).'


@pytest.mark.asyncio
async def test_filter_films(make_get_request, es_write_data):
    """Поиск фильмов определенного жанра."""

    await es_write_data(
        index='movies',
        data=es_test_data.movies,
    )
    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={
            'sort': '-imdb_rating',
            'page[number]': 1,
            'page[size]': 50,
            'filter[genre]': '120a21cf-9097-479e-904a-13dd7198c1dd',
        },
    ) as response:
        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == 30, 'Проверка наличия всех фильмов.'

    async with make_get_request(
        handler_url='/api/v1/films/',
        query_data={
            'sort': '-imdb_rating',
            'page[number]': 1,
            'page[size]': 50,
            'filter[genre]': 'g333',
        },
    ) as response:
        assert (
            response.status == http.HTTPStatus.UNPROCESSABLE_ENTITY
        ), 'Проверка фильтрации с невалидными данными (filter[genre] not is UUID).'


@pytest.mark.asyncio
async def test_search_films(make_get_request, es_write_data):
    """Поиск фильмов по названию."""

    await es_write_data(
        index='movies',
        data=es_test_data.movies,
    )
    async with make_get_request(
        handler_url='/api/v1/films/search/',
        query_data={'query': 'man'},
    ) as response:
        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == 50, 'Проверка наличия всех фильмов.'

    async with make_get_request(
        handler_url='/api/v1/films/search/',
        query_data={'query': 'jail'},
    ) as response:
        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == 30, 'Проверка наличия всех фильмов.'
