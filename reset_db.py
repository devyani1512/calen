# reset_db.py


# reset_db.py

from app import app
from models import db

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Database reset: All tables dropped and recreated.")
