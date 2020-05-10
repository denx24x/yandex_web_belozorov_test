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
parser.add_argument('val', required=True, type=int)
parser.add_argument('type', required=True, type=str, choices=('comment', 'mod'))
parser.add_argument('api_key', required=False)


class VoteResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        now_user = get_sender_user(session, args)
        if args['type'] == 'mod':
            mod = session.query(Mod).get(args['id'])
            if not mod:
                return abort(404)
            was = session.query(ModRating).filter(and_(ModRating.mod_id == mod.id, ModRating.user_id == now_user.id)).first()
            rate = ModRating(user_id=now_user.id, mod_id=mod.id, rating=(1 if args['val'] else -1))
            if was:
                if was.rating == (1 if args['val'] else -1):
                    session.delete(was)
                    session.commit()
                    session.close()
                    return jsonify({'success': 'OK'})
                session.delete(was)
            session.add(rate)
        else:
            comment = session.query(Comment).get(args['id'])
            if not comment:
                return abort(404)
            was = session.query(CommentRating).filter(and_(CommentRating.comment_id == comment.id, CommentRating.user_id == now_user.id)).first()
            if was:
                if was.rating == (1 if args['val'] else -1):
                    session.delete(was)
                    session.commit()
                    session.close()
                    return jsonify({'success': 'OK'})
                session.delete(was)
            rate = CommentRating(user_id=now_user.id, comment_id=comment.id, rating=(1 if args['val'] else -1))
            session.add(rate)
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})
