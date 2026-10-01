from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialisation des extensions avec l'application
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configuration de la page de redirection si un utilisateur non connecté essaie d'accéder à une page protégée
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."
    login_manager.login_message_category = "info"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Importation et enregistrement des routes (Blueprint)
    from app.routes.main_routes import main_bp
    app.register_blueprint(main_bp)

    return app
