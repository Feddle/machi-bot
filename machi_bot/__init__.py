"""Initialization for twitter bot"""
import sys
import os
import subprocess
import shlex
import json
import requests
from pathlib import Path
import argparse
from loguru import logger
from . import create_tweet
from . import media_upload
from . import database as machidb

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")
with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    CONFIG = json.load(file)

def main() -> None:
    """Main function"""
    configure_logger()

    parser = argparse.ArgumentParser(prog="machi-bot", description="Twitter bot for posting videos")
    parser.add_argument("-r", "--rebuild", action="store_true",
        help="Rebuilds the media database")
    parser.add_argument("-s", "--scan", action="store_true",
        help="Scans the media library")
    parser.add_argument("-p", "--post", action="store_true",
        help="Posts a tweet. If no text or media is given a random media is chosen")
    parser.add_argument("-t", "--text", type=str, nargs="?", action="store", default="",
        help="Text for the tweet")
    parser.add_argument("-m", "--media", metavar="PATH", type=str, nargs="?", action="store",
        help="Path for post media")
    parser.add_argument("--previous", metavar="COUNT", const=10, nargs="?",
        help="Prints number of previous posts")
    parser.add_argument("-g", "--get", action="store_true",
        help="Fetches a single tweet. For now only for auth testing.")

    args = parser.parse_args()

    if args.rebuild:
        machidb.setup_tables(args.rebuild)
    if args.scan:
        # Do media scan
        machidb.setup_tables(args.rebuild)
    if args.post:
        machidb.setup_tables(args.rebuild)
        # Select media and text and do a post
        create_post(text=args.text, media_path=args.media)
    if args.previous:
        # Print previous posts
        posts = machidb.get_posts(args.previous)
        json_string = json.dumps(posts, indent=4)
        logger.info(f"{json_string}")
    if args.get:
        create_tweet.get_tweet()


def create_post(text: str, media_path: str) -> None:
    """Main function for posting tweets

    Args:
        text (str): Text to tweet
        media_path (str): Media filepath
    """
    # Select file and convert it to mp4
    media = get_file(media_path)
    media_id = media[0]
    file_path = media[1]
    title = media[2]

    # Upload media
    twitter_media_id = media_upload.upload_media(file_path)

    # Create the tweet
    if len(text) == 0: text = title
    response = create_tweet.post_tweet(text, twitter_media_id)

    if response.status_code == 201:
        # Insert post to db
        link = machidb.insert_post(response.json(), media_id)

        if CONFIG.get("discord-webhook-url"):
            post_to_discord(link)

def post_to_discord(content: str) -> None:
    """Post message to discord webhook

    Args:
        content (str): message content
    """
    payload = {"content": content}
    requests.request(
        method="POST",
        url=CONFIG.get("discord-webhook-url"),
        data=payload,
        timeout=10
    )


def get_file(media_path: str) -> tuple[int, str, str]:
    """Fetches media file from database and converts it to mp4

    Args:
        media_path (str): File path

    Returns:
        tuple[int, str, str]: Tuple with database media_id, mp4 file path and media title
    """
    media = machidb.get_media(media_path)
    media_id = media[0]
    file_path = media[1]
    title = media[2]
    logger.info(f"Media fetched: {file_path}")
    file_path_new = convert_to_mp4(file_path)
    return (media_id, file_path_new, title)

def convert_to_mp4(file_path: str) -> str:
    """Converts file from webm to mp4 using ffmpeg

    Args:
        file_path (str): path to file

    Returns:
        str: file path of the mp4
    """
    logger.info("Converting video to mp4")
    new_filename = Path(file_path).stem + ".mp4"
    temp_dir = PROJECT_ROOT.joinpath("video_tmp")
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    file_path_new = temp_dir.joinpath(new_filename).as_posix()

    ffmpeg = CONFIG.get("ffmpeg-location")
    args = "-movflags faststart -c:v libx264 -vf 'pad=ceil(iw/2)*2:ceil(ih/2)*2' -preset slow -crf 17 -c:a aac -b:a 160k"
    command = f"{ffmpeg} -y -i \"{file_path}\" {args} \"{file_path_new}\""
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

    logger.success("Conversion successful!")
    return file_path_new

def configure_logger() -> None:
    """Configures the loguru logger
    """
    time_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>"
    log_format = f"{time_format} | <level>{{level: <8}}</level> - <level>{{message}}</level>"
    config = {
        "handlers": [
            {"sink": sys.stderr, "format": log_format},
        ],
    }
    logger.configure(**config)
