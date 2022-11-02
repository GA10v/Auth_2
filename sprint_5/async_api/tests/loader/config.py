from pathlib import Path

from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    class Config:
        env_file = Path(Path(__file__).parent.parent.parent, '.test.env')
        env_file_encoding = 'utf-8'


class TestSettings(BaseConfig):
    USER: str
    PASSWORD: str
    DB: str
    HOST: str
    PORT: str = '5432'

    @property
    def uri(self):
        return f'postgresql://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}'

    @property
    def dsl(self):
        return {
            'dbname': self.DB,
            'user': self.USER,
            'password': self.PASSWORD,
            'host': self.HOST,
            'port': self.PORT,
        }

    class Config:
        env_prefix = 'PG_'


settings = TestSettings()
