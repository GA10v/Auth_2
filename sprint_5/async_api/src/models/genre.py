from typing import Optional

from pydantic.fields import Field

from models.utils import DefaultModel


class ESGenre(DefaultModel):
    """Модель описывающая document в Elasticserch."""

    uuid: str = Field(..., alias='id')
    name: str
    description: Optional[str]


class GenreResponse(DefaultModel):
    """Информация о жанре."""

    uuid: str
    name: str


class DetailGenreResponse(GenreResponse):
    """Полная информация по жанрам."""

    description: Optional[str]
