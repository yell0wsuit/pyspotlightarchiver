"""Module for parsing v4 API data"""

import json
import os
import requests


def parse_v4_data(data, orientation="landscape", verbose=False):
    """Code block to parse v4 API data"""
    results = []
    items = data.get("batchrsp", {}).get("items", [])
    for i, item in enumerate(items):
        # Each item['item'] is a JSON string
        nested = json.loads(item["item"])
        ad = nested.get("ad", {})
        entry = {}
        if orientation == "landscape":
            entry["image_url"] = ad.get("landscapeImage", {}).get("asset")
        elif orientation == "portrait":
            entry["image_url"] = ad.get("portraitImage", {}).get("asset")
        elif orientation == "both":
            entry["image_url_landscape"] = ad.get("landscapeImage", {}).get("asset")
            entry["image_url_portrait"] = ad.get("portraitImage", {}).get("asset")
        # iconHoverText: text before first \r\n
        icon_hover = ad.get("iconHoverText", "")
        entry["picture_title"] = (
            icon_hover.split("\r\n")[0] if "\r\n" in icon_hover else icon_hover
        )
        entry["copyright"] = ad.get("copyright")
        entry["caption_title"] = ad.get("title")
        entry["caption_description"] = ad.get("description")
        results.append(entry)
        if verbose:
            print(f"Picture metadata {i+1}: {entry}")
    return results


def v4_helper(use_local=False, orientation="landscape", locale="en-us", verbose=False):
    """Code block to get and return v4 API data"""
    _, country = locale.split("-")
    if use_local:
        local_path = os.path.join(os.path.dirname(__file__), "../tests/v4_api.json")
        with open(local_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        url = (
            f"https://fd.api.iris.microsoft.com/v4/api/selection?"
            f"&placement=88000820"
            f"&bcnt=4"
            f"&country={country}"
            f"&locale={locale}"
            f"&fmt=json"
        )
        response = requests.get(url, timeout=10)
        data = response.json()
    return parse_v4_data(data, orientation=orientation, verbose=verbose)
