import psycopg2  # noqa: F401
from data.models import PG_MODELS
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch  # noqa: F401


class PGLoader:
    def __init__(
        self,
        connection: _connection,
    ) -> None:
        self.connection = connection

    def load_all(self, data: list) -> None:
        for table_name, table_data in data:
            self._load(table_name, table_data)

    def _load(self, table_name: str, data: list) -> None:
        fields_list = [
            field.name for field in [_ for _ in PG_MODELS.get('film_work').__dict__.get('__fields__')]  # noqa: C416
        ]  # noqa: C416
        fields_list
        pass
