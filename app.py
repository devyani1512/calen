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
from flask import Flask, redirect, url_for, request, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from utils import ask_openai
from models import db, User, init_db

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your-default-dev-secret")

# PostgreSQL database from Neon
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
init_db(app)

# Load Google OAuth client config from env
CLIENT_CONFIG_JSON = os.getenv("CLIENT_CONFIG_JSON")
if not CLIENT_CONFIG_JSON:
    raise RuntimeError("CLIENT_CONFIG_JSON not set in environment.")

CLIENT_SECRETS = json.loads(CLIENT_CONFIG_JSON)
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Routes

@app.route("/")
def home():
    return render_template_string("""
        <h2>Google Calendar Assistant</h2>
        {% if "user_id" in session %}
            <p>Welcome back! <a href='/logout'>Logout</a></p>
            <form method="POST" action="/ask">
                <input name="query" placeholder="e.g. Book meeting tomorrow 2pm" style="width:300px"/>
                <button>Ask</button>
            </form>
        {% else %}
            <a href="/login">Login with Google</a>
        {% endif %}
    """)


@app.route("/login")
def login():
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    auth_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    session["state"] = state
    return redirect(auth_url)


@app.route("/oauth2callback")
def oauth2callback():
    state = session.get("state")
    if not state:
        return "Missing OAuth state", 400

    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
        state=state,
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials

    # Get user info from calendar API
    service = build("calendar", "v3", credentials=credentials)
    profile = service.settings().get(setting="user").execute()
    email = profile.get("value")

    if not email:
        return "Could not get email from calendar API.", 500

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, credentials_json=json.dumps(credentials.to_json()))
        db.session.add(user)
    else:
        user.credentials_json = json.dumps(credentials.to_json())
    db.session.commit()

    session["user_id"] = user.id
    return redirect(url_for("home"))


@app.route("/ask", methods=["POST"])
def ask():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    query = request.form.get("query")
    user = db.session.get(User, user_id)
    if not user:
        return "User not found", 400

    creds = get_user_credentials(user)
    response = ask_openai(query, creds)
    return render_template_string("""
        <p><strong>You asked:</strong> {{query}}</p>
        <p><strong>Assistant:</strong> {{response}}</p>
        <a href="/">Go back</a>
    """, query=query, response=response)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
