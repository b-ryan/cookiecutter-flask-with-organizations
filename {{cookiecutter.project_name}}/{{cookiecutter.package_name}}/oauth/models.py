# See http://tinyurl.com/y8tmssmm
from ..database import SurrogatePK, reference_col, StandardMixin
from ..extensions import db
from datetime import datetime, timedelta


class Client(StandardMixin, db.Model):
    __tablename__ = "oauth_clients"
    organization_id = reference_col("organizations", nullable=False)
    organization = db.relationship("Organization")
    name = db.Column(db.Text)
    description = db.Column(db.Text)
    homepage_url = db.Column(db.Text)
    client_id = db.Column(db.Text, primary_key=True)
    client_secret = db.Column(db.Text, unique=True, index=True, nullable=False)
    is_confidential = db.Column(db.Boolean)
    pubkey = db.Column(db.Text)
    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)
    __table_args__ = (
        db.UniqueConstraint("organization_id", "name", name="_org_name_uc"),
    )

    @property
    def client_type(self):
        if self.is_confidential:
            return "confidential"
        return "public"

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    def __repr__(self):
        return "<oauth client '{}'>".format(self.client_id)


class Grant(StandardMixin, SurrogatePK, db.Model):
    __tablename__ = "oauth_grants"

    organization_id = reference_col("organizations", nullable=False)
    organization = db.relationship("Organization")
    client_id = reference_col("oauth_clients", pk_name="client_id", nullable=False)
    client = db.relationship("Client")
    code = db.Column(db.Text, index=True, nullable=False)
    redirect_uri = db.Column(db.Text)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    @property
    def user(self):
        # The "user" property of this class is different than the "user" used
        # elsewhere in this application. It is the "user" that the grant is
        # authorized for. We authorize applications for organizations, not users
        return self.organization

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(StandardMixin, SurrogatePK, db.Model):
    __tablename__ = "oauth_tokens"
    client_id = reference_col("oauth_clients", pk_name="client_id", nullable=False)
    client = db.relationship("Client")
    organization_id = reference_col("organizations", nullable=False)
    organization = db.relationship("Organization")
    access_token = db.Column(db.Text, unique=True)
    refresh_token = db.Column(db.Text, unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)
    token_type = "bearer"  # Only "bearer" supported by Flask-OAuthlib

    @property
    def user(self):
        # The "user" property of this class is different than the "user" used
        # elsewhere in this application. It is the "user" that the grant is
        # authorized for. We authorize applications for organizations, not users
        return self.organization

    def __init__(self, **kwargs):
        expires_in = kwargs.pop("expires_in", None)
        if expires_in:
            if type(expires_in) == int:
                expires_in = timedelta(seconds=expires_in)
            self.expires = datetime.utcnow() + expires_in
        scope = kwargs.pop("scope", "")
        self._scopes = scope
        for k, v in kwargs.items():
            setattr(self, k, v)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []
