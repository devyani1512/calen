# reset_db.py

from your_app_file import app, db  # Replace with the actual app module

with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Database reset: All tables dropped and recreated.")
