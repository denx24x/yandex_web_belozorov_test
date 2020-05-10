import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
import random


class UserMessage(SqlAlchemyBase):
    __tablename__ = 'UserMessage'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    sender_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("User.id"))
    receiver_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("User.id"))

    sender = orm.relation("User", foreign_keys=[sender_id])
    receiver = orm.relation("User", foreign_keys=[receiver_id])

    message = sqlalchemy.Column(sqlalchemy.String, default="")
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
