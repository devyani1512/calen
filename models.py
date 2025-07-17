# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"  # avoid using "user", which is a reserved SQL keyword

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    name = db.Column(db.String(256), nullable=True)
    credentials_json = db.Column(db.Text, nullable=False)  # stores OAuth credentials

    def __repr__(self):
        return f"<User {self.email}>"

