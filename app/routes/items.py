from datetime import datetime
from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from werkzeug.utils import secure_filename

from app import db
from app.models import Item


items_bp = Blueprint(
    "items",
    __name__,
    url_prefix="/items"
)

ALLOWED_ITEM_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def _is_supported_image(photo, extension):
    header = photo.stream.read(12)
    photo.stream.seek(0)

    if extension == "png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if extension in {"jpg", "jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if extension == "webp":
        return header[:4] == b"RIFF" and header[8:12] == b"WEBP"
    return False


def _render_declaration(item_type, form):
    return render_template(
        "items/declare.html",
        titre_page=(
            "Déclarer un objet perdu"
            if item_type == "lost"
            else "Déclarer un objet trouvé"
        ),
        item_type=item_type,
        form=form,
    )


@items_bp.route("/lost", methods=["GET", "POST"])
@login_required
def declare_lost():

    if request.method == "POST":
        return create_item("lost")

    return _render_declaration("lost", request.form)


@items_bp.route("/found", methods=["GET", "POST"])
@login_required
def declare_found():

    if request.method == "POST":
        return create_item("found")

    return _render_declaration("found", request.form)


def create_item(item_type):

    title = request.form.get("title", "").strip()
    category = (request.form.get("category", "").strip() or request.form.get("category_custom", "").strip())
    description = request.form.get("description", "").strip()
    location_selection = request.form.get("location_select", "").strip()
    location = request.form.get("location", "").strip()
    location_detail = request.form.get("location_detail", "").strip()
    finder_phone = request.form.get("finder_phone", "").strip()
    finder_note = request.form.get("finder_note", "").strip()
    event_date = request.form.get("event_date", "").strip()
    photo = request.files.get("photo")
    photo_filename = secure_filename(photo.filename) if photo and photo.filename else ""
    photo_extension = photo_filename.rpartition(".")[2].lower()

    # Basic validation
    if not title or not category or not description or not location_selection or not location or not event_date:
        flash(
            "Veuillez remplir tous les champs obligatoires.",
            "danger"
        )

        return _render_declaration(item_type, request.form)

    if photo_filename and photo_extension not in ALLOWED_ITEM_IMAGE_EXTENSIONS:
        flash(
            "Format d'image non accepté. Utilisez PNG, JPG ou WebP.",
            "danger"
        )
        return _render_declaration(item_type, request.form)

    if photo_filename and not _is_supported_image(photo, photo_extension):
        flash(
            "Le fichier sélectionné ne semble pas être une image valide.",
            "danger"
        )
        return _render_declaration(item_type, request.form)

    # Date conversion
    try:
        event_date = datetime.strptime(
            event_date,
            "%Y-%m-%d"
        ).date()

    except ValueError:
        flash(
            "La date est invalide.",
            "danger"
        )

        return _render_declaration(item_type, request.form)

    stored_photo = None
    if photo_filename:
        stored_photo = f"{uuid4().hex}_{photo_filename}"
        upload_folder = Path(current_app.static_folder) / "uploads"
        upload_folder.mkdir(parents=True, exist_ok=True)
        photo.save(upload_folder / stored_photo)

    if location_detail:
        location = f"{location} • {location_detail}" if location else location_detail

    # Create item
    item = Item(
        user_id=current_user.id,
        item_type=item_type,
        title=title,
        category=category,
        description=description,
        location=location,
        location_detail=location_detail or None,
        finder_phone=finder_phone or None,
        finder_note=finder_note or None,
        event_date=event_date,
        photo=stored_photo,
        status="actif"
    )

    db.session.add(item)
    db.session.commit()

    flash(
        "Votre déclaration a été enregistrée avec succès.",
        "success"
    )

    return redirect(
        url_for("items.item_detail", item_id=item.id)
    )


@items_bp.route("/<int:item_id>")
def item_detail(item_id):

    item = Item.query.get_or_404(item_id)

    return render_template(
        "items/details.html",
        item=item,
        is_owner=current_user.is_authenticated and item.user_id == current_user.id,
    )


@items_bp.route("/")
def list_items():

    item_type = request.args.get("type", "").strip()
    search_term = request.args.get("q", "").strip()
    category_filter = request.args.get("category", "").strip()

    query = Item.query.filter_by(status="actif")

    if item_type in ("lost", "found"):
        query = query.filter_by(item_type=item_type)

    if category_filter:
        query = query.filter_by(category=category_filter)

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                Item.title.ilike(search_pattern),
                Item.category.ilike(search_pattern),
                Item.description.ilike(search_pattern),
                Item.location.ilike(search_pattern),
            )
        )

    items = query.order_by(
        Item.created_at.desc()
    ).all()

    return render_template(
        "items/list.html",
        items=items,
        item_type=item_type,
        search_term=search_term,
        category_filter=category_filter,
    )


@items_bp.route("/mine")
@login_required
def my_items():

    items = (
        Item.query
        .filter_by(user_id=current_user.id)
        .order_by(Item.created_at.desc())
        .all()
    )

    return render_template(
        "items/mine.html",
        items=items,
    )


@items_bp.route("/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id):

    item = Item.query.get_or_404(item_id)

    # Only the owner can delete their item
    if item.user_id != current_user.id:
        flash(
            "Vous n'avez pas le droit de supprimer cet objet.",
            "danger"
        )

        return redirect(
            url_for("items.item_detail", item_id=item.id)
        )

    db.session.delete(item)
    db.session.commit()

    flash(
        "La déclaration a été supprimée.",
        "success"
    )

    return redirect(
        url_for("items.my_items")
    )