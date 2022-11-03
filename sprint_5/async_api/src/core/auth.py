import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings


class AuthHandler:
    security = HTTPBearer()
    secret = settings.SECRET

    async def decode_token(self, token):
        try:
            return jwt.decode(token, self.secret, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Signature has expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Token is invalid')

    async def auth_wrapper(self, auth: HTTPAuthorizationCredentials = Security(security)):
        return await self.decode_token(auth.credentials)
