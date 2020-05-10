import sqlalchemy
from .db_session import SqlAlchemyBase


ViewerAssociation = sqlalchemy.Table('ViewerAssociation', SqlAlchemyBase.metadata,
    sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('User.id'), primary_key=True),
    sqlalchemy.Column('mod_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('Mod.id'), primary_key=True)
)
