"""Implements decorator functions required by
Flask-OAuthlib.

See http://tinyurl.com/y9e4ev9e"""
from datetime import datetime, timedelta
from flask import request
from flask_login import current_user
from .models import Client, Grant, Token
from ..extensions import db, oauth

GRANT_EXPIRATION = timedelta(minutes=2)


@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


@oauth.grantsetter
def save_grant(client_id, code, oauth_request, *args, **kwargs):
    expires = datetime.utcnow() + GRANT_EXPIRATION
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=oauth_request.redirect_uri,
        _scopes=' '.join(oauth_request.scopes),
        organization_id=int(request.args["org"]),
        expires=expires,
    )
    db.session.add(grant)
    db.session.commit()


@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()


@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    # make sure that every client has only one token connected to an
    # organization
    # TODO this could be done in one query
    grantor_org_id = request.user.id
    toks = Token.query.filter_by(client_id=request.client.client_id,
                                 organization_id=grantor_org_id)
    for t in toks:
        db.session.delete(t)
    tok = Token(**token)
    tok.organization_id = grantor_org_id
    tok.client_id = request.client.client_id
    db.session.add(tok)
    db.session.commit()
