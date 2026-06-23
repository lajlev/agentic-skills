---
name: rema1000-offer-recipes
description: Use when the user asks for dinner ideas or recipes and wants to save money using this week's REMA 1000 tilbudsavis. Fetch or refresh weekly REMA 1000 offers, build recipe suggestions that use discounted items, and save the selected recipe as markdown in recipes/.
---

# REMA 1000 Offer Recipes

## Workflow

1. Refresh weekly offers first:
```bash
bash /workspace/skills/rema1000-weekly-offers/scripts/save_weekly_offers.sh
```
If the fetch step fails, continue with the newest existing file in `offers/rema1000/`.

2. Load the newest file matching:
`offers/rema1000/rema1000_{year}_week-{weekNumber}.json`

3. Identify savings opportunities:
- Prefer offers where `prePrice` is present and greater than `price`.
- It is allowed to include regular-priced items for a complete, good recipe.

4. Suggest recipe options:
- Return 1-3 dinner recipes for the requested number of people.
- For each recipe, include:
  - recipe name,
  - short reason why it fits,
  - key offer items used,
  - estimated savings from known discounted items.

5. If the user selects a recipe, save markdown in:
`recipes/`
Use filename format:
`YYYY-MM-DD-<slugified-title>.md`

6. Use this markdown structure when saving:

```markdown
# <Recipe title>

## Metadata
- Date: <YYYY-MM-DD>
- Servings: <number>
- Source offers file: <relative path>
- Offer week: <year-week>

## Why this recipe
<1-3 short bullets on taste/value fit>

## Offer items used
- <item> - <offer price> (before <prePrice>, saved <amount>)

## Other ingredients (regular price)
- <item> - <amount>

## Ingredients
- <full ingredient list with amounts>

## Steps
1. <step>
2. <step>
3. <step>

## Estimated budget
- Offer items subtotal: <amount DKK>
- Non-offer items subtotal: <amount DKK>
- Estimated total: <amount DKK>
- Estimated savings vs regular prices: <amount DKK>
```

## Response Rules

- Always use Denmark-local week/day context when talking about "this week".
- Keep ingredient names close to the offer wording so they are easy to find in the store.
- If savings cannot be estimated for all items, clearly label only the known savings.
