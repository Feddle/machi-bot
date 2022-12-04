"""Initialization for twitter bot"""
import sys
import os
import subprocess
import shlex
import json
from loguru import logger
from . import create_tweet
from . import media_upload
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")
with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    CONFIG = json.load(file)

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

    # Select a random file and convert it to mp4
    file_path = get_file()

    # Upload media
    try:
        media_id = media_upload.upload_media(file_path)
    except Exception:
        raise
    finally:
        # Delete the created mp4
        logger.info(f"Removing {file_path}")
        os.remove(file_path)

    # Create the tweet
    create_tweet.post_tweet(media_id)


def get_file() -> str:
    media_location = CONFIG.get("media-location")
    file_name = "anzio.webm"
    file_path = os.path.join(media_location, file_name)
    file_path_new = convert_to_mp4(file_path)
    return file_path_new

def convert_to_mp4(file_path: str) -> str:
    """Converts file from webm to mp4 using ffmpeg

    Args:
        file_path (str): path to file

    Returns:
        str: file path of the mp4
    """
    logger.info("Converting webm to mp4")
    file_path_new = file_path.replace(".webm", ".mp4")

    ffmpeg = CONFIG.get("ffmpeg-location")
    args = "-movflags faststart -c:v libx264 -preset slow -crf 17 -c:a aac -b:a 160k"
    command = f"{ffmpeg} -y -i '{file_path}' {args} '{file_path_new}'"
    logger.info("Running ffmpeg...")
    try:
        ffmpeg_output = CONFIG.get("ffmpeg-output")
        if ffmpeg_output:
            error_pipe = None
        else:
            error_pipe = subprocess.DEVNULL
        subprocess.run(
            shlex.split(command),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=error_pipe
        )
    except subprocess.CalledProcessError:
        logger.error("Error when running ffmpeg")
        sys.exit(1)
    logger.success("Converting webm to mp4 successful!")
    return file_path_new
