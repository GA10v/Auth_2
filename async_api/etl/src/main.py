import argparse
import datetime
import logging.config
from time import sleep

import jwt
import psycopg2
import requests
from config import settings
from elasticsearch import Elasticsearch
from psycopg2.extras import DictCursor
from states.state import State
from states.state_storage import JsonFileStorage
from utils import Backoff, db_conn

from etl.extract import PartName, PostgresExtracting
from etl.load import ElasticLoader
from etl.transform import ElasticTransformer

logging.config.dictConfig(settings.LOG_CONFIG)
logger = logging.getLogger(__name__)


@Backoff()
def start_etl_process(
    parts_to_extract: list[PartName],
    pg_batch_size: int,
    es_batch_size: int,
) -> None:
    state = State(JsonFileStorage('./src/data/state.json'))

    with db_conn(psycopg2.connect(**settings.postgres.dsl, cursor_factory=DictCursor)) as conn:
        extract = PostgresExtracting(conn, state, settings.DEFAULT_PROCESS_TIME, parts_to_extract, pg_batch_size)

        transform = ElasticTransformer(extract)

        loader = ElasticLoader(
            transform,
            Elasticsearch(settings.elastic.hosts),
            settings.elastic.INDEX,
            settings.elastic.INDEX_FILES,
            es_batch_size,
        )

        loader.load()

        if loader.is_loaded:
            token = jwt.encode(
                {'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=5), 'iat': datetime.datetime.utcnow()},
                settings.SECRET,
                algorithm='HS256',
            )
            url = settings.FAST_APU_URL + '/api/v1/services/flush-cache'
            response = requests.post(url=url, headers={'Authorization': f'Bearer {token}'})
            if response.status_code != 200:
                logger.warning('Request for url %s, return status_code: %s', url, response.status_code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--init',
        help='Start ETL process only for films parts',
        action='store_const',
        const=True,
        default=False,
    )
    parser.add_argument('--ex-batch-size', type=int, help='Count extracted data from', default=1000)
    parser.add_argument('--ld-batch-size', type=int, help='Count loaded data for one iteration of ETL', default=1000)
    parser.add_argument('--freq', type=int, help='How often should the process be performed in minutes', default=10)
    args = parser.parse_args()

    if args.init:
        parts = [PartName.films]
    else:
        parts = [PartName.films, PartName.films_persons, PartName.films_genres, PartName.persons, PartName.genres]

    while True:
        start_etl_process(parts, args.ex_batch_size, args.ld_batch_size)
        sleep(args.freq * 60)
