"""Helper to report duplicates in the DB."""

import os
from pyspotlightarchiver.helpers.download_db import (  # pylint: disable=import-error
    get_all_images,
)


def get_report_path(save_dir):
    """
    Returns the path for the duplicates report, using the provided save_dir or the default.
    """
    if save_dir:
        return os.path.join(save_dir, "phash_duplicates_report.md")
    return os.path.join(
        os.getcwd(), "downloaded_spotlight", "phash_duplicates_report.md"
    )


def report_duplicates(save_dir):
    """
    Scans the DB for duplicate pHashes and writes a Markdown report.
    Returns True if duplicates found, else False.
    """
    report_path = get_report_path(save_dir)
    images = get_all_images(save_dir)
    phash_map = {}
    for url, phash, path in images:
        if phash not in phash_map:
            phash_map[phash] = []
        phash_map[phash].append((url, path))

    duplicates = {phash: items for phash, items in phash_map.items() if len(items) > 1}

    if not duplicates:
        return False

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Potential duplicates\n\n")
        for idx, (phash, items) in enumerate(duplicates.items()):
            f.write(f"## phash `{phash}`\n\n")
            f.write(f"![phash {phash}]({items[0][0]})\n")
            for url, path in items:
                f.write(f"\n- {url}  \n  Saved to `{path}`\n")
            if idx < len(duplicates) - 1:  # Only add extra newline between groups
                f.write("\n")
    return True
