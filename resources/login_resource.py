from flask import jsonify, abort
from data import db_session
from data.news import News
from data.users import User
from flask_restful import Resource, reqparse
from flask_login import current_user
from data.longpoll_events import *
from data.user_messages import UserMessage
from .resource_basic import *
import json
from sqlalchemy import and_
from email_handle import *
from flask_login import login_user

parser = reqparse.RequestParser()
parser.add_argument('email', required=True, type=str)
parser.add_argument('password', required=True, type=str)
parser.add_argument('remember', required=True, type=str)


class LoginResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).filter(User.email == args['email']).first()
        if not user:
            return {'answer': 'Неверный логин или пароль', 'success': 'failed'}
        if user.check_password(args['password']):
            if user.verified:
                login_user(user, remember=(True if args['remember'] == 'on' else False))
                return {'answer': ' формат', 'success': 'OK'}
            else:
                return {'answer': 'Ваш аккаунт не подтвержден.', 'success': 'failed'}
        return {'answer': 'Неверный логин или пароль', 'success': 'failed'}
