from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    items = db.relationship("Item", back_populates="user", cascade="all, delete-orphan")
    claims = db.relationship("Claim", back_populates="claimer", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    item_type = db.Column(db.String(20), nullable=False)  # lost / found
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(150), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(30), default="actif", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="items")
    claims = db.relationship("Claim", back_populates="item", cascade="all, delete-orphan")


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"), nullable=False)
    claimer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    proof_description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="en_attente", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    review_note = db.Column(db.Text, nullable=True)

    item = db.relationship("Item", back_populates="claims")
    claimer = db.relationship("User", back_populates="claims")
