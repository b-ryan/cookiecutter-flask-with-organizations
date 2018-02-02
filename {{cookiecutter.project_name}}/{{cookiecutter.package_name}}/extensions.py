from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_oauthlib.provider import OAuth2Provider
from flask_jsonschema import JsonSchema
from flask_gravatar import Gravatar
from flask_mail import Mail
from flask_babel import Babel
from flask_jsglue import JSGlue

bcrypt = Bcrypt()
csrf_protect = CSRFProtect()
login_manager = LoginManager()
db = SQLAlchemy()
migrate = Migrate()
cache = Cache()
oauth = OAuth2Provider()
json_schema = JsonSchema()
gravatar = Gravatar(size=300, rating='g', default='retro', use_ssl=True)
mail = Mail()
babel = Babel()
jsglue = JSGlue()

try:
    from flask_debugtoolbar import DebugToolbarExtension
    debug_toolbar = DebugToolbarExtension()
except ImportError:
    debug_toolbar = None
