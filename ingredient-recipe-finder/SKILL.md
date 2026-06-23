---
name: ingredient-recipe-finder
description: Find recipe matches in Firestore by one or more ingredients. Always use the Firestore client (`google.cloud.firestore`) against project `lillefar-com`, database `recipes`, collections `recipes` and `ingredients`.
---

# Ingredient Recipe Finder

Use this skill when the user wants recipe lookup by ingredients from Firestore data in:
- project: `lillefar-com`
- database: `recipes`
- collections: `recipes`, `ingredients`

Hard requirements:
- Always access recipe data with the Firestore client (`google.cloud.firestore`).
- Never show raw ISO durations such as `PT45M`; format as human-friendly values, e.g. `Forberedelse: 45min`.

## Workflow

1. Run the ingredient search script from `/workspace`:
```bash
scripts/venv_run.sh skills/ingredient-recipe-finder/scripts/find_recipes_by_ingredients.py \
  --query "Find 3 opskrifter der bruger broccoli og nudler"
```

Quick examples:
```bash
# Match all terms (default)
scripts/venv_run.sh skills/ingredient-recipe-finder/scripts/find_recipes_by_ingredients.py \
  --query "Find 3 opskrifter der bruger broccoli og nudler"

# Explicit terms
scripts/venv_run.sh skills/ingredient-recipe-finder/scripts/find_recipes_by_ingredients.py \
  --ingredients broccoli nudler --limit 3

# Match any term
scripts/venv_run.sh skills/ingredient-recipe-finder/scripts/find_recipes_by_ingredients.py \
  --ingredients broccoli nudler --any --limit 3
```

2. Default behavior requires all requested ingredients to match in each recipe.
- Example query: `--query "Find 3 opskrifter der bruger broccoli og nudler"` returns recipes containing both terms.
- Example explicit args: `--ingredients broccoli nudler --limit 3` returns recipes containing both terms.
- Use `--any` when at least one term is enough.
- Matching uses both:
  - `recipes.ingredients` (ingredient text lines),
  - `recipes.ingredientTaxIds` resolved through `ingredients` collection (`name` + `slug`).
 - Output is ranked by number of matched terms and recipe id relevance, then trimmed to requested limit.

3. Return concise results to the user:
- title,
- id,
- formatted time values (e.g. `Forberedelse: 45min`, `Tilberedning: 35min`),
- 1 matched ingredient line.
- Telegram formatting: plain text only (no markdown headings, tables, code blocks, or markdown links).

4. If the user asks for full recipe details, fetch and show:
- full ingredients list,
- full instructions,
- relevant metadata (`title`, `id`, `prepTime`, `cookTime`) with formatted durations in user-facing text.

## Script

Use:
`skills/ingredient-recipe-finder/scripts/find_recipes_by_ingredients.py`

Arguments:
- `--query` (optional): natural-language query with ingredients and optional count.
  - Supports digit and word count forms after `Find`, e.g. `Find 3 ...` and `Find tre ...`.
- `--ingredients` / `-i` (optional): one or more ingredient terms.
- `--limit` / `-n` (optional, default `3`): max recipes returned.
- `--database` (optional, default `recipes`): Firestore database id.
- `--scan-limit` (optional, default `3000`): number of docs scanned.
- `--any` (optional): match any term instead of all terms.
- `--json` (optional): print JSON output for downstream processing.

Note:
- Use either `--query` or `--ingredients`.
- If both are provided, `--ingredients` is used for terms while count can still be inferred from `--query`.

## Environment

Required secrets/env vars:
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`
- `FIRESTORE_PROJECT_ID`

Do not ask the user to paste credentials in chat. If missing, tell the user to add them in the Secrets panel.

## Expected Response Format

When responding to the user, return:
- recipe title,
- recipe id,
- formatted time (no `PTxxM`; use labels like `Forberedelse: 45min`),
- one concrete matched ingredient line.

If no results are found, state that clearly and suggest trying:
- `--any`,
- a larger `--scan-limit`,
- fewer ingredient terms.

For Telegram delivery, always keep output as plain text with simple line breaks and numbered lists.
