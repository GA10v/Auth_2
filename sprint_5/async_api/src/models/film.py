from typing import Optional

from pydantic.fields import Field

from models.genre import GenreResponse
from models.person import PersonResponse
from models.utils import DefaultModel


class ESFilmPerson(DefaultModel):

    uuid: str = Field(..., alias='id')
    full_name: str = Field(..., alias='name')


class ESFilmGenre(DefaultModel):

    uuid: str = Field(..., alias='id')
    name: str


class ESFilm(DefaultModel):
    """Модель описывающая document в Elasticserch."""

    uuid: str = Field(..., alias='id')
    title: str
    description: Optional[str]
    imdb_rating: float
    directors: Optional[list[ESFilmPerson]] = Field(..., alias='director')
    actors_names: Optional[list[str]]
    writers_names: Optional[list[str]]
    actors: Optional[list[ESFilmPerson]]
    writers: Optional[list[ESFilmPerson]]
    genre: Optional[list[ESFilmGenre]]


class FilmResponse(DefaultModel):
    """Информация о фильме на главной странице | странице поиска."""

    uuid: str
    title: str
    imdb_rating: float


class DetailFilmResponse(FilmResponse):
    """Полная информация по фильму."""

    description: Optional[str] = ''
    genre: Optional[list[GenreResponse]] = []
    actors: Optional[list[PersonResponse]] = []
    writers: Optional[list[PersonResponse]] = []
    directors: Optional[list[PersonResponse]] = []
