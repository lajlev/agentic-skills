#!/usr/bin/env python3
import argparse
import json
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://braetspilspriser.dk/api"


def fetch_json(endpoint: str, params: dict) -> dict:
    query = urlencode({k: v for k, v in params.items() if v not in (None, "")})
    url = f"{BASE_URL}/{endpoint}?{query}"
    req = Request(url, headers={"User-Agent": "codex-braetspilspriser-skill/1.0"})
    with urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def cmd_search(args: argparse.Namespace) -> int:
    payload = fetch_json(
        "search",
        {
            "sitename": args.sitename,
            "search": args.query,
            "currency": args.currency,
            "destination": args.destination,
            "delivery": args.delivery,
            "stock": "Y" if args.in_stock_only else None,
            "tags": args.tags,
            "page": args.page,
        },
    )

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    items = payload.get("items", [])
    if not items:
        print(f'No products found for "{args.query}".')
        return 0

    print(f"Found {payload.get('count', len(items))} products (page {payload.get('pages', 1)} pages total).")
    for idx, item in enumerate(items[: max(1, args.limit)], start=1):
        item_id = item.get("id")
        name = item.get("name", "Unknown")
        version = item.get("version")
        best = item.get("bestprice")
        best_ccy = item.get("bestprice_ccy")

        line = f"{idx}. [{item_id}] {name}"
        if version:
            line += f" | {version}"
        if best is not None:
            line += f" | best={best} {best_ccy or ''}".rstrip()
        print(line)

    return 0


def cmd_info(args: argparse.Namespace) -> int:
    if not args.id and not args.eid:
        print("Either --id or --eid must be provided.", file=sys.stderr)
        return 2

    payload = fetch_json(
        "info",
        {
            "sitename": args.sitename,
            "id": args.id,
            "eid": args.eid,
            "currency": args.currency,
            "destination": args.destination,
            "delivery": args.delivery,
            "sort": args.sort,
            "locale": args.locale,
            "preferred_language": args.preferred_language,
        },
    )

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    items = payload.get("items", [])
    if not items:
        print("No matching items found.")
        return 0

    print(f"Currency: {payload.get('currency')} | Site: {payload.get('sitename')} | URL: {payload.get('url')}")
    for idx, item in enumerate(items[: max(1, args.limit)], start=1):
        prices = item.get("prices", [])
        best = prices[0] if prices else None
        print(f"{idx}. [{item.get('id')}] {item.get('name', 'Unknown')}")
        print(f"   item_url={item.get('url')}")
        print(f"   bgg_id={item.get('external_id')} offers={len(prices)}")
        if best:
            print(
                "   best_offer="
                f"price:{best.get('price')} product:{best.get('product')} "
                f"shipping:{best.get('shipping')} stock:{best.get('stock')} country:{best.get('country')}"
            )

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query Brætspilspriser API endpoints.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Search products via /api/search")
    search.add_argument("--query", required=True, help="Search text")
    search.add_argument("--limit", type=int, default=5, help="Max products to print")
    search.add_argument("--page", type=int, default=1, help="Results page")
    search.add_argument("--tags", help="Comma-separated tag IDs")
    search.add_argument("--in-stock-only", action="store_true", help="Only include in-stock offers")
    search.add_argument("--json", action="store_true", help="Print raw JSON response")
    search.add_argument("--sitename", default="codex", help="Value for required sitename parameter")
    search.add_argument("--currency", default="DKK", help="Currency, e.g. DKK/EUR/SEK/GBP/USD")
    search.add_argument("--destination", default="DK", help="Shipping destination country code")
    search.add_argument("--delivery", default="PACKAGE,POSTOFFICE", help="Comma-separated delivery methods")
    search.set_defaults(func=cmd_search)

    info = subparsers.add_parser("info", help="Get item offers via /api/info")
    info.add_argument("--id", help="Comma-separated Brætspilspriser item IDs")
    info.add_argument("--eid", help="Comma-separated BoardGameGeek IDs")
    info.add_argument("--limit", type=int, default=5, help="Max items to print")
    info.add_argument("--sort", default="SMART", help="Sort mode: SMART/CHEAP1/CHEAP2/STOCK")
    info.add_argument("--locale", help="Locale: da/en/sv/fr/de")
    info.add_argument("--preferred-language", help="Preferred language code, e.g. GB, DK, SE")
    info.add_argument("--json", action="store_true", help="Print raw JSON response")
    info.add_argument("--sitename", default="codex", help="Value for required sitename parameter")
    info.add_argument("--currency", default="DKK", help="Currency, e.g. DKK/EUR/SEK/GBP/USD")
    info.add_argument("--destination", default="DK", help="Shipping destination country code")
    info.add_argument("--delivery", default="PACKAGE,POSTOFFICE", help="Comma-separated delivery methods")
    info.set_defaults(func=cmd_info)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        return int(args.func(args))
    except Exception as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
