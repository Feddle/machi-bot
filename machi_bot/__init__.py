"""Initialization for twitter bot"""

import datetime
import json
import requests
from . import oauth


def post_tweet():
    """Posts a Tweet"""

    manage_tweets_endpoint = "https://api.twitter.com/2/tweets"

    request_body = {}

    access_token = oauth.handle_oauth2()

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
