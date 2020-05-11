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
from data.mods import *
from data.mod_rating import *
from data.comments import *
from data.comment_rating import *
from sqlalchemy import and_

parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('api_key', required=False)


class UserRestrictComment(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        now_user = get_sender_user(session, args)
        if not now_user.can_control_users:
            abort(403)
        user = session.query(User).get(args['id'])
        if not user:
            abort(404)
        user.can_comment = not user.can_comment
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class UserRestrictPostMod(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        now_user = get_sender_user(session, args)
        if not now_user.can_control_users:
            abort(403)
        user = session.query(User).get(args['id'])
        if not user:
            abort(404)
        user.can_make_mods = not user.can_make_mods
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class UserRestrictControlNews(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        now_user = get_sender_user(session, args)
        if not now_user.can_control_users:
            abort(403)
        user = session.query(User).get(args['id'])
        if not user:
            abort(404)
        user.can_control_news = not user.can_control_news
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class UserRestrictControlMods(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        now_user = get_sender_user(session, args)
        if not now_user.can_control_users:
            abort(403)
        user = session.query(User).get(args['id'])
        if not user:
            abort(404)
        user.can_control_mods = not user.can_control_mods
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})


class UserRestrictControlUsers(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        now_user = get_sender_user(session, args)
        if not now_user.can_control_users:
            abort(403)
        user = session.query(User).get(args['id'])
        if not user:
            abort(404)
        user.can_control_users = not user.can_control_users
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})
