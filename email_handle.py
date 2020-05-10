from data import db_session
from data.confirmations import Confirmation
from sqlalchemy import desc, func, case, and_, or_
import datetime
import smtplib
from email.mime.text import MIMEText

self_url = "yandex-web-belozorov.herokuapp.com"


def send_email(message, email):
    try:
        server = smtplib.SMTP_SSL('smtp.mail.ru')  # лучший вариант - просто берет и шлет что надо и куда надо
        server.login("ylwebproject@mail.ru", "1234YLWP")
        server.sendmail("ylwebproject@mail.ru", email, message.as_string())
        server.quit()
        return True
    except Exception:
        return False


def send_verification_message(user):
    session = db_session.create_session()
    new_conf = Confirmation(user_id=user.id, type="verification")
    new_conf.generate_code()
    link = self_url + '/register/confirm/' + new_conf.code
    message = MIMEText("<p>Вы были зарегистрированы на " + self_url + '! Осталось только подтвердить регистрацию, перейдя по ссылке:</p><a href="' + link + '">' + link + "</a><p>Если вы не регистрировались, проигнорируйте это письмо.</p>", 'html')
    message['From'] = 'ylwebproject@mail.ru'
    message['To'] = user.email
    message['Subject'] = 'Подтверждение аккаунта'
    if not send_email(message, user.email):
        session.close()
        return False
    conf = session.query(Confirmation).filter(Confirmation.user_id == user.id and Confirmation.type == "verification").first()
    if conf is not None:
        conf.code = new_conf.code
        conf.created_date = datetime.datetime.now()
    else:
        session.add(new_conf)
    session.commit()
    return True


def send_password_reset_message(user):
    session = db_session.create_session()
    new_conf = Confirmation(user_id=user.id, type="password_reset")
    new_conf.generate_code()
    link = self_url + '/register/confirm/' + new_conf.code
    message = MIMEText('<p>Для восстановления пароля перейдите по ссылке:</p><a href="' + link + '">' + link + "</a><p>Если вы не запрашивали восставовление пароля, проигнорируйте это письмо.</p>", 'html')
    message['From'] = 'ylwebproject@mail.ru'
    message['To'] = user.email
    message['Subject'] = 'Восстановление пароля'
    if not send_email(message, user.email):
        session.close()
        return False
    conf = session.query(Confirmation).filter(and_(Confirmation.user_id == user.id, Confirmation.type == "password_reset")).first()
    if conf is not None:
        conf.code = new_conf.code
        conf.created_date = datetime.datetime.now()
    else:
        session.add(new_conf)
    session.commit()
    return True


def check_email(email):  # проверка что email существует
    try:
        server = smtplib.SMTP_SSL('smtp.mail.ru')
        return server.verify(email)
    except Exception:
        return False
