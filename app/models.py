from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.String(200), default='default_avatar.svg')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    images = db.relationship('Image', backref='owner', lazy=True, cascade='all, delete-orphan')
    exhibitions = db.relationship('Exhibition', backref='owner', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    original_name = db.Column(db.String(200), nullable=False)
    title = db.Column(db.String(100), default='')
    description = db.Column(db.Text, default='')
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    file_size = db.Column(db.BigInteger, default=0)  # File size in bytes

    exhibition_items = db.relationship('ExhibitionItem', backref='image', lazy=True, cascade='all, delete-orphan')


class Exhibition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    items = db.relationship('ExhibitionItem', backref='exhibition', lazy=True, cascade='all, delete-orphan', order_by='ExhibitionItem.order')


class ExhibitionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exhibition_id = db.Column(db.Integer, db.ForeignKey('exhibition.id'), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    caption = db.Column(db.String(200), default='')
