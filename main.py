from flask import Flask, render_template, redirect, Blueprint, jsonify, abort, request
from data import db_session
from forms import *
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from data.users import *
from data.news import *
from data.mods import *
import shutil
from functools import wraps
from data.longpoll_events import LongPollEvent
from data.comments import Comment
from data.comment_rating import CommentRating
from data.mod_rating import ModRating
from data.confirmations import Confirmation
from data.user_messages import UserMessage
from sqlalchemy import desc, func, case, and_, or_
from data.viewer_association import ViewerAssociation
from resources import news_resource, users_resource, message_resource, vote_resource, confirmation_resource, login_resource, api_update_resource, comment_resource, mod_resource
from flask_restful import reqparse, abort, Api, Resource
from flask_restful import reqparse
from werkzeug.utils import secure_filename
import random
from email_handle import *
from string import ascii_letters
import os
import time
import json
import datetime
import copy
import smtplib
from email.mime.text import MIMEText
import threading

from werkzeug.middleware.shared_data import SharedDataMiddleware
import sys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdxjPMUAAAAAEmmGwakbtfjn2x3heWhavRy_jml'
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdxjPMUAAAAAG_kKlRdY7kpG7pixTbZ1Qmaf45A'  # ой...

app.config['MOD_IMAGES_UPLOAD_FOLDER'] = 'uploads\\modImages'
app.config['USER_IMAGES_UPLOAD_FOLDER'] = 'uploads\\userImages'
app.config['MOD_FILES_UPLOAD_FOLDER'] = 'uploads\\modFiles'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

app.add_url_rule('/uploads/<filename>', 'uploaded_file',
                 build_only=True)
app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
    '/uploads':  app.config['UPLOAD_FOLDER']
})

login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)
self_url = "yandex-web-belozorov.herokuapp.com"

online_lock = threading.Lock()
longpoll_lock = threading.Lock()

users_online = {}
connected = {}


class OnlineHandler(threading.Thread):  # выносит юзера из списка онлайновых если тот долго не лонгполлил
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        time.sleep(90)
        online_lock.acquire()
        try:
            for i in users_online.keys():
                if (datetime.datetime.now() - users_online[i]).total_seconds() > 60:
                    del users_online[i]
        finally:
            online_lock.release()


class LongPollHandler(threading.Thread):  # раздача лонгполлов)))
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            time.sleep(1)
            longpoll_lock.acquire()
            try:
                for i in connected.keys():
                    user_state = check_user_state(None if i == 'other' else i)

                    for g in connected[i].keys():
                        general_state = check_general_state(None if i == 'other' else i, connected[i][g][0])
                        connected[i][g][1] = {'change': user_state['change'] + general_state['change']}
            finally:
                longpoll_lock.release()


def get_all_comments(session, id, parent_type):
    res = []
    for i in session.query(Comment).filter(and_(Comment.parent_type == parent_type, Comment.parent_id == id)).order_by(Comment.created_date).all():
        if session.query(Comment).filter(and_(Comment.parent_type == 'comment', Comment.parent_id == i.id)).order_by(Comment.created_date).first():
            res.append([i, get_all_comments(session, i.id, "comment")])
        else:
            res.append([i])
    return res


def check_user_state(user_id):  # подгоняет данные пользователя под актуальные данные сервера
    session = db_session.create_session()
    res = []
    if user_id is not None:
        user = session.query(User).get(user_id)
        changes = session.query(LongPollEvent).filter(LongPollEvent.user_id == user.id).order_by(
            LongPollEvent.created_date).all()
        for i in changes:
            res.append({i.event_type: json.loads(i.event_body)})
            if i.delete_when_received:
                session.delete(i)
    session.commit()
    session.close()
    return {'change': res}


def check_general_state(user_id, user_data):  # подгоняет данные пользователя под актуальные данные сервера
    session = db_session.create_session()
    res = []
    if user_id is not None:
        user = session.query(User).get(user_id)
        if user_data['self'] != user.name:
            res.append({'self': user.name})
    if set(user_data['online']) != set(users_online.keys()):
        res.append({'online': list(users_online.keys())})
    best_users = list(sorted([(i.name, i.get_rating()) for i in session.query(User).all()], key=lambda x: -x[1])[:10])
    if set([(i[0], i[1]) for i in user_data['best_users']]) != set(best_users):
        res.append({'best_users': best_users})
    session.close()
    if not len(res):
        return {'change': []}
    return {'change': res}


@app.route('/poll', methods=['POST'])
def poll():  # (лонг)полл
    try:
        user_data = json.loads(request.data)
    except Exception:
        return abort(400)
    key = ''.join([random.choice(ascii_letters) for i in range(32)])
    user_id = current_user.id if current_user.is_authenticated else 'other'
    if current_user.is_authenticated:
        online_lock.acquire()
        try:
            users_online[current_user.name] = datetime.datetime.now()
        finally:
            online_lock.release()

    longpoll_lock.acquire()
    try:
        if user_id not in connected:
            connected[user_id] = {}
        connected[user_id][key] = [user_data, {'change': []}]
    finally:
        longpoll_lock.release()

    for i in range(25):  # больше heroku обрубает
        longpoll_lock.acquire()
        try:
            change = copy.deepcopy(connected[user_id][key][1])
        finally:
            longpoll_lock.release()
        if len(change['change']) > 0:
            longpoll_lock.acquire()
            try:
                del connected[user_id][key]
            finally:
                longpoll_lock.release()
            return json.dumps(change)
        time.sleep(1)

    longpoll_lock.acquire()
    try:
        del connected[user_id][key]
    finally:
        longpoll_lock.release()
    return json.dumps({'change': []})


@app.errorhandler(404)
def handle_404(e):
    return render_template('/status_codes/404.html')


@app.errorhandler(401)
def handle_401(e):
    return render_template('/status_codes/401.html')


@app.errorhandler(403)
def handle_404(e):
    return render_template('/status_codes/403.html')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/register/confirm/<code>')
def confirm(code):
    session = db_session.create_session()
    conf = session.query(Confirmation).filter(Confirmation.code == code).first()
    if not conf:
        return abort(404)
    if conf.type == "verification":
        conf.user.verified = True
        login_user(conf.user)
    elif conf.type == "password_reset":
        new_password = ''.join([random.choice(ascii_letters) for i in range(32)])
        message = MIMEText(
            '<p>Ваш новый пароль:</p>' + new_password + "<p>Вы можете сменить его в настройках профиля.</p>",
            'html')
        if not send_email(message, conf.user.email):
            session.close()
            return abort(500)
        conf.user.set_password(new_password)
    session.delete(conf)
    session.commit()
    return redirect("/")


@app.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect("/")
    if current_user.name in users_online:
        del users_online[current_user.name]
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
    form = AddUserForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('/add/users.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('/add/users.html', title='Регистрация',
                                   form=form,
                                   message="Такая почта уже использовалась")
        if session.query(User).filter(User.name == form.name.data).first():
            return render_template('/add/users.html', title='Регистрация',
                                   form=form,
                                   message="Такое имя уже занято")
        if not check_email(form.email.data):
            return render_template('/add/users.html', title='Регистрация',
                                   form=form,
                                   message="email недействителен")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_api_key()
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        if form.profile_image.data is not None:
            try:
                os.makedirs(os.path.join(app.config['USER_IMAGES_UPLOAD_FOLDER'], str(user.id)))
                filename = 'profile_image.' + form.profile_image.data.filename.rsplit('.', 1)[1].lower()
                form.profile_image.data.save(
                    os.path.join(app.root_path, app.config['USER_IMAGES_UPLOAD_FOLDER'], str(user.id), filename))
                user.profile_image = os.path.join('\\', app.config['USER_IMAGES_UPLOAD_FOLDER'], str(user.id), filename)
                session.commit()
            except Exception:
                shutil.rmtree(os.path.join(app.config['USER_IMAGES_UPLOAD_FOLDER'], str(user.id)))
                session.delete(user)
                session.commit()
                return render_template('/add/users.html', title='Регистрация', form=form, message='Ошибка загрузки изображения!')
        send_verification_message(user)
        return render_template('/add/users.html', title='Регистрация', form=form, message='Успешно! Осталось только подтвердить регистрацию, перейдя по ссылке в письме, которое мы Вам отправим.')
    return render_template('/add/users.html', title='Регистрация', form=form)


@app.route('/news')
def news():
    session = db_session.create_session()
    news = session.query(News).order_by(desc(News.created_date))
    session.close()
    return render_template("news.html", news=news)


@app.route('/news/<int:id>')
def news_single(id):
    session = db_session.create_session()
    news = session.query(News).get(id)
    if not news:
        return abort(404)
    return render_template("news_single.html", item=news, comments=get_all_comments(session, news.id, 'news'))


@app.route('/edit/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    if not load_user(current_user.id).can_control_news:
        return abort(403)
    form = EditNewsForm()
    session = db_session.create_session()
    obj = session.query(News).get(id)
    if not obj:
        return abort(404)
    if form.validate_on_submit():
        if form.submit.data:
            obj.title = form.title.data
            obj.content = form.content.data
            obj.updated_date = datetime.datetime.now()
        else:
            session.delete(obj)
        session.commit()
        session.close()
        return redirect("/news/" + str(id) if form.submit.data else '/news')
    form.title.data = obj.title
    form.content.data = obj.content
    return render_template('/edit/news.html', title='Изменить новость', form=form)


@app.route('/add/news/', methods=['GET', 'POST'])
@login_required
def add_news():
    if not load_user(current_user.id).can_control_news:
        return abort(403)
    form = AddNewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        news = News(title=form.title.data, content=form.content.data, user_id=current_user.id, user=session.query(User).filter(User.id == current_user.id).first())
        session.add(news)
        session.commit()
        return redirect("/news/" + str(news.id))
    return render_template('/add/news.html', title='Добавить новость', form=form)


@app.route('/users/')
@login_required
def users():
    if not load_user(current_user.id).can_control_users:
        abort(403)
    session = db_session.create_session()
    users = session.query(User).order_by(User.email)
    session.close()
    return render_template("users.html", users=users)


@app.route('/edit/users/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_users(id):
    if not load_user(current_user.id).can_control_users:
        abort(403)
    form = EditUserForm()
    if form.validate_on_submit():
        return redirect("/news")
    return render_template('/edit/user.html', title='Изменить пользователя', form=form)


@app.route('/profile/<name>')
def profile(name):
    session = db_session.create_session()
    user = session.query(User).filter(User.name == name).first()
    if not user or not user.verified:
        return abort(404)
    return render_template("profile.html", user=user)


@app.route('/')
@app.route('/index')
def index():
    session = db_session.create_session()
    nws = session.query(News).order_by(desc(News.updated_date)).limit(3)
    mods_new = session.query(Mod).order_by(Mod.created_date.desc()).limit(10)
    mods_popular = sorted(session.query(Mod).all(), key=lambda x: -x.get_popularity())[:10]
    mods_best = session.query(Mod).outerjoin(ModRating).group_by(Mod).order_by(func.sum(ModRating.rating).desc()).limit(10)
    return render_template("index.html", news=nws, mods_new=mods_new, mods_popular=mods_popular, mods_best=mods_best)


@app.route('/mod')
def mods():
    session = db_session.create_session()
    mods = session.query(Mod)
    return render_template("mods.html", mods=mods)


@app.route('/mod/<int:id>')
def mod(id):
    session = db_session.create_session()
    mod = session.query(Mod).get(id)
    if not mod:
        return abort(404)
    rate = None
    if current_user.is_authenticated:
        user = session.query(User).get(current_user.id)
        if not user.viewed.filter(Mod.id == mod.id).first():
            user.viewed.append(mod)
        rate = session.query(ModRating).filter(and_(ModRating.user_id == current_user.id, ModRating.mod_id == mod.id)).first()
    session.commit()
    return render_template("mod_single.html", mod=mod, rate=rate, comments=get_all_comments(session, mod.id, 'mod'))


@app.route('/add/mod', methods=['GET', 'POST'])
@login_required
def add_mod():
    if not current_user.can_make_mods:
        return abort(403)
    form = AddModForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        mod = Mod(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        session.add(mod)
        session.commit()
        try:
            filename = secure_filename(form.file_content.data.filename)
            os.makedirs(os.path.join(app.config['MOD_FILES_UPLOAD_FOLDER'], str(mod.id)))
            os.makedirs(os.path.join(app.config['MOD_IMAGES_UPLOAD_FOLDER'], str(mod.id)))
            form.file_content.data.save(os.path.join(app.root_path, app.config['MOD_FILES_UPLOAD_FOLDER'], str(mod.id), filename))
            mod.file = os.path.join('\\', app.config['MOD_FILES_UPLOAD_FOLDER'], str(mod.id), filename)
            if form.poster.data is not None:
                filename = 'poster.' + form.poster.data.filename.rsplit('.', 1)[1].lower()
                form.poster.data.save(os.path.join(app.root_path, app.config['MOD_IMAGES_UPLOAD_FOLDER'], str(mod.id), filename))
                mod.poster = os.path.join('\\', app.config['MOD_IMAGES_UPLOAD_FOLDER'], str(mod.id), filename)
            for ind, item in enumerate(form.additional_images):
                if item.data is not None:
                    filename = str(ind + 1) + '.' + item.data.filename.rsplit('.', 1)[1].lower()
                    item.data.save(os.path.join(app.root_path, app.config['MOD_IMAGES_UPLOAD_FOLDER'], str(mod.id), filename))
                    mod.images.append(ModImages(content=os.path.join('\\', app.config['MOD_IMAGES_UPLOAD_FOLDER'], str(mod.id), filename)))
        except Exception:
            shutil.rmtree(os.path.join(app.config['MOD_FILES_UPLOAD_FOLDER'], str(mod.id)))
            shutil.rmtree(os.path.join(app.config['MOD_IMAGES_UPLOAD_FOLDER'], str(mod.id)))
            session.delete(mod)
            session.commit()
            return render_template('add/mod.html', form=form, message='Ошибка загрузки!')
        session.commit()
        return redirect('/mod/' + str(mod.id))
    if request.method == 'GET':
        for i in range(10):
            form.additional_images.append_entry()
    return render_template('add/mod.html', form=form)


@app.route('/edit/mod/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_mod(id):
    if not current_user.is_authenticated:
        return abort(403)
    form = AddUserForm()
    if form.validate_on_submit():
        return render_template('/add/users.html', title='Регистрация', form=form, message='Успешно! Осталось только подтвердить регистрацию, перейдя по ссылке в письме, которое мы Вам отправим.')
    return render_template('/add/users.html', title='Регистрация', form=form)


@app.route('/search', methods=['POST'])
def search():
    try:
        query = request.form['search']
    except Exception:
        return abort(400)
    session = db_session.create_session()
    result = session.query(Mod).join(User).filter(or_(or_(Mod.title.like(query), User.name.like(query)), Mod.content.like(query))).all()
    return render_template('search_results.html', results=result)


@app.route('/messages')
@login_required
def messages():
    session = db_session.create_session()
    vars = dict()
    for i in session.query(UserMessage).filter(or_(UserMessage.sender_id == current_user.id, UserMessage.receiver_id == current_user.id)).order_by(UserMessage.created_date):
        vars[i.sender.name if i.sender.name != current_user.name else i.receiver.name] = i.message
    return render_template('messages_all.html', messages=list(vars.items()))


@app.route('/messages/<name>', methods=['GET'])
@login_required
def message(name):
    session = db_session.create_session()
    user = session.query(User).filter(User.name == name).first()
    if not user or not user.verified:
        return abort(404)
    session.query(LongPollEvent).filter(and_(LongPollEvent.user_id == user.id, and_(LongPollEvent.sender == str(user.id), LongPollEvent.event_type == 'message_unread'))).delete()
    messages_list = session.query(UserMessage).filter(or_(and_(UserMessage.sender_id == current_user.id, UserMessage.receiver_id == user.id), and_(UserMessage.sender_id == user.id, UserMessage.receiver_id == current_user.id))).order_by(UserMessage.created_date)
    session.commit()
    return render_template('messages_user.html', messages=messages_list, receiver=user.name)


def main():
    db_session.global_init("db/main.sqlite")
    api.add_resource(news_resource.NewsListResource, '/api/news')
    api.add_resource(news_resource.NewsResource, '/api/news/<int:id>')
    api.add_resource(users_resource.UserListResource, '/api/users')
    api.add_resource(message_resource.MessageResource, '/send_message')
    api.add_resource(vote_resource.VoteResource, '/vote')
    api.add_resource(login_resource.LoginResource, '/login')
    api.add_resource(api_update_resource.ApiKeyUpdate, '/update_api_key')
    api.add_resource(users_resource.UserResource, '/api/users/<int:id>')
    api.add_resource(comment_resource.CommentResource, '/send_comment')
    api.add_resource(confirmation_resource.ConfirmationResource, '/send_confirmation')
    api.add_resource(mod_resource.ModsListResource, '/api/mod')
    api.add_resource(mod_resource.ModResource, '/api/mod/<int:id>')
    session = db_session.create_session()
    bf = session.query(User).filter(User.name == 'admin').first()
    if not bf:
        usr = User(email="admin@this", name='admin', can_control_users=True, can_control_mods=True, can_control_comments=True, can_control_news=True, verified=True, api_key='yes, i am admin')
        usr.set_password('123')
        session.add(usr)
        usr = User(email="test@this", name='test', can_control_users=False, can_control_mods=False,
                   can_control_comments=False, can_control_news=False, verified=True, api_key='yes, i am test')
        usr.set_password('123')
        session.add(usr)
    else:
        pass
    session.commit()
    session.close()

    online_handler = OnlineHandler()
    online_handler.start()

    longpoll_hangler = LongPollHandler()
    longpoll_hangler.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', threaded=True)


if __name__ == '__main__':
    main()
