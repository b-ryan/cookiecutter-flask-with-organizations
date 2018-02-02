import os


class Config(object):
    APP_NAME = "{{cookiecutter.flask_app_name}}"
    SUPPORT_EMAIL = "support@{{cookiecutter.production_domain}}"
    COPYRIGHT = "{{cookiecutter.copyright_text}}"
    APP_DIR = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    BCRYPT_LOG_ROUNDS = 13
    DEBUG_TB_ENABLED = False  # Disable debug toolbar
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSONSCHEMA_DIR = os.path.join(APP_DIR, "schemas")
    MAIL_USERNAME = "___"
    MAIL_DEFAULT_SENDER = "Support <support@{{cookiecutter.production_domain}}>"
    MAIL_SERVER = "smtp.mandrillapp.com"
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    BABEL_DEFAULT_LOCALE = "en"


class ProdConfig(Config):
    ENV = "prod"
    DEBUG = False
    SERVER_NAME = "{{cookiecutter.production_domain}}"


class DevConfig(Config):
    SECRET_KEY = "secret-key"
    ENV = "dev"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://myuser:password@localhost/myapp"
    DEBUG_TB_ENABLED = True
    CACHE_TYPE = "simple"  # Can be "memcached", "redis", etc.
    SERVER_NAME = "localhost:5000"


class TestConfig(Config):
    SECRET_KEY = "secret-key"
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://myuser:password@localhost/myapp_test"
    # BCRYPT_LOG_ROUNDS is here for faster tests; it needs at least 4 to avoid
    # "ValueError: Invalid rounds"
    BCRYPT_LOG_ROUNDS = 4
    WTF_CSRF_ENABLED = False
