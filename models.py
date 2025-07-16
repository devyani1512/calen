from db import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auth_info = db.Column(db.Text)
