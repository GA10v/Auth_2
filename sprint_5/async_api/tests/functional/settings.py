from pydantic import BaseSettings, Field


class TestSettings(BaseSettings):
    es_host: str = Field('http://127.0.0.1:9200', env='ES_HOST')
    es_index: str = Field('http://127.0.0.1:9200', env='ES_INDEX')
    # es_id_field: str = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')
    # es_index_mapping: dict = Field('http://127.0.0.1:9200', env='ELASTIC_HOST')

    redis_host: str = Field('http://127.0.0.1:6379', env='REDIS_HOST')
    # service_url: str =Field('http://127.0.0.1:8000', env='ELASTIC_HOST')


test_settings = TestSettings()
