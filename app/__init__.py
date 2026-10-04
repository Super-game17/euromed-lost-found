from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from app.config import Config


# Shared database instance

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "items.declare_lost"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.home import home_bp
    from app.routes.items import items_bp
    from app.routes.matching import matching_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(matching_bp)

    with app.app_context():
        db.create_all()

    return app
