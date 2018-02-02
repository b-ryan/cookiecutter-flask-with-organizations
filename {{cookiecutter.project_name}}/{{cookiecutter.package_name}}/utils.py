import os
from datetime import datetime, timedelta
from functools import wraps
import logging
import binascii
import json as json_
import flask
from flask import current_app, request, render_template
from jsonschema import validate as __validate
import itsdangerous

logger = logging.getLogger(__name__)


def flash_errors(form, category="warning"):
    for field, errors in form.errors.items():
        for error in errors:
            label = getattr(form, field).label.text
            full_msg = "{0} - {1}".format(label, error)
            flask.flash(full_msg, category)


def gen_token(nbytes=24):
    return binascii.hexlify(os.urandom(nbytes)).decode("utf-8")


def get_schema(*path):
    jsonschema = current_app.extensions["jsonschema"]
    return jsonschema.get_schema(path)


def validate_json(json, *schema_path):
    __validate(json, get_schema(*schema_path))


def validate_request_json(*schema_path):
    validate_json(request.json, *schema_path)


def now():
    return datetime.utcnow()


def from_now(*args, **kwargs):
    """Constructs a datetemie.timedelta from *args and **kwargs and returns a
    datetime that is utcnow + timedelta"""
    return now() + timedelta(*args, **kwargs)


def expired(deadline):
    return datetime.utcnow() > deadline


def jsonify_with_status(*args, _status_code, **kwargs):
    response = flask.jsonify(*args, **kwargs)
    response.status_code = _status_code
    return response


def json_response(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        return flask.jsonify(f(*args, **kwargs))
    return wrapped


def grand_redirect(org_id=None):
    return flask.redirect(
        request.args.get("next") or
        request.referrer or
        (org_id and flask.url_for("orgs.home", organization_id=org_id)) or
        flask.url_for("main.index")
    )


def templated(template=None):
    # http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = request.endpoint \
                    .replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return render_template(template_name, **ctx)
        return decorated_function
    return decorator


def signer():
    secret = current_app.config["SECRET_KEY"]
    return itsdangerous.TimestampSigner(secret)


def sign_str(str_):
    return signer().sign(str(str_)).decode()


def unsign(str_, *, expire):
    max_age = int(expire.total_seconds())
    return signer().unsign(str_, max_age=max_age)


def unsign_or_flash(token, *, expire, desc):
    try:
        return int(unsign(token, expire=expire))
    except itsdangerous.SignatureExpired:
        flask.flash("Your {} token has expired.".format(desc), "error")
    except itsdangerous.BadSignature:
        flask.flash("Your {} token is invalid.".format(desc), "error")
    return None


class ValidationError(Exception):
    """A generic exception class for validation issues."""
    code = 400
    def __init__(self, errors):
        super().__init__()
        self.errors = errors


def request_wants_json():
    # http://flask.pocoo.org/snippets/45/
    best = request.accept_mimetypes \
        .best_match(["application/json", "text/html"])
    return best == "application/json" and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes["text/html"]


def if_duplicate__validation_error(exception, err_msg):
    """Given a sqlalchemy.exc.IntegrityError, if the error is for a duplicate
    key, raise a ValidationError with the given :param err_msg:. Otherwise
    re-raise the exception."""
    if "duplicate key" in exception.orig.pgerror:
        raise ValidationError([err_msg])
    raise exception
