from flask import redirect, request, session
import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from models import db, User  # ✅ updated import

def oauth_login():
    client_config = json.loads(os.getenv("CLIENT_CONFIG_JSON"))

    flow = Flow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/calendar"],
        redirect_uri="https://calen-o3rg.onrender.com/oauth2callback"
    )

    auth_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )

    session["state"] = state
    return redirect(auth_url)

def oauth_callback():
    if "state" not in session:
        return "Session expired or invalid. Please try logging in again.", 400

    client_config = json.loads(os.getenv("CLIENT_CONFIG_JSON"))

    flow = Flow.from_client_config(
        client_config,
        scopes=["https://www.googleapis.com/auth/calendar"],
        state=session["state"]
    )
    flow.redirect_uri = "https://calen-o3rg.onrender.com/oauth2callback"
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    user_info = {
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "token": creds.token,
        "scopes": creds.scopes
    }

    print("🔐 Saving user info:", json.dumps(user_info, indent=2))

    user = User(credentials_json=json.dumps(user_info))
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id

    return redirect("/")

