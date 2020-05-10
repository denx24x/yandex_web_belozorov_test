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

parser = reqparse.RequestParser()
parser.add_argument('email', required=True, type=str)
parser.add_argument('type', required=True, type=str, choices=['verification', 'password_reset'])


class ConfirmationResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = session.query(User).filter(User.email == args['email']).first()
        if not user:
            return {'answer': 'Неверный email', 'success': 'failed'}
        conf = session.query(Confirmation).filter(
            and_(Confirmation.user_id == user.id, Confirmation.type == args['type'])).first()
        if conf:
            dif = datetime.datetime.now() - conf.created_date
            if dif.total_seconds() < 300:
                return {'answer': 'Нельзя запрашивать чаще, чем раз в 5 минут', 'success': 'failed'}
        if args['type'] == "verification":
            if user.verified:
                return {'answer': 'Аккаунт уже подтвержден', 'success': 'failed'}
            if send_verification_message(user):
                return {'answer': 'Подтверждение отправлено на ' + args['email'] + '!', 'success': 'OK'}
        elif args['type'] == "password_reset":
            if send_password_reset_message(user):
                return {'answer': 'Подтверждение отправлено на ' + args['email'] + '!', 'result': 'success'}
        return {'answer': 'Невозможно отправить подтверждение на заданный email', 'success': 'failed'}
