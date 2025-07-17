# from flask import Flask, redirect, session, url_for, request, render_template
# from auth import oauth_login, oauth_callback
# from db import db, init_db
# from models import User
# from utils import ask_openai
# from calendar_tools import handle_calendar_command
# from dotenv import load_dotenv
# import os

# load_dotenv()

# app = Flask(__name__)
# app.secret_key = os.getenv("FLASK_SECRET_KEY")
# app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# db.init_app(app)
# init_db(app)

# @app.route("/")
# def home():
#     if "user_id" not in session:
#         return redirect(url_for("login"))
#     return render_template("index.html")

# @app.route("/logout")
# def logout():
#     session.clear()
#     return redirect(url_for("home"))


# @app.route("/login")
# def login():
#     return oauth_login()

# @app.route("/oauth2callback")
# def oauth2callback():
#     return oauth_callback()

# @app.route("/chat", methods=["POST"])
# def chat():
#     if "user_id" not in session:
#         return "Unauthorized", 401
#     user = db.get_or_404(User, session["user_id"])
#     user_input = request.form.get("message")
#     response = ask_openai(user_input, user)
#     return response

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from db import db, User  # Assuming you have your db models in db.py
from assistant import ask_openai  # Your main function that processes the prompt and returns reply
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
db.init_app(app)

@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))

    response = None
    if request.method == "POST":
        user = db.get_or_404(User, session["user_id"])
        user_input = request.form.get("message")
        result = ask_openai(user_input, user)
        response = result  # adjust this if `ask_openai` returns a dict

    return render_template("index.html", response=response)

@app.route("/login")
def login():
    return "Login page logic here"

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
