from flask import Flask
from config import Config
from app.routes.home import home_bp
from app.routes.items import items_bp
from app.routes.matching import matching_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp)

    return app

__all__ = ["home_bp", "items_bp", "matching_bp"]
