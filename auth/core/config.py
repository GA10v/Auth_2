from datetime import timedelta
from enum import Enum
from logging import config as logging_config
from pathlib import Path

from core.logger import LOGGING
from pydantic import BaseSettings

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


class PostgresSettings(BaseConfig):
    USER: str
    PASSWORD: str
    DB: str
    HOST: str = '127.0.0.1'
    PORT: int = 5432

    @property
    def uri(self):
        return f'postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}'

    class Config:
        env_prefix = 'PG_'


class FlaskSettings(BaseConfig):
    HOST: str = '127.0.0.1'
    PORT: int = 5000

    class Config:
        env_prefix = 'FLASK_'


class JWTSettings(BaseConfig):
    SECRET_KEY: str = '245585dbb5cbe2f151742298d61d364880575bff0bdcbf4ae383f0180e7e47dd'
    REFRESH_TOKEN_EXP: timedelta = timedelta(days=10)
    ACCESS_TOKEN_EXP: timedelta = timedelta(minutes=20)
    JWT_TOKEN_LOCATION: list = ['headers']
    ALGORITHM: str = 'HS256'

    class Config:
        env_prefix = 'JWT_'


class SecuritySettings(BaseConfig):
    SECURITY_PASSWORD_SALT: str = 'a5a8f573-3cee-4ccc-8a2b-91cb9f55250a'
    SECURITY_PASSWORD_HASH: str = 'bcrypt'


class SwaggerSettings(BaseConfig):
    SPEC_TAGS: list = [
        {
            'name': 'Auth',
            'description': 'Auth',
        },
        {
            'name': 'User',
            'description': 'User data',
        },
        {
            'name': 'Role',
            'description': 'Roles',
        },
    ]
    SWAGGER_URL: str = '/swagger'
    API_URL: str = '/static/swagger.json'


class PermissionSettings(Enum):
    User = 0
    Subscriber = 1
    Vip_subscriber = 2
    Moderator = 3


class OAuthProviders(Enum):
    yandex: str = 'yandex'
    google: str = 'google'

    @classmethod
    def check_value(cls, value):
        return value in cls._value2member_map_


class OAuthSettings(BaseConfig):
    providers: OAuthProviders = OAuthProviders
    credentials: dict = {
        'yandex': {
            'name': 'yandex',
            'id': '93bfa237f2c9460eb1f6b7b027fd335c',
            'secret': '767fb1eb31c9438796e112bc3ab16455',
            'authorize_url': 'https://oauth.yandex.ru/authorize',
            # https://yandex.ru/dev/id/doc/dg/oauth/reference/web-client.html
            'access_token_url': 'https://oauth.yandex.ru/token',
            # https://yandex.ru/dev/id/doc/dg/oauth/reference/auto-code-client.html#auto-code-client__get-token
            'base_url': 'https://login.yandex.ru/info',
            # https://yandex.ru/dev/id/doc/dg/api-id/reference/request.html
        },
        'google': {
            'name': 'google',
            'id': '...',
            'secret': '...',
            'authorize_url': '...',
            'access_token_url': '...',
            'base_url': '...',
        },
    }


class ProjectSettings(BaseConfig):
    redis: RedisSettings = RedisSettings()
    postgres: PostgresSettings = PostgresSettings()
    flask: FlaskSettings = FlaskSettings()
    jwt: JWTSettings = JWTSettings()
    security: SecuritySettings = SecuritySettings()
    swagger: SwaggerSettings = SwaggerSettings()
    permission = PermissionSettings
    oauth: OAuthSettings = OAuthSettings()


settings = ProjectSettings()
