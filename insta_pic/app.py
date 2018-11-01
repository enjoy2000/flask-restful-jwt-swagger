from flask import Flask, jsonify

from insta_pic import auth, api
from insta_pic.extensions import db, jwt, migrate


def create_app(config=None, testing=False, cli=False):
    """Application factory, used to create application
    """
    app = Flask('insta_pic')

    configure_app(app, testing)
    configure_extensions(app, cli)
    register_blueprints(app)

    @app.errorhandler(Exception)
    def error_handler(e):
        return jsonify({'msg': str(e)}), 500

    return app


def configure_app(app, testing=False):
    """set configuration for application
    """
    # default configuration
    app.config.from_object('insta_pic.config')

    if testing is True:
        # override with testing config
        app.config.from_object('insta_pic.configtest')
    else:
        # override with env variable, fail silently if not set
        app.config.from_envvar("INSTA_PIC_CONFIG", silent=True)


def configure_extensions(app, cli):
    """configure flask extensions
    """
    db.init_app(app)
    jwt.init_app(app)

    if cli is True:
        migrate.init_app(app, db)


def register_blueprints(app):
    """register all blueprints for application
    """
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(api.views.blueprint)
