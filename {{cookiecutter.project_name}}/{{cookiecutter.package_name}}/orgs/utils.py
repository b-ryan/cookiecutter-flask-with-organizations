import flask
from flask import request, abort
from flask_login import current_user
from functools import wraps
from werkzeug.local import LocalProxy
import logging
from flask_mail import Message
from .models import Organization
from ..extensions import db, mail
from ..utils import gen_token, from_now


logger = logging.getLogger(__name__)


def _get_org():
    """Extracts an organization ID out of the route and looks the
    organization up in the DB.

    .. note: For this to work the `view` must be set up so there is
    `<int:organization_id>` somewhere in the route.

    .. note: This does NOT ensure the user has the correct rights to the
    organization. That must be verified in some other way, typically with :func
    membership_required:.
    """
    org = getattr(flask.g, "organization", None)
    if org:
        return org
    if not request.view_args:
        return None
    org_id = request.view_args.get("organization_id")
    if not org_id:
        return None
    org = Organization.get_by_id(org_id)
    flask.g.organization = org
    return org


def _get_membership():
    """Finds a Membership where the organization is `current_org` and the user
    is `flask_login.current_user`.

    .. note: This returns a Membership even if it is inactive.

    .. note: Unlike `current_org`, this can be used as a way to do basic
    authorization of a request. If the user does not belong to the organization
    in the route, this function will return None."""
    mem = getattr(flask.g, "membership", None)
    if mem:
        return mem
    if not current_user:
        return None
    if not current_org:
        return None
    mem = current_user.matching_membership(current_org.id)
    flask.g.membership = mem
    return mem

current_org = LocalProxy(_get_org)
current_membership = LocalProxy(_get_membership)


def assert_membership(accepted_roles, organization_id, *, active_only=True):
    """Checks whether the current_user has the accepted roles for the given
    organization_id, aborting the request otherwise.

    :param accepted_roles: List of roles the current_user must have.
    :param organization_id: The organization the current_user must belong to
    :param active_only: Whether or not the Membership.active flag is checked
    :returns: The authorized Membership

    If the authorization fails, the request will be aborted with a 403 status.
    """
    if not current_membership:
        abort(403)
    if active_only and not current_membership.active:
        abort(403)
    if current_membership.role not in accepted_roles:
        abort(403)


def membership_required(accepted_roles, active_only=True):
    """A decorator that confirms the current user has access to the
    organization they are trying to access. Confirms the user's role for the
    organization is one of accepted_roles.

    This decorator assumes the @login_required decorator has already been used
    on the route to confirm there is an authenticated user.

    If active_only is False, then if the Membership found is not
    active, it will still be allowed. This is probably only useful in one
    situation: when an invite activation code is being redeemed."""
    def wrap(f):
        @wraps(f)
        def wrapped_f(*args, organization_id, **kwargs):
            assert_membership(accepted_roles, organization_id,
                              active_only=active_only)
            # FIXME now that current_org exists, this should probably not
            # change the *args and **kwargs
            return f(*args, organization=current_org, **kwargs)
        return wrapped_f
    return wrap


def authed_user():
    return current_user and current_user.is_authenticated


def authed_membership():
    return authed_user() and current_membership and current_membership.active


def injections():
    """A flask context processor that fetches the organization out of the URL
    and makes an "organization" object available to all templates.

    NOTE: This injects the organization into the template whether or not the
    user is authenticated or belongs to the organization. It's on you to make
    sure to protect things properly with the membership_required decorator."""
    return {
        "authed_user": authed_user,
        "authed_membership": authed_membership,
        "current_org": current_org,
        "current_membership": current_membership,
        # FIXME use current_org
        "organization": current_org,
    }
