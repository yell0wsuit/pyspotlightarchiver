"""Module for getting locale data"""

import json
import os
import re
from babel import localedata
from babel.core import Locale
from pyspotlightarchiver.utils.exclude_locale import is_excluded


def generate_locale_codes():
    """Generate all valid xx-XX locale codes."""
    pattern = re.compile(r"^[a-z]{2}-[A-Z]{2}$")
    locale_codes = set()

    for loc in localedata.locale_identifiers():
        try:
            locale = Locale.parse(loc)
            if locale.language and locale.territory:
                code = f"{locale.language}-{locale.territory}"
                if pattern.match(code):
                    locale_codes.add(code)
        except Exception:
            continue

    return sorted(locale_codes)


def get_cache_file(api_ver):
    """Get the cache file for a given API version."""
    return os.path.join(os.getcwd(), ".cache", f"locale_cache_{api_ver}.json")


def get_locale_codes(api_ver=3):
    """Load locale codes from cache if available."""
    cache_file = get_cache_file(api_ver)
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass  # Fallback to regenerate if file is corrupted

    # Generate and cache
    codes = generate_locale_codes()
    clean_codes = [code for code in codes if not is_excluded(code, version=api_ver)]
    # Ensure the .cache directory exists
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(clean_codes, f, indent=4)

    return clean_codes


def get_language_codes():
    """
    Returns a sorted list of 2-letter language codes used in valid xx-XX locales.
    """
    codes = get_locale_codes()
    languages = {code.split("-")[0] for code in codes}
    return sorted(languages)


def get_country_codes():
    """
    Returns a sorted list of 2-letter country codes used in valid xx-XX locales.
    """
    codes = get_locale_codes()
    countries = {code.split("-")[1] for code in codes}
    return sorted(countries)
