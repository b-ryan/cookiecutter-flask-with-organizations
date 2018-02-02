from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_user
from ..extensions import db
from ..public.forms import LoginForm
from ..users.models import User
from ..users import emails
from ..orgs.forms import RegisterForm
from ..orgs.models import Organization, Membership
from .. import utils

blueprint = Blueprint("public", __name__)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)
    redirect_url = request.args.get("next") or url_for("main.index")
    if request.method == "POST":
        if form.validate_on_submit():
            login_user(form.user)
            flash("You are logged in.", "success")
            return redirect(redirect_url)
        else:
            utils.flash_errors(form)
    else:
        if current_user and current_user.is_authenticated:
            return redirect(redirect_url)
    return render_template("public/login.html", form=form)


@blueprint.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        org = Organization(name=form.organization_name.data)
        user = User(
            email=form.email.data,
            password=form.password.data,
            active=True,
        )
        membership = Membership(
            organization=org,
            user=user,
            role="owner",
            active=True,
        )
        for o in [org, user, membership]:
            db.session.add(o)
        db.session.commit()
        emails.send_email_confirmation(user)
        login_user(user)
        flash("Success! Please check your email for a confirmation email",
              "success")
        redirect_url = request.args.get("next") \
            or url_for("orgs.home", organization_id=org.id)
        return redirect(redirect_url)
    else:
        utils.flash_errors(form)
    return render_template("public/register.html", form=form)
