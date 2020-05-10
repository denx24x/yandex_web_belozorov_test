import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
import random
from string import ascii_letters


class Confirmation(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Confirmation'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    code = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("User.id"))
    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    user = orm.relation('User')

    def generate_code(self):
        self.code = ''.join([random.choice(ascii_letters) for i in range(32)])

    def to_dict(self, only=(), rules=(),
                date_format=None, datetime_format=None, time_format=None, tzinfo=None,
                decimal_format=None, serialize_types=None):
        return {
            'id': self.id,
            'code': self.title,
            'user_id': self.content,
        }

