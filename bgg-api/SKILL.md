# BGG API Skill

Use this skill when the user wants BoardGameGeek data (search, game details, hotness, collection-related lookups) through Python.

## Trigger
- User asks for board game info from BGG.
- User asks to query BGG with their API token.
- User asks for scripted/repeatable BGG lookups.

## Requirements
- Python virtual environment in `.venv`
- Package `bgg-api` installed in that environment
- `BGG_TOKEN` environment variable present

## Workflow
1. Validate that `BGG_TOKEN` exists in the environment.
2. Run `.venv/bin/python skills/bgg-api/scripts/bgg_query.py --query "<name>"`.
3. If user asks for detailed metadata, use `--details`.
4. Return concise results with BGG URLs and key stats.

## Commands
- Quick search:
  - `.venv/bin/python skills/bgg-api/scripts/bgg_query.py --query "Terraforming Mars"`
- Search with details:
  - `.venv/bin/python skills/bgg-api/scripts/bgg_query.py --query "Brass" --details --limit 3`

## Safety
- Never print or expose `BGG_TOKEN`.
- If `BGG_TOKEN` is missing, instruct user to add it via Secrets as `BGG_TOKEN`.
