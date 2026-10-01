from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for

from app import db
from app.models import Item


items_bp = Blueprint("items", __name__, url_prefix="/items")


def declarer(item_type, titre_page):
    if request.method == "POST":
        item = Item(
            item_type=item_type,
            title=request.form["title"],
            description=request.form["description"],
            category=request.form["category"],
            location=request.form["location"],
            date_event=datetime.strptime(
                request.form["date_event"],
                "%Y-%m-%d"
            ).date(),
            user_id=1,  # Temporaire, en attendant l'authentification
        )

        db.session.add(item)
        db.session.commit()

        # Redirection selon le type d'objet déclaré
        if item_type == "lost":
            return redirect(url_for("items.declare_lost"))
        else:
            return redirect(url_for("items.declare_found"))

    return render_template(
        "items/declare.html",
        titre_page=titre_page,
        item_type=item_type
    )


@items_bp.route("/lost", methods=["GET", "POST"])
def declare_lost():
    return declarer("lost", "Déclarer un objet perdu")


@items_bp.route("/found", methods=["GET", "POST"])
def declare_found():
    return declarer("found", "Déclarer un objet trouvé")
```
