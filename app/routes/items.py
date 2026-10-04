from datetime import datetime

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from app import db
from app.models import Item, User


items_bp = Blueprint("items", __name__, url_prefix="/items")


def get_user_id():
    if current_user.is_authenticated:
        return current_user.id

    demo_user = User.query.filter_by(email="demo@euromed.local").first()
    if demo_user is None:
        demo_user = User(
            first_name="Demo",
            last_name="User",
            email="demo@euromed.local",
        )
        demo_user.set_password("demo")
        db.session.add(demo_user)
        db.session.flush()

    return demo_user.id


def declarer(item_type, titre_page):
    if request.method == "POST":
        item = Item(
            user_id=get_user_id(),
            item_type=item_type,
            title=request.form["title"],
            description=request.form["description"],
            category=request.form["category"],
            location=request.form["location"],
            event_date=datetime.strptime(
                request.form["date_event"],
                "%Y-%m-%d"
            ).date(),
            status="actif",
        )

        db.session.add(item)
        db.session.commit()

        return redirect(url_for("matching.matches_for_item", item_id=item.id))

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
