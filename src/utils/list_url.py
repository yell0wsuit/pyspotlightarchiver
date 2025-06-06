"""Module to list URLs for a given API version, locale, and orientation"""

import time

from helpers.v3_helper import v3_helper  # pylint: disable=import-error
from helpers.v4_helper import v4_helper  # pylint: disable=import-error
from utils.locale_data import get_locale_codes  # pylint: disable=import-error
from helpers.retry_helper import retry_operation  # pylint: disable=import-error


def print_results(results, orientation, verbose=False):
    """Helper to print URLs from results based on orientation"""
    if verbose:
        print(f"Found {len(results)} URLs")
    for entry in results:
        if orientation == "both":
            print(
                entry.get("image_url_landscape"),
                entry.get("image_url_portrait"),
            )
        else:
            print(entry.get("image_url"))


def get_results(api_ver, locale, orientation):
    """Helper to get results from the correct API version"""
    if api_ver == 3:
        return v3_helper(locale=locale, orientation=orientation)
    return v4_helper(locale=locale, orientation=orientation)


def list_url(api_ver, locale, orientation, verbose=False):
    """List URLs for a given API version, locale, and orientation"""
    all_locales = get_locale_codes()
    all_locales_lower = [l.lower() for l in all_locales]
    locale = locale.lower()
    orientation = orientation.lower()

    total_urls = 0

    print("Listing URLs...")

    if locale == "all":
        chunk_size = 15
        for chunk_index, i in enumerate(range(0, len(all_locales), chunk_size)):
            chunk = all_locales[i : i + chunk_size]
            for loc in chunk:
                if verbose:
                    print(f"--- {loc} ---")
                results = retry_operation(
                    api_ver, loc, orientation, operation=get_results
                )
                print_results(results, orientation)

            # Calculate delay: group = chunk_index // 10, delay = 10 * (chunk_index + 1)
            if i + chunk_size < len(all_locales):
                delay = 10 * ((chunk_index + 1) / 2)
                if verbose:
                    print(
                        f"Chunk {chunk_index + 1}. Delaying {delay} seconds to avoid rate limiting..."
                    )
                time.sleep(delay)
    else:
        if locale not in all_locales_lower:
            print(
                f"Locale '{locale}' is not valid. Use one of: {', '.join(all_locales)}"
            )
            return
        # Use the correctly-cased locale from all_locales
        real_locale = all_locales[all_locales_lower.index(locale)]
        results = get_results(api_ver, real_locale, orientation)
        print_results(results, orientation)
        total_urls = len(results)

    print(f"Done. Found {total_urls} URLs.")
