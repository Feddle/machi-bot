"""Database module"""
import sys
import os
import glob
import sqlite3
import json
import re
from pathlib import Path
from loguru import logger

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")
with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    CONFIG = json.load(file)
APPDATA = Path(CONFIG.get("appdata"))
DB_FILE = os.path.join(APPDATA, "database.db")

def setup_tables(rebuild = False):
    """Create necessary tables if they don't exist"""
    if rebuild:
        logger.info("Rebuilding media database")
    else:
        logger.info("Setting up database")
    db_connection = sqlite3.connect(DB_FILE)
    try:
        media_table = db_connection.execute("SELECT name FROM sqlite_master WHERE name = 'media'")
        table_exists = media_table.fetchone() is not None
        if table_exists and rebuild:
            db_connection.execute("""DROP TABLE media""")
        if not table_exists or rebuild:
            db_connection.execute("""
                CREATE TABLE media(
                    media_id INTEGER PRIMARY KEY,
                    title NVARCHAR NOT NULL,
                    file_path NVARCHAR UNIQUE NOT NULL,
                    added TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

        posts_table = db_connection.execute("SELECT name FROM sqlite_master WHERE name = 'posts'")
        if posts_table.fetchone() is None:
            db_connection.execute("""
                CREATE TABLE posts(
                    post_id INTEGER PRIMARY KEY,
                    post_body TEXT NOT NULL,
                    media_id INTEGER,
                    link TEXT NOT NULL,
                    tweet_id TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(media_id) REFERENCES media(media_id) ON DELETE SET NULL
                )
            """)

        # Populate new db
        scan()
    except:
        raise
    finally:
        db_connection.close()


def scan():
    """Iterate over media folder and populate database with filepaths"""
    logger.info("Scanning media files and populating database")
    db_connection = sqlite3.connect(DB_FILE)
    media_location = Path(CONFIG.get("media-location"))
    try:
        with db_connection:
            for media_file in glob.iglob(media_location.joinpath("**").as_posix(), recursive=True):
                file_path = media_location.joinpath(Path(media_file)).as_posix()
                dir_name = Path(file_path).parent.name
                title = Path(file_path).stem
                if Path(file_path).is_dir(): continue
                if dir_name in CONFIG.get("exclude-folders"): continue
                try:
                    db_connection.execute(
                        "INSERT INTO media(title, file_path) VALUES (?, ?)",
                        (title, file_path)
                    )
                except sqlite3.IntegrityError as err:
                    if err.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
                        pass
                        # TODO: print files being inserted and not already in db
                        # logger.info(f"Filepath '{file_path}' already in database")
                    else:
                        raise
    except:
        raise
    finally:
        db_connection.close()

def get_media(media: str) -> tuple[int, str, str]:
    """Fetches a file from database

    Args:
        media (str): Response from twitter

    Returns:
        tuple[int, str, str]: Tuple with database media_id, file path and media title
    """
    db_connection = sqlite3.connect(DB_FILE)
    if media is not None and len(media) > 0:
        media_result = db_connection.execute(
            """
            SELECT media_id, file_path, title
            FROM media
            WHERE file_path = ?
            """,
            (Path(media).as_posix(),)
        ).fetchone()
        if media_result is None:
            logger.error(f"No media found with path '{media}'")
            sys.exit(1)
    else:
        # Fetch random media that hasn't been posted
        media_result = db_connection.execute(
            """
            SELECT m.media_id, m.file_path, m.title
            FROM media m
            LEFT JOIN posts p ON p.media_id = m.media_id
            WHERE p.post_id IS NULL
            ORDER BY RANDOM()
            LIMIT 1
            """
        ).fetchone()
        # If all media has been posted, pick the first timestamped post
        if media_result is None:
            media_result = db_connection.execute(
                """
                SELECT m.media_id, m.file_path, m.title
                FROM media m
                LEFT JOIN posts p ON p.media_id = m.media_id
                ORDER BY p.timestamp ASC
                LIMIT 1
                """
            ).fetchone()
        # If still no media found print an error
        if media_result is None:
            logger.error("No media found. Try scanning the library first.")
            sys.exit(1)

    # If file is not on disk
    if not os.path.exists(media_result[1]):
        logger.error(f"Media found in database but not on disk ({media_result[1]}). Removing db entry.")
        db_connection.execute(
            """DELETE FROM media WHERE media_id = ?""",
            (media_result[0],)
        )
        db_connection.commit()
        sys.exit(1)

    db_connection.close()
    return media_result

def insert_post(twitter_response: dict, media_id: str) -> str:
    """Inserts tweet into posts table

    Args:
        twitter_response (dict): Response from twitter
        media_id (str): database media_id

    Returns:
        str: tweet link
    """
    data = twitter_response["data"]
    link = re.search(r"https://t\.co/.+$", data["text"]).group()
    data = (data["text"], media_id, link, data["id"])
    db_connection = sqlite3.connect(DB_FILE)
    with db_connection:
        db_connection.execute(
            "INSERT INTO posts(post_body, media_id, link, tweet_id) VALUES (?, ?, ?, ?)",
            data
        )
    db_connection.close()
    return link


def get_posts(max_posts: int):
    """Fetches previous posts from database"""
    db_connection = sqlite3.connect(DB_FILE)
    posts_result = db_connection.execute(
        """
        SELECT post_id, post_body, media_id, link, tweet_id, timestamp
        FROM posts
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (max_posts,)
    )
    result = posts_result.fetchall()
    db_connection.close()
    return result
