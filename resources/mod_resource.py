from flask import jsonify, abort
from data import db_session
from data.news import News
from data.mods import Mod
from flask_restful import Resource, reqparse
from .resource_basic import *


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
