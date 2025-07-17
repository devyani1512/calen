from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120))
    credentials_json = db.Column(db.Text)  # Store serialized Google credentials here

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
