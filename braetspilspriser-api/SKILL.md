# Braetspilspriser API Skill

Use this skill when the user wants live price/search data from `https://braetspilspriser.dk/api/plugin`.

## Trigger
- User asks for Danish board game price comparisons.
- User asks to search products on Brætspilspriser.
- User asks for offers/details by Brætspilspriser item ID or BoardGameGeek ID.

## Requirements
- Python at `.venv/bin/python`
- No API token is required.

## Workflow
1. Use `.venv/bin/python skills/braetspilspriser-api/scripts/braetspilspriser_query.py`.
2. For product discovery, run with `search --query "<name>"`.
3. For price offers/details, run with `info --eid <bgg_id>` or `info --id <item_id>`.
4. Return concise results with item URLs and best-price/offer summary.

## Commands
- Search products:
  - `.venv/bin/python skills/braetspilspriser-api/scripts/braetspilspriser_query.py search --query "Slay the Spire" --limit 5`
- Get price offers by BGG id:
  - `.venv/bin/python skills/braetspilspriser-api/scripts/braetspilspriser_query.py info --eid 338960 --limit 3`
- Get raw JSON:
  - `.venv/bin/python skills/braetspilspriser-api/scripts/braetspilspriser_query.py info --eid 338960 --json`

## Safety
- No credentials are needed for this API.
- Keep responses concise; only include fields useful for the user request.
