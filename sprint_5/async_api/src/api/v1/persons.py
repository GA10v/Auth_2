from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from api.v1.utils import PaginatedParams
from core.logger import logger as _logger
from models.film import FilmResponse
from models.person import DetailPersonResponse
from services.person import PersonService, get_person_service
from services.response_messages import PersonMessages as Msg

logger = _logger(__name__)
router = APIRouter()


@router.get(
    path='/search',
    response_model=list[DetailPersonResponse],
    summary='Поиск персон',
    description='Полнотекстовый поиск по персонам',
    response_description='Список персон с их именем, ролями и фильмографией',
)
async def search_person(
    query: str,
    service: PersonService = Depends(get_person_service),
    paginate: PaginatedParams = Depends(),
) -> list[DetailPersonResponse] | None:
    person = await service.get_person_by_search(
        query=query,
        page_num=paginate.num,
        page_size=paginate.size,
    )
    if not person:
        logger.debug('[-] %s. query: %s', Msg.not_found.value, query)
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=Msg.not_found.value)
    return person


@router.get(
    path='/{person_id}',
    response_model=DetailPersonResponse,
    summary='Поиск персоны по ID',
    description='Поиск персоны по ID',
    response_description='Имя, роль и фильмография персоны',
)
async def person_details(
    person_id: str,
    service: PersonService = Depends(get_person_service),
) -> DetailPersonResponse | None:
    person = await service.get_by_id(person_id=person_id)
    if not person:
        logger.debug('[-] %s. id: %s', Msg.not_found.value, person_id)
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=Msg.not_found.value)
    return person


@router.get(
    path='/{person_id}/film',
    response_model=list[FilmResponse],
    summary='Поиск всех кинопроизведений персоны по его ID',
    description='Поиск персоны по его ID и выдача всех его кинопроизведений',
    response_description='Список названий и рейтингов кинопроизведений',
)
async def person_films(
    person_id: str,
    service: PersonService = Depends(get_person_service),
) -> list[FilmResponse] | None:
    person_films = await service.get_film_person_by_search(_person=person_id)
    if not person_films:
        logger.debug('[-] %s. id: %s', Msg.not_found.value, person_id)
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=Msg.not_found.value)
    return person_films
