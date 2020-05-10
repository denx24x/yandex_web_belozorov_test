from flask import jsonify, abort
from data import db_session
from data.news import News
from data.users import User
from flask_restful import Resource, reqparse
from flask_login import current_user
from data.longpoll_events import *
from data.user_messages import UserMessage
import json
from sqlalchemy import and_


def abort_if_user_not_found(session, id):
    user = session.query(User).get(id)
    if not user:
        abort(404, f"User {id} not found")


def check_api_key(session, api_key):
    sender = session.query(User).filter(User.api_key == api_key).first()
    if not sender:
        abort(400, "Wrong api_key")
    if not sender.verified:
        abort(403, "Account is not verified")


def abort_if_news_not_found(id):
    session = db_session.create_session()
    news = session.query(News).get(id)
    if not news:
        abort(404, f"News {id} not found")


def get_sender_user(session, args):
    if not current_user.is_authenticated:
        if 'api_key' not in args:
            return abort(404)
        now_user = session.query(User).filter(
            User.api_key == args['api_key']).first()
    else:
        now_user = session.query(User).get(current_user.id)
    if not now_user:
        return abort(400)
    if not now_user.verified:
        return abort(403, "Account is not verified")
    return now_user
