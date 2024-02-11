# app/__init__.py

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from .config import Config

csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CSRF protection
    csrf.init_app(app)

    # Import and register blueprints
    from .auth.oauth import slack_auth_bp
    app.register_blueprint(slack_auth_bp)

    return app
