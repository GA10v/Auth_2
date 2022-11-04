from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from core.logger import logger as _logger
from models.genre import DetailGenreResponse
from services.genre import GenreService, get_genre_service
from services.response_messages import GenreMessages as Msg

logger = _logger(__name__)
router = APIRouter()


@router.get(
    path='/{uuid}',
    response_model=DetailGenreResponse,
    summary='Поиск жанра по ID',
    description='Поиск жанра по ID',
    response_description='Полная информация о жанре',
)
async def get_genre(
    uuid: str,
    service: GenreService = Depends(get_genre_service),
) -> DetailGenreResponse | None:
    genre = await service.get(uuid)
    if not genre:
        logger.debug('[-] %s. uuid:%s', Msg.not_found.value, uuid)
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=Msg.not_found.value)
    return genre


@router.get(
    path='/',
    response_model=list[DetailGenreResponse],
    summary='Главная страница жанров',
    description='Полный перечень жанров',
    response_description='Список с полной информацией о жанрах',
)
async def get_genres(
    service: GenreService = Depends(get_genre_service),
) -> list[DetailGenreResponse] | None:
    return await service.get_multi()
