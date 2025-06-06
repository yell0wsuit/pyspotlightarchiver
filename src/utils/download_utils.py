"""Module for downloading images from API"""

import random
import time

from helpers.download_helper import (  # pylint: disable=import-error
    download_image,
    download_images,
)
from helpers.retry_helper import retry_operation  # pylint: disable=import-error
from helpers.v3_helper import v3_helper  # pylint: disable=import-error
from helpers.v4_helper import v4_helper  # pylint: disable=import-error
from utils.locale_data import get_locale_codes  # pylint: disable=import-error


def _api_call(api_ver, locale, orientation):
    """Helper to call the API."""
    return (
        v3_helper(False, orientation, locale)
        if api_ver == 3
        else v4_helper(False, orientation, locale)
    )


def _download_both_orientations(entry, api_ver):
    found = False
    for key in ["image_url_landscape", "image_url_portrait"]:
        url = entry.get(key)
        if url:
            path = download_image(url, api_ver=api_ver)
            print(
                f"{'Landscape' if key == 'image_url_landscape' else 'Portrait'} image saved to: {path}"
            )
            found = True
    return found


def download_single(api_ver, locale, orientation, verbose=False):
    """
    Download a single image (first entry) from the specified API version.
    If locale == "all", randomly pick a locale and keep trying until a valid image is found.
    """
    all_locales = get_locale_codes()
    all_locales_lower = [l.lower() for l in all_locales]
    locale = locale.lower()

    if locale == "all":
        locales_shuffled = all_locales[:]
        random.shuffle(locales_shuffled)
        for loc in locales_shuffled:
            if verbose:
                print(f"Trying locale: {loc}")
            result = retry_operation(
                api_ver, loc, orientation, verbose, operation=download_single
            )
            if result:  # If a download succeeded, stop
                return True
        if verbose:
            print("No valid images found in any locale.")
        return False

    if locale not in all_locales_lower:
        print(f"Locale '{locale}' is not valid. Use one of: {', '.join(all_locales)}")
        return False

    # Use the correctly-cased locale from all_locales
    real_locale = all_locales[all_locales_lower.index(locale)]

    entries = _api_call(api_ver, real_locale, orientation)

    entry = (
        random.choice(entries) if entries else None
    )  # Random pick one of the entries

    if entry:
        if orientation == "both":
            found = _download_both_orientations(entry, api_ver)
            return found
        url = entry.get("image_url")
        if url:
            path = download_image(url, api_ver=api_ver)
            print(f"Image saved to: {path}")
            return True
    else:
        print(f"No entries found to download for locale '{real_locale}'.")
        return False


def _download_multiple_for_locale(api_ver, locale, orientation, verbose):
    """Helper to download all images for a single locale. Returns count."""
    entries = _api_call(api_ver, locale, orientation)

    if not entries:
        if verbose:
            print("No entries found to download.")
        return 0

    for i, entry in enumerate(entries):
        paths = download_images(entry, orientation, api_ver=api_ver)
        if verbose:
            print(f"Downloaded entry {i+1}: {paths}")
    return len(entries)


def download_multiple(api_ver, locale, orientation, verbose=False):
    """
    Download multiple images (all entries) from the specified API version.
    Returns the number of images downloaded.
    """
    all_locales = get_locale_codes()
    all_locales_lower = [l.lower() for l in all_locales]
    locale = locale.lower()

    if locale == "all":
        chunk_size = 15
        total_downloaded = 0
        for chunk_index, i in enumerate(range(0, len(all_locales), chunk_size)):
            chunk = all_locales[i : i + chunk_size]
            for loc in chunk:
                if verbose:
                    print(f"--- {loc} ---")
                total_downloaded += retry_operation(
                    api_ver,
                    loc,
                    orientation,
                    verbose,
                    operation=_download_multiple_for_locale,
                )
            if i + chunk_size < len(all_locales):
                delay = 10 * (chunk_index + 1)
                if verbose:
                    print(
                        f"Chunk {chunk_index + 1}. Delaying {delay} seconds to avoid rate limiting..."
                    )
                time.sleep(delay)
        return total_downloaded

    if locale not in all_locales_lower:
        print(f"Locale '{locale}' is not valid. Use one of: {', '.join(all_locales)}")
        return 0

    # Use the correctly-cased locale from all_locales
    real_locale = all_locales[all_locales_lower.index(locale)]
    return _download_multiple_for_locale(api_ver, real_locale, orientation, verbose)
