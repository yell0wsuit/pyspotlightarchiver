import json
import os
import re
from babel import localedata
from babel.core import Locale

CACHE_FILE = os.path.join(os.path.dirname(__file__), ".cache", "locale_cache.json")


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


def get_locale_codes():
    """Load locale codes from cache if available."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass  # Fallback to regenerate if file is corrupted

    # Generate and cache
    codes = generate_locale_codes()
    # Ensure the .cache directory exists
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(codes, f, indent=4)

    return codes


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
