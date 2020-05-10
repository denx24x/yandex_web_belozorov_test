import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
import random


class ModRating(SqlAlchemyBase):
    __tablename__ = 'ModRating'
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("User.id"), primary_key=True)
    mod_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("Mod.id"), primary_key=True)
    user = orm.relation('User')
    mod = orm.relation('Mod')
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)
