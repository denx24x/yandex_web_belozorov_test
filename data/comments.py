import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Rating:
    def __init__(self, plus, minus):
        self.plus = plus
        self.minus = minus

    def get_absolute(self):
        return self.plus - self.minus


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Comment'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("User.id"))
    user = orm.relation('User')
    ratings = orm.relation('CommentRating')
    update_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    parent_type = sqlalchemy.Column(sqlalchemy.String)
    parent_id = sqlalchemy.Column(sqlalchemy.Integer)

    def get_rating(self):
        plus = 0
        minus = 0
        for i in self.ratings:
            if i.rating == 1:
                plus += 1
            elif i.rating == -1:
                minus += 1
        return Rating(plus, minus)
