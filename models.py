from datetime import datetime

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(200), unique=True, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(200))
    created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return "<User {}>".format(self.username)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    title = db.Column(db.String(50))
    price = db.Column(db.Numeric(10, 2), default=0)
    category = db.Column(db.String(50))
    description = db.Column(db.TEXT)
    image = db.Column(db.String)

    def __repr__(self):
        return "<Product {}".format(self.title)
