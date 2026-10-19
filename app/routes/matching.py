import re

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.models import Claim, Item


matching_bp = Blueprint(
    "matching",
    __name__,
    url_prefix="/matching"
)


def normalize_text(value):
    if not value:
        return ""

    return " ".join(
        re.findall(
            r"[a-zA-ZÀ-ÿ0-9]+",
            value.lower()
        )
    )


def compute_match_score(lost_item, found_item):

    score = 0

    # Category = 50 points
    if (
        lost_item.category
        and found_item.category
        and lost_item.category.lower()
        == found_item.category.lower()
    ):
        score += 50

    # Location = 25 points
    if (
        lost_item.location
        and found_item.location
        and lost_item.location.lower()
        == found_item.location.lower()
    ):
        score += 25

    # Date = 15 points
    if lost_item.event_date and found_item.event_date:

        if found_item.event_date >= lost_item.event_date:
            score += 15

    # Title keyword overlap = 10 points
    lost_keywords = set(
        normalize_text(lost_item.title).split()
    )

    found_keywords = set(
        normalize_text(found_item.title).split()
    )

    overlap = len(
        lost_keywords & found_keywords
    )

    score += min(
        10,
        overlap * 3
    )

    return score


@matching_bp.route("/matches/<int:item_id>")
@login_required
def matches_for_item(item_id):

    item = Item.query.get_or_404(item_id)

    opposite_type = (
        "found"
        if item.item_type == "lost"
        else "lost"
    )

    candidates = (
        Item.query
        .filter_by(
            item_type=opposite_type,
            status="actif"
        )
        .all()
    )

    scored_matches = []

    for candidate in candidates:

        if candidate.id == item.id:
            continue

        score = compute_match_score(
            item,
            candidate
        )

        if score >= 50:

            scored_matches.append(
                {
                    "item": candidate,
                    "score": score
                }
            )

    scored_matches.sort(
        key=lambda entry: entry["score"],
        reverse=True
    )

    return render_template(
        "matching/matches.html",
        item=item,
        matches=scored_matches
    )


@matching_bp.route(
    "/claim/<int:item_id>",
    methods=["GET", "POST"]
)
@login_required
def claim_item(item_id):

    item = Item.query.get_or_404(item_id)

    # Don't claim your own item
    if item.user_id == current_user.id:

        flash(
            "Vous ne pouvez pas réclamer votre propre déclaration.",
            "danger"
        )

        return redirect(
            url_for(
                "items.item_detail",
                item_id=item.id
            )
        )

    # Don't claim a lost item if you're the owner, etc.
    existing_claim = Claim.query.filter_by(
        item_id=item.id,
        claimer_id=current_user.id
    ).first()

    if existing_claim:

        flash(
            "Vous avez déjà envoyé une réclamation pour cet objet.",
            "info"
        )

        return redirect(
            url_for("matching.my_claims")
        )

    if request.method == "POST":

        proof = request.form.get(
            "proof_description",
            ""
        ).strip()

        if not proof:

            return render_template(
                "matching/claim_form.html",
                item=item,
                error="Merci de donner au moins un détail de preuve."
            )

        claim = Claim(
            item_id=item.id,
            claimer_id=current_user.id,
            proof_description=proof,
            status="en_attente"
        )

        item.status = "en_cours"

        db.session.add(claim)
        db.session.commit()

        flash(
            "Votre réclamation a été envoyée.",
            "success"
        )

        return redirect(
            url_for("matching.my_claims")
        )

    return render_template(
        "matching/claim_form.html",
        item=item,
        error=None
    )


@matching_bp.route("/my-claims")
@login_required
def my_claims():

    claims = (
        Claim.query
        .filter_by(
            claimer_id=current_user.id
        )
        .order_by(
            Claim.created_at.desc()
        )
        .all()
    )

    return render_template(
        "matching/my_claims.html",
        claims=claims
    )


@matching_bp.route(
    "/manage/<int:claim_id>",
    methods=["GET", "POST"]
)
@login_required
def manage_claim(claim_id):

    claim = Claim.query.get_or_404(claim_id)

    # Only the owner of the item can manage its claims
    if claim.item.user_id != current_user.id:

        flash(
            "Vous n'avez pas le droit de gérer cette réclamation.",
            "danger"
        )

        return redirect(
            url_for("home.index")
        )

    if request.method == "POST":

        action = request.form.get("action")

        if action == "validate":

            claim.status = "valide"
            claim.item.status = "en_cours"
            claim.review_note = "Réclamation validée."

        elif action == "reject":

            claim.status = "rejete"
            claim.item.status = "actif"
            claim.review_note = "Réclamation refusée."

        elif action == "restitute":

            claim.status = "restitue"
            claim.item.status = "restitue"
            claim.review_note = "Objet restitué."

        else:

            flash(
                "Action inconnue.",
                "danger"
            )

            return redirect(
                url_for(
                    "matching.manage_claim",
                    claim_id=claim.id
                )
            )

        db.session.commit()

        flash(
            "La réclamation a été mise à jour.",
            "success"
        )

        return redirect(
            url_for(
                "matching.manage_claim",
                claim_id=claim.id
            )
        )

    return render_template(
        "matching/manage_claim.html",
        claim=claim
    )