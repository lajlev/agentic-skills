#!/usr/bin/env python3
import argparse
import os
import sys

from boardgamegeek import BGGClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Query BoardGameGeek using the bgg-api package and BGG_TOKEN."
    )
    parser.add_argument("--query", required=True, help="Game name to search.")
    parser.add_argument("--limit", type=int, default=5, help="Number of results to print.")
    parser.add_argument(
        "--details",
        action="store_true",
        help="Fetch and print expanded details for each result.",
    )
    return parser


def require_token() -> str:
    token = os.getenv("BGG_TOKEN")
    if not token:
        print(
            "BGG_TOKEN is not set. Add it in the Secrets panel as BGG_TOKEN.",
            file=sys.stderr,
        )
        sys.exit(2)
    return token


def main() -> int:
    args = build_parser().parse_args()
    token = require_token()

    client = BGGClient(access_token=token)
    results = client.search(query=args.query)

    if not results:
        print(f'No results found for "{args.query}".')
        return 0

    sliced = results[: max(1, args.limit)]
    for idx, item in enumerate(sliced, start=1):
        game_id = getattr(item, "id", None)
        name = getattr(item, "name", "Unknown")
        year = getattr(item, "year", None)
        line = f"{idx}. {name}"
        if year:
            line += f" ({year})"
        if game_id:
            line += f" - https://boardgamegeek.com/boardgame/{game_id}"
        print(line)

        if args.details and game_id:
            game = client.game(game_id=game_id)
            min_players = getattr(game, "min_players", None)
            max_players = getattr(game, "max_players", None)
            play_time = getattr(game, "playing_time", None)
            rank = getattr(game, "bgg_rank", None)
            rating = getattr(game, "rating_average", None)
            print(
                f"   players={min_players}-{max_players} play_time={play_time}m "
                f"rank={rank} rating={rating}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
