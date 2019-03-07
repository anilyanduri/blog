# third-party imports
from flask import Flask, Blueprint, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap

# local imports
from config import app_config

# db variable initialization
db = SQLAlchemy()


def page_not_found(e):
  return render_template('404.html'), 404


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.register_error_handler(404, page_not_found)
    from blog import models
    db.init_app(app)
    migrate = Migrate(app, db)

    Bootstrap(app)

    from .posts import posts as posts_blueprint
    app.register_blueprint(posts_blueprint)

    return app