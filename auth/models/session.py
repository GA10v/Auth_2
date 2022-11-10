from datetime import datetime

from db.db import db
from models.utils import BaseModel, create_sessions_partition_by_auth_date
from sqlalchemy.dialects.postgresql import UUID


class AllowedDevice(BaseModel):
    __tablename__ = 'allowed_device'
    __table_args__ = (db.UniqueConstraint('user_id', 'user_agent'), {'schema': 'auth'})
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    user_agent = db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        return f'Device: {self.id}'


class Session(BaseModel):
    __tablename__ = 'sessions'
    __table_args__ = (
        {
            'schema': 'auth',
            'postgresql_partition_by': 'RANGE (auth_date)',
            'listeners': [('after_create', create_sessions_partition_by_auth_date)],
        },
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    device_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.allowed_device.id'), nullable=False)
    auth_date = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)

    def __repr__(self) -> str:
        return f'Session: {self.id} {self.auth_date}'
