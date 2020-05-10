from flask import jsonify, abort
from data import db_session
from data.news import News
from data.users import User
from data.comments import *
from data.mods import *
from flask_restful import Resource, reqparse
from flask_login import current_user
from data.longpoll_events import *
from data.user_messages import UserMessage
from .resource_basic import *
import json
from sqlalchemy import and_

parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('message', required=True, type=str)
parser.add_argument('type', required=True, type=str, choices=['mod', 'news', 'comment'])
parser.add_argument('api_key', required=False, type=str)


class CommentResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = get_sender_user(session, args)
        if args['type'] == 'comment':
            comment = session.query(Comment).get(args['id'])
        elif args['type'] == 'mod':
            comment = session.query(Mod).get(args['id'])
        else:
            comment = session.query(News).get(args['id'])
        if not comment:
            return abort(404)
        session.add(Comment(user_id=user.id, parent_id=args['id'], parent_type=args['type'], content=args['message']))
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})
