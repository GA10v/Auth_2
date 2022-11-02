from datetime import datetime

from faker import Faker
from pydantic import BaseModel

from models import FilmWork, Genre, Person

faker = Faker()


class DefaultModel(BaseModel):
    @staticmethod
    def _person():
        return {
            'full_name': faker.name(),
            'created_at': faker.past_datetime(start_date='-30d', tzinfo=None),
            'updated_at': datetime.now(),
        }

    @staticmethod
    def _genre():
        return {
            'name': faker.name(),
            'description': faker.text(max_nb_chars=150),
            'created_at': faker.past_datetime(start_date='-30d', tzinfo=None),
            'updated_at': datetime.now(),
        }

    @staticmethod
    def _film_work():
        return {
            'title': faker.text(max_nb_chars=10),
            'description': faker.text(max_nb_chars=150),
            'creation_date': faker.past_datetime(start_date='-30y', tzinfo=None),
            'type': faker.random_element(elements=('movie', 'tv_show')),
            'created_at': faker.past_datetime(start_date='-30d', tzinfo=None),
            'updated_at': datetime.now(),
            'file_path': faker.file_path(),
            'rating': faker.random_digit(),
        }

    @staticmethod
    def _person_fw(fw: FilmWork, person: Person, role: str):
        return {'film_work_id': str(fw.id), 'person_id': str(person.id), 'role': role, 'created_at': fw.created_at}

    @staticmethod
    def _genre_fw(fw: FilmWork, genre: Genre):
        return {'film_work_id': str(fw.id), 'genre_id': str(genre.id), 'created_at': fw.created_at}
