"""Initialization for twitter bot"""

from . import create_tweet
from . import media_upload

def main():
    """Upload and tweet media"""
    # Upload media
    file_path = "./media/imprint.m4v"
    media_id = media_upload.upload_media(file_path)
    print(f"Media id: {media_id}")

    # Create the tweet
    create_tweet.post_tweet(media_id)
    return
