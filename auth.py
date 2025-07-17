def oauth_callback():
    if "state" not in session:
        return "Session expired or invalid. Please try logging in again.", 400

    client_config = json.loads(os.getenv("CLIENT_CONFIG_JSON"))

    flow = Flow.from_client_config(
        client_config,
        scopes=[
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ],
        state=session["state"]
    )
    flow.redirect_uri = "https://calen-o3rg.onrender.com/oauth2callback"
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials

    # 👇 Fetch user's email and name
    userinfo_service = build('oauth2', 'v2', credentials=creds)
    userinfo = userinfo_service.userinfo().get().execute()
    email = userinfo.get("email")
    name = userinfo.get("name")

    if not email:
        return "Failed to retrieve user email from Google", 400

    # Prepare credentials to save
    user_info = {
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "token": creds.token,
        "scopes": creds.scopes
    }

    print("🔐 Saving user:", email, "Info:", json.dumps(user_info, indent=2))

    # 🔄 Create or update user
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, name=name, credentials_json=json.dumps(user_info))
        db.session.add(user)
    else:
        user.name = name
        user.credentials_json = json.dumps(user_info)
    db.session.commit()

    session["user_id"] = user.id
    return redirect("/")


