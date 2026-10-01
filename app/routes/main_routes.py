from flask import Blueprint, render_template, redirect, url_for, flash, request
from app import db
from app.models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Création du Blueprint pour regrouper les routes
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

# ==========================================
# INSCRIPTION (GROUPE 1)
# ==========================================
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        prenom = request.form.get('prenom')
        nom = request.form.get('nom')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Vérifier si l'utilisateur existe déjà
        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('Cet email est déjà utilisé. Veuillez vous connecter.', 'danger')
            return redirect(url_for('main.register'))
            
        # Hachage sécurisé du mot de passe
        hashed_password = generate_password_hash(password, method='scrypt')
        
        # Création du nouvel utilisateur
        new_user = User(
            prenom=prenom,
            nom=nom,
            email=email,
            password_hash=hashed_password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Compte créé avec succès ! Vous pouvez maintenant vous connecter.', 'success')
        return redirect(url_for('main.login'))
        
    return render_template('register.html')

# ==========================================
# CONNEXION (GROUPE 1)
# ==========================================
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        # Vérification du mot de passe et de l'existence de l'utilisateur
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Bienvenue, {user.prenom} !', 'success')
            return redirect(url_for('main.profile'))
        else:
            flash('Échec de la connexion. Vérifiez votre email et votre mot de passe.', 'danger')
            
    return render_template('login.html')

# ==========================================
# PROFIL (PROtégé par @login_required)
# ==========================================
@main_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# ==========================================
# DÉCONNEXION
# ==========================================
@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('main.login'))
