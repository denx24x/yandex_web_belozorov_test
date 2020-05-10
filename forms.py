from wtforms import StringField, MultipleFileField, PasswordField, BooleanField, SubmitField, TextAreaField, FieldList
from wtforms.validators import DataRequired, Length
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileRequired, FileAllowed, FileField
from flask_wtf import FlaskForm, RecaptchaField
IMAGES = ('jpg', 'jpe', 'jpeg', 'png', 'gif', 'svg', 'bmp', 'webp')
ARCHIVES = ('gz', 'bz2', 'zip', 'tar', 'tgz', 'txz', '7z', 'rar')


class AddUserForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired(), Length(0, 100)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(0, 100)])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired(), Length(0, 100)])
    name = StringField('Имя пользователя', validators=[DataRequired(), Length(0, 50)])
    profile_image = FileField('Фото', validators=[
        FileAllowed(IMAGES, 'Изображене')
    ])
    recaptcha = RecaptchaField()
    submit = SubmitField('Зарегистрироваться')


class AddNewsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(0, 500)])
    content = TextAreaField('Содержание', validators=[DataRequired(), Length(0, 50000)])
    submit = SubmitField('Добавить')


class AddModForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(0, 100)])
    content = TextAreaField('Содержание', validators=[DataRequired(), Length(0, 50000)])
    file_content = FileField('Модификация ', validators=[
        FileRequired(), FileAllowed(ARCHIVES, 'Архив')
    ])
    poster = FileField('Постер', validators=[
        FileAllowed(IMAGES, 'Изображене')
    ])
    additional_images = FieldList(FileField('', validators=[FileAllowed(IMAGES, 'Изображения')]), max_entries=10)
    submit = SubmitField('Добавить')


class EditNewsForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired(), Length(0, 500)])
    content = TextAreaField('Содержание', validators=[DataRequired(), Length(0, 50000)])
    submit = SubmitField('Сохранить')
    abort = SubmitField('Удалить')


class EditUserForm(FlaskForm):
    name = StringField('Имя пользователя', validators=[DataRequired(), Length(0, 50)])
    email = StringField('Почта пользователя', validators=[DataRequired(), Length(0, 50)])
    can_control_news = BooleanField('Управление новостями', validators=[])
    can_control_mods = BooleanField('Управление модами', validators=[])
    can_control_users = BooleanField('Управление пользователями', validators=[])
    can_control_comments = BooleanField('Управление комментариями', validators=[])
    can_make_mods = BooleanField('Может создавать и редактировать моды', validators=[])
    can_comment = BooleanField('Может комментировать', validators=[])
    verified = BooleanField('Подтвержден', validators=[])
    submit = SubmitField('Обновить')
