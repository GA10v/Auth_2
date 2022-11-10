from datetime import datetime

from db import db
from flask_security import UserMixin
from models.utils import BaseModel, create_user_info_partition_by_country
from sqlalchemy.dialects.postgresql import UUID


class User(BaseModel, UserMixin):
    __tablename__ = 'users'
    username = db.Column(db.String(length=150), nullable=False, index=True)
    password = db.Column(db.String(length=150), nullable=False)
    email = db.Column(db.String(length=150), unique=True, nullable=False, index=True)
    is_super = db.Column(db.Boolean(), default=False)

    def __repr__(self) -> str:
        return f'User: {self.username} {self.id}'


class UserInfo(BaseModel):
    __tablename__ = 'user_info'
    __table_args__ = (
        db.UniqueConstraint('id', 'country'),
        {
            'schema': 'auth',
            'postgresql_partition_by': 'LIST (country)',
            'listeners': [('after_create', create_user_info_partition_by_country)],
        },
    )
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    full_name = db.Column(db.String, nullable=False)
    country = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    birthday = db.Column(db.TIMESTAMP, default=datetime.now(), nullable=False)

    def __repr__(self) -> str:
        return f'Login: {self.id} {self.date}'


class SocialAccount(BaseModel):
    __tablename__ = 'social_account'
    __table_args__ = (db.UniqueConstraint('social_id', 'social_name'), {'schema': 'auth'})
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('auth.users.id'), nullable=False)
    social_name = db.Column(db.String, nullable=False)
    social_id = db.Column(db.String, nullable=False)

    def __repr__(self) -> str:
        return f'SocialAccount: {self.social_name} {self.user_id}'
