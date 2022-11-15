import json
from http import HTTPStatus

import requests
from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, auth_url: str) -> None:
        super().__init__(app)
        self.auth_url = auth_url

    async def dispatch(self, request: Request, call_next) -> Response:
        if settings.debug.DEBUG:
            auth = requests.get(
                self.auth_url,
                headers={
                    'Authorization': f'Bearer {settings.debug.access_token}',
                },
            )
        else:
            auth_header = request.headers.get('Authorization')
            if auth_header is None:
                return Response('Authorization header is missing', HTTPStatus.UNAUTHORIZED)

            auth = requests.get(
                url=self.auth_url,
                headers={'Authorization': auth_header},
            )
        _content = json.loads(auth._content)['auth']
        claims = json.loads(_content)
        if claims.get('is_super'):
            return await call_next(request)

        if auth.status_code == HTTPStatus.UNAUTHORIZED:
            return Response('Not authorized', HTTPStatus.UNAUTHORIZED)

        if 'http://fastapi:8000/api/v1/films/detail/' in str(request.url):
            if settings.permission.Subscriber in claims.get('permissions'):
                return await call_next(request)
            return Response('Permission denied', HTTPStatus.FORBIDDEN)
        return await call_next(request)
