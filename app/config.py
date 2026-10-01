import os

class Config:
    # Clé secrète indispensable pour sécuriser les sessions et les messages flash
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cle- secrete-euromed-lost-found-2026'
    
    # Configuration de la base de données (SQLite en local par défaut, PostgreSQL sur Render si configuré)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///euromed_lost_found.db'
    
    # Désactivation du suivi des modifications pour économiser de la mémoire
    SQLALCHEMY_TRACK_MODIFICATIONS = False
