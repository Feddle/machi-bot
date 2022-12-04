import os
import sqlite3
import json
import re
from pathlib import Path
from loguru import logger

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = os.path.join(PROJECT_ROOT, "config.json")
DB_FILE = os.path.join(PROJECT_ROOT, "database.db")
with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    CONFIG = json.load(file)

def setup():
    """Main database setup function"""
    logger.info("Setting up database...")
    setup_tables()
    logger.info("Scanning media files and populating database...")
    populate()

def setup_tables():
    """Create necessary tables if they don't exist"""
    db_connection = sqlite3.connect(DB_FILE)
    try:
        media_table = db_connection.execute("SELECT name FROM sqlite_master WHERE name = 'media'")
        if media_table.fetchone() is None:
            db_connection.execute("""
                CREATE TABLE media(
                    media_id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    file_path TEXT UNIQUE NOT NULL,
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
                    FOREIGN KEY(media_id) REFERENCES media(media_id)
                )
            """)
    except:
        raise
    finally:
        db_connection.close()


def populate():
    """Iterate over media folder and populate database with filepaths"""
    db_connection = sqlite3.connect(DB_FILE)
    media_location = CONFIG.get("media-location")
    try:
        with db_connection:
            for file in os.listdir(media_location):
                file_path = Path(media_location).joinpath(Path(file)).as_posix()
                title = Path(file_path).stem
                try:
                    db_connection.execute("INSERT INTO media(title, file_path) VALUES (?, ?)", (title, file_path))
                except sqlite3.IntegrityError as err:
                    if err.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE":
                        logger.info(f"Filepath '{file_path}' already in database")
                    else:
                        raise
    except:
        raise
    finally:
        db_connection.close()

def get_media() -> tuple[int, str]:
    """Fetches file from database ordered by oldest timestamp"""
    db_connection = sqlite3.connect(DB_FILE)
    exec = db_connection.execute("""
        SELECT m.media_id, m.file_path
        FROM media m
        LEFT JOIN posts p ON p.media_id = m.media_id
        ORDER BY p.timestamp ASC
        LIMIT 1
    """)
    result = exec.fetchone()
    db_connection.close()
    # TODO: if file is not found on disk delete the database row
    return result

def insert_post(twitter_response: dict, media_id: str):
    """Inserts tweet into posts table"""
    data = twitter_response["data"]
    link = re.search(r"https://t\.co/.+$", data["text"]).group()
    data = (data["text"], media_id, link, data["id"])
    db_connection = sqlite3.connect(DB_FILE)
    with db_connection:
        db_connection.execute("INSERT INTO posts(post_body, media_id, link, tweet_id) VALUES (?, ?, ?, ?)", data)
    db_connection.close()
