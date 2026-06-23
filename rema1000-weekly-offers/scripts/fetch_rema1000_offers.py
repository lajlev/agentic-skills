#!/usr/bin/env python3
"""Fetch the REMA 1000 weekly offers from etilbudsavis.dk (Tjek API)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_BASE = "https://squid-api.tjek.com/v2"
USER_AGENT = "Mozilla/5.0"
DEFAULT_TIMEOUT = 45


def now_copenhagen() -> dt.datetime:
    from zoneinfo import ZoneInfo

    return dt.datetime.now(ZoneInfo("Europe/Copenhagen"))


def parse_run_datetime(value: str) -> dt.datetime:
    return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")


def http_get_json(url: str) -> Any:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def get_rema_dealer_id(country: str) -> str:
    query = urlencode({"query": "REMA 1000", "country": country, "limit": 10})
    url = f"{API_BASE}/dealers?{query}"
    payload = http_get_json(url)
    if not isinstance(payload, list) or not payload:
        raise RuntimeError("Could not find REMA 1000 dealer in Tjek API.")

    for item in payload:
        if isinstance(item, dict) and str(item.get("name", "")).strip().upper() == "REMA 1000":
            dealer_id = str(item.get("id", "")).strip()
            if dealer_id:
                return dealer_id

    first = payload[0] if isinstance(payload[0], dict) else {}
    dealer_id = str(first.get("id", "")).strip()
    if not dealer_id:
        raise RuntimeError("Dealer search returned no usable dealer id for REMA 1000.")
    return dealer_id


def is_weekly_catalog(catalog: dict[str, Any]) -> bool:
    label = str(catalog.get("label", "")).strip()
    return bool(re.fullmatch(r"Uge\s+\d{1,2}", label, flags=re.IGNORECASE))


def extract_week_number(catalog: dict[str, Any], fallback_dt: dt.datetime) -> int:
    label = str(catalog.get("label", ""))
    match = re.search(r"(\d{1,2})", label)
    if match:
        week = int(match.group(1))
        if 1 <= week <= 53:
            return week
    return int(fallback_dt.isocalendar().week)


def choose_catalog(
    catalogs: list[dict[str, Any]], reference: dt.datetime, forced_catalog_id: str | None
) -> dict[str, Any]:
    if forced_catalog_id:
        for catalog in catalogs:
            if str(catalog.get("id")) == forced_catalog_id:
                return catalog
        raise RuntimeError(f"Forced catalog id not found in REMA 1000 catalog list: {forced_catalog_id}")

    weekly = [c for c in catalogs if is_weekly_catalog(c)]
    if not weekly:
        raise RuntimeError("No weekly REMA 1000 catalog (label matching 'Uge NN') was found.")

    active: list[dict[str, Any]] = []
    for catalog in weekly:
        run_from = parse_run_datetime(str(catalog["run_from"]))
        run_till = parse_run_datetime(str(catalog["run_till"]))
        if run_from <= reference.astimezone(run_from.tzinfo) <= run_till:
            active.append(catalog)

    if active:
        return sorted(active, key=lambda c: parse_run_datetime(str(c["run_from"])), reverse=True)[0]

    future = [c for c in weekly if parse_run_datetime(str(c["run_from"])) > reference]
    if future:
        return sorted(future, key=lambda c: parse_run_datetime(str(c["run_from"])))[0]

    return sorted(weekly, key=lambda c: parse_run_datetime(str(c["run_from"])), reverse=True)[0]


def first_page_from_locations(locations: Any) -> int | None:
    if not isinstance(locations, dict):
        return None
    page_numbers: list[int] = []
    for key in locations.keys():
        try:
            page_numbers.append(int(key))
        except Exception:
            continue
    return min(page_numbers) if page_numbers else None


def format_price(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def infer_category(heading: Any, description: Any) -> str:
    text = f"{normalize_text(heading)} {normalize_text(description)}"

    # Handle specific phrases before broad keyword matching.
    if any(k in text for k in ("hønsesalat", "tunsalat", "makrelsalat", "frugtsalat")):
        return "Ready Meals & Convenience"

    category_rules: list[tuple[str, tuple[str, ...]]] = [
        (
            "Fresh Produce",
            (
                "frugt",
                "grønt",
                "grøntsag",
                "banan",
                "æble",
                "pære",
                "appelsin",
                "citron",
                "lime",
                "tomat",
                "agurk",
                "salat",
                "kartoffel",
                "løg",
                "peberfrugt",
                "gulerod",
                "broccoli",
                "avocado",
                "bær",
            ),
        ),
        (
            "Meat & Poultry",
            (
                "kylling",
                "okse",
                "svin",
                "gris",
                "kalv",
                "hakket",
                "bacon",
                "spegepølse",
                "skinke",
                "mørbrad",
                "kød",
            ),
        ),
        (
            "Fish & Seafood",
            (
                "fisk",
                "laks",
                "tun",
                "makrel",
                "reje",
                "torsk",
                "sild",
                "skaldyr",
            ),
        ),
        (
            "Dairy & Eggs",
            (
                "mælk",
                "yoghurt",
                "ost",
                "smør",
                "fløde",
                "æg",
                "skyr",
                "creme fraiche",
                "danette",
                "caffèlatte",
                "cappuccino",
            ),
        ),
        (
            "Bread, Bakery & Breakfast",
            (
                "brød",
                "rugbrød",
                "bolle",
                "croissant",
                "kage",
                "wienerbrød",
                "morgenmad",
                "havregryn",
                "müsli",
                "cornflakes",
                "morgenbolle",
                "tærtedej",
                "pizzadej",
            ),
        ),
        (
            "Ready Meals & Convenience",
            (
                "ready to serve",
                "færdigret",
                "pizza",
                "salatbar",
                "take away",
                "to go",
                "hønsesalat",
                "tun salat",
                "makrelsalat",
                "frugtsalat",
            ),
        ),
        (
            "Pantry Staples",
            (
                "pasta",
                "ris",
                "mel",
                "sukker",
                "salt",
                "olie",
                "eddike",
                "konserves",
                "tomatpuré",
                "krydderi",
                "sauce",
                "dressing",
                "leverpostej",
            ),
        ),
        (
            "Frozen Foods",
            (
                "frost",
                "dybfrost",
                "frossen",
                "is",
                "fryse",
            ),
        ),
        (
            "Snacks & Sweets",
            (
                "slik",
                "chokolade",
                "chips",
                "kiks",
                "karamel",
                "bolsje",
                "haribo",
                "ga-jol",
                "spunk",
                "mariehøner",
                "müslibar",
            ),
        ),
        (
            "Beverages",
            (
                "juice",
                "sodavand",
                "vand",
                "øl",
                "vin",
                "kaffe",
                "te",
                "drik",
                "saft",
                "energidrik",
            ),
        ),
        (
            "Baby & Kids Food",
            (
                "baby",
                "børn",
                "kids",
                "grød",
                "modermælk",
                "danonino",
            ),
        ),
        (
            "Health, Personal Care & Pharmacy",
            (
                "vitamin",
                "kosttilskud",
                "shampoo",
                "deodorant",
                "tandpasta",
                "creme",
                "smertestillende",
                "plaster",
                "håndsprit",
                "personlig pleje",
            ),
        ),
        (
            "Household & Cleaning",
            (
                "opvask",
                "rengøring",
                "vaskemiddel",
                "toiletpapir",
                "køkkenrulle",
                "affaldspose",
                "husholdning",
                "sæbe",
            ),
        ),
        (
            "Pet Food & Pet Care",
            (
                "hund",
                "kat",
                "kæledyr",
                "pet",
                "dyrefoder",
                "kattemad",
                "hundemad",
            ),
        ),
    ]

    for category, keywords in category_rules:
        if any(keyword in text for keyword in keywords):
            return category
    return "Seasonal & Special Campaign Items"


def extract_offers_from_hotspots(hotspots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    offers_by_id: dict[str, dict[str, Any]] = {}
    for item in hotspots:
        if not isinstance(item, dict):
            continue
        offer = item.get("offer")
        if not isinstance(offer, dict):
            continue
        offer_id = str(offer.get("id", "")).strip()
        if not offer_id:
            continue
        pricing = offer.get("pricing", {}) if isinstance(offer.get("pricing"), dict) else {}
        quantity = offer.get("quantity", {}) if isinstance(offer.get("quantity"), dict) else {}

        heading = offer.get("heading")
        description = offer.get("description")
        offers_by_id[offer_id] = {
            "id": offer_id,
            "page": first_page_from_locations(item.get("locations")),
            "heading": heading,
            "description": description,
            "price": format_price(pricing.get("price")),
            "prePrice": format_price(pricing.get("pre_price")),
            "currency": pricing.get("currency"),
            "category": infer_category(heading, description),
            "quantity": quantity,
            "run_from": offer.get("run_from"),
            "run_till": offer.get("run_till"),
            "publish": offer.get("publish"),
            "catalog_id": offer.get("catalog_id"),
            "dealer_id": offer.get("dealer_id"),
            "images": offer.get("images"),
        }

    results = list(offers_by_id.values())
    results.sort(key=lambda x: ((x.get("page") is None), x.get("page") or 0, str(x.get("heading", "")).lower()))
    return results


def run(output_dir: Path, country: str, forced_catalog_id: str | None, ref_date: str | None) -> Path:
    if ref_date:
        from zoneinfo import ZoneInfo

        naive = dt.datetime.strptime(ref_date, "%Y-%m-%d")
        reference = naive.replace(tzinfo=ZoneInfo("Europe/Copenhagen"))
    else:
        reference = now_copenhagen()

    dealer_id = get_rema_dealer_id(country)
    catalogs_url = f"{API_BASE}/catalogs?{urlencode({'dealer_id': dealer_id, 'limit': 50})}"
    catalogs_raw = http_get_json(catalogs_url)
    if not isinstance(catalogs_raw, list):
        raise RuntimeError("Unexpected catalogs response from Tjek API.")
    catalogs = [item for item in catalogs_raw if isinstance(item, dict)]
    catalog = choose_catalog(catalogs, reference, forced_catalog_id)

    catalog_id = str(catalog.get("id", "")).strip()
    if not catalog_id:
        raise RuntimeError("Selected catalog does not contain an id.")

    hotspots = http_get_json(f"{API_BASE}/catalogs/{catalog_id}/hotspots")
    if not isinstance(hotspots, list):
        raise RuntimeError("Unexpected hotspots response from Tjek API.")
    offers = extract_offers_from_hotspots([h for h in hotspots if isinstance(h, dict)])

    run_from = parse_run_datetime(str(catalog["run_from"]))
    week_number = extract_week_number(catalog, run_from)
    iso_year = int(run_from.isocalendar().year)

    payload = {
        "source": "https://etilbudsavis.dk/REMA-1000",
        "apiBase": API_BASE,
        "retrievedAt": now_copenhagen().isoformat(),
        "referenceDate": reference.date().isoformat(),
        "year": iso_year,
        "weekNumber": week_number,
        "catalog": {
            "id": catalog_id,
            "label": catalog.get("label"),
            "run_from": catalog.get("run_from"),
            "run_till": catalog.get("run_till"),
            "publish": catalog.get("publish"),
            "page_count": catalog.get("page_count"),
            "offer_count": catalog.get("offer_count"),
            "dealer_id": catalog.get("dealer_id"),
            "publicationUrl": f"https://etilbudsavis.dk/REMA-1000/?publication={catalog_id}",
            "pdf_url": catalog.get("pdf_url"),
        },
        "offerCount": len(offers),
        "offers": offers,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"rema1000_{iso_year}_week-{week_number}.json"
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch REMA 1000 weekly offers from eTilbudsavis/Tjek API.")
    parser.add_argument("--output-dir", default="/workspace/offers/rema1000")
    parser.add_argument("--country", default="dk", help="Country code for dealer search (default: dk)")
    parser.add_argument("--catalog-id", default=None, help="Optional explicit catalog/publication id")
    parser.add_argument("--date", default=None, help="Reference date in YYYY-MM-DD (Copenhagen timezone)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        output = run(
            output_dir=Path(args.output_dir),
            country=str(args.country).lower(),
            forced_catalog_id=args.catalog_id,
            ref_date=args.date,
        )
    except Exception as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote offers JSON: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
