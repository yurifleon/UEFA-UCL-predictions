from . import db

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    match = db.Column(db.String(100))
    prediction = db.Column(db.String(10))
    actual = db.Column(db.String(10))
    score = db.Column(db.Integer)

