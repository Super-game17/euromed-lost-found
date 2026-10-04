import re
from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user

from app import db
from app.models import Claim, Item

matching_bp = Blueprint("matching", __name__, url_prefix="/matching")


def current_user_id():
    """Temporary fallback while the auth module is not fully integrated."""
    if current_user.is_authenticated:
        return current_user.id
    return 1


def normalize_text(value):
    if not value:
        return ""
    return " ".join(re.findall(r"[a-zA-Z0-9]+", value.lower()))


def compute_match_score(lost_item, found_item):
    score = 0

    if lost_item.category.lower() == found_item.category.lower():
        score += 50

    if lost_item.location.lower() == found_item.location.lower():
        score += 25

    if found_item.event_date and lost_item.event_date:
        if found_item.event_date >= lost_item.event_date:
            score += 15

    lost_keywords = set(normalize_text(lost_item.title).split())
    found_keywords = set(normalize_text(found_item.title).split())
    overlap = len(lost_keywords & found_keywords)
    if overlap:
        score += min(10, overlap * 3)

    return score


@matching_bp.route("/matches/<int:item_id>", methods=["GET"])
def matches_for_item(item_id):
    item = Item.query.get_or_404(item_id)

    opposite_type = "found" if item.item_type == "lost" else "lost"
    candidates = Item.query.filter_by(item_type=opposite_type, status="actif").all()

    scored_matches = []
    for candidate in candidates:
        if candidate.id == item.id:
            continue

        score = compute_match_score(item, candidate)
        if score >= 50:
            scored_matches.append({"item": candidate, "score": score})

    scored_matches.sort(key=lambda entry: entry["score"], reverse=True)

    return render_template(
        "matching/matches.html",
        item=item,
        matches=scored_matches,
    )


@matching_bp.route("/claim/<int:item_id>", methods=["GET", "POST"])
def claim_item(item_id):
    item = Item.query.get_or_404(item_id)

    if request.method == "POST":
        proof = request.form.get("proof_description", "").strip()
        if not proof:
            return render_template(
                "matching/claim_form.html",
                item=item,
                error="Merci de donner au moins un détail de preuve.",
            )

        claim = Claim(
            item_id=item.id,
            claimer_id=current_user_id(),
            proof_description=proof,
            status="en_attente",
        )

        item.status = "en_cours"
        db.session.add(claim)
        db.session.commit()

        return redirect(url_for("matching.my_claims"))

    return render_template("matching/claim_form.html", item=item, error=None)


@matching_bp.route("/my-claims", methods=["GET"])
def my_claims():
    claims = (
        Claim.query.filter_by(claimer_id=current_user_id())
        .order_by(Claim.created_at.desc())
        .all()
    )
    return render_template("matching/my_claims.html", claims=claims)


@matching_bp.route("/manage/<int:claim_id>", methods=["GET", "POST"])
def manage_claim(claim_id):
    claim = Claim.query.get_or_404(claim_id)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "validate":
            claim.status = "valide"
            claim.item.status = "en_cours"
            claim.review_note = "Réclamation validée."
        elif action == "reject":
            claim.status = "rejete"
            claim.review_note = "Réclamation refusée."
        elif action == "restitute":
            claim.status = "restitue"
            claim.item.status = "restitue"
            claim.review_note = "Objet restitué."

        db.session.commit()
        return redirect(url_for("matching.manage_claim", claim_id=claim.id))

    return render_template("matching/manage_claim.html", claim=claim)
