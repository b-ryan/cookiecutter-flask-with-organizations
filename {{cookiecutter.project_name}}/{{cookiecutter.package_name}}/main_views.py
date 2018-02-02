from flask import (
    Blueprint,
    flash,
    redirect,
    request,
    url_for,
)
from flask_login import current_user, login_required, logout_user
from .extensions import login_manager
from .users.models import User

blueprint = Blueprint("main", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for("public.login", next=request.url))


@blueprint.route("/", methods=["GET"])
@login_required
def index():
    # TODO Store whatever organization the user used last
    org_id = current_user.memberships[0].organization_id
    return redirect(url_for("orgs.home", organization_id=org_id))


@blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You are logged out.", "info")
    return redirect(url_for("public.login"))
