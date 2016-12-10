"""Database configuration
"""

from flask_sqlalchemy import SQLAlchemy
from catalog import app

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
        }


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'user': self.user.name,
        }


class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)

    level = db.Column(db.String(20))  # Beginner, Intermediate, Advanced
    url = db.Column(db.String(250))
    image_url = db.Column(db.String(250))
    description = db.Column(db.String(250))
    provider = db.Column(db.String(30))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship(Category)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship(User)

    @property
    def serialize(self):
        return {
            'category': self.category.name,
            'user': self.user.name,
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'url': self.url,
            'image_url': self.image_url,
            'description': self.description,
            'provider': self.provider,
        }
