import uuid

film_ids_1 = [str(uuid.uuid4()) for _ in range(20)]
film_ids_2 = [str(uuid.uuid4()) for _ in range(30)]

movies = [
    {
        'id': film_id,
        'title': 'The Man',
        'imdb_rating': 8.5,
        'description': 'Man',
        'genre': [
            {'id': '6c162475-c7ed-4461-9184-001ef3d9f26e', 'name': 'Action'},
            {'id': 'fb58fd7f-7afd-447f-b833-e51e45e2a778', 'name': 'Sci-Fi'},
        ],
        'director': [
            {'id': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', 'name': 'Stan'},
        ],
        'actors_names': ['Ann'],
        'writers_names': ['Ben'],
        'actors': [
            {'id': '26e83050-29ef-4163-a99d-b546cac208f8', 'name': 'Ann'},
        ],
        'writers': [
            {'id': 'e039eedf-4daf-452a-bf92-a0085c68e156', 'name': 'Ben'},
        ],
    }
    for film_id in film_ids_1
]

movies_2 = [
    {
        'id': film_id,
        'imdb_rating': 8.5,
        'genre': [
            {'id': '120a21cf-9097-479e-904a-13dd7198c1dd', 'name': 'Drama'},
        ],
        'title': 'The Shawshank Redemption',
        'description': 'Jail break man',
        'director': [
            {'id': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a"', 'name': 'Stan'},
        ],
        'actors_names': ['Bob'],
        'writers_names': ['Howard', 'Ann'],
        'actors': [
            {'id': 'b5d2b63a-ed1f-4e46-8320-cf52a32be358', 'name': 'Bob'},
        ],
        'writers': [
            {'id': '26e83050-29ef-4163-a99d-b546cac208f8', 'name': 'Ann'},
            {'id': 'efdd1787-8871-4aa9-b1d7-f68e55b913ed', 'name': 'Howard'},
        ],
    }
    for film_id in film_ids_2
]

movies.extend(movies_2)

genres = [
    {'id': '6c162475-c7ed-4461-9184-001ef3d9f26e', 'name': 'Action', 'description': 'Description'},
    {'id': 'fb58fd7f-7afd-447f-b833-e51e45e2a778', 'name': 'Sci-Fi', 'description': 'Description'},
    {'id': '120a21cf-9097-479e-904a-13dd7198c1dd', 'name': 'Drama', 'description': 'Description'},
]

persons = [
    {'id': 'p777', 'full_name': 'Joe', 'role': ['actor', 'director'], 'film_ids': ['f000', 'f111', 'f222']},
    {
        'id': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a"',
        'full_name': 'Stan',
        'role': ['director'],
        'film_ids': film_ids_1 + film_ids_2,
    },
    {
        'id': '26e83050-29ef-4163-a99d-b546cac208f8',
        'full_name': 'Ann',
        'role': ['director'],
        'film_ids': film_ids_1 + film_ids_2,
    },
    {'id': 'b5d2b63a-ed1f-4e46-8320-cf52a32be358', 'full_name': 'Bob', 'role': ['director'], 'film_ids': film_ids_2},
    {'id': 'e039eedf-4daf-452a-bf92-a0085c68e156', 'full_name': 'Ben', 'role': ['director'], 'film_ids': film_ids_1},
    {'id': 'efdd1787-8871-4aa9-b1d7-f68e55b913ed', 'full_name': 'Howard', 'role': ['director'], 'film_ids': film_ids_2},
    {'id': 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a', 'full_name': 'Boby', 'role': ['director'], 'film_ids': film_ids_1},
]
