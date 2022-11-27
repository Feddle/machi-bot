"""Initialization for twitter bot"""
import sys
from loguru import logger
from . import create_tweet
from . import media_upload

def main():
    """Upload and tweet media"""
    # Configure logger
    time_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
    log_format = f"{time_format} | <level>{{level: <8}}</level> - <level>{{message}}</level>"
    config = {
        "handlers": [
            {"sink": sys.stderr, "format": log_format},
        ],
    }
    logger.configure(**config)

    # Upload media
    file_path = "./media/imprint.m4v"
    media_id = media_upload.upload_media(file_path)

    # Create the tweet
    create_tweet.post_tweet(media_id)
