import logging
import flask
from flask import (
    abort,
    redirect,
    render_template,
    request,
    url_for,
)
import flask_login
from flask_login import login_required
from . import emails
from .models import Organization, Membership
from . import forms
from .utils import membership_required
from . import utils as org_utils
from .. import utils
from ..extensions import db
from ..users.models import User
from .. import permissions as perms

blueprint = flask.Blueprint("orgs", __name__,
                            url_prefix="/orgs/<int:organization_id>")
logger = logging.getLogger(__name__)


@blueprint.route("", methods=["GET"])
@login_required
@membership_required(perms.EVERYBODY)
def home(organization):
    return render_template("index.html")


def _mem_status_for_sorting(mem):
    if not mem.active:
        return 2
    if mem.is_pending_redemption():
        return 1
    return 0


@blueprint.route("/members", methods=["GET"])
@login_required
@membership_required(perms.VIEW_USERS)
def members(organization):
    sorted_mems = organization.memberships.copy()
    sorted_mems.sort(key=lambda m: m.user.email)
    sorted_mems.sort(key=lambda m: m.role)
    sorted_mems.sort(key=_mem_status_for_sorting)
    return render_template("organizations/members.html",
                           memberships=sorted_mems)


def _create_invite(organization, form):
    user = form.user or User(email=form.email.data)
    # The user may have already been invited, in which case they'll
    # have a membership. For those cases, regenerate the invite code.
    membership = user.matching_membership(organization.id) \
        or Membership(organization=organization, user=user)
    membership.role = "admin" if form.is_admin.data else "standard"
    membership.invite_code = utils.gen_token()
    membership.invite_expires = utils.from_now(weeks=1)
    db.session.add(user)
    db.session.add(membership)
    db.session.commit()
    return membership


@blueprint.route("/members/invite", methods=["GET", "POST"])
@login_required
@membership_required(perms.INVITE_USERS)
def invite(organization):
    form = forms.InviteForm(request.form, organization=organization)
    if request.method == "POST":
        if form.validate_on_submit():
            mem = _create_invite(organization, form)
            emails.send_invite(mem)
            flask.flash("An invite has been sent to {}".format(form.email.data),
                        "success")
            return redirect(url_for("orgs.members", organization_id=organization.id))
        else:
            utils.flash_errors(form)
    return render_template("organizations/invite.html", form=form)


@blueprint.route("/members/redeem", methods=["GET", "POST"])
def redeem(organization_id):
    code = request.args.get("code")
    if not code:
        abort(400)
    membership = Membership.query.filter_by(
        organization_id=organization_id, invite_code=code).first()
    if not membership:
        abort(404)
    if org_utils.authed_user():
        flask_login.logout_user()
    org = membership.organization
    form_cls = forms.RedeemForm if membership.user.active \
        else forms.RedeemWithRegistrationForm
    form = form_cls(request.form)
    if request.method == "POST":
        if form.confirm.data == "no":
            membership.update(invite_code=None, invite_expires=None)
            return redirect(url_for("public.login"))
        if form.validate_on_submit():
            membership.update(invite_code=None, invite_expires=None,
                              active=True, commit=False)
            membership.user.confirm_now()
            if form.password:
                membership.user.active = True
                membership.user.set_password(form.password.data)
            db.session.commit()
            flask.flash("Success! You are now a member of {}".format(org.name),
                        "success")
            return redirect(url_for("orgs.home", organization_id=org.id))
        else:
            utils.flash_errors(form)
    return render_template("organizations/redeem.html", form=form)


@blueprint.route("/members/deactivate", methods=["POST"])
@login_required
@membership_required(perms.DELETE_USERS)
def deactivate(organization):
    form = forms.DeactivateForm(request.form)
    if not form.validate_on_submit():
        raise utils.ValidationError(form.errors)
    mem = Membership.get_by_id(form.membership_id.data)
    if not mem or mem.organization_id != organization.id:
        abort(404)
    emails.send_deactivation(mem)
    mem.active = False
    db.session.commit()
    flask.flash("Successfully deactivated {}. Please give the agent some time"
                "to remove this user from your databases."
                .format(mem.user.email),
                "success")
    return redirect(url_for("orgs.members", organization_id=organization.id))
