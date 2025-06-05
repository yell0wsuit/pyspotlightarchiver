import json
import requests
import os

from utils.locale_data import get_country_codes, get_language_codes


def parse_v3_data(data, orientation="landscape"):
    results = []
    items = data.get("batchrsp", {}).get("items", [])
    for item in items:
        # Each item['item'] is a JSON string
        nested = json.loads(item["item"])
        ad = nested.get("ad", {})
        entry = {}
        if orientation == "landscape":
            entry["image_url"] = ad.get("image_fullscreen_001_landscape", {}).get("u")
        elif orientation == "portrait":
            entry["image_url"] = ad.get("image_fullscreen_001_portrait", {}).get("u")
        elif orientation == "both":
            entry["image_url_landscape"] = ad.get(
                "image_fullscreen_001_landscape", {}
            ).get("u")
            entry["image_url_portrait"] = ad.get(
                "image_fullscreen_001_portrait", {}
            ).get("u")
        entry["title"] = ad.get("title_text", {}).get("tx")
        entry["copyright"] = ad.get("copyright_text", {}).get("tx")
        results.append(entry)
    return results


def v3_helper(use_local=False, orientation="landscape"):
    country = get_country_codes()
    language = get_language_codes()
    if use_local:
        local_path = os.path.join(os.path.dirname(__file__), "../tests/v3_api.json")
        with open(local_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        url = f"https://fd.api.iris.microsoft.com/v3/Delivery/Placement?&pid=338387&fmt=json&ctry={country}&lc={country}-{language}&ua=WindowsShellClient%2F9.0.40929.0%20%28Windows%29&bcnt=3&cdm=1"
        response = requests.get(url)
        data = response.json()
    return parse_v3_data(data, orientation=orientation)
