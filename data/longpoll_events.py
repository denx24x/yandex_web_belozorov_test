import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
import random


class LongPollEvent(SqlAlchemyBase):
    __tablename__ = 'LongPollEvent'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("User.id"))
    user = orm.relation('User')
    sender = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    event_body = sqlalchemy.Column(sqlalchemy.String, nullable=False)  # json
    event_type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    delete_when_received = sqlalchemy.Column(sqlalchemy.Boolean, default=True, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
