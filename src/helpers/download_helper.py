"""Module for downloading images from API"""

import os
import requests


def get_save_dir(api_ver, save_dir=None):
    """
    Returns the appropriate save directory based on API version.
    Ensures the directory exists.
    """
    base_dir = (
        save_dir if save_dir else os.path.join(os.getcwd(), "downloaded_spotlight")
    )
    if api_ver == 3:
        save_dir = (
            os.path.join(base_dir, "1080p")
            if save_dir
            else os.path.join(base_dir, "1080p")
        )
    elif api_ver == 4:
        save_dir = (
            os.path.join(base_dir, "4K") if save_dir else os.path.join(base_dir, "4K")
        )
    else:
        save_dir = base_dir
    os.makedirs(save_dir, exist_ok=True)
    return save_dir


def ensure_jpg_extension(filename):
    """Ensure the filename ends with .jpg"""
    if not filename.lower().endswith(".jpg"):
        filename += ".jpg"
    return filename

def download_image(url, save_dir=None, api_ver=None):
    """
    Download an image from the given URL using a cached session.
    If save_path is provided, saves the image to disk and returns the path.
    Otherwise, saves to the appropriate folder based on api_ver.
    Returns the image file path.
    """
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    save_dir = get_save_dir(api_ver, save_dir)
    filename = os.path.basename(url.split("?")[0])
    save_file = os.path.join(save_dir, ensure_jpg_extension(filename))
    with open(save_file, "wb") as f:
        f.write(response.content)
    return save_file


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
                results[url] = download_image(url, save_dir, api_ver)
    else:
        url = entry.get("image_url")
        if url:
            results[url] = download_image(url, save_dir, api_ver)
            print(f"Image saved to: {results[url]}")
    return results
