import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from .config import Config


# Extensions
db = SQLAlchemy()
login_manager = LoginManager()

login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


def _ensure_db_schema(app):
    with app.app_context():
        from sqlalchemy import inspect, text

        inspector = inspect(db.engine)
        if "items" not in inspector.get_table_names():
            db.create_all()
            return

        existing_columns = {column["name"] for column in inspector.get_columns("items")}
        migrations = {
            "location_detail": "ALTER TABLE items ADD COLUMN location_detail VARCHAR(255)",
            "finder_phone": "ALTER TABLE items ADD COLUMN finder_phone VARCHAR(30)",
            "finder_note": "ALTER TABLE items ADD COLUMN finder_note TEXT",
        }

        for column_name, statement in migrations.items():
            if column_name not in existing_columns:
                db.session.execute(text(statement))

        db.session.commit()


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)

    # Configuration
    app.config.from_object(config_class)

    # Make sure instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)

    # Put SQLite database inside instance/
    if app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///euromed_lost_found.db":
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            "sqlite:///"
            + os.path.join(app.instance_path, "euromed_lost_found.db")
        )

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import models so SQLAlchemy knows them
    from . import models

    # Register routes
    from .routes.home import home_bp
    from .routes.auth import auth_bp
    from .routes.items import items_bp
    from .routes.matching import matching_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(matching_bp)

    # Create database tables and upgrade missing columns for the existing database
    with app.app_context():
        db.create_all()
        _ensure_db_schema(app)

    return app


@login_manager.user_loader
def load_user(user_id):
    from .models import User

    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None