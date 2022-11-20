"""Initialization for twitter bot"""

import os
import datetime
import base64
import hashlib
import re
import json
from dotenv import load_dotenv
import requests
from requests_oauthlib import OAuth2Session

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

TWITTER_CLIENT_ID = os.environ.get("TWITTER_CLIENT_ID")
TWITTER_CLIENT_SECRET = os.environ.get("TWITTER_CLIENT_SECRET")

POST_TWEET_URL = "https://api.twitter.com/2/tweets"


def handle_oauth():
    """Fetch and return the access token for user authenticated requests"""

    # This must match *exactly* the redirect URL specified in the Developer Portal.
    callback_url = "https://localhost"

    # Set the scopes needed to be granted by the authenticating user.
    scopes = ["tweet.read", "tweet.write", "users.read"]

    # Create a code verifier
    code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
    code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)

    # Create a code challenge
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
    code_challenge = code_challenge.replace("=", "")

    # State should be stored somewhere so it can be later validated
    state = hashlib.sha256(os.urandom(1024)).hexdigest()

    # Start an OAuth 2.0 session
    oauth = OAuth2Session(TWITTER_CLIENT_ID, redirect_uri=callback_url, scope=scopes, state=state)

    # Create an authorize URL
    auth_url = "https://twitter.com/i/oauth2/authorize"
    authorization_url = oauth.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )

    print(
        "Visit the following URL to authorize your App on behalf of your Twitter handle:"
    )
    print(authorization_url)

    authorization_response = input(
        "Paste in the full URL after you've authorized your App:\n"
    )

    # Fetch your access token
    token_url = "https://api.twitter.com/2/oauth2/token"
    token = oauth.fetch_token(
        token_url=token_url,
        authorization_response=authorization_response,
        client_secret=TWITTER_CLIENT_SECRET,
        code_verifier=code_verifier
    )

    access_token = token["access_token"]
    return access_token

def post_tweet():
    """Posts a Tweet"""

    manage_tweets_endpoint = "https://api.twitter.com/2/tweets"

    request_body = {}

    access_token = handle_oauth()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "machikuma-bot"
    }

    now = datetime.datetime.now()
    request_body['text'] = f"Testing! {now}"

    # Post Tweet
    response = requests.request(
        "POST",
        manage_tweets_endpoint,
        headers=headers,
        json=request_body,
        timeout=10
    )

    if response.status_code != 201:
        print(f"Request returned an error: {response.status_code} {response.text}")
    else:
        json_string = json.dumps(response.json())
        print(f"Response: {json_string}")
