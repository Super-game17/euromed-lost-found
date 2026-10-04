from flask import Blueprint, render_template

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    return render_template("home/index.html")


# Actuellement / est dans auth.py uniquement parce qu'on l'a utilisé pour tester Flask.
# Quand on commencera l'authentification, on fera :
# routes/
# │
# ├── home.py       ← accueil
# ├── auth.py       ← login/register/logout
# ├── items.py      ← lost/found
# └── matching.py   ← matching/restitution