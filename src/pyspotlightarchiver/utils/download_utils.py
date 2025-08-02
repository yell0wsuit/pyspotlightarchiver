"""Module for downloading images from API"""

import os
import random
import time
from rich import print as rprint

from pyspotlightarchiver.helpers.download_helper import (
    download_image,
    download_images,
)
from pyspotlightarchiver.helpers.retry_helper import (
    retry_operation,
)
from pyspotlightarchiver.helpers.v3_helper import (
    v3_helper,
)
from pyspotlightarchiver.helpers.v4_helper import (
    v4_helper,
)
from pyspotlightarchiver.helpers.download_db import (
    get_image_url_from_db,
    add_image_url_to_db,
    is_image_filename_valid,
)
from pyspotlightarchiver.helpers.report_duplicates_helper import (
    report_duplicates,
    get_report_path,
)
from pyspotlightarchiver.helpers.imagehash_helper import (
    compute_phash,
)
from pyspotlightarchiver.utils.locale_data import (
    get_locale_codes,
)
from pyspotlightarchiver.utils.exif_utils import (
    set_exif_metadata_exiftool,
)
from pyspotlightarchiver.utils.countdown import (
    inline_countdown,
)

CONSECUTIVE_MAX = 50


def _api_call(api_ver, locale, orientation, verbose=False):
    """Helper to call the API."""
    return (
        v3_helper(False, orientation, locale, verbose=verbose)
        if api_ver == 3
        else v4_helper(False, orientation, locale, verbose=verbose)
    )


def _download_both_orientations(
    entry, api_ver, save_dir=None, embed_exif=True, exiftool_path=None, verbose=False
):
    found = False
    for key in ["image_url_landscape", "image_url_portrait"]:
        url = entry.get(key)
        if url:
            record = get_image_url_from_db(url, save_dir)
            if record:
                filename = record[2]  # 3rd element is filename
                if is_image_filename_valid(filename, save_dir, api_ver):
                    rprint(f"ℹ️ [gray]Image already downloaded:[/gray] {url}")
                    continue
            path = download_image(url, api_ver=api_ver, save_dir=save_dir)
            rprint(
                f"✅ [green]{'Landscape' if key == 'image_url_landscape' else 'Portrait'} image saved to:[/green] {path}"
            )
            filename = os.path.basename(path)
            add_image_url_to_db(url, compute_phash(path), filename, save_dir=save_dir)
            if embed_exif:
                set_exif_metadata_exiftool(
                    path,
                    title=entry.get("title") or entry.get("picture_title"),
                    copyright_text=entry.get("copyright"),
                    caption_title=entry.get("caption_title"),
                    caption_description=entry.get("caption_description"),
                    exiftool_path=exiftool_path,
                    verbose=verbose,
                )
                rprint("✅ [green]EXIF metadata embedded[/green]")
            found = True
    return found


def _download_for_locale(
    api_ver,
    locale,
    orientation,
    verbose,
    save_dir=None,
    embed_exif=True,
    exiftool_path=None,
):
    all_locales = get_locale_codes(api_ver)
    all_locales_lower = [l.lower() for l in all_locales]
    if locale not in all_locales_lower:
        rprint(
            f"❗ [red]Locale '{locale}' is not valid.[/red] Use one of: {', '.join(all_locales)}"
        )
        return False

    real_locale = all_locales[all_locales_lower.index(locale)]
    entries = _api_call(api_ver, real_locale, orientation, verbose)
    entry = random.choice(entries) if entries else None

    if not entry:
        rprint(
            f"ℹ️ [gray]No entries found to download for locale '{real_locale}'.[/gray]"
        )
        return False

    if orientation == "both":
        return _download_both_orientations(
            entry, api_ver, save_dir, embed_exif, exiftool_path
        )
    url = entry.get("image_url")
    if url:
        record = get_image_url_from_db(url, save_dir)
        if record:
            filename = record[2]
            if is_image_filename_valid(filename, save_dir, api_ver):
                rprint(f"ℹ️ [gray]Image already downloaded:[/gray] {url}")
                return True
        path = download_image(url, api_ver=api_ver, save_dir=save_dir)
        rprint(f"✨ [green]New image found:[/green] {url}")
        rprint(f"✅ [green]Image saved to:[/green] {path}")
        filename = os.path.basename(path)
        add_image_url_to_db(url, compute_phash(path), filename, save_dir=save_dir)
        if embed_exif:
            set_exif_metadata_exiftool(
                path,
                title=entry.get("title") or entry.get("picture_title"),
                copyright_text=entry.get("copyright"),
                caption_title=entry.get("caption_title"),
                caption_description=entry.get("caption_description"),
                exiftool_path=exiftool_path,
                verbose=verbose,
            )
            rprint("✅ [green]EXIF metadata embedded[/green]")
        return True
    return False


def _download_for_all_locales(
    api_ver, orientation, verbose=False, save_dir=None, exiftool_path=None
):
    all_locales = get_locale_codes(api_ver)
    locales_shuffled = all_locales[:]
    random.shuffle(locales_shuffled)
    for loc in locales_shuffled:
        if verbose:
            rprint(
                f"ℹ️ [gray]LOG: [download_for_all_locales]Trying locale: {loc}[/gray]"
            )
        if retry_operation(
            api_ver,
            loc,
            orientation,
            verbose,
            operation=download_single,
            save_dir=save_dir,
            exiftool_path=exiftool_path,
        ):
            return True
    if verbose:
        rprint(
            "ℹ️ [gray]LOG: [download_for_all_locales]No valid images found in any locale.[/gray]"
        )
    return False


def download_single(
    api_ver,
    locale,
    orientation,
    verbose=False,
    save_dir=None,
    embed_exif=True,
    exiftool_path=None,
):
    """
    Download a single image (first entry) from the specified API version.
    If locale == "all", randomly pick a locale and keep trying until a valid image is found.
    """
    locale = locale.lower()
    if locale == "all":
        embed_exif = False
        return _download_for_all_locales(
            api_ver,
            orientation,
            verbose=verbose,
            save_dir=save_dir,
            exiftool_path=exiftool_path,
        )
    result = _download_for_locale(
        api_ver, locale, orientation, verbose, save_dir, embed_exif, exiftool_path
    )
    if report_duplicates(save_dir):
        rprint(
            f"⚠️ [yellow]Potential duplicates found.[/yellow] Reports are written to [orange]{get_report_path(save_dir)}[/orange]"
        )
    return result


def _download_multiple_for_locale(
    api_ver,
    locale,
    orientation,
    verbose=False,
    save_dir=None,
    embed_exif=True,
    exiftool_path=None,
):
    """Helper to download all images for a single locale. Returns count."""
    entries = _api_call(api_ver, locale, orientation, verbose)

    if not entries:
        if verbose:
            rprint(
                "ℹ️ [gray]LOG: [download_multiple_for_locale]No entries found to download.[/gray]"
            )
        return 0, 0

    downloaded = 0
    already_downloaded = 0

    for i, entry in enumerate(entries):
        url = entry.get("image_url")
        if url:
            record = get_image_url_from_db(url, save_dir)
            if record:
                filename = record[2]
                if is_image_filename_valid(filename, save_dir, api_ver):
                    rprint(f"ℹ️ [gray]Image already downloaded:[/gray] {url}")
                    already_downloaded += 1
                    continue
        paths = download_images(entry, orientation, api_ver=api_ver, save_dir=save_dir)
        if paths:
            for url, path in paths.items():
                if path:
                    filename = os.path.basename(path)
                    add_image_url_to_db(
                        url, compute_phash(path), filename, save_dir=save_dir
                    )
                    if embed_exif and locale != "all":
                        set_exif_metadata_exiftool(
                            path,
                            title=entry.get("title") or entry.get("picture_title"),
                            copyright_text=entry.get("copyright"),
                            caption_title=entry.get("caption_title"),
                            caption_description=entry.get("caption_description"),
                            exiftool_path=exiftool_path,
                            verbose=verbose,
                        )
                        rprint("✅ [green]EXIF metadata embedded[/green]")
                    if verbose:
                        rprint(
                            f"✅ [green]LOG: [download_multiple_for_locale]Downloaded entry {i+1}:[/green] {url}"
                        )
                    downloaded += 1
    return downloaded, already_downloaded


def download_multiple(
    api_ver,
    locale,
    orientation,
    verbose=False,
    save_dir=None,
    embed_exif=True,
    exiftool_path=None,
):
    """
    Download multiple images (all entries) from the specified API version.
    Returns the number of images downloaded.
    """

    all_locales = get_locale_codes(api_ver)
    locale = locale.lower()

    if locale == "all":
        embed_exif = False
        chunk_size = 15
        total_downloaded = 0
        total_already_downloaded = 0
        for chunk_index, i in enumerate(range(0, len(all_locales), chunk_size)):
            chunk = all_locales[i : i + chunk_size]
            for loc in chunk:
                if verbose:
                    rprint(f"ℹ️ [gray]LOG: [download_multiple]--- {loc} ---[/gray]")
                downloaded, already_downloaded = retry_operation(
                    api_ver,
                    loc,
                    orientation,
                    verbose,
                    operation=_download_multiple_for_locale,
                    save_dir=save_dir,
                    exiftool_path=exiftool_path,
                    embed_exif=embed_exif,
                )
                total_downloaded += downloaded
                total_already_downloaded += already_downloaded
            if i + chunk_size < len(all_locales):
                max_delay = 180  # maximum delay in seconds
                delay = min(5 * (chunk_index + 1), max_delay)
                inline_countdown(delay)

        if report_duplicates(save_dir):
            rprint(
                f"⚠️ [yellow]Potential duplicates found.[/yellow] Reports are written to [orange]{get_report_path(save_dir)}[/orange]"
            )
        return {
            "downloaded": total_downloaded,
            "already_downloaded": total_already_downloaded,
        }

    if locale not in [l.lower() for l in all_locales]:
        rprint(
            f"❗ [red]Locale '{locale}' is not valid.[/red] Use one of: {', '.join(all_locales)}"
        )
        return {"downloaded": 0, "already_downloaded": 0}

    # Use the correctly-cased locale from all_locales
    real_locale = all_locales[[l.lower() for l in all_locales].index(locale)]
    downloaded, already_downloaded = _download_multiple_for_locale(
        api_ver, real_locale, orientation, verbose, save_dir, embed_exif, exiftool_path
    )
    return {"downloaded": downloaded, "already_downloaded": already_downloaded}


def download_multiple_until_exhausted(
    api_ver,
    locale,
    orientation,
    verbose=False,
    save_dir=None,
    embed_exif=True,
    exiftool_path=None,
    max_consecutive=CONSECUTIVE_MAX,
):
    """
    Repeatedly call download_multiple until all images are already downloaded
    for max_consecutive times in a row. Delays between every 10 calls to avoid rate limiting.
    """
    consecutive = 0
    call_count = 0
    delays = [5, 10, 15, 20, 30, 45, 60, 90, 120, 180]  # seconds
    total_downloaded = 0
    total_already_downloaded = 0
    while consecutive < max_consecutive:
        for _ in range(max_consecutive):
            if consecutive >= max_consecutive:
                break
            time.sleep(2)
            status = download_multiple(
                api_ver,
                locale,
                orientation,
                verbose=verbose,
                save_dir=save_dir,
                embed_exif=embed_exif,
                exiftool_path=exiftool_path,
            )
            downloaded = status.get("downloaded", 0)
            already_downloaded = status.get("already_downloaded", 0)
            total_downloaded += downloaded
            total_already_downloaded += already_downloaded
            if downloaded == 0 and already_downloaded > 0:
                consecutive += 1
                rprint(
                    f"😐 [powderblue]Number of consecutive calls with no new downloads:[/powderblue] [orange]{consecutive}/{max_consecutive}[/orange]"
                )
            else:
                consecutive = 0

            call_count += 1

            if call_count % 10 == 0 and consecutive < max_consecutive:
                delay = (
                    delays[min(call_count // 10 - 1, len(delays) - 1)]
                    if call_count // 10 <= len(delays)
                    else 180
                )
                inline_countdown(delay)

    rprint(
        f"[bold magenta]=== Result ===[/bold magenta]\n"
        f"✅ [green]Download finished![/green]\n"
        f"✨ [green]New images downloaded:[/green] [orange]{total_downloaded}[/orange]\n"
        f"🆗 [green]Already downloaded:[/green] [orange]{total_already_downloaded}[/orange]"
    )

    if report_duplicates(save_dir):
        rprint(
            f"⚠️ [yellow]Potential duplicates found.[/yellow] Reports are written to [orange]{get_report_path(save_dir)}[/orange]"
        )
