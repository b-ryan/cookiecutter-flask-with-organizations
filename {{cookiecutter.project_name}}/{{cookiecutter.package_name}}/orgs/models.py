from datetime import datetime
from ..database import (
    SurrogatePK,
    reference_col,
    StandardMixin,
)
from ..extensions import bcrypt, db
from .. import permissions as perms


class Organization(SurrogatePK, StandardMixin, db.Model):
    __tablename__ = "organizations"
    name = db.Column(db.Text, nullable=False, unique=True)

    def __str__(self):
        return self.name


class Membership(SurrogatePK, StandardMixin, db.Model):
    __tablename__ = "memberships"
    organization_id = reference_col("organizations", nullable=False)
    organization = db.relationship("Organization", backref="memberships")
    user_id = reference_col("users", nullable=False)
    user = db.relationship("User", backref="memberships")
    role = db.Column(db.Text)
    active = db.Column(db.Boolean(), default=False)
    invite_code = db.Column(db.Text)
    invite_expires = db.Column(db.DateTime)
    __table_args__ = (
        db.UniqueConstraint("organization_id", "user_id", name="_org_user_uc"),
    )
    # TODO add check constraint that makes sure invite_expires and invite_code
    # are both null or non-null?

    def __str__(self):
        return "({}, {})".format(self.organization.name, self.user.email)

    def is_pending_redemption(self):
        return self.invite_code and self.invite_expires > datetime.utcnow()

    @classmethod
    def filter_by_org(cls, organization):
        org_id = organization if type(organization) == int else organization.id
        return cls.query.filter_by(organization_id=org_id)

    def can(self, permname):
        return self.role in getattr(perms, permname)
