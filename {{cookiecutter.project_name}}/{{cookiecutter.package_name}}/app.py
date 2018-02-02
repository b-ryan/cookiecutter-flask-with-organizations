import logging
import json
import os
from flask import Flask, render_template, request, current_app
import flask_jsonschema
from flask_babel import format_datetime
import jinja2
from . import (
    commands,
    main_views,
    users,
    orgs,
    public,
    oauth,
)
from . import extensions as ex
from .extensions import db
from .settings import ProdConfig
from . import filters, utils
from .admin import admin

logging.basicConfig()
logging.getLogger("").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

jinja2.filters.FILTERS["sortby"] = filters.sortby
jinja2.filters.FILTERS["pretty_date"] = filters.pretty_date
jinja2.filters.FILTERS["datetime"] = format_datetime


def create_app(config_object=ProdConfig):
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    json_file = os.getenv("FLASK_APP_JSON_CONFIG")
    if json_file:
        app.config.from_json(json_file)
    app.logger.setLevel(logging.DEBUG)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_context_processors(app)
    register_shellcontext(app)
    register_commands(app)
    register_jinja_filters(app)
    return app


def register_extensions(app):
    ex.bcrypt.init_app(app)
    ex.cache.init_app(app)
    ex.db.init_app(app)
    ex.csrf_protect.init_app(app)
    ex.login_manager.init_app(app)
    ex.migrate.init_app(app, db)
    ex.oauth.init_app(app)
    ex.json_schema.init_app(app)
    ex.gravatar.init_app(app)
    ex.mail.init_app(app)
    ex.babel.init_app(app)
    ex.jsglue.init_app(app)
    if ex.debug_toolbar:
        ex.debug_toolbar.init_app(app)
    admin.init_app(app)


def register_blueprints(app):
    app.register_blueprint(main_views.blueprint)
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(users.views.blueprint)
    app.register_blueprint(orgs.views.blueprint)
    app.register_blueprint(oauth.views.blueprint)


def _render_error(error):
    error_code = getattr(error, "code", 500)
    if error_code == 500:
        logger.error(error)
    if utils.request_wants_json():
        errs = getattr(error, "errors", [])
        # The description key is used by the werkzeug exceptions
        desc = getattr(error, "description", None)
        if desc:
            errs.append(desc)
        response = {"errors": errs if errs else ["unknown"]}
        return utils.jsonify_with_status(response, _status_code=error_code)
    return render_template("{0}.html".format(error_code),
                           error=error), error_code


def _jsonschema_error(error):
    logger.info(error)
    error.code = 400
    error.description = "{}: {}".format(list(error.path), error.message)
    return _render_error(error)


def register_errorhandlers(app):
    for errcode in [400, 401, 404, 403, 500]:
        app.errorhandler(errcode)(_render_error)
    app.errorhandler(flask_jsonschema.ValidationError)(_jsonschema_error)
    app.errorhandler(utils.ValidationError)(_render_error)


def register_context_processors(app):
    app.context_processor(orgs.injections)


def register_shellcontext(app):
    def shell_context():
        return {
            "db": db,
            "User": orgs.models.User,
        }

    app.shell_context_processor(shell_context)


def register_commands(app):
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)
    app.cli.add_command(commands.test_email)


def register_jinja_filters(app):
    def attrs(value, path):
        for p in path:
            value = getattr(value, p)
        return value
    app.jinja_env.filters["attrs"] = attrs
