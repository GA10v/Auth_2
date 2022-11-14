from enum import Enum
from logging import config as logging_config
from pathlib import Path

from pydantic import BaseSettings

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class BaseConfig(BaseSettings):
    class Config:
        env_file = Path(Path(__file__).parent.parent.parent, '.env')
        env_file_encoding = 'utf-8'


class RedisSettings(BaseConfig):
    HOST: str = '127.0.0.1'
    PORT: int = 6379

    class Config:
        env_prefix = 'REDIS_'

    @property
    def url(self):
        return f'redis://{self.HOST}:{self.PORT}'


class ElasticSettings(BaseConfig):
    HOST: str = '127.0.0.1'
    PORT: int = 9200

    class Config:
        env_prefix = 'ES_'

    @property
    def hosts(self):
        return [{'host': self.HOST, 'port': self.PORT}]


class JWTSettings(BaseConfig):
    SECRET_KEY: str = '245585dbb5cbe2f151742298d61d364880575bff0bdcbf4ae383f0180e7e47dd'
    JWT_TOKEN_LOCATION: list = ['headers']
    ALGORITHM: str = 'HS256'

    class Config:
        env_prefix = 'JWT_'


class PermissionSettings(Enum):
    User = 0
    Subscriber = 1
    Vip_subscriber = 2
    Moderator = 3


class AuthSettings(BaseConfig):
    HOST: str = '127.0.0.1'
    PORT: int = 10443

    class Config:
        env_prefix = 'AUTH_'

    @property
    def url(self):
        return f'http://{self.HOST}:{self.PORT}/api/v1/fastapi/'


class DebugSettings:
    DEBUG: bool = True
    access_token: str = '...'


class ProjectSettings(BaseConfig):

    SECRET: str = '245585dbb5cbe2f151742298d61d364880575bff0bdcbf4ae383f0180e7e47dd'
    PROJECT_NAME: str = 'movies'
    BASE_DIR = Path(__file__).parent.parent
    FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5
    redis: RedisSettings = RedisSettings()
    elastic: ElasticSettings = ElasticSettings()
    jwt: JWTSettings = JWTSettings()
    permission = PermissionSettings
    auth: AuthSettings = AuthSettings()
    debug: DebugSettings = DebugSettings()


settings = ProjectSettings()
