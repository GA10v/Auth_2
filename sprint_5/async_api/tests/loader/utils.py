from contextlib import contextmanager
from pathlib import Path

import psycopg2
from config import models_pg, settings  # noqa: F401
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor


@contextmanager
def pg_conn_context(dsl: settings.dsl, cursor_factory=DictCursor) -> _connection:
    """Контекстный менеджер для psql.

    Args:
        dsl: Данные для подключения к psql
        cursor_factory: Курсор
    """
    try:
        conn = psycopg2.connect(**dsl, cursor_factory=cursor_factory)
        yield conn
    except psycopg2.Error as er:
        raise er
    finally:
        conn.close()


def check_pg_models(
    dsl: settings.dsl,
    ddl_path: str = f'{Path(__file__).parent.parent}/new_movies_database.ddl',
) -> bool:
    """Функция проверки наличия схемы БД.

    Args:
        dsl: Данные для подключения к pg
        ddl_path: Путь к файлу с настройками БД
    """
    with pg_conn_context(dsl) as pg_conn:  # noqa: SIM117
        with pg_conn.cursor() as cursor:
            table_names = {
                'film_work',
                'person',
                'genre',
                'person_film_work',
                'genre_film_work',
            }
            try:
                cursor.execute(
                    "SELECT table_name \
                                FROM information_schema.tables \
                                WHERE table_schema = 'content';",
                )

                if not table_names.issubset(set([colum[0] for colum in cursor])):  # noqa: C403
                    with open(ddl_path, 'r') as f:
                        cursor.execute(f.read())
                        pg_conn.commit()
            except (FileNotFoundError, psycopg2.OperationalError) as er:
                raise er
