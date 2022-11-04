import testdata.es_mapping as idx_mapping
from pydantic.env_settings import BaseSettings
from pydantic.fields import Field


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    es_index: list[str] = ['movies', 'persons', 'genres']
    es_id_field: str = 'id'
    es_index_mapping: dict = {
        'movies': idx_mapping.movies,
        'persons': idx_mapping.persons,
        'genres': idx_mapping.genres,
    }

    redis_host: str = Field('127.0.0.1', env='REDIS_HOST')
    service_url: str = Field('http://127.0.0.1:8000', env='SERVICE_URL')
    SECRET: str = '245585dbb5cbe2f151742298d61d364880575bff0bdcbf4ae383f0180e7e47dd'


test_settings = TestSettings()
