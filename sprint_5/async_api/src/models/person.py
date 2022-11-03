from typing import Optional

from pydantic.fields import Field

from models.utils import DefaultModel


class ESPerson(DefaultModel):
    """Модель описывающая document в Elasticserch."""

    uuid: str = Field(..., alias='id')
    full_name: str
    role: Optional[list[str]]
    film_ids: Optional[list[str]]


class PersonResponse(DefaultModel):
    """Информация о персонах."""

    uuid: str
    full_name: str


class DetailPersonResponse(PersonResponse):
    """Полная информация по персонам."""

    role: Optional[list[str]]
    film_ids: Optional[list[str]]
