import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
import random
from string import ascii_letters


class CommentRating(SqlAlchemyBase):
    __tablename__ = 'CommentRating'
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("User.id"), primary_key=True)
    comment_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("Comment.id"), primary_key=True)
    user = orm.relation('User')
    comment = orm.relation('Comment')
    rating = sqlalchemy.Column(sqlalchemy.Integer, default=0)

