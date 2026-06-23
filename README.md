# Agentic Skills

This repository is an export of the skill sources from `/workspace/files/skills`.

Included:
- skill definitions and supporting docs
- no generated archives
- no embedded secrets, API keys, or token material

The public export is intentionally minimal so it can be mirrored or reused safely.

## Skills

### Board games
- **bgg-api** — Query BoardGameGeek for game search, details, hotness, and collection lookups via a Python script (requires a `BGG_TOKEN`).
- **braetspilspriser-api** — Live Danish board game price comparisons and offers from braetspilspriser.dk; search by name or look up offers by Brætspilspriser/BGG ID. No token required.

### Reddit
- **reddit-rss** — On-demand or recurring summaries of recent `/r/boardgames` posts from Reddit's public RSS feed. No token required.

### Grocery offers (eTilbudsavis)
- **bilka-weekly-offers** — Fetch the current week's Bilka offers from etilbudsavis.dk and save them to `offers/bilka/bilka_{year}_week-{weekNumber}.json`.
- **rema1000-weekly-offers** — Fetch the current week's REMA 1000 offers from etilbudsavis.dk and save them to `offers/rema1000/rema1000_{year}_week-{weekNumber}.json`.
- **rema1000-offer-recipes** — Build money-saving dinner/recipe suggestions from this week's discounted REMA 1000 items and save the chosen recipe as markdown in `recipes/`.

### Recipes (Firestore)
- **find-opskrifter** — Find recipes by ingredient(s) in the `lillefar-com` Firestore database, with Danish UI and human-friendly durations (e.g. `Forberedelse: 45min`).
- **ingredient-recipe-finder** — English-language ingredient-based recipe lookup against the same `lillefar-com` Firestore data.
