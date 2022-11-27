"""Initialization for twitter bot"""
import sys
import subprocess
import shlex
import json
from loguru import logger
from . import create_tweet
from . import media_upload

with open("machi_bot/config.json", "r", encoding="utf-8") as file:
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
        #os.remove(file_path)

    # Create the tweet
    create_tweet.post_tweet(media_id)


def get_file() -> str:
    root_folder = "./media/"
    file_name = "Congratulations! Your Account Is Now Enabled For Uploads Longer Than 15 Minutes. [K7wyj8cql9i].webm"
    file_path = f"{root_folder}{file_name}"
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
        subprocess.run(
            shlex.split(command),
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        logger.error("Error when running ffmpeg")
        sys.exit(1)
    logger.success("Converting webm to mp4 successful!")
    return file_path_new
