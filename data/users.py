import datetime
from flask_login import UserMixin
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.datastructures import FileStorage
from sqlalchemy import orm
from string import ascii_letters
import random
from .viewer_association import ViewerAssociation
from sqlalchemy.ext.declarative import declarative_base
from .db_session import SqlAlchemyBase
import base64


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'User'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              unique=True, nullable=True)
    can_control_news = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    can_control_mods = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    can_control_users = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    can_control_comments = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    can_make_mods = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    can_comment = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    api_key = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)

    profile_image = sqlalchemy.Column(sqlalchemy.String, default='\\$HOME\\tmp\\profile_image_default.png')

    verified = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    update_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    rated_mods = orm.relation('ModRating', lazy='dynamic')
    rated_comments = orm.relation('CommentRating', lazy='dynamic')

    posted_news = orm.relation('News', lazy='dynamic')
    posted_mods = orm.relation('Mod', lazy='dynamic')
    posted_comments = orm.relation('Comment', lazy='dynamic')

    viewed = orm.relationship("Mod", secondary="ViewerAssociation", backref=orm.backref("viewed"), lazy='dynamic')

    def get_rating(self):
        res = 0
        for i in self.posted_mods:
            res += i.get_rating().get_absolute()
        for i in self.posted_comments:
            res += i.get_rating().get_absolute()
        return res

    def set_api_key(self):
        self.api_key = ''.join([random.choice(ascii_letters) for i in range(32)])

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def to_dict(self, only=(), rules=(),
                date_format=None, datetime_format=None, time_format=None, tzinfo=None,
                decimal_format=None, serialize_types=None):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'verified': self.verified,
            'created_date': self.created_date,
            'can_control_news': self.can_control_news,
            'can_control_mods': self.can_control_mods,
            'can_control_users': self.can_control_users,
            'can_control_comments': self.can_control_comments,
            'can_make_mods': self.can_make_mods,
            'can_comment': self.can_comment
        }
