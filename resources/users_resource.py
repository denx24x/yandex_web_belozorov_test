from flask import jsonify, abort
from data import db_session
from data.users import User
from flask_restful import Resource, reqparse
from .resource_basic import *


class UserResource(Resource):
    def get(self, id):
        session = db_session.create_session()
        abort_if_user_not_found(session, id)
        users = session.query(User).get(id)
        session.close()
        return jsonify({'users': users.to_dict(
            only=('id', 'name', 'email'))})


class UserListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        session.close()
        return jsonify({'users': [item.to_dict(
            only=('id', 'name', 'email')) for item in users]})
