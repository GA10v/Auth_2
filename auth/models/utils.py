import uuid
from datetime import datetime

from db import db
from flask_sqlalchemy import BaseQuery
from psycopg2.errors import UniqueViolation
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import IntegrityError, PendingRollbackError


class QueryWithSoftDelete(BaseQuery):
    def __new__(cls, *args, **kwargs):
        obj = super(QueryWithSoftDelete, cls).__new__(cls)
        with_deleted = kwargs.pop('_with_deleted', False)
        if len(args) > 0:
            super(QueryWithSoftDelete, obj).__init__(*args, **kwargs)
            return obj.filter_by(is_deleted=False) if not with_deleted else obj
        return obj

    def __init__(self, *args, **kwargs):
        pass

    def with_deleted(self):
        return self.__class__(db.class_mapper(self._mapper_zero().class_), session=db.session(), _with_deleted=True)


class BaseModel(db.Model):
    __abstract__ = True
    __table_args__ = {'schema': 'auth'}
    id = db.Column(  # noqa: VNE003
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    create_at = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now(), onupdate=datetime.now(), nullable=False)
    is_deleted = db.Column(db.Boolean(), nullable=False, default=False)
    query_class = QueryWithSoftDelete

    def set(self) -> None:
        try:
            db.session.add(self)
            db.session.commit()
        except (PendingRollbackError, UniqueViolation, IntegrityError):
            raise

    def cond_delete(self):
        self.is_deleted = True


def create_user_info_partition_by_country(target, connection, **kwargs) -> None:
    """
    Партицированные таблицы user_info по полю country.

    cis('Azerbaijan', 'Armenia', 'Russia', 'Belarus', 'Kazakhstan', 'Kyrgyzstan')
    eu('Austria', 'Belgium', 'Hungary', 'Greece', 'Denmark','France', 'Germany', 'Netherlands')
    asia('China', 'Indonesia', 'Republic of Korea', 'Singapore', 'South Korea', 'Thailand', 'Japan')
    na('Canada', 'Mexico', 'USA')
    """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_info_cis" PARTITION OF "user_info"
        FOR VALUES IN ('Azerbaijan', 'Armenia', 'Russia', 'Belarus', 'Kazakhstan', 'Kyrgyzstan')""",
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_info_eu" PARTITION OF "user_info"
        FOR VALUES IN ('Austria', 'Belgium', 'Hungary', 'Greece', 'Denmark','France', 'Germany', 'Netherlands')""",
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_info_asia" PARTITION OF "user_info"
        FOR VALUES IN ('China', 'Indonesia', 'Republic of Korea', 'Singapore', 'South Korea', 'Thailand', 'Japan')""",
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_info_na" PARTITION OF "user_info"
        FOR VALUES IN ('Canada', 'Mexico', 'USA')""",
    )


def create_sessions_partition_by_auth_date(target, connection, **kwargs) -> None:
    """
    Партицированные таблицы sessions по полю auth_date.
    """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "sessions_2021" PARTITION OF "sessions"
        FOR VALUES FROM ('2021-01-01') TO ('2022-12-31');""",
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "sessions_2022" PARTITION OF "sessions"
        FOR VALUES FROM ('2022-01-01') TO ('2022-12-31');""",
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "sessions_2023" PARTITION OF "sessions"
        FOR VALUES FROM ('2023-01-01') TO ('2023-12-31');""",
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "sessions_2024" PARTITION OF "sessions"
        FOR VALUES FROM ('2024-01-01') TO ('2024-12-31');""",
    )
