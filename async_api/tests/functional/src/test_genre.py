import http

import pytest
from testdata import index_fillings as es_test_data


@pytest.fixture
def genre_by_id_exepted():
    return {
        'uuid': es_test_data.genres[0].get('id'),
        'name': es_test_data.genres[0].get('name'),
        'description': es_test_data.genres[0].get('description'),
    }


@pytest.fixture
def genre_full_exepted():
    return [
        {
            'uuid': genre.get('id'),
            'name': genre.get('name'),
            'description': genre.get('description'),
        }
        for genre in es_test_data.genres
    ]


@pytest.mark.asyncio
async def test_genre_by_id(make_get_request, es_write_data, genre_by_id_exepted):
    """Поиск по id."""

    await es_write_data(
        index='genres',
        data=es_test_data.genres,
    )
    genre_id = es_test_data.genres[0].get('id')
    async with make_get_request(
        handler_url=f'/api/v1/genres/{genre_id}',
    ) as response:

        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == len(genre_by_id_exepted), 'Проверка количества полей'
        assert body == genre_by_id_exepted, 'Проверка соответствия данных'

    wrong_genre_id = 'g000-000-000-000-000'
    async with make_get_request(
        handler_url=f'/api/v1/genres/{wrong_genre_id}',
    ) as response:

        assert response.status == http.HTTPStatus.NOT_FOUND, 'Проверка поиска по несуществующему id.'


@pytest.mark.asyncio
async def test_full_films(make_get_request, es_write_data, genre_full_exepted):
    """Поиск всех жанров."""

    await es_write_data(
        index='genres',
        data=es_test_data.genres,
    )
    async with make_get_request(
        handler_url='/api/v1/genres/',
    ) as response:

        assert response.status == http.HTTPStatus.OK
        body = await response.json()
        assert len(body) == len(genre_full_exepted), 'Проверка наличия всех фильмов.'

        assert body == genre_full_exepted, 'Проверка соответствия данных.'
