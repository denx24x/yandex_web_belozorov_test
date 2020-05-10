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

parser = reqparse.RequestParser()
parser.add_argument('name', required=True, type=str)
parser.add_argument('message', required=True, type=str)
parser.add_argument('api_key', required=False)


class MessageResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        now_user = get_sender_user(session, args)
        user = session.query(User).filter(User.name == args['name']).first()
        if not user or not user.verified:
            return abort(404)
        session.add(UserMessage(message=args['message'], receiver_id=user.id, sender_id=now_user.id))
        load = json.dumps({'sender': now_user.name, 'receiver': user.name, 'message': args['message'], 'created_date': str(datetime.datetime.now())})
        session.add(LongPollEvent(event_body=load, event_type='message_receive', user_id=now_user.id, delete_when_received=True))
        if user.id != now_user.id:
            session.add(LongPollEvent(event_body=load, event_type='message_receive', user_id=user.id, delete_when_received=True, sender=str(user.id)))
            if not session.query(LongPollEvent).filter(and_(LongPollEvent.sender == str(now_user.id),
                                                            and_(LongPollEvent.user_id == user.id,
                                                                 LongPollEvent.event_type == 'message'))).first():
                session.add(LongPollEvent(event_type='message_unread', event_body=json.dumps({'sender': now_user.name}),
                                          delete_when_received=False, sender=str(now_user.id)))
        session.commit()
        return jsonify({'success': 'OK'})
