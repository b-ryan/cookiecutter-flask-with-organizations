import json
from flask import (
    Blueprint,
    render_template,
    request,
    abort,
    redirect,
    url_for,
    current_app,
)
from flask_login import login_required, current_user
from .models import Client
from .forms import OAuthClientForm, ConfirmationForm
from ..extensions import oauth, csrf_protect, db
from ..orgs.utils import membership_required, assert_membership, current_org
from ..utils import gen_token, flash_errors, validate_json
from .. import permissions as perms

# decorators just need to be imported somewhere, they're
# not directly used in this module
from . import decorators

blueprint = Blueprint("oauth", __name__)


@blueprint.route("/orgs/<int:organization_id>/applications", methods=["GET"])
@login_required
@membership_required(perms.OAUTH_APPLICATIONS)
def clients(organization):
    clients = Client.query.filter_by(organization_id=organization.id).all()
    return render_template("oauth/applications/list.html", clients=clients)


@blueprint.route("/orgs/<int:organization_id>/applications/<string:client_id>",
                 methods=["GET", "POST"])
@login_required
@membership_required(perms.OAUTH_APPLICATIONS)
def client_details(organization, client_id):
    client = Client.query.filter_by(
        client_id=client_id,
        organization_id=organization.id
    ).first()
    form = OAuthClientForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            client.name = form.name.data
            client.description = form.description.data
            client.homepage_url = form.homepage_url.data
            client._redirect_uris = form.redirect_uri.data
            db.session.commit()
            return redirect(url_for("oauth.client_details",
                                    organization_id=organization.id,
                                    client_id=client.client_id))
    else:
        form.name.data = client.name
        form.description.data = client.description
        form.homepage_url.data = client.homepage_url
        form.redirect_uri.data = client._redirect_uris
    if not client:
        abort(404)
    return render_template("oauth/applications/details.html", client=client, form=form)



@blueprint.route("/orgs/<int:organization_id>/applications/new", methods=["GET", "POST"])
@login_required
@membership_required(perms.OAUTH_APPLICATIONS)
def new_client(organization):
    form = OAuthClientForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            client = Client(
                organization_id=organization.id,
                name=form.name.data,
                description=form.description.data,
                homepage_url=form.homepage_url.data,
                client_id=gen_token(nbytes=12),
                client_secret=gen_token(),
                is_confidential=True,
                _redirect_uris=form.redirect_uri.data,
                _default_scopes="a_scope",
            )
            db.session.add(client)
            db.session.commit()
            return redirect(url_for("oauth.client_details",
                                    organization_id=organization.id,
                                    client_id=client.client_id))
        else:
            flash_errors(form)
    return render_template("oauth/applications/new.html", form=form)


@blueprint.route("/oauth/authorize", methods=["GET", "POST"])
@login_required
@oauth.authorize_handler
def authorize(**kwargs):
    if "org" not in request.args:
        user_orgs = [m.organization for m in current_user.memberships
                     if m.role in ["owner", "admin"]]
        if len(user_orgs) > 1:
            return render_template("oauth/select_org.html",
                                   user_organizations=user_orgs)
        return redirect(request.url + "&org=" + str(user_orgs[0].id))
    if request.method == "GET":
        client_id = kwargs.get("client_id")
        client = Client.query.filter_by(client_id=client_id).first()
        kwargs["client"] = client
        return render_template("oauth/authorize.html", **kwargs)
    confirm = request.form.get("confirm", "no")
    return confirm == "yes"


@blueprint.route("/oauth/token", methods=["POST"])
@oauth.token_handler
@csrf_protect.exempt
def access_token():
    return None
