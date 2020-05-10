from flask import jsonify, abort
from data import db_session
from data.news import News
from data.users import User
from flask_restful import Resource, reqparse
from .resource_basic import *


postParser = reqparse.RequestParser()
postParser.add_argument('title', required=True)
postParser.add_argument('api_key', required=True)
postParser.add_argument('content', required=True)

deleteParser = reqparse.RequestParser()
deleteParser.add_argument('id', required=True, type=int)
deleteParser.add_argument('api_key', required=True)

putParser = reqparse.RequestParser()
putParser.add_argument('id', required=True, type=int)
putParser.add_argument('api_key', required=True)
putParser.add_argument('title', required=True)
putParser.add_argument('content', required=True)


class NewsResource(Resource):
    def get(self, id):
        abort_if_news_not_found(id)
        session = db_session.create_session()
        news = session.query(News).get(id)
        return jsonify({'news': news.to_dict(
            only=('id', 'title', 'content', 'user_id'))})


class NewsListResource(Resource):
    def get(self):
        session = db_session.create_session()
        news = session.query(News).all()
        return jsonify({'news': [item.to_dict(
            only=('id', 'title', 'content', 'user.name')) for item in news]})

    def post(self):
        args = postParser.parse_args()
        session = db_session.create_session()
        check_api_key(session, args['api_key'])
        news = News(
            title=args['title'],
            content=args['content'],
            user_id=session.query(User).filter(User.api_key == args['api_key']).first().id,
        )
        session.add(news)
        session.commit()
        return jsonify({'success': 'OK'})

    def delete(self):
        args = deleteParser.parse_args()
        session = db_session.create_session()
        check_api_key(session, args['api_key'])
        id = args['id']
        abort_if_news_not_found(id)
        news = session.query(News).get(id)
        session.delete(news)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self):
        args = putParser.parse_args()
        session = db_session.create_session()
        check_api_key(session, args['api_key'])
        abort_if_news_not_found(args['id'])
        news = session.query(News).get(args['id'])
        newNews = News(
            id=news.id,
            title=args['title'],
            content=args['content'],
            user_id=news.user_id,
            created_date=news.created_date
        )
        session.delete(news)
        session.add(newNews)
        session.commit()
        return jsonify({'success': 'OK'})
