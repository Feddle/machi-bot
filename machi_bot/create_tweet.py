"""Creating and posting a tweet"""

import json
import requests
from loguru import logger

from .oauth import OAuth1
from requests_oauthlib import OAuth1 as oauth_helper

def post_tweet(text: str, media_id: str) -> dict:
    """Posts a Tweet"""

    manage_tweets_endpoint = "https://api.twitter.com/2/tweets"

    request_body = {}

    oauth = OAuth1()
    oauth.handle_oauth1()

    auth_session = oauth_helper(
        client_key=oauth.twitter_api_key,
        client_secret=oauth.twitter_api_secret,
        resource_owner_key=oauth.oauth_token,
        resource_owner_secret=oauth.oauth_token_secret
    )

    request_body["text"] = text

    if media_id:
        request_body["media"] = {"media_ids": [media_id]}

    # Post Tweet
    response = requests.request(
        "POST",
        manage_tweets_endpoint,
        auth=auth_session,
        json=request_body,
        timeout=10
    )

    if response.status_code != 201:
        logger.error(f"Posting tweet returned an error: {response.status_code} {response.text}")
    else:
        json_string = json.dumps(response.json(), indent=4)
        logger.success("Tweet posted!")
        logger.success(f"{json_string}")

    return response

def get_tweet():
    """Fetches single tweet. Only for auth testing for now.
    """
    manage_tweets_endpoint = "https://api.twitter.com/2/tweets"
    oauth = OAuth1()
    oauth.handle_oauth1()

    auth_session = oauth_helper(
        client_key=oauth.twitter_api_key,
        client_secret=oauth.twitter_api_secret,
        resource_owner_key=oauth.oauth_token,
        resource_owner_secret=oauth.oauth_token_secret
    )
    request_body = {"ids": "1635294771139997700", "tweet.fields": "created_at"}
    response = requests.request(
        "GET",
        manage_tweets_endpoint,
        auth=auth_session,
        params=request_body,
        timeout=10
    )
    logger.debug(response.json())
