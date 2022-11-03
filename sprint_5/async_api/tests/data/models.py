import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class DefaultModel(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)  # noqa: VNE003


class FilmWork(DefaultModel):
    """Определение типа данных для полей таблицы film_work."""

    title: str
    description: str
    creation_date: date
    type: str  # noqa: VNE003
    created_at: datetime
    updated_at: datetime
    file_path: str
    rating: float = Field(default=0.0)


class Genre(DefaultModel):
    """Определение типа данных для полей таблицы genre."""

    name: str
    description: str
    created_at: datetime
    updated_at: datetime


class GenreFilmWork:
    """Определение типа данных для полей таблицы genre_film_work."""

    film_work_id: uuid.UUID
    genre_id: uuid.UUID
    created_at: datetime


class Person(DefaultModel):
    """Определение типа данных для полей таблицы person."""

    full_name: str
    created_at: datetime
    updated_at: datetime


class PersonFilmWork:
    """Определение типа данных для полей таблицы person_film_work."""

    film_work_id: uuid.UUID
    person_id: uuid.UUID
    role: str
    created_at: datetime


PG_MODELS = {
    'film_work': FilmWork,
    'genre': Genre,
    'genre_film_work': GenreFilmWork,
    'person': Person,
    'person_film_work': PersonFilmWork,
}
