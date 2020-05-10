from flask import jsonify, abort
from data import db_session
from data.news import News
from data.users import User
from flask_restful import Resource, reqparse
from .resource_basic import *


postParser = reqparse.RequestParser()
postParser.add_argument('api_key', required=False)


class ApiKeyUpdate(Resource):
    def post(self):
        args = postParser.parse_args()
        session = db_session.create_session()
        user = get_sender_user(session, args)
        user.set_api_key()
        session.commit()
        return user.api_key
