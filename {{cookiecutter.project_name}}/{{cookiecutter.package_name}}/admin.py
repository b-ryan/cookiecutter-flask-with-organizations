from flask import (redirect, request, url_for, abort)
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib import sqla
from flask_login import current_user
from .extensions import db
from .orgs.utils import authed_user
from .orgs.models import Organization, Membership
from .users.models import User


class _AdminAuthMixin(object):
    """Provides common functionality for securing the admin panel. Note that
    this mixin should be the first class for the inheriting class. Ie.

    class Foo(_AdminAuthMixin, Other)

    In order for it to properly override the desired functions."""
    def is_accessible(self):
        return authed_user() and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        if authed_user():
            abort(403)
        return redirect(url_for("public.login", next=request.url))


class FilteredModelView(_AdminAuthMixin, sqla.ModelView):
    column_exclude_list = ["created_at", "updated_at"]
    form_excluded_columns = ["created_at", "updated_at"]


class AuthedIndexView(_AdminAuthMixin, AdminIndexView):
    pass


class UserModelView(FilteredModelView):
    column_exclude_list = ["created_at", "updated_at", "password"]
    form_excluded_columns = ["created_at", "updated_at", "password"]


class GrantModelView(FilteredModelView):
    column_exclude_list = ["created_at", "updated_at", "password_encrypted",
                           "version", "sql_statement", "use_templates"]
    form_excluded_columns = ["created_at", "updated_at", "password_encrypted",
                             "version"]

admin = Admin(template_mode="bootstrap3",
              index_view=AuthedIndexView())
views = [
    FilteredModelView(Membership, db.session, endpoint="admin_memberships"),
]
for v in views:
    admin.add_view(v)
