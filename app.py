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

from flask import Flask, request, session, redirect, url_for, jsonify
from flask_cors import CORS
import os, json
from utils import ask_openai
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")

# --- Google OAuth Setup ---
CLIENT_CONFIG = json.loads(os.getenv("CLIENT_CONFIG_JSON"))

@app.route("/login")
def login():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    auth_url, _ = flow.authorization_url(prompt="consent", include_granted_scopes="true")
    return redirect(auth_url)

@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials
    session["user_credentials"] = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    return redirect("/chat-ui")  # or frontend

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message")
        session_id = session.get("user_id")
        response = ask_openai(user_input, session_id)
        return jsonify({"message": response, "success": True})
    except Exception as e:
        return jsonify({"message": f"❌ Assistant error: {str(e)}", "success": False}), 500

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/")
def home():
    return "✅ Google Calendar Assistant running!"


