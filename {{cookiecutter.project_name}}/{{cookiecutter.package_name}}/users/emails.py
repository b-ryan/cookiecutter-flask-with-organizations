from flask import render_template, current_app
from flask_mail import Message
from ..extensions import mail
from .. import utils


def send_email_confirmation(user):
    mail.send(Message(
        subject="Confirm your email address",
        html=render_template(
            "users/emails/confirm.html",
            token=utils.sign_str(user.id),
        ),
        recipients=[user.email],
    ))


def send_forgot_password(user):
    app_name = current_app.config["APP_NAME"]
    mail.send(Message(
        subject="Reset your {} password".format(app_name),
        recipients=[user.email],
        html=render_template(
            "users/emails/forgot.html",
            token=utils.sign_str(user.id),
        )
    ))
