from flask import jsonify, abort
from data import db_session
from data.news import News
from data.mods import Mod
from flask_restful import Resource, reqparse
from data.mods import *
from .resource_basic import *

parser = reqparse.RequestParser()
parser.add_argument('id', required=True, type=int)
parser.add_argument('api_key', required=False)


class ModResource(Resource):
    def get(self, id):
        session = db_session.create_session()
        mods = session.query(Mod).get(id)
        if not mods:
            return abort(404)
        return jsonify({'mods': mods.to_dict(
            only=('id', 'title', 'content', 'user_id'))})


class ModsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        mods = session.query(Mod).all()
        return jsonify({'mods': [mods.to_dict(
            only=('id', 'title', 'content', 'user.name')) for item in mods]})


class ModConfirmResource(Resource):
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        now_user = get_sender_user(session, args)
        if not now_user.can_control_mods:
            abort(403)
        mod = session.query(Mod).get(args['id'])
        if not mod:
            abort(404)
        mod.verified_by_admin = True
        session.commit()
        session.close()
        return jsonify({'success': 'OK'})
