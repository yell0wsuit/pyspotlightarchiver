"""Module to manage the SQLite database for downloaded images."""

import sqlite3
import os
from contextlib import closing
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), ".cache", "downloaded_images.sqlite")


def init_db(db_path=DB_PATH):
    """Initialize the SQLite database and create the table if it doesn't exist."""
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS downloaded_images (
                    url TEXT PRIMARY KEY,
                    phash TEXT,
                    local_path TEXT,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
        conn.commit()


def add_image_url_to_db(url, phash, local_path, db_path=DB_PATH):
    """Add a new image URL record to the database."""
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO downloaded_images (url, phash, local_path, downloaded_at)
                VALUES (?, ?, ?, ?)
            """,
                (url, phash, local_path, datetime.now()),
            )
        conn.commit()


def get_image_url_from_db(url, db_path=DB_PATH):
    """Retrieve an image record by URL."""
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                SELECT url, phash, local_path, downloaded_at
                FROM downloaded_images
                WHERE url = ?
            """,
                (url,),
            )
            return cursor.fetchone()


def get_image_path_from_db(local_path, db_path=DB_PATH):
    """Retrieve an image path by local path."""
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                SELECT local_path
                FROM downloaded_images
                WHERE local_path = ?
                """,
                (local_path,),
            )
            return cursor.fetchone()


def is_image_path_valid(local_path, db_path=DB_PATH):
    """Check if the image path is in the DB and the file exists on disk."""
    record = get_image_path_from_db(local_path, db_path)
    return record is not None and os.path.exists(local_path)
