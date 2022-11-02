from fastapi import APIRouter, Depends

from core import auth
from core.logger import logger as _logger
from db.cache import CacheProtocol, get_cache_instance

logger = _logger(__name__)
router = APIRouter()
auth_handler = auth.AuthHandler()


@router.post('/flush-cache')
async def flush_cache(
    _user: dict = Depends(auth_handler.auth_wrapper),
    cache: CacheProtocol = Depends(get_cache_instance),
):
    await cache.flushall()
