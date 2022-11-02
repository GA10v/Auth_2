import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from api.v1 import films, genres, persons, services
from core.config import settings
from core.logger import LOGGING
from db import cache, elastic, redis

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

cache_middleware = cache.CacheMiddleWare(redis.redis)
app.add_middleware(BaseHTTPMiddleware, dispatch=cache_middleware)


@app.on_event('startup')
async def startup():
    elastic.es = AsyncElasticsearch(hosts=settings.elastic.hosts)


@app.on_event('shutdown')
async def shutdown():
    await redis.redis.close()
    await elastic.es.close()


app.include_router(films.router, prefix='/api/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/api/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/api/v1/persons', tags=['persons'])
app.include_router(services.router, prefix='/api/v1/services', tags=['services'])


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level='debug',
    )
