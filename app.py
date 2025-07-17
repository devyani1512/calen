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

from flask import Flask, redirect, session, url_for, request, render_template
from auth import oauth_login, oauth_callback
from models import db, User
from utils import ask_openai, handle_user_query
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize DB
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/login")
def login():
    return oauth_login()

@app.route("/oauth2callback")
def oauth2callback():
    return oauth_callback()

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return "Unauthorized", 401

    user = db.get_or_404(User, session["user_id"])
    user_input = request.form.get("message", "")
    if not user_input:
        return "No message provided", 400

    try:
        response = ask_openai(user_input, user)
        return response
    except Exception as e:
        return f"❌ Assistant error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
