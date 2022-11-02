from typing import Awaitable, Protocol

import orjson
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import StreamingResponse

from core.config import settings
from db.redis import redis


class CacheProtocol(Protocol):
    def get(self, *args, **kwargs) -> Awaitable:
        ...

    def set(self, *args, **kwargs) -> Awaitable:
        ...

    def flushall(self, *args, **kwargs) -> Awaitable:
        ...


class CacheMiddleWare:
    def __init__(
        self,
        client: CacheProtocol,
    ):
        self.client = client

    async def __call__(self, request: Request, call_next):
        key = str(request.url.include_query_params())
        cached_response = await self.client.get(key)
        if not cached_response:
            response = await call_next(request)
            if response.status_code == 200 and response.headers.get('content-type') == 'application/json':
                response, json_response = await self.serialize_response(response)
                await self.client.set(key, json_response, ex=settings.FILM_CACHE_EXPIRE_IN_SECONDS)
            return response
        return await self.deserialize_response(cached_response)

    async def serialize_response(self, response: StreamingResponse) -> tuple[ORJSONResponse, bytes]:
        serialized_response = {}
        content = b''
        async for chunk in response.body_iterator:
            content += chunk

        content = orjson.loads(content)
        serialized_response['content'] = content
        serialized_response['headers'] = dict(response.headers.items())
        serialized_response['media_type'] = response.media_type

        return ORJSONResponse(
            status_code=response.status_code,
            content=content,
            headers=response.headers,
            media_type=response.media_type,
            background=response.background,
        ), orjson.dumps(serialized_response)

    async def deserialize_response(self, data: bytes) -> ORJSONResponse:

        deserialized_data: dict = orjson.loads(data)

        return ORJSONResponse(
            content=deserialized_data['content'],
            headers=deserialized_data['headers'],
            media_type=deserialized_data['media_type'],
        )


async def get_cache_instance() -> CacheProtocol:
    return redis
