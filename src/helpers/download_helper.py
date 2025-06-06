"""Module for downloading images from API"""

import os
from requests_cache import CachedSession

CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "cached_response.sqlite")


def strip_content(response):
    """Remove blob content before caching to avoid inflated cache size"""
    response._content = b""  # pylint: disable=protected-access
    response._content_consumed = True  # pylint: disable=protected-access
    return response


session = CachedSession(
    CACHE_FILE,
    backend="sqlite",
    cache_control=True,
    stale_if_error=True,
    filter_fn=strip_content,
)


def get_save_dir(api_ver):
    """
    Returns the appropriate save directory based on API version.
    Ensures the directory exists.
    """
    base_dir = os.path.join(os.getcwd(), "downloaded_spotlight")
    if api_ver == 3:
        save_dir = os.path.join(base_dir, "1080p")
    elif api_ver == 4:
        save_dir = os.path.join(base_dir, "4K")
    else:
        save_dir = base_dir
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def download_image(url, save_path=None, api_ver=None):
    """
    Download an image from the given URL using a cached session.
    If save_path is provided, saves the image to disk and returns the path.
    Otherwise, saves to the appropriate folder based on api_ver.
    Returns the image file path.
    """
    response = session.get(url, timeout=10)
    response.raise_for_status()
    if not save_path:
        # Default save path logic
        save_dir = get_save_dir(api_ver)
        filename = os.path.basename(url.split("?")[0])
        save_path = os.path.join(save_dir, filename)
    else:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(response.content)
    return save_path


def download_images(entry, orientation="landscape", save_dir=None, api_ver=None):
    """
    Download images from a v3/v4 entry dict.
    Supports both single and dual (landscape/portrait) URLs.
    If save_dir is provided, saves images to that directory.
    Otherwise, saves to the appropriate folder based on api_ver.
    Returns a dict with file paths.
    """
    results = {}
    if orientation == "both":
        for key in ["image_url_landscape", "image_url_portrait"]:
            url = entry.get(key)
            if url:
                filename = os.path.basename(url.split("?")[0])
                if save_dir:
                    os.makedirs(save_dir, exist_ok=True)
                    save_path = os.path.join(save_dir, filename)
                else:
                    save_path = None
                results[key] = download_image(url, save_path, api_ver)
    else:
        url = entry.get("image_url")
        if url:
            filename = os.path.basename(url.split("?")[0])
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                save_path = os.path.join(save_dir, filename)
            else:
                save_path = None
            results["image"] = download_image(url, save_path, api_ver)
            print(f"Image saved to: {results['image']}")
    return results
