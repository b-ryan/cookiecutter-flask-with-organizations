import logging
from datetime import datetime, timedelta
import flask
from flask import request, url_for
import flask_login
from flask_login import login_required, current_user
import itsdangerous
from . import emails, forms
from .. import utils
from ..extensions import db
from ..orgs import utils as org_utils
from ..users.models import User

logger = logging.getLogger(__name__)
blueprint = flask.Blueprint("users", __name__, url_prefix="/users")


@blueprint.route("/settings", methods=["GET", "POST"])
@login_required
@utils.templated()
def settings():
    return dict(pw_form=forms.ChangePasswordForm())


@blueprint.route("/resend-confirmation", methods=["POST"])
@login_required
def resend_confirmation():
    if current_user.confirmed_at:
        flask.abort(400)
    emails.send_email_confirmation(current_user)
    flask.flash("A confirmation email has been sent.", "success")
    return flask.redirect(url_for("users.settings"))


@blueprint.route("/change-password", methods=["GET", "POST"])
@login_required
@utils.templated("users/settings.html")
def change_password():
    form = forms.ChangePasswordForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flask.flash("Your password has been updated.", "success")
            return flask.redirect(url_for("users.settings"))
        else:
            utils.flash_errors(form)
    return dict(pw_form=form)


@blueprint.route("/forgot-password", methods=["GET", "POST"])
@utils.templated()
def forgot_password():
    form = forms.ForgotPasswordForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                emails.send_forgot_password(user)
            flask.flash("An email has been sent (if this user exists)",
                        "success")
        else:
            utils.flash_errors(form)
    return dict(form=form)


@blueprint.route("/confirm", methods=["GET"])
@utils.templated()
def confirm():
    token = request.args.get("token")
    if not token:
        flask.abort(400)
    user_id = utils.unsign_or_flash(token, expire=timedelta(days=2),
                                    desc="confirmation")
    if not user_id:
        return flask.redirect("public.login")
    User.get_by_id(user_id).confirm_now()
    db.session.commit()
    flask.flash("Your email has been confirmed.", "success")
    return utils.grand_redirect()


@blueprint.route("/reset-password", methods=["GET", "POST"])
@utils.templated()
def reset_password():
    token = request.args.get("token")
    if not token:
        flask.abort(401)
    if org_utils.authed_user():
        flask_login.logout_user()
    user_id = utils.unsign_or_flash(token, expire=timedelta(days=2),
                                    desc="reset password")
    if not user_id:
        return flask.redirect("public.login")
    user = User.get_by_id(user_id)
    user.confirm_now()
    db.session.commit()
    form = forms.ResetPasswordForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            user.set_password(form.new_password.data)
            db.session.commit()
            flask.flash("Your password has been reset.", "success")
            flask_login.login_user(user)
            redirect_url = request.args.get("next") or url_for("main.index")
            return flask.redirect(redirect_url)
        else:
            utils.flash_errors(form)
    return dict(form=form)
