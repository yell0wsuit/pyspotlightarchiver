"""Module to manage the SQLite database for downloaded images."""

import sqlite3
import os
from contextlib import closing
from datetime import datetime
from pyspotlightarchiver.helpers.download_helper import get_save_dir  # pylint: disable=import-error

DB_FILENAME = "downloaded_images.sqlite"


def get_db_path(save_dir=None):
    """
    Returns the path to the database file, using the provided save_dir or the default.
    """
    if save_dir:
        cache_dir = os.path.join(save_dir, ".cache")
    else:
        cache_dir = os.path.join(os.getcwd(), "downloaded_spotlight", ".cache")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, DB_FILENAME)


def init_db(save_dir):
    """Initialize the SQLite database and create the table if it doesn't exist."""
    db_path = get_db_path(save_dir)
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS downloaded_images (
                    url TEXT PRIMARY KEY,
                    phash TEXT,
                    filename TEXT,
                    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
        conn.commit()


def add_image_url_to_db(url, phash, filename, save_dir):
    """Add a new image URL record to the database."""
    db_path = get_db_path(save_dir)
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                INSERT OR REPLACE INTO downloaded_images (url, phash, filename, downloaded_at)
                VALUES (?, ?, ?, ?)
            """,
                (url, phash, filename, datetime.now()),
            )
        conn.commit()


def get_image_url_from_db(url, save_dir):
    """Retrieve an image record by URL."""
    db_path = get_db_path(save_dir)
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                SELECT url, phash, filename, downloaded_at
                FROM downloaded_images
                WHERE url = ?
            """,
                (url,),
            )
            return cursor.fetchone()


def get_image_filename_from_db(filename, save_dir):
    """Retrieve an image by filename."""
    db_path = get_db_path(save_dir)
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                SELECT filename
                FROM downloaded_images
                WHERE filename = ?
                """,
                (filename,),
            )
            return cursor.fetchone()


def is_image_filename_valid(filename, save_dir, api_ver=None):
    """Check if the image filename is in the DB and the file exists on disk."""
    record = get_image_filename_from_db(filename, save_dir)

    full_path = os.path.join(get_save_dir(api_ver, save_dir), filename)
    return record is not None and os.path.exists(full_path)


def get_all_images(save_dir):
    """
    Returns a list of (url, phash, filename) for all images in the DB.
    """
    db_path = get_db_path(save_dir)
    with sqlite3.connect(db_path) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute(
                """
                SELECT url, phash, filename
                FROM downloaded_images
                """
            )
            return cursor.fetchall()
