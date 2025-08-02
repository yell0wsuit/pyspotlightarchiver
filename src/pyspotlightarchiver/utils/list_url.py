"""Module to list URLs for a given API version, locale, and orientation"""

from rich import print as rprint

from pyspotlightarchiver.helpers.v3_helper import (
    v3_helper,
)
from pyspotlightarchiver.helpers.v4_helper import (
    v4_helper,
)
from pyspotlightarchiver.helpers.retry_helper import (
    retry_operation,
)
from pyspotlightarchiver.utils.locale_data import (
    get_locale_codes,
)
from pyspotlightarchiver.utils.countdown import (
    inline_countdown,
)


def print_results(results, orientation, verbose=False):
    """Helper to print URLs from results based on orientation"""
    if verbose:
        rprint(f"ℹ️ [gray]LOG: [list_url]Found {len(results)} URLs[/gray]")
    for entry in results:
        if orientation == "both":
            rprint(
                entry.get("image_url_landscape"),
                entry.get("image_url_portrait"),
            )
        else:
            rprint(entry.get("image_url"))
    rprint(f"✅ [green]Found {len(results)} URLs[/green]")


def get_results(api_ver, locale, orientation):
    """Helper to get results from the correct API version"""
    if api_ver == 3:
        return v3_helper(locale=locale, orientation=orientation)
    return v4_helper(locale=locale, orientation=orientation)


def process_all_locales(api_ver, all_locales, orientation, verbose):
    """Process all locales in chunks to avoid rate limiting"""
    chunk_size = 15
    for chunk_index, i in enumerate(range(0, len(all_locales), chunk_size)):
        chunk = all_locales[i : i + chunk_size]
        for loc in chunk:
            if verbose:
                rprint(f"ℹ️ [gray]LOG: [list_url]--- {loc} ---[/gray]")
            results = retry_operation(api_ver, loc, orientation, operation=get_results)
            print_results(results, orientation)

        # Calculate delay: group = chunk_index // 10, delay = 5 * (chunk_index + 1)
        if i + chunk_size < len(all_locales):
            max_delay = 180  # maximum delay in seconds
            delay = min(5 * (chunk_index + 1), max_delay)
            inline_countdown(delay)


def list_url(api_ver, locale, orientation, verbose=False):
    """List URLs for a given API version, locale, and orientation"""
    all_locales = get_locale_codes(api_ver)
    locale = locale.lower()
    orientation = orientation.lower()

    total_urls = 0

    rprint("ℹ️ [gray]Listing URLs...[/gray]")

    if locale == "all":
        process_all_locales(api_ver, all_locales, orientation, verbose)
    else:
        if locale not in [l.lower() for l in all_locales]:
            rprint(
                f"❗ [red]Locale '{locale}' is not valid.[/red] Use one of: {', '.join(all_locales)}"
            )
            return
        # Use the correctly-cased locale from all_locales
        real_locale = all_locales[[l.lower() for l in all_locales].index(locale)]
        results = get_results(api_ver, real_locale, orientation)
        print_results(results, orientation)
        total_urls = len(results)

    rprint(f"✅ [green]Done.[/green] Found {total_urls} URLs.")
