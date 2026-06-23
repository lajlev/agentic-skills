#!/usr/bin/env python3
"""Find recipes by ingredient terms in Firestore database 'recipes'."""

import argparse
import json
import os
import re
import sys
import unicodedata
from typing import Any

try:
    from google.cloud import firestore
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Missing Python dependency in runtime environment. "
        "Run via /workspace/scripts/venv_run.sh so dependencies are auto-managed."
    ) from exc
from google.oauth2 import service_account


STOPWORDS = {
    "find",
    "opskrift",
    "opskrifter",
    "der",
    "bruger",
    "med",
    "og",
    "samt",
    "eller",
    "i",
    "på",
    "til",
    "af",
    "udgangspunkt",
}

NUMBER_WORDS = {
    "en": 1,
    "et": 1,
    "to": 2,
    "tre": 3,
    "fire": 4,
    "fem": 5,
    "seks": 6,
    "syv": 7,
    "otte": 8,
    "ni": 9,
    "ti": 10,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text.lower()).strip()


def slug_score(recipe_id: str, terms: list[str]) -> int:
    rid = normalize(recipe_id)
    return sum(1 for t in terms if t in rid)


def format_duration(value: Any) -> str | None:
    if not value:
        return None
    if not isinstance(value, str):
        return str(value)

    text = value.strip().upper()
    # Convert ISO-8601 durations like PT45M to human-friendly Danish text.
    match = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", text)
    if not match:
        plain_match = re.fullmatch(r"(?:(\d+)\s*(?:H|T(?:IME)?))?\s*(?:(\d+)\s*M(?:IN(?:UTTER)?)?\.?)?", text)
        if not plain_match:
            return value
        hours = int(plain_match.group(1) or 0)
        minutes = int(plain_match.group(2) or 0)
        if hours == 0 and minutes == 0:
            return value
        parts: list[str] = []
        if hours:
            parts.append(f"{hours}t")
        if minutes:
            parts.append(f"{minutes}min")
        return " ".join(parts)

    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    if seconds >= 30:
        minutes += 1
    if minutes >= 60:
        hours += minutes // 60
        minutes = minutes % 60

    parts: list[str] = []
    if hours:
        parts.append(f"{hours}t")
    if minutes:
        parts.append(f"{minutes}min")
    if not parts:
        parts.append("0min")
    return " ".join(parts)


def extract_ingredient_lines(ingredients_field: Any) -> list[str]:
    if not isinstance(ingredients_field, list):
        return []

    lines: list[str] = []
    for item in ingredients_field:
        if isinstance(item, str):
            lines.append(item)
            continue
        if isinstance(item, dict):
            for key in ("text", "name", "ingredient", "title"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    lines.append(value.strip())
                    break
    return lines


def load_ingredient_name_map(
    client: firestore.Client,
    scan_limit: int,
) -> dict[str, str]:
    ingredient_map: dict[str, str] = {}
    docs = client.collection("ingredients").limit(scan_limit).stream()
    for doc in docs:
        data = doc.to_dict() or {}
        slug = str(data.get("slug") or doc.id).strip()
        if not slug:
            continue
        name = str(data.get("name") or slug).strip()
        ingredient_map[slug] = name
    return ingredient_map


def build_client(database_id: str) -> firestore.Client:
    creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not creds_json:
        raise RuntimeError(
            "Missing GOOGLE_APPLICATION_CREDENTIALS_JSON. "
            "Add it in the Secrets panel."
        )

    try:
        info = json.loads(creds_json)
    except json.JSONDecodeError as exc:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS_JSON is not valid JSON") from exc

    credentials = service_account.Credentials.from_service_account_info(info)
    project_id = os.environ.get("FIRESTORE_PROJECT_ID") or info.get("project_id")
    if not project_id:
        raise RuntimeError(
            "Missing FIRESTORE_PROJECT_ID and no project_id in credentials JSON. "
            "Add FIRESTORE_PROJECT_ID in the Secrets panel."
        )

    return firestore.Client(project=project_id, credentials=credentials, database=database_id)


def parse_query(query: str) -> tuple[list[str], int | None]:
    normalized = normalize(query)
    limit = None
    limit_match = re.search(r"\bfind\s+(\d+)\b", normalized)
    if limit_match:
        limit = int(limit_match.group(1))
    else:
        word_match = re.search(r"\bfind\s+([a-z]+)\b", normalized)
        if word_match:
            limit = NUMBER_WORDS.get(word_match.group(1))

    segment = normalized
    for marker in (
        "der bruger",
        "med udgangspunkt i",
        "som bruger",
        "indeholder",
        "med",
    ):
        idx = normalized.find(marker)
        if idx != -1:
            segment = normalized[idx + len(marker) :].strip()
            break

    parts = [
        p.strip(" .,:;!?")
        for p in re.split(r"\bog\b|\bsamt\b|,|/|\+|&", segment)
        if p.strip()
    ]

    terms: list[str] = []
    for raw in parts:
        words = [w for w in raw.split() if w and w not in STOPWORDS and not w.isdigit()]
        if not words:
            continue
        term = " ".join(words)
        if term and term not in terms:
            terms.append(term)

    return terms, limit


def find_recipes(
    client: firestore.Client,
    terms: list[str],
    limit: int,
    require_all: bool,
    scan_limit: int,
) -> list[dict[str, Any]]:
    normalized_terms = [normalize(t) for t in terms if normalize(t)]
    if not normalized_terms:
        raise ValueError("Provide at least one non-empty ingredient term")

    ingredient_name_map = load_ingredient_name_map(client=client, scan_limit=scan_limit)

    matches: list[dict[str, Any]] = []
    docs = client.collection("recipes").limit(scan_limit).stream()

    for doc in docs:
        data = doc.to_dict() or {}
        ingredient_lines = extract_ingredient_lines(data.get("ingredients"))
        ingredient_blob = "\n".join(ingredient_lines)
        normalized_blob = normalize(ingredient_blob)
        ingredient_tax_ids = [str(v).strip() for v in (data.get("ingredientTaxIds") or [])]
        normalized_taxonomy_blob = normalize(
            "\n".join(
                f"{slug} {ingredient_name_map.get(slug, slug)}"
                for slug in ingredient_tax_ids
                if slug
            )
        )

        term_hits = [
            t
            for t in normalized_terms
            if t in normalized_blob or t in normalized_taxonomy_blob
        ]
        if require_all and len(term_hits) != len(normalized_terms):
            continue
        if not require_all and not term_hits:
            continue

        matched_lines = [
            line
            for line in ingredient_lines
            if any(t in normalize(line) for t in term_hits)
        ]

        recipe_id = doc.id
        title = data.get("title") or recipe_id
        prep_time = data.get("prepTime")
        cook_time = data.get("cookTime")

        score = (len(term_hits) * 10) + slug_score(recipe_id, normalized_terms)
        matches.append(
            {
                "id": recipe_id,
                "title": title,
                "prepTimeFormatted": format_duration(prep_time),
                "cookTimeFormatted": format_duration(cook_time),
                "matched_terms": term_hits,
                "matched_ingredients": matched_lines[:5],
                "matched_taxonomy": [
                    ingredient_name_map.get(slug, slug)
                    for slug in ingredient_tax_ids
                    if any(t in normalize(f"{slug} {ingredient_name_map.get(slug, slug)}") for t in term_hits)
                ][:5],
                "score": score,
            }
        )

    matches.sort(key=lambda row: (-row["score"], row["title"]))
    return matches[:limit]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Find recipe documents whose ingredients contain specific terms"
    )
    parser.add_argument(
        "--ingredients",
        "-i",
        nargs="+",
        help="Ingredient terms, e.g. broccoli nudler",
    )
    parser.add_argument(
        "--query",
        help=(
            "Natural-language query, e.g. "
            "'Find 3 opskrifter der bruger broccoli og nudler'"
        ),
    )
    parser.add_argument("--limit", "-n", type=int, default=3)
    parser.add_argument("--database", default="recipes", help="Firestore database id")
    parser.add_argument(
        "--scan-limit",
        type=int,
        default=3000,
        help="How many recipe docs to scan before filtering",
    )
    parser.add_argument(
        "--any",
        action="store_true",
        help="Match recipes containing any ingredient term (default is all terms)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON output instead of formatted text",
    )
    args = parser.parse_args()

    parsed_terms: list[str] = []
    parsed_limit: int | None = None
    if args.query:
        parsed_terms, parsed_limit = parse_query(args.query)

    if args.ingredients:
        search_terms = args.ingredients
    else:
        search_terms = parsed_terms

    if not search_terms:
        print(
            "ERROR: Provide --ingredients or a parseable --query with ingredient terms.",
            file=sys.stderr,
        )
        return 1

    limit = parsed_limit or args.limit
    if limit < 1:
        print("ERROR: --limit must be at least 1.", file=sys.stderr)
        return 1

    require_all = not args.any
    try:
        client = build_client(database_id=args.database)
        rows = find_recipes(
            client=client,
            terms=search_terms,
            limit=limit,
            require_all=require_all,
            scan_limit=args.scan_limit,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0

    if not rows:
        mode = "alle" if require_all else "mindst én"
        print(
            f"Ingen opskrifter fundet for {mode} af: {', '.join(search_terms)} "
            f"(scan-limit={args.scan_limit})."
        )
        return 0

    print(f"Fandt {len(rows)} opskrifter:")
    for idx, row in enumerate(rows, start=1):
        print(f"{idx}. {row['title']}")
        print(f"   id: {row['id']}")
        if row.get("prepTimeFormatted"):
            print(f"   Forberedelse: {row['prepTimeFormatted']}")
        if row.get("cookTimeFormatted"):
            print(f"   Tilberedning: {row['cookTimeFormatted']}")
        print(f"   match: {', '.join(row['matched_terms'])}")
        if row["matched_ingredients"]:
            print(f"   ingrediens-hit: {row['matched_ingredients'][0]}")
        elif row["matched_taxonomy"]:
            print(f"   ingrediens-hit: {row['matched_taxonomy'][0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
