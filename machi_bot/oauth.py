"""Helper functions for OAuth"""

import os
import base64
import hashlib
import re
import json
import time
from urllib.parse import urlparse, parse_qs
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session, OAuth1Session
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_CLIENT_ID = os.environ.get("TWITTER_CLIENT_ID")
TWITTER_CLIENT_SECRET = os.environ.get("TWITTER_CLIENT_SECRET")

POST_TWEET_URL = "https://api.twitter.com/2/tweets"


def handle_oauth2():
    """Fetch and return the access token for user authenticated requests using OAuth2"""

    # This must match *exactly* the redirect URL specified in the Developer Portal.
    redirect_uri = "https://localhost"

    # Set the scopes needed to be granted by the authenticating user.
    scopes = ["tweet.read", "tweet.write", "users.read", "offline.access"]

    # Create a code verifier
    code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

    # Create a code challenge
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")

    # State should be stored somewhere so it can be later validated
    state = hashlib.sha256(os.urandom(1024)).hexdigest()

    token_url = "https://api.twitter.com/2/oauth2/token"

    try:
        # Try to open the token file
        with open("token.json", "r", encoding="utf-8") as file:
            previous_token = json.load(file)

        # If token has expired refresh it
        # Subtract 5 minutes from expiration to account for clock skew
        now = time.time()
        expire_time = previous_token["expires_at"] - 300
        if now >= expire_time:
            print("Refreshing token")
            oauth = OAuth2Session(
                client_id=TWITTER_CLIENT_ID,
                token=previous_token,
                redirect_uri=redirect_uri,
                scope=scopes,
                state=state
            )
            auth = HTTPBasicAuth(TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET)
            response = oauth.refresh_token(
                client_id=TWITTER_CLIENT_ID,
                client_secret=TWITTER_CLIENT_SECRET,
                token_url=token_url,
                auth=auth,
                refresh_token=previous_token["refresh_token"]
            )

            access_token = response["access_token"]
            with open("token_v2.json", "w+", encoding="utf-8") as file:
                file.write(json.dumps(response, indent=4))
        else:
            print("Using previous token")
            access_token = previous_token["access_token"]

    except FileNotFoundError:
        # If v2 token doesn't exist authorize the app and get a new access token
        print("Token file not found. Starting authorization.")

        # Create an authorize URL
        oauth = OAuth2Session(
            client_id=TWITTER_CLIENT_ID,
            redirect_uri=redirect_uri,
            scope=scopes,
            state=state
        )
        auth_url = "https://twitter.com/i/oauth2/authorize"
        authorization_url = oauth.authorization_url(
            auth_url, code_challenge=code_challenge, code_challenge_method="S256"
        )

        print(
            "Visit the following URL to authorize your App on behalf of your Twitter handle:"
        )
        print(authorization_url)

        authorization_response = input("Paste in the full URL after you've authorized your App:\n")

        response = oauth.fetch_token(
            token_url=token_url,
            authorization_response=authorization_response,
            client_secret=TWITTER_CLIENT_SECRET,
            code_verifier=code_verifier
        )
        print("Access token acquired!")

        # Write the token to file
        with open("token_v2.json", "w+", encoding="utf-8") as file:
            file.write(json.dumps(response, indent=4))

        access_token = response["access_token"]


    return access_token

def handle_oauth1():
    """Fetch and return the access token for user authenticated requests using OAuth1"""

    try:
        # Try to open the token file
        with open("token_v1.json", "r", encoding="utf-8") as file:
            token_file = json.load(file)

        access_token = token_file
    except FileNotFoundError:
        # If token file doesn't exist authorize the app and get a new access token

        request_token_url = "https://api.twitter.com/oauth/request_token"
        oauth_auth_session = OAuth1Session(
            client_key=TWITTER_API_KEY,
            client_secret=TWITTER_API_SECRET
        )

        fetch_response = oauth_auth_session.fetch_request_token(request_token_url)

        resource_owner_key = fetch_response.get("oauth_token")
        resource_owner_secret = fetch_response.get("oauth_token_secret")
        print(f"Got OAuth token: {resource_owner_key}")

        # Get authorization
        base_authorization_url = "https://api.twitter.com/oauth/authorize"
        authorization_url = oauth_auth_session.authorization_url(base_authorization_url)
        print(f"Please go here and authorize: {authorization_url}")
        authorization_response = input("Paste the full URL here: ")

        # Parse query parameters
        response_params = urlparse(authorization_response).query
        verifier = parse_qs(response_params)["oauth_verifier"]
        verifier = "".join(verifier)

        token_keys = {
            "resource_owner_key": resource_owner_key,
            "resource_owner_secret": resource_owner_secret,
            "verifier": verifier
        }

        # Get the access token
        access_token_url = "https://api.twitter.com/oauth/access_token"
        oauth_token_session = OAuth1Session(
            client_key=TWITTER_API_KEY,
            client_secret=TWITTER_API_SECRET,
            resource_owner_key=token_keys["resource_owner_key"],
            resource_owner_secret=token_keys["resource_owner_secret"],
            verifier=token_keys["verifier"],
        )
        access_token = oauth_token_session.fetch_access_token(access_token_url)

        # Write the token to file
        with open("token_v1.json", "w+", encoding="utf-8") as file:
            file.write(json.dumps(access_token, indent=4))

    return access_token
