from flask import render_template
from ..extensions import mail
from .. import utils
from flask_mail import Message


def send_invite(membership):
    mail.send(Message(
        subject=("You have been invited to join {}"
                 .format(membership.organization.name)),
        html=render_template(
            "organizations/emails/invite.html",
            code=membership.invite_code,
        ),
        recipients=[membership.user.email],
    ))


def send_deactivation(membership):
    mail.send(Message(
        subject=("You have been removed from the {} organization"
                 .format(membership.organization.name)),
        html=render_template(
            "organizations/emails/deactivation.html",
            membership=membership,
        ),
        recipients=[membership.user.email],
    ))
