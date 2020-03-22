from flask import Flask, render_template, redirect, Blueprint, jsonify, abort
from flask_wtf import FlaskForm
from data import db_session
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from flask_login import LoginManager, login_required, logout_user, current_user, login_user
from data.users import User
from data.news import News
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


class NewsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = StringField('Содержание', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    if current_user.is_authenticated:
        return redirect('/')
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/news')
def news():
    session = db_session.create_session()
    news = session.query(News)
    session.close()
    return render_template("news.html", news=sorted(news, key=lambda x: x.created_date, reverse=True)[:3])


@app.route('/edit/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    session = db_session.create_session()
    news = session.query(News).filter(News.id == id).first()
    session.close()
    if not news:
        abort(404)
    return add_news(news)


@app.route('/add/news/', methods=['GET', 'POST'])
@login_required
def add_news(pattern=None):
    form = NewsForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if pattern is not None:
            session.delete(session.query(News).filter(News.id == pattern.id).first())
            session.commit()
            session.add(News(title=form.title.data, content=form.content.data, user_id=pattern.id, created_date=pattern.created_date))
        else:
            session.add(News(title=form.title.data, content=form.content.data, user_id=current_user.id))
        session.commit()
        session.close()
        return redirect("/")
    if pattern is not None:
        form.title.data = pattern.title
        form.content.data = pattern.content
    return render_template('add_news.html', title='Добавить новость', form=form)


@app.route('/')
@app.route('/index')
def index():
    session = db_session.create_session()
    news = session.query(News)
    session.close()
    for i in news:
        if len(i.content) > 100:
            i.content = i.content[:97] + '...'
    return render_template("index.html", news=sorted(news, key=lambda x: x.created_date, reverse=True)[:3])


def main():
    db_session.global_init("db/blogs.sqlite")
    app.run()


if __name__ == '__main__':
    main()
