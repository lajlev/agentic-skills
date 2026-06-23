#!/usr/bin/env python3
import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

DEFAULT_URL = "https://www.reddit.com/r/boardgames.rss"
USER_AGENT = "codex-reddit-rss-skill/1.0"
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


@dataclass
class FeedItem:
    title: str
    link: str
    published: str
    published_iso: str


def parse_feed(url: str) -> list[FeedItem]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as response:
        raw = response.read()

    root = ET.fromstring(raw)
    items: list[FeedItem] = []

    if root.tag.endswith("feed"):
        for node in root.findall("atom:entry", ATOM_NS):
            title = (node.findtext("atom:title", default="", namespaces=ATOM_NS) or "").strip()
            published = (
                node.findtext("atom:updated", default="", namespaces=ATOM_NS)
                or node.findtext("atom:published", default="", namespaces=ATOM_NS)
                or ""
            ).strip()
            link = ""
            for link_node in node.findall("atom:link", ATOM_NS):
                if (link_node.attrib.get("rel") or "alternate") == "alternate":
                    link = (link_node.attrib.get("href") or "").strip()
                    break

            published_iso = ""
            if published:
                try:
                    published_iso = datetime.fromisoformat(published).astimezone(timezone.utc).isoformat()
                except Exception:
                    published_iso = ""

            items.append(
                FeedItem(
                    title=title,
                    link=link,
                    published=published,
                    published_iso=published_iso,
                )
            )
        return items

    for node in root.findall(".//item"):
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        published = (node.findtext("pubDate") or "").strip()

        published_iso = ""
        if published:
            try:
                published_iso = parsedate_to_datetime(published).astimezone(timezone.utc).isoformat()
            except Exception:
                published_iso = ""

        items.append(
            FeedItem(
                title=title,
                link=link,
                published=published,
                published_iso=published_iso,
            )
        )

    return items


def filter_by_hours(items: list[FeedItem], hours: int | None) -> list[FeedItem]:
    if hours is None:
        return items

    cutoff = datetime.now(timezone.utc) - timedelta(hours=max(1, hours))
    kept: list[FeedItem] = []
    for item in items:
        if not item.published_iso:
            continue
        try:
            ts = datetime.fromisoformat(item.published_iso)
        except Exception:
            continue
        if ts >= cutoff:
            kept.append(item)
    return kept


def sort_newest(items: list[FeedItem]) -> list[FeedItem]:
    def key(item: FeedItem) -> datetime:
        if item.published_iso:
            try:
                return datetime.fromisoformat(item.published_iso)
            except Exception:
                pass
        return datetime.min.replace(tzinfo=timezone.utc)

    return sorted(items, key=key, reverse=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch and summarize Reddit RSS posts.")
    parser.add_argument("--url", default=DEFAULT_URL, help="RSS feed URL")
    parser.add_argument("--limit", type=int, default=10, help="Number of entries to print")
    parser.add_argument("--hours", type=int, help="Only include posts from the last N hours")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    parser.add_argument(
        "--format",
        choices=["plain", "markdown"],
        default="plain",
        help="Human-readable output format",
    )
    parser.add_argument(
        "--timezone",
        default="UTC",
        help="Timezone for printed timestamps (for example Europe/Copenhagen)",
    )
    parser.add_argument(
        "--title-max",
        type=int,
        default=90,
        help="Maximum title length in human-readable output",
    )
    return parser


def format_timestamp(iso_value: str, timezone_name: str) -> str:
    if not iso_value:
        return "unknown"
    try:
        ts = datetime.fromisoformat(iso_value)
        local_ts = ts.astimezone(ZoneInfo(timezone_name))
        return local_ts.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_value


def truncate_title(title: str, max_len: int) -> str:
    if max_len < 10:
        max_len = 10
    if len(title) <= max_len:
        return title
    return f"{title[: max_len - 3].rstrip()}..."


def main() -> int:
    args = build_parser().parse_args()
    try:
        items = parse_feed(args.url)
    except Exception as exc:
        print(f"Failed to fetch RSS feed: {exc}", file=sys.stderr)
        return 1

    items = sort_newest(filter_by_hours(items, args.hours))
    limit = max(1, args.limit)
    items = items[:limit]

    if args.json:
        print(json.dumps([asdict(item) for item in items], ensure_ascii=False, indent=2))
        return 0

    if not items:
        print("No RSS items found for the selected filter.")
        return 0

    tz_name = args.timezone
    try:
        ZoneInfo(tz_name)
    except Exception:
        print(f"Invalid timezone: {tz_name}", file=sys.stderr)
        return 2

    if args.format == "markdown":
        print(f"### /r/boardgames ({len(items)} posts)")
        if args.hours:
            print(f"_Window: last {args.hours}h | Timezone: {tz_name}_")
        else:
            print(f"_Timezone: {tz_name}_")
        for idx, item in enumerate(items, start=1):
            title = truncate_title(item.title, args.title_max)
            when = format_timestamp(item.published_iso, tz_name)
            print(f"{idx}. [{title}]({item.link}) ({when})")
        return 0

    for idx, item in enumerate(items, start=1):
        when = format_timestamp(item.published_iso, tz_name)
        title = truncate_title(item.title, args.title_max)
        print(f"{idx}. {title}")
        print(f"   published={when} ({tz_name})")
        print(f"   link={item.link}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
