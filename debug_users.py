# debug_users.py
from db import db
from models import User
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.secret_key = os.getenv("FLASK_SECRET_KEY")
db.init_app(app)

with app.app_context():
    users = User.query.all()
    for user in users:
        print(f"🧑‍💻 ID: {user.id}")
        print(f"🔐 auth_info:\n{user.auth_info}\n")
