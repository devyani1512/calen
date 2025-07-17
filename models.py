from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"  # safer name than "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), unique=True, nullable=False)
    name = db.Column(db.String(256), nullable=True)
    credentials_json = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()


