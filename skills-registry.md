# Skills Registry

Persistent record of skill coverage for this user.

## Installed Skills
- Name: find-opskrifter
  - Source: local workspace skill (`/workspace/skills/find-opskrifter`)
  - Purpose: Find opskrifter i Firestore ud fra ingredienser med krav om Firestore-klient og menneskeligt tidsformat (fx `Forberedelse: 45min`).
  - Status: active
- Name: ingredient-recipe-finder
  - Source: local workspace skill (`/workspace/skills/ingredient-recipe-finder`)
  - Purpose: Find recipes in Firestore (`lillefar-com`, database `recipes`, collection `recipes`) from one or more ingredient terms.
  - Status: active
- Name: rema1000-weekly-offers
  - Source: local workspace skill (`/workspace/skills/rema1000-weekly-offers`)
  - Purpose: Fetch current-day REMA 1000 weekly tilbudsavis offers from etilbudsavis.dk and save JSON.
  - Status: active
- Name: rema1000-offer-recipes
  - Source: local workspace skill (`/workspace/skills/rema1000-offer-recipes`)
  - Purpose: Build recipe suggestions from this week's REMA 1000 offers and save selected recipes as markdown in `recipes/`.
  - Status: active
- Name: bilka-weekly-offers
  - Source: local workspace skill (`/workspace/skills/bilka-weekly-offers`)
  - Purpose: Fetch current-day Bilka weekly tilbudsavis offers from etilbudsavis.dk and save JSON.
  - Status: active
- Name: google-keep-shopping-list
  - Source: local workspace skill (`/workspace/skills/google-keep-shopping-list`)
  - Purpose: Add items directly to a Google Keep note (default `Indkøbslisten`) using secrets-based authentication.
  - Status: removed (2026-03-17)

## Missing Capabilities
- Capability: none currently tracked
  - Candidate skill: n/a
  - Priority: low

## Skill Change Log
- YYYY-MM-DD: Installed `skill-name` from <source> for <reason>
- YYYY-MM-DD: Updated `skill-name` for <reason>
- YYYY-MM-DD: Removed `skill-name` for <reason>
- 2026-04-23: Added `files/skills/skills-overblik.md` as a persistent quick-reference summary for future "hvad er dine skills?" requests.
- 2026-04-08: Updated personalization policy to always include recipe source attribution in recipe replies (e.g., Mambeno, Arla).
- 2026-04-08: Updated personalization policy to keep REMA 1000 as default for meal plans/shopping and only use Bilka when explicitly requested by the user.
- 2026-04-08: Installed `bilka-weekly-offers` from local for etilbudsavis current-day Bilka offer extraction and JSON export to `offers/bilka/bilka_{year}_week-{weekNumber}.json`.
- 2026-04-08: Standardized Python runtime with `/workspace/scripts/venv_run.sh`, expanded shared `requirements.txt` (Firestore + Calendar API), and updated recipe skills to use the shared runner.
- 2026-03-20: Updated `find-opskrifter` wording and default prompt to enforce exact user-facing time label format (`Forberedelse: 45min`, not `PT45M`) for ingredient-based recipe search.
- 2026-03-20: Updated `find-opskrifter` output contract to avoid raw ISO durations in result payloads and keep only human-readable labels (`Forberedelse: 45min`, `Tilberedning: 35min`).
- 2026-03-20: Updated and revalidated `find-opskrifter` for strict Firestore-client usage and human-readable durations (`Forberedelse: 45min`, not `PT45M`); fixed SKILL frontmatter YAML.
- 2026-03-20: Updated `find-opskrifter` to enforce Firestore client usage and explicit user-facing duration labels (`Forberedelse: 45min`, never `PT45M`).
- 2026-03-20: Hardened `find-opskrifter` setup and runtime errors by documenting `google-cloud-firestore` installation and adding explicit missing-dependency guidance in script output.
- 2026-03-20: Installed `find-opskrifter` from local for ingredient-based Firestore lookup with forced human-readable time formatting (`Forberedelse: 45min`).
- 2026-03-20: Installed `ingredient-recipe-finder` from local for ingredient-based recipe lookup in Firestore database `recipes`.
- 2026-03-20: Updated `ingredient-recipe-finder` trigger description for multi-ingredient queries (e.g. broccoli + nudler) and revalidated skill.
- 2026-03-20: Updated `ingredient-recipe-finder` with natural-language `--query` parsing (e.g. "Find 3 opskrifter der bruger broccoli og nudler") and validated live results.
- 2026-03-20: Updated `ingredient-recipe-finder` with explicit quick-start command examples for combined ingredient lookups (e.g. broccoli + nudler).
- 2026-03-20: Revalidated `ingredient-recipe-finder` on live database `lillefar-com/recipes` with query "Find 3 opskrifter der bruger broccoli og nudler" and confirmed 3 matches.
- 2026-03-20: Revalidated `ingredient-recipe-finder` again on live database `lillefar-com/recipes` for prompt-style query "Find 3 opskrifter der bruger broccoli og nudler" and confirmed stable top-3 results.
- 2026-03-20: Revalidated `ingredient-recipe-finder` on live query "Find 3 opskrifter der bruger broccoli og nudler" and confirmed correct dual-ingredient matching output.
- 2026-03-20: Updated `ingredient-recipe-finder` to require Firestore client usage (`google.cloud.firestore`) and format recipe times as human-friendly labels (e.g. `Forberedelse: 45min` instead of `PT45M`).
- 2026-03-20: Updated `find-opskrifter` with explicit hard rule to always use Firestore client (never Datastore client) and keep user-facing time formatting as `Forberedelse: 45min` (not `PT45M`).
- 2026-03-20: Revalidated `find-opskrifter` with live query "Find 3 opskrifter der bruger broccoli og nudler" and confirmed human-readable time output (e.g. `Forberedelse: 25min`, not `PT25M`).
- 2026-03-12: Installed `rema1000-weekly-offers` from local for etilbudsavis current-day weekly offer extraction and JSON export.
- 2026-03-12: Removed `rema1000-weekly-offers` from local after user request.
- 2026-03-12: Registered `rema1000-weekly-offers` in the skills registry and confirmed status as active.
- 2026-03-10: Installed `rema1000-weekly-offers` from local for automated weekly REMA offers extraction.
- 2026-03-10: Updated `rema1000-weekly-offers` to use OpenAI API for PDF-to-offers extraction.
- 2026-03-10: Updated `rema1000-weekly-offers` with chat-based upvote/downvote flow and persisted preferences.
- 2026-03-12: Recreated and validated `rema1000-weekly-offers` for eTilbudsavis current-day week matching and JSON export to `offers/rema1000/rema1000_{year}_week-{weekNumber}.json`.
- 2026-03-12: Installed `rema1000-offer-recipes` from local to enforce recipe suggestions based on this week's REMA 1000 offers and markdown save in `recipes/`.
- 2026-03-16: Installed `google-keep-shopping-list` from local to add grocery items directly to Google Keep note `Indkøbslisten`.
- 2026-03-17: Removed `google-keep-shopping-list` from local after user request.
- 2026-03-19: Installed `mambeno-opskrifter-firestore` from local for sitemap-based recipe extraction from mambeno.dk and Firestore sync.
- 2026-03-19: Updated `mambeno-opskrifter-firestore` with batch support (`--offset`) and improved timeout resilience for partial sitemap failures.
- 2026-03-19: Updated `mambeno-opskrifter-firestore` with clearer Firestore 403 permission error handling.
- 2026-03-19: Updated `mambeno-opskrifter-firestore` with clearer Firestore permission diagnostics and troubleshooting guidance.
- 2026-03-19: Updated `mambeno-opskrifter-firestore` with runtime-budgeted chunk sync (`--max-runtime-seconds`, `--fetch-batch-size`) and resumable `next_offset` output.
- 2026-03-19: Updated `mambeno-opskrifter-firestore` docs with corrected command references and explicit chunked-run guidance to avoid CLI timeout.
- 2026-03-19: Validated `mambeno-opskrifter-firestore` live against 3,483 discovered URLs (dry-run OK) and documented Firestore 403 remediation with explicit credentials.
- 2026-03-19: Updated `mambeno-opskrifter-firestore` runner to skip repeated dependency installation and reduce 300s timeout risk.
- 2026-03-19: Updated `mambeno-opskrifter-firestore` from Firestore API assumptions to Datastore Mode writes and completed full sync of 3,483 recipes to kind `mambeno_recipes`.
- 2026-03-19: Updated `mambeno-opskrifter-firestore` with auto-resume state file, default runtime budget, and validated Datastore write success (`datastore_writes=1` smoke test).
- 2026-03-19: Removed `mambeno-opskrifter-firestore` from local after user request.
