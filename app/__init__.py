#C'est le fichier très important.
#Il va créer notre application Flask.

from flask import Flask
from app.routes import create_app
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes.auth import auth_bp

    app.register_blueprint(auth_bp)

    return app