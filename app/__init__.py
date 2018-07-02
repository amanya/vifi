from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_jwt_extended import JWTManager

import jinja2

db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, static_folder='../static/dist/static')

    CORS(app)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    template_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader('./static/dist'),
        ])
    app.jinja_loader = template_loader

    jwt = JWTManager(app)

    db.init_app(app)

    if app.config['SSL_REDIRECT']:
        from flask_sslify import SSLify
        sslify = SSLify(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/v1')

    return app
