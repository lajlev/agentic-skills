# Agentic Skills

![Agentic skills illustration](assets/agentic-skills.png)

A collection of self-contained **agentic skills** — small, focused capabilities (a `SKILL.md` describing when and how to use it, plus any supporting scripts) that an AI agent can load on demand to perform a real task: querying APIs, fetching weekly grocery offers, or finding recipes.

Each skill is just a folder of plain files, so it isn't tied to any single tool. You can use them with:

- **Claude Code** — drop a skill folder into your project (or `~/.claude/skills/`) and the agent picks it up automatically; trigger it by describing the task or with `/<skill-name>`.
- **Codex / OpenAI agents** — point your agent at the `SKILL.md` as instructions; several skills ship an `agents/openai.yaml` for this.
- **Any other agentic setup** — the `SKILL.md` is human- and model-readable, and the scripts run standalone (Python / bash), so you can wire them into any framework or run them by hand.


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
