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
import os
import json
from flask import Flask, redirect, url_for, session, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Internal modules
from models import init_db, db, User
from utils import ask_openai
from calendar_tools import handle_calendar_command, get_user_credentials, store_user_credentials

# Load environment variables
load_dotenv()

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret")

# ✅ Use DATABASE_URL from env for SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

# Setup session
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Initialize DB
init_db(app)

# Google OAuth config
CLIENT_CONFIG_JSON = os.getenv("CLIENT_CONFIG_JSON")
if not CLIENT_CONFIG_JSON:
    raise ValueError("CLIENT_CONFIG_JSON is missing in environment")

client_config = json.loads(CLIENT_CONFIG_JSON)
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# --- Routes ---

@app.route("/")
def index():
    if "user_id" in session:
        return render_template("index.html")
    return render_template("login.html")

@app.route("/login")
def login():
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    auth_url, _ = flow.authorization_url(prompt="consent", include_granted_scopes="true")
    return redirect(auth_url)

@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    user_info_service = build("oauth2", "v2", credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()

    # Store credentials and user info in DB
    user = store_user_credentials(
        email=user_info["email"],
        name=user_info.get("name"),
        credentials=credentials
    )
    session["user_id"] = user.id
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/ask", methods=["POST"])
def ask():
    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    user = db.session.get(User, session["user_id"])
    if not user:
        return {"error": "User not found"}, 404

    user_credentials = get_user_credentials(user)
    if not user_credentials:
        return {"error": "No credentials found"}, 400

    query = request.json.get("query", "")
    response = ask_openai(query, tools=[handle_calendar_command], user_credentials=user_credentials)
    return {"response": response}

# --- Entry Point ---
if __name__ == "__main__":
    app.run(debug=True)
