"""Creating and posting a tweet"""

import datetime
import json
import requests
from loguru import logger

from .oauth import OAuth2


def post_tweet(media_id: str) -> dict:
    """Posts a Tweet"""

    manage_tweets_endpoint = "https://api.twitter.com/2/tweets"

    request_body = {}
    oauth = OAuth2()
    access_token = oauth.handle_oauth2()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": "machikuma-bot"
    }

    now = datetime.datetime.now()
    request_body["text"] = f"Testing! {now}"
    if media_id:
        request_body["media"] = {"media_ids": [media_id]}

    # Post Tweet
    response = requests.request(
        "POST",
        manage_tweets_endpoint,
        headers=headers,
        json=request_body,
        timeout=10
    )

    if response.status_code != 201:
        logger.error(f"Posting tweet returned an error: {response.status_code} {response.text}")
    else:
        json_string = json.dumps(response.json(), indent=4)
        logger.success("Tweet posted!")
        logger.success(f"{json_string}")

    return response.json()
