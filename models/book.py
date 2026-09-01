from database import db


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100))
    isbn = db.Column(db.String(50), unique=True)
    quantity = db.Column(db.Integer, default=1)
    available_quantity = db.Column(db.Integer, default=1)