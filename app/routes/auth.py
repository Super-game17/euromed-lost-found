from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from urllib.parse import urlsplit

from app import db
from app.models import User


auth_bp = Blueprint("auth", __name__)
PASSWORD_RESET_MAX_AGE = 30 * 60


def _password_reset_payload_serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt="password-reset-payload",
    )


def _password_reset_serializer(user):
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"],
        salt=f"password-reset:{user.password_hash}",
    )


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        # Validation
        if not first_name or not last_name or not email or not password:
            flash("Veuillez remplir tous les champs.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Le mot de passe doit contenir au moins 6 caractères.", "danger")
            return render_template("auth/register.html")

        # Check duplicate email
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("Cet email est déjà utilisé.", "danger")
            return render_template("auth/register.html")

        # Create user
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Compte créé avec succès ! Vous pouvez maintenant vous connecter.", "success")

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)

            flash(
                f"Bienvenue {user.first_name} !",
                "success"
            )

            next_url = request.form.get("next") or request.args.get("next", "")
            parsed_next = urlsplit(next_url)
            if (
                parsed_next.scheme == ""
                and parsed_next.netloc == ""
                and parsed_next.path.startswith("/")
                and not parsed_next.path.startswith("//")
                and not parsed_next.path.startswith("/\\")
            ):
                return redirect(next_url)

            return redirect(url_for("home.index"))

        flash(
            "Email ou mot de passe incorrect.",
            "danger"
        )

    return render_template("auth/login.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            payload_token = _password_reset_payload_serializer().dumps(
                {"user_id": user.id}
            )
            proof_token = _password_reset_serializer(user).dumps({})
            token = f"{payload_token}~{proof_token}"
            reset_url = url_for("auth.reset_password", token=token, _external=True)
            current_app.logger.warning(
                "PROTOTYPE ONLY - password reset link for %s: %s",
                user.email,
                reset_url,
            )

        flash(
            "Si cette adresse correspond à un compte, un lien de réinitialisation "
            "est disponible dans le terminal du serveur (prototype local).",
            "info",
        )
        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("home.index"))

    try:
        payload_token, proof_token = token.split("~", 1)
        payload = _password_reset_payload_serializer().loads(
            payload_token,
            max_age=PASSWORD_RESET_MAX_AGE,
        )
    except SignatureExpired:
        flash("Ce lien de réinitialisation a expiré. Demandez-en un nouveau.", "danger")
        return redirect(url_for("auth.forgot_password"))
    except (BadSignature, ValueError):
        flash("Ce lien de réinitialisation est invalide.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user_id = payload.get("user_id")
    user = db.session.get(User, user_id) if isinstance(user_id, int) else None
    if user is None:
        flash("Ce lien de réinitialisation est invalide.", "danger")
        return redirect(url_for("auth.forgot_password"))

    try:
        _password_reset_serializer(user).loads(
            proof_token,
            max_age=PASSWORD_RESET_MAX_AGE,
        )
    except SignatureExpired:
        flash("Ce lien de réinitialisation a expiré. Demandez-en un nouveau.", "danger")
        return redirect(url_for("auth.forgot_password"))
    except BadSignature:
        flash("Ce lien de réinitialisation est invalide ou a déjà été utilisé.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        password_confirmation = request.form.get("password_confirmation", "")

        if len(password) < 6:
            flash("Le mot de passe doit contenir au moins 6 caractères.", "danger")
        elif password != password_confirmation:
            flash("Les mots de passe ne correspondent pas.", "danger")
        else:
            user.set_password(password)
            db.session.commit()
            flash("Votre mot de passe a été modifié. Vous pouvez vous connecter.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()

    flash(
        "Vous avez été déconnecté.",
        "info"
    )

    return redirect(url_for("home.index"))


@auth_bp.route("/profile")
@login_required
def profile():
    return render_template(
        "profile/profile.html",
        user=current_user
    )