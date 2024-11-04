import requests
import json
import logging
from flask import Flask, request, redirect, session, url_for
from oauthlib.oauth2 import WebApplicationClient
from backend.src.config.env_config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_DISCOVERY_URL, GOOGLE_REDIRECT_URI
from backend.src.models.user_model import UserModel
from backend.src.utils.jwt_util import generate_jwt_token

app = Flask(__name__)
app.secret_key = 'supersecretkey' 

client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    try:
        response = requests.get(GOOGLE_DISCOVERY_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch Google provider configuration: {e}")
        return None

@app.route("/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        return "Google OAuth configuration is unavailable", 500

    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=GOOGLE_REDIRECT_URI,
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    google_provider_cfg = get_google_provider_cfg()
    if not google_provider_cfg:
        return "Google OAuth configuration is unavailable", 500

    token_endpoint = google_provider_cfg["token_endpoint"]

    code = request.args.get("code")
    if not code:
        return "Missing authorization code", 400

    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_uri=GOOGLE_REDIRECT_URI,
        code=code
    )

    try:
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
        )
        token_response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch token: {e}")
        return "Failed to fetch token", 500

    client.parse_request_body_response(json.dumps(token_response.json()))

    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)

    try:
        userinfo_response = requests.get(uri, headers=headers, data=body)
        userinfo_response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch user info: {e}")
        return "Failed to fetch user info", 500

    user_info = userinfo_response.json()

    if not user_info.get("email_verified"):
        return "User email not available or not verified", 400

    user = UserModel.find_by_email(user_info["email"])
    if not user:
        user = UserModel(
            email=user_info["email"],
            full_name=user_info["name"],
            profile_pic=user_info["picture"],
            google_id=user_info["sub"]
        )
        user.save_to_db()

    session["user"] = user_info["email"]

    jwt_token = generate_jwt_token(user_info["email"])
    session["jwt_token"] = jwt_token

    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("jwt_token", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(ssl_context="adhoc")