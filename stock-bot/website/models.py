from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock = db.Column(db.String(7))
    quantity = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    current_price = db.Column(db.Float)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    balance = db.Column(db.Float)
    stocks = db.relationship('Stock')
    


