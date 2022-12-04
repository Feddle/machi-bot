"""Initialization for twitter bot"""
import sys
import os
import subprocess
import shlex
import json
from pathlib import Path
from loguru import logger
from . import create_tweet
from . import media_upload
from . import database as machidb

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

    # Setup database
    machidb.setup()

    # Select a random file and convert it to mp4
    media = get_file()
    media_id = media[0]
    file_path = media[1]

    # Upload media
    twitter_media_id = media_upload.upload_media(file_path)

    # Create the tweet
    response = create_tweet.post_tweet(twitter_media_id)

    # Insert post to db
    machidb.insert_post(response, media_id)


def get_file() -> tuple[int, str]:
    media = machidb.get_media()
    media_id = media[0]
    file_path = media[1]
    # TODO: if file is mp4 no need for conversion (propably)
    file_path_new = convert_to_mp4(file_path)
    return (media_id, file_path_new)

def convert_to_mp4(file_path: str) -> str:
    """Converts file from webm to mp4 using ffmpeg

    Args:
        file_path (str): path to file

    Returns:
        str: file path of the mp4
    """
    logger.info("Converting video to mp4")
    new_filename = Path(file_path).stem + ".mp4"
    file_path_new = Path(file_path).parent.joinpath(new_filename).as_posix()

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
        # Delete the created mp4
        if os.path.isfile(file_path_new):
            logger.info(f"Removing {file_path_new}")
            os.remove(file_path_new)
        raise

    logger.success("Converting video to mp4 successful!")
    return file_path_new
