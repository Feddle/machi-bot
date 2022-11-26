"""Initialization for twitter bot"""

from . import create_tweet
from . import media_upload

def main():
    """Upload and tweet media"""
    # Upload media
    media_id = media_upload.upload_media()
    print(f"Media id: {media_id}")

    # Create the tweet
    create_tweet.post_tweet(media_id)
    return
