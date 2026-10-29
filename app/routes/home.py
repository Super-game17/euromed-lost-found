from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import and_, or_

from app import db
from app.models import ChatMessage, Item, User


home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():
    recent_items = []
    chat_preview = None
    chat_preview_url = url_for("home.community_chat")
    chat_preview_title = "Discussion communautaire"
    if current_user.is_authenticated:
        recent_items = (
            Item.query
            .filter_by(status="actif")
            .order_by(Item.created_at.desc())
            .limit(3)
            .all()
        )
        chat_preview = (
            ChatMessage.query
            .filter(
                or_(
                    ChatMessage.sender_id == current_user.id,
                    ChatMessage.recipient_id == current_user.id,
                )
            )
            .order_by(ChatMessage.created_at.desc())
            .first()
        )
        if chat_preview and chat_preview.recipient_id is not None:
            other_user_id = (
                chat_preview.recipient_id
                if chat_preview.sender_id == current_user.id
                else chat_preview.sender_id
            )
            other_user = db.session.get(User, other_user_id)
            if other_user:
                chat_preview_title = f"{other_user.first_name} {other_user.last_name}"
                chat_preview_url = url_for(
                    "home.community_chat",
                    user_id=other_user.id,
                )

    return render_template(
        "home/index.html",
        recent_items=recent_items,
        chat_preview=chat_preview,
        chat_preview_url=chat_preview_url,
        chat_preview_title=chat_preview_title,
    )


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