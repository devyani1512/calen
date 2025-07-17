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
from models import db, User
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")  # Neon Postgres
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# --- Google OAuth Setup ---
CLIENT_CONFIG = json.loads(os.getenv("CLIENT_CONFIG_JSON"))

@app.route("/login")
def login():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    auth_url, _ = flow.authorization_url(prompt="consent", include_granted_scopes="true")
    return redirect(auth_url)

@app.route("/oauth2callback")
def oauth2callback():
    flow = Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/userinfo.email"],
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    # Fetch user info (email)
    oauth_service = build("oauth2", "v2", credentials=creds)
    user_info = oauth_service.userinfo().get().execute()
    email = user_info["email"]
    name = user_info.get("name", "")

    # Serialize credentials
    credentials_json = json.dumps({
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    })

    # Store or update user in DB
    user = User.query.filter_by(email=email).first()
    if user:
        user.credentials_json = credentials_json
    else:
        user = User(email=email, name=name, credentials_json=credentials_json)
        db.session.add(user)

    db.session.commit()

    session["user_id"] = user.id  # ✅ Store user ID in session
    return redirect("/chat-ui")  # or wherever your frontend is

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_input = data.get("message")
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"message": "❌ Not logged in", "success": False}), 401

        response = ask_openai(user_input, user_id)
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

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)



