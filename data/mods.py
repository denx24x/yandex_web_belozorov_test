import datetime
import sqlalchemy
from sqlalchemy import orm, func
from .viewer_association import ViewerAssociation
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Rating:
    def __init__(self, plus, minus):
        self.plus = plus
        self.minus = minus

    def get_absolute(self):
        return self.plus - self.minus


class Mod(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Mod'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("User.id"))
    user = orm.relation('User', foreign_keys=[user_id])
    poster = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='\\uploads\\poster_default.png')

    verified_by_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    images = orm.relation('ModImages', lazy='dynamic')
    file = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    updated_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    viewers = orm.relationship("User", secondary="ViewerAssociation", backref=orm.backref("viewers"), lazy='dynamic')

    ratings = orm.relationship('ModRating', lazy='dynamic')

    def get_view_count(self):
        return len(self.viewers.all())

    def get_popularity(self):
        return self.get_view_count() / max(1, (datetime.datetime.now() - self.created_date).total_seconds())

    def get_rating(self):
        plus = 0
        minus = 0
        for i in self.ratings:
            if i.rating == 1:
                plus += 1
            elif i.rating == -1:
                minus += 1
        return Rating(plus, minus)

    def to_dict(self, only=(), rules=(),
                date_format=None, datetime_format=None, time_format=None, tzinfo=None,
                decimal_format=None, serialize_types=None):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_date': self.created_date,
            'updated_date': self.updated_date,
            'poster': self.poster,
            'images': [i.id for i in self.images],
            'author_id': self.user_id,
        }


class ModImages(SqlAlchemyBase):
    __tablename__ = 'ModImages'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    mod_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("Mod.id"))
    mod = orm.relation('Mod')
