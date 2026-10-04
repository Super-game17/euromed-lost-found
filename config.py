import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
    # Plus tard, sur Render, nous mettrons une vraie clé dans les variables d'environnement.