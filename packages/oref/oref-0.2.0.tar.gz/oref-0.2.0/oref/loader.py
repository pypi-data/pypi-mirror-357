from typing import List, Literal
import requests
import logging

from .types import Alert, AlertTranslation, Guideline, Location
from .config import ALERT_TRANSLATIONS_URL, LOCATIONS_URL, GUIDELINES_URL

_locations: List[Location] = []
_guidelines: List[Guideline] = []
_alert_translations: List[AlertTranslation] = []


def _fetch_locations(lang):
    logger = logging.getLogger(__name__)

    url = f"{LOCATIONS_URL}{lang}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error("[!] Error fetching locations.")
        raise requests.HTTPError(response)


def _fetch_guidelines(lang):
    logger = logging.getLogger(__name__)

    url = GUIDELINES_URL.replace("##", lang)
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error("[!] Error fetching guidelines.")
        raise requests.HTTPError(response)


def _fetch_alert_translations():
    logger = logging.getLogger(__name__)

    response = requests.get(ALERT_TRANSLATIONS_URL)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error("[!] Error fetching alert categories.")
        raise requests.HTTPError(response)


def init(extra_languages: List[Literal["ar", "he", "ru"]] = []):
    """Initializes locations and guidelines.

    Args:
        extra_languages (List[Literal[&quot;ar&quot;, &quot;he&quot;, &quot;ru&quot;]], optional): _description_. Defaults to [].
    """
    logger = logging.getLogger(__name__)

    suppported_langs = ["en", "he", "ar", "ru"]

    logger.info("[i] Initializing...")
    languages = ["en"]
    languages.extend(extra_languages)

    fetched_alert_translations = _fetch_alert_translations()
    fetched_locations = []
    fetched_guidelines = []

    for lang in list(set(languages)):
        loc_result = _fetch_locations(lang)
        guide_result = _fetch_guidelines(lang)

        for i in guide_result["notes"]:
            if any(j.get("code") == i.get("code") for j in fetched_guidelines):
                for idx, j in enumerate(fetched_guidelines):
                    if j.get("code") == i.get("code"):
                        fetched_guidelines[idx][f"label_{lang}"] = i.get(
                            "areaname")
                        break
            else:
                fetched_guide = {**i}

                fetched_guide[f"label_he"] = fetched_guide.pop("heb_name")
                fetched_guide[f"label_{lang}"] = fetched_guide.pop("area_name")

                fetched_guidelines.append(fetched_guide)

        for i in loc_result:
            if any(j.get("id") == i.get("id") for j in fetched_locations):
                for idx, j in enumerate(fetched_locations):
                    if j.get("id") == i.get("id"):
                        fetched_locations[idx][f"label_{lang}"] = i.get(
                            "label")
                        fetched_locations[idx][f"areaname_{lang}"] = i.get(
                            "areaname")
                        break
            else:
                fetched_loc = {**i}

                fetched_loc[f"label_{lang}"] = fetched_loc.pop("label")
                fetched_loc[f"areaname_{lang}"] = fetched_loc.pop("areaname")

                fetched_locations.append(fetched_loc)

    processed_alert_translations = [
        AlertTranslation(
            heb=item["heb"],
            eng=item["eng"],
            rus=item["rus"],
            arb=item["arb"],
            cat_id=item["catId"],
            matrix_cat_id=item["matrixCatId"],
            heb_title=item.get("hebTitle"),
            eng_title=item.get("engTitle"),
            rus_title=item.get("rusTitle"),
            arb_title=item.get("arbTitle"),
            update_type=item["updateType"]
        )
        for item in fetched_alert_translations
    ]

    processed_locations: List[Location] = []
    for loc in fetched_locations:
        name = {lang: loc.get(f"label_{lang}") for lang in suppported_langs}
        region = {lang: loc.get(f"areaname_{lang}")
                  for lang in suppported_langs}

        for lang in suppported_langs:
            loc.pop(f"label_{lang}", None)
            loc.pop(f"areaname_{lang}", None)

        new_location = Location(**{
            **loc,
            "name": name,
            "region": region,
            "area_id": loc["areaid"],
            "shelter_time": loc["migun_time"]
        })

        processed_locations.append(new_location)

    processed_guidelines: List[Guideline] = []
    for guide in fetched_guidelines:
        label = {lang: guide.get(f"label_{lang}") for lang in suppported_langs}
        new_guideline = Guideline(
            **{**guide, "label": label, "color_code": guide.get("colorCode", "")})
        processed_guidelines.append(new_guideline)

    global _locations, _guidelines, _alert_translations
    _locations = processed_locations
    _guidelines = processed_guidelines
    _alert_translations = processed_alert_translations


def validate_location(loc: int | str):
    if not _locations:
        raise RuntimeError("You must initialize")
    assert not (
        any(l.id == int(loc) for l in _locations if str(l.id).isdigit())
        or any(l.name.en == str(loc) for l in _locations)
        or any(l.name.he == str(loc) for l in _locations)
        or any(l.name.ar == str(loc) for l in _locations)
        or any(l.name.ru == str(loc) for l in _locations)
    )


def alert_translations():
    return _alert_translations


def locations():
    return _locations


def guidelines():
    return _guidelines


def location(loc: int | str):
    for location in _locations:
        if (
            loc == location.id
            or loc == location.name.en
            or loc == location.name.he
            or loc == location.name.ar
            or loc == location.name.ru
        ):
            return location

    return False


def translate(alert: Alert, lang: Literal["en", "he", "ar", "ru"]):
    for i in _alert_translations:
        if alert.title in i.all_titles or alert.title in i.all_descs or alert.description in i.all_titles or alert.description in i.all_descs:
            return i[f"{lang}_title"], i[lang]

    return alert.title, alert.description
