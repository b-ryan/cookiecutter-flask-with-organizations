from flask.helpers import get_debug_flag
from {{cookiecutter.package_name}}.app import create_app
from {{cookiecutter.package_name}}.settings import DevConfig, ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig
app = create_app(CONFIG)
