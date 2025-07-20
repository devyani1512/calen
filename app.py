
import os
import json
from flask import Flask, redirect, url_for, session, request, render_template # Changed import
from flask_sqlalchemy import SQLAlchemy
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from models import db, User
from utils import ask_openai

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev") # Change in production

#  Configure DB 
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Load client config from environment 
CLIENT_CONFIG_JSON = os.getenv("CLIENT_CONFIG_JSON")
client_config = json.loads(CLIENT_CONFIG_JSON)

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]

# Home Page
@app.route("/", methods=["GET", "POST"])
def index():
    user_email = session.get("user_email")
    response_message = None 
    error_message = None 
    
    if request.method == "POST":
        query = request.form.get("query")
        if user_email:
            user = User.query.filter_by(email=user_email).first()
            if user:
                credentials_info = json.loads(user.credentials_json)
                creds = Credentials.from_authorized_user_info(credentials_info, SCOPES)
                response_message = ask_openai(query, creds) # Store response
            else:
                error_message = "User not found in database. Please re-login."
        else:
            error_message = "You need to log in to ask something."
    
    # Pass all relevant variables to the template
    return render_template(
        "index.html",
        user_email=user_email,
        response=response_message, # Pass the response message
        error=error_message       # Pass the error message
    )


#  Login 
@app.route("/login")
def login():
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    session["state"] = state
    return redirect(auth_url)


#  OAuth2 Callback 
@app.route("/oauth2callback")
def oauth2callback():
    state = session.get("state")
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for("oauth2callback", _external=True),
    )
    flow.fetch_token(authorization_response=request.url)
    creds = flow.credentials

    # Get user info
    userinfo_service = build("oauth2", "v2", credentials=creds)
    userinfo = userinfo_service.userinfo().get().execute()

    email = userinfo["email"]
    name = userinfo.get("name", "")

    # Save or update user in DB
    user = User.query.filter_by(email=email).first()
    if user:
        user.credentials_json = json.dumps(json.loads(creds.to_json()))
    else:
        user = User(
            email=email,
            name=name,
            credentials_json=json.dumps(json.loads(creds.to_json()))
        )
        db.session.add(user)
    db.session.commit()

    session["user_email"] = email
    return redirect(url_for("index"))


#  Logout 
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    
    with app.app_context():
        db.create_all()
    app.run(debug=True)
