"""Module to list URLs for a given API version, locale, and orientation"""

import time

from helpers.v3_helper import v3_helper # pylint: disable=import-error
from helpers.v4_helper import v4_helper # pylint: disable=import-error
from utils.locale_data import get_locale_codes # pylint: disable=import-error


def list_url(api_ver, locale, orientation):
    """List URLs for a given API version, locale, and orientation"""
    all_locales = get_locale_codes()
    all_locales_lower = [l.lower() for l in all_locales]
    locale = locale.lower()
    orientation = orientation.lower()

    if locale == "all":
        chunk_size = 10
        for i in range(0, len(all_locales), chunk_size):
            chunk = all_locales[i : i + chunk_size]
            for loc in chunk:
                print(f"--- {loc} ---")
                if api_ver == 3:
                    results = v3_helper(locale=loc, orientation=orientation)
                else:
                    results = v4_helper(locale=loc, orientation=orientation)
                print(f"Found {len(results)} URLs")
                for entry in results:
                    if orientation == "both":
                        print(
                            entry.get("image_url_landscape"),
                            entry.get("image_url_portrait"),
                        )
                    else:
                        print(entry.get("image_url"))
            if i + chunk_size < len(all_locales):
                print("Sleeping 10 seconds to avoid rate limiting...")
                time.sleep(10)
    else:
        if locale not in all_locales_lower:
            print(
                f"Locale '{locale}' is not valid. Use one of: {', '.join(all_locales)}"
            )
            return
        # Use the correctly-cased locale from all_locales
        real_locale = all_locales[all_locales_lower.index(locale)]
        if api_ver == 3:
            results = v3_helper(locale=real_locale, orientation=orientation)
        else:
            results = v4_helper(locale=real_locale, orientation=orientation)
        print(f"Found {len(results)} URLs")
        for entry in results:
            if orientation == "both":
                print(entry.get("image_url_landscape"), entry.get("image_url_portrait"))
            else:
                print(entry.get("image_url"))
