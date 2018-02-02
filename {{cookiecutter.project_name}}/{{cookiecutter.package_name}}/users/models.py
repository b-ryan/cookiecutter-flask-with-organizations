from datetime import datetime
from flask_login import UserMixin
from ..database import (
    SurrogatePK,
    reference_col,
    StandardMixin,
)
from ..extensions import bcrypt, db
from .. import permissions as perms


class User(UserMixin, SurrogatePK, StandardMixin, db.Model):
    __tablename__ = "users"
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.Binary(128), nullable=True)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    active = db.Column(db.Boolean(), nullable=False, default=False)
    is_admin = db.Column(db.Boolean(), default=False)
    confirmed_at = db.Column(db.DateTime)

    def __init__(self, email, password=None, **kwargs):
        db.Model.__init__(self, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    def __str__(self):
        return self.email

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        return "<User({email!r})>".format(email=self.email)

    def matching_membership(self, organization_id):
        """Finds any Membership for the current user and the given
        organization_id or None if there isn't one.

        Note that this includes inactive roles, use active_membership to limit
        to active roles only."""
        filtered = [r for r in self.memberships
                    if r.organization_id == organization_id]
        return filtered[0] if filtered else None

    def active_membership(self, organization_id):
        """Finds an *active* Membership for the current user and the
        given organization_id or None if there isn't one."""
        role = self.matching_membership(organization_id)
        return role if role and role.active else None

    def confirm_now(self):
        if not self.confirmed_at:
            self.confirmed_at = datetime.utcnow()
