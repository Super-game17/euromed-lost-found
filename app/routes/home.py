from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_, or_

from app import db
from app.models import ChatMessage, User


home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    return render_template("home/index.html")


@home_bp.route("/community/chat", methods=["GET", "POST"])
@login_required
def community_chat():
    active_user = None
    if request.method == "POST":
        recipient_value = request.form.get("recipient_id", "").strip()
        if recipient_value:
            try:
                recipient_id = int(recipient_value)
            except ValueError:
                abort(400)

            active_user = db.session.get(User, recipient_id)
            if active_user is None or active_user.id == current_user.id:
                abort(404)

        body = request.form.get("message", "").strip()
        if not body:
            flash("Écrivez un message avant de l’envoyer.", "danger")
        elif len(body) > 2000:
            flash("Votre message ne peut pas dépasser 2 000 caractères.", "danger")
        else:
            db.session.add(
                ChatMessage(
                    sender_id=current_user.id,
                    recipient_id=active_user.id if active_user else None,
                    body=body,
                )
            )
            db.session.commit()

        if active_user:
            return redirect(url_for("home.community_chat", user_id=active_user.id))
        return redirect(url_for("home.community_chat"))

    user_id = request.args.get("user_id", type=int)
    if user_id is not None:
        active_user = db.session.get(User, user_id)
        if active_user is None or active_user.id == current_user.id:
            abort(404)

        message_query = ChatMessage.query.filter(
            or_(
                and_(
                    ChatMessage.sender_id == current_user.id,
                    ChatMessage.recipient_id == active_user.id,
                ),
                and_(
                    ChatMessage.sender_id == active_user.id,
                    ChatMessage.recipient_id == current_user.id,
                ),
            )
        )
    else:
        message_query = ChatMessage.query.filter(ChatMessage.recipient_id.is_(None))

    messages = message_query.order_by(ChatMessage.created_at.desc()).limit(100).all()
    messages.reverse()
    users = (
        User.query
        .filter(User.id != current_user.id)
        .order_by(User.first_name, User.last_name)
        .all()
    )

    return render_template(
        "home/chat.html",
        messages=messages,
        users=users,
        active_user=active_user,
    )